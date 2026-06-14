---
name: 06-tech-tooling
description: >
  Creates development tooling: Cursor hooks for linting, formatting, typechecking, and testing;
  rules for spec-adherence, TDD, atomic commits, and build execution; and tool configuration
  files. Blocking stage — must complete before build execution begins.
---

# 06 — Technical Tooling

Create dev tooling hooks, rules, and configuration that enforce technical standards during
implementation.

**Preamble:** [pipeline-preamble.md](../pipeline-preamble.md) — shared conventions for stages 00–17.
**Cross-cutting:** [considerations.md](../considerations.md), [connectivity-gates.md](../connectivity-gates.md).
**State agent:** [workflow-state-manager](../../agents/workflow-state-manager.md) — mandatory read/update.

## Connectivity (stage 06)

Dev tooling must catch wiring regressions **before** 13-deploy-smoke:

| Check | Requirement |
|-------|-------------|
| CI pytest | Includes `tests/unit/test_cors_policy.py` and `tests/integration` |
| Smoke layout | `tests/smoke/test_staging_connectivity.py` exists (`@pytest.mark.live`) |
| Scripts | `scripts/deploy/verify_connectivity.sh` executable |
| Docs | `docs/deploy.md §Runbook` documents H4–H5 env vars |

Optional hook: run `test_cors_policy.py` on files under `apps/*/app.py` when touched.

Record verification in stage `workflow-state.yaml` block (06 `verification`).

## Prerequisites

1. **05-verify-tech** must be `completed`. Technical plan audited.
2. Required:
   - `workflow-state.yaml + execution plan artifact` — §Tech Stack Summary for tool choices
   - `docs/dependency-inventory.md` — for package versions
3. Plan tooling from 03-plan-tooling must still be installed.

## Why This Stage Blocks

Technical tooling must be installed **before** build execution (Stage 07) because:
- Lint/format/typecheck hooks catch errors on every edit
- TDD rules enforce test-first workflow
- Atomic commit rules prevent WIP commits
- Build execution rules enforce pre/post task validation
- Without these, code quality degrades silently

## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).
**Stage key:** `stages.06-tech-tooling`.

Invoke **workflow-state-manager** `read_context` before any other action; `update` after each
substep. **Do not** edit `workflow-state.yaml` directly.


### On invocation — check state

1. Use **workflow-state-manager** context brief for §stages.06-tech-tooling (from agent `read_context`).
2. **If `completed`**: Ask: "Reuse existing tooling, update, or regenerate?"
3. **If `in_progress`**: Report progress. Resume or restart.
4. **If `pending`**: Start fresh.

### Commit-as-you-go

Commit artifacts to an appropriate branch before transitioning to the next stage or
asking the user a blocking question. Branch type per
[workflow-state-reference.md](../workflow-state-reference.md) §Git history.
Record every commit in `workflow-state.yaml` §`git_history.commits` with
`stage: "06-tech-tooling"`.

## Delta / feature-addition mode

Run when evolve cycle adds **new dependencies, hooks, CI steps, or formatters**:

- Update `docs/dependency-inventory.md` for new packages.
- Extend hooks/CI only for stack changes in cycle scope.

## Workflow

### Phase 1 — Load Tool Configuration

Read `workflow-state.yaml + execution plan artifact` §Tech Stack Summary to determine:

| Category | Tool | Config File | Command |
|----------|------|------------|---------|
| Linter | [e.g., Ruff] | [e.g., ruff.toml] | [e.g., ruff check .] |
| Formatter | [e.g., Ruff format] | [same or separate] | [e.g., ruff format --check .] |
| Typechecker | basedpyright | `pyproject.toml` `[tool.basedpyright]`, `pyrightconfig.json` | `uv run basedpyright` (ADR-018) |
| Test runner | [e.g., pytest] | [e.g., pyproject.toml] | [e.g., pytest -v] |

If any tool is not configured, surface as `[Decision]` via AskQuestion with recommendations.

### Phase 2 — Present Tooling Plan

Present to user via AskQuestion:

```
prompt: "Technical tooling plan:
  Rules:   4 (spec-adherence, TDD, atomic-commits, build-execution)
  Hooks:   6 (lint, format, typecheck, pre-task, post-test, pr-checklist)
  Configs: [N] (linter, formatter, typechecker, test runner)

  Approve all, or review individually?"

options:
  1. "Approve all — create everything"
  2. "Review individually"
  3. "Select specific hooks — I'll choose"
  4. "Let me explain / provide more context"
```

### Phase 3 — Create Tooling (Parallel Agents)

Launch three parallel agents in a single message:

#### Agent A — Rules

Create or update `.cursor/rules/` files. See [rules-reference.md](../build-planner/rules-reference.md)
for full content of each rule.

1. **`spec-adherence.mdc`** (always-apply):
   - Before any code change, verify relevant spec exists
   - Check execution-plan.md §Current State for active phase/milestone/task
   - Enforce work belongs to active phase
   - Verify task dependencies are met
   - Use only approved tools/libraries/patterns
   - Raise uncertainty as AskQuestion
   - Back-add on-the-fly decisions to specs
   - Keep task status bookkeeping current

2. **`tdd.mdc`** (scoped to source file patterns):
   - Test file must exist before implementation file
   - Test must fail before implementation (red phase)
   - Test must pass after implementation (green phase)
   - Refactor keeps tests green
   - Naming: `test_[function]_[scenario]_[expected]`
   - Coverage awareness

3. **`atomic-commits.mdc`** (always-apply):
   - One task per commit
   - Commit message: `[T{id}] {type}: {description}`
   - Post-commit checks must pass
   - No WIP commits
   - Branch naming conventions
   - Minor PR per milestone, major PR per phase

4. **`build-execution.mdc`** (always-apply):
   - Pre-task validation (read spec, check deps, check branch)
   - Post-task verification (lint, typecheck, test suite)
   - Milestone boundary behavior
   - Phase boundary behavior
   - Parallel agent coordination
   - Error escalation

**Merge with existing rules**: If 03-plan-tooling already created rules, merge rather
than overwrite. Preserve plan-adherence.mdc and project-specific rules.

#### Agent B — Hooks

Create hook scripts and update `.cursor/hooks.json`:

1. **`lint.sh`** — fires on `afterFileEdit`, scoped to source patterns
   - Reads `filePath` from stdin JSON
   - Runs linter on the file
   - Returns findings in `additional_context` or empty on success
   - Exits 0 always

2. **`format.sh`** — fires on `afterFileEdit`, scoped to source patterns
   - Runs formatter in check mode
   - Returns diff in `additional_context` if changes needed

3. **`typecheck.sh`** — fires on `afterFileEdit`, scoped to source patterns
   - Runs typechecker on the file
   - Returns type errors in `additional_context`

4. **`pre-task-check.sh`** — fires on `preToolUse` (Write)
   - Verifies the active task's spec source has been read
   - Cross-references execution-plan.md §Current State

5. **`post-test-sync.sh`** — fires on `afterShellExecution` (test commands)
   - After test runs, updates execution-plan.md task status

6. **`pr-checklist.sh`** — fires on `preToolUse` (Shell, git push)
   - Verifies PR checklist criteria before pushing

**Merge with existing hooks**: Read existing `.cursor/hooks.json` from 03-plan-tooling,
merge new hooks alongside existing scope-check and feature-drift hooks.

Hook script contract:
- Read `filePath` (or command context) from stdin JSON
- Run the tool
- Return `additional_context` with errors or empty on success
- Always exit 0 (errors go in context, not exit code)

#### Agent C — Configuration Files

Create tool configuration files:

- **Linter config** (e.g., `ruff.toml`, `.eslintrc.js`)
  - Rules derived from project conventions in specs
  - Severity levels appropriate for the project

- **Formatter config** (e.g., in `pyproject.toml [tool.black]`, `.prettierrc`)
  - Line length, quote style, indentation from specs or conventions

- **Typechecker config** (`pyrightconfig.json`, `[tool.basedpyright]`, `docs/typing-policy.md`, `tsconfig.json`)
  - Strictness level from tech plan
  - Include/exclude patterns matching project structure

- **Test runner config** (e.g., `pytest.ini`, `conftest.py`, `jest.config.*`)
  - Test discovery patterns
  - Fixtures and plugins

#### Agent D — Template CI/CD & Hooks (if template selected)

Read `workflow-state.yaml` §template and [template-registry.md](../template-registry.md).

- **CI/CD workflow**: Ensure `.github/workflows/deploy_to_modal.yml` matches the template
  pattern. If the project was scaffolded from the template, this file already exists —
  validate it rather than creating from scratch.
- **Template conformance hook** (`template-check.sh`, fires on `afterFileEdit`):
  - Reads the edited file path
  - Checks if changes break template structural patterns:
    - Utility: Modal imports in `src/service.py`, new GPU classes, volume mounts
    - Job: Missing `i_am_running()` in new GPU classes, Modal imports in `src/utils.py`
  - Returns advisory warning in `additional_context` if drift detected
  - Exits 0 (advisory, not blocking)

### Phase 4 — Verify Installation

After all agents complete:

1. Verify all rule files exist with valid `.mdc` frontmatter
2. Verify `.cursor/hooks.json` is valid JSON with all hooks registered
3. Verify hook scripts exist (on Windows, verify script content is correct)
4. Verify config files are valid (e.g., `ruff check --config ruff.toml` doesn't error)
5. Run each tool once in dry-run mode to confirm it works

Report results:

```
Technical Tooling Installed.

  Rules: [N] total ([N] new, [N] merged with existing)
    - spec-adherence.mdc (always-apply)
    - tdd.mdc (scoped: [patterns])
    - atomic-commits.mdc (always-apply)
    - build-execution.mdc (always-apply)
    [+ plan tooling rules preserved]

  Hooks: [N] total ([N] new, [N] merged with existing)
    - lint.sh (afterFileEdit)
    - format.sh (afterFileEdit)
    - typecheck.sh (afterFileEdit)
    - pre-task-check.sh (preToolUse: Write)
    - post-test-sync.sh (afterShellExecution)
    - pr-checklist.sh (preToolUse: Shell)
    [+ plan tooling hooks preserved]

  Configs: [N]
    - [tool config files created]

  Verification: All [N] artifacts valid ✓
```

### Phase 5 — Summary

```
Technical Tooling Complete.

Phase B gate check:
  ✓ Execution plan audited (05-verify-tech)
  ✓ Consistency check passed (05-verify-tech)
  ✓ Technical tooling installed
  → Ready for Phase C: Build

Guardrails active: [N] rules + [N] hooks
  - Every file edit triggers lint/format/typecheck
  - Every task requires spec source to be read first
  - Every commit must be atomic and pass all checks
  - Test-first workflow enforced

Next step: 07-build
```

**State**: Set status to `completed`.

## Idempotency

On re-invocation:
- Read existing rule files and update in place
- Merge hooks into existing hooks.json
- Preserve user-modified tool configurations
- Only update what changed in the execution plan

## Output Rules

1. **Merge, don't overwrite**: Respect existing tooling from 03-plan-tooling.
2. **Non-blocking hooks**: Hooks provide context, never block the agent.
3. **Verify installation**: Confirm tools work before marking complete.
4. **Match tech stack**: Tool choices must match execution-plan.md §Tech Stack Summary.
5. **Executable scripts**: Hook scripts must be valid for the user's platform.
