---
name: 08-verify-build
description: >
  Runs quality checks at milestone boundaries during the build. Auto-corrects lint and format
  issues without blocking. Only blocks on test failures, type errors, or security issues that
  require user decisions. Invoked by 07-build at milestone and phase boundaries, not as a
  separate pipeline step.
---

# 08 — Verify Build

Run quality checks in parallel, auto-correct where possible, and surface non-trivial
failures to the user.

**Preamble:** [pipeline-preamble.md](../pipeline-preamble.md) — shared conventions for stages 00–17.
**Cross-cutting:** [considerations.md](../considerations.md), [connectivity-gates.md](../connectivity-gates.md).
**State agent:** [workflow-state-manager](../../agents/workflow-state-manager.md) — mandatory read/update.

## Connectivity (stage 08)

**Blocking:** `tests/unit/test_cors_policy.py` and `tests/integration` must pass.
Report connectivity artifact presence (`test_staging_connectivity.py`, `verify_connectivity.sh`)
in `docs/verification-report.md`. See connectivity-gates §Stage 08.

## When to Use

- **During 07-build**: Automatically invoked at milestone and phase boundaries
- **Standalone**: Can verify the codebase at any point
- **Pre-PR**: Run before creating minor or major PRs

## Behavior: Non-Blocking Auto-Correction

Unlike a traditional gate that blocks until everything is clean, this skill uses a
**tiered** approach:

| Issue Type | Action | Blocking? |
|-----------|--------|-----------|
| Lint errors (auto-fixable) | Auto-fix with `--fix` flag | No |
| Format issues | Auto-format | No |
| Lint errors (manual) | Present to user | Yes |
| Type errors | Present to user | Yes |
| Test failures | Present to user | Yes |
| Security issues | Present to user | **Always** blocking |
| Data integrity | Present to user | Advisory (not blocking) |

## Prerequisites

1. `workflow-state.yaml + execution plan artifact` — §Tech Stack Summary for tool commands
2. Source files and tests must exist

## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).
**Stage key:** `stages.08-verify-build`.

Invoke **workflow-state-manager** `read_context` before any other action; `update` after each
substep. **Do not** edit `workflow-state.yaml` directly.


**Detail:** `docs/verification-report.md` — overwrite each run; set `report` on the stage block.

## Delta / feature-addition mode

- Run at **07-build milestone boundaries** for delta tasks only.
- Scope verification to changed modules and tests tied to new Fn.

## Workflow

### Phase 1 — Load Configuration

Read `workflow-state.yaml + execution plan artifact` §Tech Stack Summary for tool commands.

### Phase 2 — Run Checks (Parallel)

Launch agents in **one** message:

**Agent 1 — Linter**: Run lint, parse findings, classify as auto-fixable or manual.

**Agent 2 — Formatter**: Run format check (dry-run mode).

**Agent 3 — Typechecker**: Run typecheck, parse errors.

**Agent 4 — Test Suite**: Run full test suite, parse results. Must include **H0c**
`tests/unit/test_cors_policy.py` (blocking for hybrid UI deploys).

**Agent 4b — Connectivity policy** (deployed service hybrid): Confirm `configure_cors` on browser-facing
FastAPI apps and `tests/smoke/test_staging_connectivity.py` exists per connectivity-gates.

**Agent 5 — Security**: Always runs:
- `pip-audit` for dependency CVEs
- Pattern scan for committed secrets
- Common vulnerability patterns (eval, pickle.loads, etc.)

**Agent 6 — Performance** (optional): Only when specs define perf thresholds.

**Agent 7 — Data Integrity** (optional): Verify staged data assets if they exist.

**Agent 9 — Modal run smoke** (optional, milestone M10+ or pre-deploy): Per
[ADR-004](../../docs/adr/ADR-004.md) T1. Run only when user approves GPU budget via
AskQuestion. Uses ` curl or httpx` ephemeral invocations (same minimum set as 13 Phase 1.5).
Skip on Windows dev machines without platform CLI — record `SKIPPED` in verification report.

**Agent 8 — Template Conformance** (if template selected): Read `workflow-state.yaml`
§template and [template-registry.md](../template-registry.md). Verify:
- File layout matches template structure (`src/app.py`, `src/service.py` or `src/utils.py`)
- Modal patterns match template type (api vs worker vs monolith)
- No Modal imports in the core logic module
- CI/CD workflow file matches template pattern
- App name is `cognichem-{service_name}`
- For job: all GPU classes have `i_am_running()`, `@modal.enter()` calls `warmup()`
- For utility: no `@modal.enter()`, no GPU, no volumes
- Return: conformance report with deviations listed

### Phase 3 — Auto-Correct

For auto-fixable issues (lint auto-fix, format):
1. Apply fixes automatically
2. Re-run only the affected check to confirm
3. Commit: `chore: auto-fix lint/format issues`
4. Report what was auto-fixed

### Phase 4 — Surface Non-Trivial Failures

For issues requiring user decisions, present via AskQuestion:

**Lint (manual)**: "Approve auto-fix / Deny (false positive) / Modify (manual fix)"
**Type errors**: "Approve fix / Deny (suppress) / Modify (provide correct type)"
**Test failures**: "Fix implementation / Fix test / Both need changes"
**Security**: "Upgrade packages and remove secrets / Accept risk / Review individually"

### Phase 5 — Compile Report

Write `docs/verification-report.md`:

```markdown
# Verification Report

> Generated: [date]
> Scope: [milestone/phase/standalone]
> Branch: [branch]

## Summary

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Lint | PASS | [N] | [N] auto-fixed | [tool] |
| Format | PASS | [N] | [N] auto-fixed | [tool] |
| Typecheck | PASS/FAIL | [N] | — | [tool] |
| Tests | PASS/FAIL | [N] failed | — | [tool] |
| Security | PASS/FAIL | [N] | — | pip-audit |
| Performance | PASS/SKIPPED | — | — | [tool] |
| Data | PASS/SKIPPED | — | — | verify_data.py |

Overall: PASS / FAIL
```

### Phase 6 — Re-verify (if fixes applied)

After user-approved fixes:
1. Re-run affected checks
2. If new failures appear, loop back to Phase 4
3. Maximum 3 fix-verify loops

## Output Rules

1. **Auto-correct first**: Fix what can be fixed automatically before presenting to user
2. **Parallel checks**: All checks run simultaneously
3. **Security always blocking**: Never auto-dismiss security findings
4. **Max 3 loops**: Prevent infinite fix-verify cycles
5. **Report persists**: Written to disk for PR and downstream reference
