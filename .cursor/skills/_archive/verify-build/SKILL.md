---
name: verify-build
description: >
  Runs comprehensive verification after build-executor completes: linting, typechecking,
  formatting, and test suite via parallel subagents. Surfaces failures to the user with
  recommendations and approve/deny/modify choices. Use after build-executor passes milestone,
  phase, or full-build checkpoints (build-executor may invoke this several times in one long
  session). Also usable standalone to verify the codebase at any point.
---

# Verify Build

Run all quality checks in parallel, collect results, and walk the user through any failures
with actionable recommendations.

**Cross-cutting:** [considerations.md](../considerations.md), [connectivity-gates.md](../connectivity-gates.md).

**Connectivity:** Same blocking checks as [08-verify-build](../08-verify-build/SKILL.md) §Connectivity — H0c + `tests/integration` must pass.

## When to use

- **After build-executor**: Automatically invoked at milestone boundaries, phase boundaries,
  or after the full build completes.
- **Standalone**: Can be invoked any time to verify the current state of the codebase.
- **Pre-PR**: Run before creating a minor or major PR to ensure all checks pass.

## Prerequisites

1. **Execution plan**: `workflow-state.yaml + execution plan artifact` must exist to determine the tech stack
   (linter, formatter, typechecker, test runner).
2. **Codebase**: Source files and tests must exist to check.
3. If the execution plan is missing, ask the user for the tool commands directly via
   AskQuestion.

## State management

**Canonical:** repo-root [`workflow-state.yaml`](../../workflow-state.yaml) §`stages.08-verify-build`.
Rules: [workflow-state-reference.md](../workflow-state-reference.md).

**Detail:** `{artifacts_dir}/reports/verification-report.md`` — overwrite on each run; set `report` path on the stage block.

### On invocation

1. Read `workflow-state.yaml` §`stages.08-verify-build`.
2. If the report exists, ask the user: "Re-run all checks, or review the last report?"
3. If re-running, overwrite the previous report and set stage `status: in_progress`.
4. On completion: `status: completed`, `overall: pass|fail`, append `{artifacts_dir}/reports/verification-report.md`` to `artifacts`.

## Workflow

### Phase 1 — Load Check Configuration

Read `workflow-state.yaml + execution plan artifact` §Tech Stack Summary to determine:

| Check | Tool | Command | Source |
|-------|------|---------|--------|
| Lint | [e.g., Ruff] | [e.g., `ruff check .`] | execution-plan.md |
| Format | [e.g., Ruff format] | [e.g., `ruff format --check .`] | execution-plan.md |
| Typecheck | basedpyright | `uv run basedpyright src tests` | `docs/typing-policy.md` |
| Tests | [e.g., pytest] | [e.g., `pytest -v`] | execution-plan.md |
| Performance (optional) | [e.g., pytest marker, locust, `ab`/`hey`] | per test-plan.md / execution-plan.md | test-plan.md |
| Security | `pip-audit` + secret scan | `pip-audit` + `rg` patterns | always |
| Data Integrity | `scripts/verify_data.py` | `python scripts/verify_data.py` | data-management-plan.md |

If any tool is not configured, surface as `[Decision]` via AskQuestion. **Performance** row
applies only when `docs/test-plan.md` or `workflow-state.yaml + execution plan artifact` defines commands, markers,
or thresholds for latency, throughput, load, or soak — otherwise skip that agent entirely.
**Security** always runs — install `pip-audit` if not present.

### Phase 2 — Run Checks in Parallel

Launch subagents in **one** message using the Task tool. **Always** run five agents (lint,
format, typecheck, tests, security); add a **sixth — Performance** only when Phase 1 listed
perf commands and thresholds. If perf validation was implied by the Research Brief but specs
omit it, surface `[Ambiguity]` instead of inventing benchmarks
([considerations.md §4](../considerations.md#4-performance-testing)).

**Agent 1 — Linter**: Run the lint command against the full codebase.
- Capture stdout/stderr
- Parse output into structured findings (file, line, rule, message, severity)
- Return: pass/fail status, finding count, full output

**Agent 2 — Formatter**: Run the format check (dry-run/check mode, no writes).
- Capture files that would be reformatted
- Return: pass/fail status, file count, list of files

**Agent 3 — Typechecker**: Run the typecheck command.
- Capture type errors
- Parse output into structured findings (file, line, error, message)
- Return: pass/fail status, error count, full output

**Agent 4 — Test Suite**: Run the full test suite.
- Capture test results
- Parse into: total, passed, failed, skipped, errors
- Return: pass/fail status, counts, failure details (test name, assertion, traceback)

**Agent 5 — Security**: Always runs. Three checks:
- **Dependency CVEs**: Run `pip-audit` (install if needed) to scan for known vulnerabilities
  in installed packages. Return: pass/fail, list of CVEs with severity and affected package.
- **Committed secrets**: Scan the codebase for accidentally committed secrets using pattern
  matching (`rg` for API keys, tokens, passwords, private keys — common patterns like
  `AKIA`, `sk-`, `ghp_`, `-----BEGIN.*PRIVATE KEY`, `.env` files with values). Return:
  pass/fail, list of files and matched patterns.
- **Known vulnerability patterns**: Check for common insecure patterns (e.g., `eval()`,
  `pickle.loads()` on untrusted input, `subprocess.shell=True` with user input). Return:
  pass/fail, list of findings with file, line, and pattern.

**Agent 6 — Performance (optional)**: When Phase 1 defined perf/load/soak commands, run them;
capture metrics vs documented thresholds; return pass/fail with evidence.

**Agent 7 — Data Integrity**: Verify all staged data assets are present and valid.
- Run `scripts/verify_data.py` if it exists (generated by the data-management skill)
- If the script doesn't exist, fall back to checking `docs/spec.md §Data` §Local
  Paths — verify each asset exists at its expected path with correct file size
- Cross-reference `workflow-state.yaml + execution plan artifact` §Data Dependencies — flag any asset that is
  needed by a completed or in-progress task but is missing or unverified
- Return: pass/fail status, per-asset results (name, expected path, exists, size match)
- Data integrity failures are **advisory** — they do not block PRs but are reported in the
  verification report under a dedicated Data Integrity section so the user knows if data
  needs re-staging

The parent waits for every launched agent to finish.

### Phase 3 — Compile Results

Merge all agent outputs into a verification report:

```markdown
# Verification Report

> **Generated**: [date/time]
> **Scope**: [milestone M1 / phase 1 / full build / standalone]
> **Branch**: [current branch]
> **Commit**: [current commit hash]

## Summary

| Check | Status | Findings | Tool |
|-------|--------|----------|------|
| Lint | PASS/FAIL | [N] issues | [tool] |
| Format | PASS/FAIL | [N] files | [tool] |
| Typecheck | PASS/FAIL | [N] errors | [tool] |
| Tests | PASS/FAIL | [N] failed / [N] total | [tool] |
| Security | PASS/FAIL | [N] CVEs, [N] secrets, [N] patterns | pip-audit + rg |
| Performance | PASS/FAIL / SKIPPED | [summary] | [tool or N/A] |
| Data Integrity | PASS/FAIL / SKIPPED | [N] assets verified / [N] total | verify_data.py |

**Overall**: PASS / FAIL ([N] checks passed, [N] failed)

## Lint Results

[If PASS]: All files pass lint checks.

[If FAIL]:
| # | File | Line | Rule | Severity | Message |
|---|------|------|------|----------|---------|
| 1 | [file] | [line] | [rule] | error/warning | [message] |
| ... | ... | ... | ... | ... | ... |

## Format Results

[If PASS]: All files are correctly formatted.

[If FAIL]:
Files that need reformatting:
- [file1]
- [file2]

## Typecheck Results

[If PASS]: No type errors found.

[If FAIL]:
| # | File | Line | Error | Message |
|---|------|------|-------|---------|
| 1 | [file] | [line] | [code] | [message] |
| ... | ... | ... | ... | ... |

## Test Results

[If PASS]: All [N] tests passed.

[If FAIL]:
| # | Test | File | Assertion | Traceback Summary |
|---|------|------|-----------|--------------------|
| 1 | [test_name] | [file] | [expected vs actual] | [brief traceback] |
| ... | ... | ... | ... | ... |

## Security Results

[If PASS]: No CVEs, committed secrets, or vulnerability patterns found.

[If FAIL]:
### Dependency CVEs
| # | Package | Version | CVE | Severity | Fix Version |
|---|---------|---------|-----|----------|-------------|
| 1 | ... | ... | ... | critical/high/medium/low | ... |

### Committed Secrets
| # | File | Line | Pattern | Matched |
|---|------|------|---------|---------|
| 1 | ... | ... | API key / token / private key | ... |

### Vulnerability Patterns
| # | File | Line | Pattern | Risk |
|---|------|------|---------|------|
| 1 | ... | ... | eval() on untrusted input | high |

## Performance Results

[If SKIPPED]: No perf/load/soak commands defined in specs.

[If PASS]: All perf checks within thresholds.

[If FAIL]:
| # | Scenario | Metric | Threshold | Actual | Notes |
|---|----------|--------|-----------|--------|-------|
| 1 | ... | ... | ... | ... | ... |

## Data Integrity Results

[If SKIPPED]: No data-management-plan.md or verify_data.py found.

[If PASS]: All [N] staged data assets verified.

[If FAIL]:
| # | Asset | Expected Path | Exists | Size Match | Notes |
|---|-------|---------------|--------|------------|-------|
| 1 | [D1] | [data/weights/esm2/] | Yes/No | Yes/No/N/A | [missing, corrupted, wrong size] |
| ... | ... | ... | ... | ... | ... |

⚠️ Data integrity failures are advisory — they do not block PRs but indicate data
may need re-staging via the data-management skill.
```

Write the report to `{artifacts_dir}/reports/verification-report.md``.

### Phase 4 — Handle Failures

If all checks pass, report success and proceed:

```
Verification Complete — ALL CHECKS PASSED.

  Lint:        PASS (0 issues)
  Format:      PASS (0 files to reformat)
  Typecheck:   PASS (0 errors)
  Tests:       PASS ([N] / [N] passed)
  Security:    PASS (0 CVEs, 0 secrets, 0 patterns)
  Performance: SKIPPED (not specified) / PASS
  Data:        PASS ([N] assets verified) / SKIPPED

Ready for PR creation.
```

If any check fails, process each failure category. For each failing check, present the
failures to the user via AskQuestion with **approve, deny, or modify** options.

#### Lint failures

Group by severity (errors first, then warnings). For each group:

```
prompt: "[Lint] [N] lint errors found across [M] files. Top issue: [rule] in [file:line].
  Recommendation: Auto-fix with `ruff check --fix` — Ruff can auto-fix [X] of [N] issues."

options:
  1. "Approve auto-fix — run `ruff check --fix` and re-verify"  [recommended]
  2. "Deny — these are false positives, suppress with noqa comments"
  3. "Modify — I'll fix specific issues manually, show me the list"
  4. "Let me explain / provide more context"
```

#### Format failures

```
prompt: "[Format] [N] files would be reformatted. These are style-only changes.
  Recommendation: Auto-format all files."

options:
  1. "Approve — run the formatter on all [N] files"  [recommended]
  2. "Deny — the current formatting is intentional"
  3. "Modify — format only specific files, show me the list"
  4. "Let me explain / provide more context"
```

#### Typecheck failures

For each type error (or grouped by file if many):

```
prompt: "[Typecheck] [N] type errors found. Most critical: [file:line] — [error message].
  Recommendation: [specific fix based on the error type — e.g., add type annotation, 
  fix return type, handle Optional]."

options:
  1. "Approve recommendation — apply the fix"  [recommended]
  2. "Deny — suppress with type: ignore comment"
  3. "Modify — I'll provide the correct type"
  4. "Let me explain / provide more context"
```

#### Test failures

For each failing test:

```
prompt: "[Test] test_[name] FAILED in [file]. 
  Expected: [expected]. Got: [actual].
  Recommendation: [analysis of likely cause — e.g., 'The implementation returns X but 
  the spec says Y. The implementation may need to be updated.']"

options:
  1. "Approve — fix the implementation to match the test"  [recommended]
  2. "Deny — the test is wrong, update the test"
  3. "Modify — both need changes, I'll explain"
  4. "Let me explain / provide more context"
```

#### Security failures

Security findings are **always blocking** — present each category:

```
prompt: "[Security] [N] dependency CVEs found. Most critical: [package] [CVE-ID] (severity: [X]).
  Fix available: upgrade to [version].
  Also found: [N] committed secrets, [N] vulnerability patterns."

options:
  1. "Approve — upgrade vulnerable packages and remove secrets"  [recommended]
  2. "Deny — accept risk for now, document in known issues"
  3. "Modify — I'll review each finding individually"
  4. "Let me explain / provide more context"
```

For committed secrets specifically: always recommend removing them and using platform secrets
or environment variables. Never leave secrets in code even if the user denies.

#### Performance failures

When Agent 5 ran and regressed thresholds:

```
prompt: "[Performance] [scenario] exceeded threshold: [metric] actual [X] vs max [Y].
  Recommendation: [profile, scale resources, fix hot path, or revise spec if target was wrong]."

options:
  1. "Approve — apply the recommended fix and re-verify"  [recommended]
  2. "Deny — accept the regression; document deviation in spec"
  3. "Modify — adjust threshold after doc/spec change"
  4. "Let me explain / provide more context"
```

### Phase 5 — Apply Fixes

For each approved fix:

1. Apply the fix (auto-fix, manual edit, or suppression as chosen).
2. **Re-run only the affected check** to verify the fix worked.
3. If the fix introduces new failures, surface those as a new round.
4. Commit fixes as a single commit: `chore: fix [check] issues from verification`

If any fixes were denied (suppressions), record the reason in the verification report
under a **Suppressions** section.

### Phase 6 — Re-verify

After all fixes are applied:

1. Re-run all checks from Phase 2 in parallel (including Performance when it was in scope).
2. If all pass, report success.
3. If new failures appear, loop back to Phase 4 for the new failures.
4. Maximum 3 fix-verify loops. If still failing after 3 rounds, report the remaining
   failures and ask the user how to proceed:
   - "Continue with known failures — I'll address them later"
   - "Stop — I need to investigate manually"

### Phase 7 — Summary

```
Verification Complete.

Results:
  Lint:        PASS ([N] auto-fixed, [N] suppressed)
  Format:      PASS ([N] files reformatted)
  Typecheck:   PASS ([N] fixed, [N] suppressed)
  Tests:       PASS ([N] / [N])
  Security:    PASS ([N] CVEs fixed, [N] secrets removed)
  Performance: PASS / SKIPPED
  Data:        PASS ([N] / [N] assets) / SKIPPED

Fix rounds: [N]
Suppressions: [N] (recorded in verification-report.md §Suppressions)

Report: `{artifacts_dir}/reports/verification-report.md`
```

Update the execution plan:
- If this was a milestone boundary: note verification result in the milestone
- If this was a phase boundary: note in the Phase Gate Log
- Back-add any suppressions to the relevant spec as `⚠️ Suppressed:`

## Idempotency

- Re-invocation reads the existing report and asks whether to re-run or review.
- Fix decisions from previous runs are preserved in the report's Suppressions section.
- Checks always run against the current state of the codebase, not cached results.

## Output Rules

1. **Checks in parallel**: Launch lint, format, typecheck, tests, security, and data integrity
   simultaneously; add Performance when Phase 1 defined it. Never run checks sequentially.
2. **Failures are not auto-fixed without approval**: Every fix requires the user's explicit
   choice via AskQuestion (approve/deny/modify).
3. **Re-verify after fixes**: Never trust a fix without running the check again.
4. **Max 3 loops**: Prevent infinite fix-verify cycles.
5. **Suppressions are documented**: Every denied finding is recorded with the user's reason.
6. **Report persists**: The verification report is written to disk so downstream skills and
   PRs can reference it.
