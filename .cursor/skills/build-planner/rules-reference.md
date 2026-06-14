# Rules Reference

Full content for each rule created by build-planner Phase 6+7.

## spec-adherence.mdc

Write the rule content from `.cursor/rules/spec-adherence.mdc`. The rule enforces:
- Spec verification before code changes
- Phased workflow adherence (active phase/milestone/task tracking)
- Phase gate checks before entering a new phase
- Tech choice enforcement from specs
- Question-raising for any uncertainty
- Back-adding on-the-fly decisions to specs
- Task status bookkeeping (in-progress, completed, blocked) synced to the execution plan

## atomic-commits.mdc

Write the rule content from `.cursor/rules/atomic-commits.mdc`. The rule enforces:
- Atomic commits: one logical change per commit, codebase valid after each
- Commit message format with task ID prefix
- Branch workflow: milestone branches (`feat/M[N]-[slug]`) target phase branches
  (`phase/[N]-[slug]`), phase branches target main
- Minor PRs per milestone, major PRs per phase — both require user review
- PR Plan table kept in sync in the execution plan

## tdd.mdc

The glob pattern should match the project's source file extensions (e.g., `**/*.py` for
Python, `**/*.{ts,tsx}` for TypeScript).

```markdown
---
description: Enforces test-driven development — tests before implementation
globs: [detected source patterns]
alwaysApply: false
---

# Test-Driven Development

When implementing any feature or component:

1. **Test first**: Write the test(s) before writing the implementation code. Each test should
   initially fail (red), then pass after implementation (green).

2. **Test coverage**: Every new public function, class, or module must have a corresponding
   test. Reference `docs/test-plan.md` for test case definitions and `docs/acceptance-criteria.md`
   for pass/fail thresholds.

3. **Test location**: Place tests in the project's test directory following existing conventions.
   Mirror the source directory structure.

4. **Test naming**: Use descriptive names that state the expected behavior:
   - `test_[function]_[scenario]_[expected_result]`

5. **Run tests**: After implementation, run the test suite to verify all tests pass before
   moving to the next task.

6. **No skipping**: Do not implement code without a corresponding test unless the user
   explicitly approves it.
```

## build-execution.mdc

```markdown
---
description: Governs build-executor workflow — pre-task validation, post-task checks, milestone/phase boundaries, and error escalation
alwaysApply: true
---

# Build Execution

Rules governing the build-executor workflow. These apply whenever tasks from the
execution plan are being implemented.

## Pre-Task Validation

Before writing any implementation code for a task:

1. **Read the spec source**: The task's Spec Source column in the execution plan must be read
   before implementation begins. Do not write code based on memory or assumptions.
2. **Verify dependencies**: All tasks listed in the Depends On column must be `completed`.
   If any are `pending`, `in_progress`, or `blocked`, do not start this task.
3. **Verify data dependencies**: If the task's Data Deps column is non-empty, verify each
   referenced asset is staged and verified (check `docs/data-management-state.md` or the Data
   Dependencies table in the execution plan). If any required data asset is missing, block
   the task and raise it to the user — do not write code that depends on absent model
   weights, datasets, or checkpoints.
4. **Check branch**: The correct milestone branch must exist and be checked out.
5. **Update state first**: Set the task to `in_progress` in the execution plan before writing
   any code.

## Post-Task Verification

After completing a task, before committing:

1. **Lint**: Run the project linter on all changed files. Must pass.
2. **Typecheck**: Run the typechecker. Must pass.
3. **Test suite**: Run the full test suite (not just the new test). All must pass.
4. **No regressions**: If any previously passing test now fails, fix the regression before
   committing. Do not commit with failing tests.
5. **Update state**: Only mark the task `completed` after the commit succeeds and all checks
   pass.

## Milestone Boundaries

When all tasks in a milestone are `completed`:

1. All checks must pass on the milestone branch.
2. A minor PR must be created before starting the next milestone.
3. Present the PR to the user (URL and checklist in the session summary). Merge requires
   explicit user approval — never auto-merge. Continue the next milestone in the same session
   once the PR exists and is recorded, unless the user asked to pause at PR boundaries or git
   policy blocks the next branch.
4. Do not start the next milestone's tasks until the minor PR is at least created (merge
   approval is not required to continue implementation).

## Phase Boundaries

When all milestones in a phase are `completed`:

1. Run the phase gate check — every criterion in the Phase Gate Check section.
2. Record the result in the Phase Gate Log.
3. If any criterion is unmet, raise a `[Decision]` — do not silently proceed.
4. A major PR must be created and presented before starting the next phase. Merge requires
   explicit user approval. If the next phase cannot branch until `main` updates, surface that
   blocker; otherwise keep executing runnable work in the same session.

## Parallel Agent Coordination

When tasks are executed by parallel subagents:

1. Each agent works on its own files — no two agents modify the same file.
2. If a conflict is detected (two agents need the same file), escalate to the parent agent
   as a `[Contradiction]`.
3. Each agent's work is committed as a separate atomic commit by the parent agent.
4. The parent agent runs the full check suite after merging all parallel work.

## Error Escalation

1. **Task blocked**: Set status to `blocked`, note the blocker, raise to user immediately.
   Do not silently skip.
2. **Cascade blocks**: If blocking a task would also block downstream tasks, identify and
   report the full cascade.
3. **Spec insufficient**: Raise as `[Ambiguity]`, get resolution, back-add to spec before
   implementing.
4. **Check failure after commit**: Amend the commit to fix the issue. Do not create a
   separate "fix" commit for post-commit check failures on the same task.
```
