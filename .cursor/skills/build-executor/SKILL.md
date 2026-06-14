---
name: build-executor
description: >
  Executes the implementation plan from build-planner, task by task, following TDD ordering,
  spec-adherence rules, and atomic commit conventions. Orchestrates parallel agents for
  independent tasks, manages branches and PRs, runs gate checks, and keeps the execution plan
  in sync with actual progress. Prefers completing as many tasks and milestones as practical
  in one invocation (PRs opened as boundaries require, without stopping the session at each PR).
  Use when the user wants to start implementing, continue implementation, execute the plan,
  build the project, or resume work from the execution plan.
---

# Build Executor

Execute the build-planner's execution plan: implement tasks in TDD order, commit atomically,
create PRs at milestone and phase boundaries, and orchestrate parallel agents for independent
work.

**Cross-cutting:** [considerations.md](../considerations.md), [connectivity-gates.md](../connectivity-gates.md).

**Connectivity:** Same obligations as [07-build](../07-build/SKILL.md) §Connectivity (stage 07) — H0c, H0i, CORS on browser-facing APIs.

## Throughput (single invocation)

Treat one agent session as **batch-oriented**: advance the Task Loop as far as dependencies,
data management, branches, and checks allow—across **multiple milestones** when possible.

- **PRs are not session boundaries.** After verify-build passes at a milestone, create the
  minor PR, record it in the PR Plan table, surface the URL in your summary, then **continue**
  with the next milestone once `build-execution.mdc` allows (typically: minor PR exists;
  merge still requires explicit user approval and never auto-merge).
- **Same for phase boundaries:** run the gate check, create the major PR, log it, then proceed
  as far as unblocked (if the next phase’s git base truly requires `main` merged first, say so
  briefly and do everything else that is still runnable).
- **Do not** end the turn right after opening a PR **waiting** for merge approval unless the
  user asked for that cadence or there is no legal next task.
- **AskQuestion** is for ambiguity, `blocked` tasks, or explicit user steering—not a mandatory
  pause before every task or milestone.

## Prerequisites

1. **Execution plan**: `workflow-state.yaml + execution plan artifact` must exist and have at least one approved phase.
   If missing, inform the user and invoke build-planner first.
2. **Data management**: Check `docs/data-management-state.md` for status. If any task in the
   execution plan has data dependencies (Data Deps column is non-empty):
   - **If `complete`**: Data is staged and verified. Proceed.
   - **If `in_progress` or `failed`**: Warn the user. Tasks with data dependencies will be
     blocked until data management completes. Offer to invoke the
     [data-staging](../data-management/SKILL.md) skill.
   - **If missing**: Inform the user that data-staging has not been run. Offer to invoke it
     before proceeding. Tasks without data dependencies can still start.
3. **Rules**: `.cursor/rules/spec-adherence.mdc`, `tdd.mdc`, `atomic-commits.mdc`, and
   `build-execution.mdc` must exist. If missing, invoke build-planner Phase 6+7.
4. **Hooks**: `.cursor/hooks.json` should exist. If missing, warn but proceed — hooks are
   non-blocking.
5. **Specs**: `docs/` must contain the spec documents referenced by the execution plan.

## State management

**Canonical:** repo-root [`workflow-state.yaml`](../../workflow-state.yaml) §`stages.07-build`.
Rules: [workflow-state-reference.md](../workflow-state-reference.md).

**Detail:** `workflow-state.yaml + execution plan artifact` §Current State — update **both** on every task/milestone change.

### On invocation

1. Read `workflow-state.yaml` §`stages.07-build` and `workflow-state.yaml + execution plan artifact` §Current State.
2. Determine the active phase, milestone, and task.
3. Report the current position to the user:

```
Execution State:
  Phase:     [N] — [Phase Name]
  Milestone: M[N] — [Milestone Name]
  Task:      T[N.N] — [Task description]
  Progress:  [N] / [N] tasks completed ([%])
  
  Ready to work on: T[N.N] — [description]
```

4. **Default:** start the Task Loop at Current State without AskQuestion. Use AskQuestion
   when tasks are `blocked`, the user narrowed scope in their message, or they explicitly want
   to choose a path; optional prompts include:
   - "Continue from T[N.N]" (after `blocked` or unclear resume)
   - "Show me the full task list for this milestone first"
   - "Jump to a different task (I'll specify)"
   - "Let me explain / provide more context"

## Workflow

### Task Loop

For each task in the execution plan, in order (respecting dependencies):

#### Step 1 — Pre-flight checks

Before starting any task:

1. **Read the spec source** cited in the task's Spec Source column. Verify the spec section
   exists and contains enough detail to implement the task.
2. **Check dependencies**: Verify all tasks in the Depends On column are `completed`. If any
   are not, skip to the next task with no unmet dependencies, or raise a `[Decision]` if all
   remaining tasks are blocked.
3. **Check data dependencies**: If the task's Data Deps column is non-empty, verify each
   referenced asset has status `verified` in the Data Dependencies table (or in
   `docs/data-management-state.md`). If any asset is not verified:
   - Check if the asset exists at its expected local path (from `docs/spec.md §Data`)
   - If missing: block the task. Surface via AskQuestion:
     - "Run data-staging to acquire this asset now"
     - "Skip this task — move to next task without data deps"
     - "I'll provide the data manually — mark as available"
     - "Let me explain / provide more context"
   - If present but unverified: run `scripts/verify_data.py` for that asset. If it passes,
     update the Data Dependencies table and proceed.
4. **Check branch**: Verify the correct milestone branch exists (per §Git Strategy). If not,
   create it from the phase branch.
5. **Update state**: Set the task to `in_progress` in the Task Tracking table and update
   Current State. Load the task into TodoWrite.

#### Step 2 — Execute the task

**If the task type is `Test`**:
1. Read the spec source (test-plan.md test case or acceptance criteria).
2. Write the test file following TDD conventions (per `tdd.mdc`):
   - Test location mirrors source structure
   - Descriptive names: `test_[function]_[scenario]_[expected]`
3. Run the test — it should fail (red phase). If it passes without implementation, surface
   as `[Uncertainty]`: the test may not be testing the right thing.

**If the task type is `Code`**:
1. Read the spec source (spec.md component details, config-spec, etc.).
2. Implement the code to make the preceding test(s) pass.
3. Run the test(s) — they should now pass (green phase).
4. Refactor if needed (refactor phase), keeping tests green.

**For either type**:
- Follow all tech choices from `workflow-state.yaml + execution plan artifact` §Tech Stack Summary.
- If anything is unclear, raise it via AskQuestion per the Uncertainty Resolution Protocol.
  Do not guess.
- If a new dependency or pattern is needed, raise as `[Decision]`, then back-add to specs.

#### Step 3 — Post-task checks

After implementing the task:

1. **Run linter**: Verify lint passes on all changed files.
2. **Run typechecker**: Verify typecheck passes.
3. **Run tests**: Run the full test suite (not just the new test). All must pass.
4. If any check fails, fix the issue before proceeding. Do not commit broken code.

#### Step 4 — Commit & record

1. Verify correct branch is checked out (create `feat/M{N}-{slug}` if needed).
2. Stage all files related to this task.
3. Commit with the format: `[T{id}] {type}: {description}` (per `atomic-commits.mdc`).
4. Verify the commit is clean: no untracked files, no unstaged changes for this task.
5. Append to `workflow-state.yaml` §`git_history.commits`:
   ```yaml
   - sha: <short-sha>
     branch: <current-branch>
     message: "[T{id}] {type}: {description}"
     stage: "07-build"
     files_changed: <count>
     timestamp: "<ISO-8601>"
   ```
6. Commit the workflow-state update (same or next commit).

**Never leave uncommitted work.** If an AskQuestion, gate check, or session end
is imminent, commit first. Progress lost to uncommitted work is unrecoverable.

#### Step 5 — Update state

1. Set the task to `completed` in the Task Tracking table, record the date.
2. Advance Current State to the next pending task.
3. Update TodoWrite.
4. Report to the user: `Completed T{id}: {description}. Next: T{next_id}: {next_description}`

### Milestone Boundary

When all tasks in a milestone are `completed`:

1. **Invoke [verify-build](../verify-build/SKILL.md)**: Run all checks (lint, format,
   typecheck, tests) via parallel agents. If failures exist, verify-build walks the user
   through approve/deny/modify for each. Wait for all checks to pass.
2. **Create minor PR** from the milestone branch to the phase branch:
   - Title: `[M{N}] {Milestone Name}`
   - Body: auto-generated from task list, spec references, check results
   - Include the PR checklist from §Git Strategy
3. **Present to the user** (PR URL and checklist in the session summary). Do **not** stop the
   implementation session here waiting for merge unless the user asked for that or the next
   milestone is impossible until the branch target updates.
4. Update the PR Plan table with URL and `open` status. **Merge only on explicit user
   approval** (`atomic-commits.mdc`); never auto-merge.
5. Report milestone completion and **continue** the Task Loop for the next milestone in the
   same invocation when unblocked.

### Phase Boundary

When all milestones in a phase are `completed`:

1. **Invoke [verify-build](../verify-build/SKILL.md)**: Full verification at phase scope.
2. **Run phase gate check**: Verify every criterion in the Phase Gate Check section.
3. **Record in Phase Gate Log**: Date, result, notes (include verification report reference).
4. If any gate criterion is not met, surface as `[Decision]`: proceed or resolve first.
5. **Create major PR** from the phase branch to main:
   - Title: `Phase {N}: {Phase Name}`
   - Body: gate check results, milestone summaries, full check results
6. **Present to the user** (URL and highlights). Do **not** treat this as the mandatory end of
   the session; merge only on explicit approval, never auto-merge.
7. Update the PR Plan table. Advance Current State to the next phase's first milestone and
   task, and **keep executing** while dependencies and branch policy allow.

## Agent Orchestration

### Parallel task execution

Within a milestone, identify tasks with no unmet dependencies that can run simultaneously:

1. **Build the dependency graph** from the Task Tracking table's Depends On column.
2. **Identify parallel groups**: Tasks with `Depends On: —` or whose dependencies are all
   `completed` form a parallel batch.
3. **Launch parallel agents**: For each parallelizable task, launch a Task subagent with
   `subagent_type: "generalPurpose"`. Each agent receives:
   - The task definition (id, description, type, spec source)
   - The relevant spec excerpts (not the full plan)
   - The tech stack summary
   - The branch name to work on
   - Instructions to follow `tdd.mdc` and `spec-adherence.mdc`
4. **Parent agent coordinates**:
   - Waits for all parallel agents to complete
   - Reviews their outputs for consistency (naming conflicts, import collisions, etc.)
   - Surfaces any conflicts as `[Contradiction]` via AskQuestion
   - Commits each task's work as a separate atomic commit
   - Updates the Task Tracking table for all completed tasks

### Sequential fallback

If tasks have chain dependencies (T1.1 → T1.2 → T1.3), execute them sequentially in the
parent agent. Do not launch subagents for single-task chains.

### User interaction stays in parent

All AskQuestion calls, PR presentations, and gate checks happen in the parent agent. Subagents
are fire-and-forget workers — they do not interact with the user.

## Error Handling

### Task failure

If a task cannot be completed (test won't pass, spec is insufficient, dependency issue):

1. Set the task to `blocked` in the Task Tracking table.
2. Note the blocker in the Blocked By column.
3. Surface to the user via AskQuestion:
   - "Fix the blocker now — I'll describe the issue"
   - "Skip this task and move to the next unblocked one"
   - "Defer this task to a later milestone"
   - "Let me explain / provide more context"
4. If skipping, verify no downstream tasks depend on this one. If they do, mark those as
   `blocked` too and surface the cascade.

### Spec gap discovered during implementation

If a task's spec source is insufficient to implement:

1. Raise as `[Ambiguity]` with what's missing and a recommendation.
2. On resolution, back-add the clarification to the spec document.
3. Continue implementation with the resolved detail.

## Idempotency

This skill is fully idempotent:

- **Completed tasks** are never re-executed. The Task Tracking table is the source of truth.
- **In-progress tasks** are resumed — the skill checks what files exist and what tests pass
  to determine how far the previous run got.
- **Blocked tasks** are re-evaluated — the blocker may have been resolved externally.
- **Branches and PRs** are checked — if the branch exists, use it. If the PR exists, skip
  creation and report its current status.

## Output Rules

1. **One task at a time**: Complete, commit, and update state for each task before starting
   the next. No batching of incomplete work.
2. **Tests before code**: Within a milestone, every code task must be preceded by its test
   task completing successfully (red phase confirmed).
3. **Never skip checks**: Lint, typecheck, and test suite must pass after every task. No
   exceptions without user approval.
4. **Atomic commits only**: One commit per task. Never bundle. Never leave the codebase in a
   broken state.
5. **PRs require approval to merge**: Minor and major PRs are always presented to the user.
   Never auto-merge. Opening a PR does **not** require ending the turn before more tasks run.
6. **State is always current**: The execution plan on disk reflects the true state of progress
   at all times. If the session ends, the next invocation picks up exactly where it left off.
7. **Verify before PR**: Always invoke [verify-build](../verify-build/SKILL.md) at milestone
   and phase boundaries. Never create a PR without a passing verification report.
8. **Deploy after final phase**: When the deployment phase completes, invoke
   [deploy-verify](../deploy-verify/SKILL.md) to deploy and validate.
9. **Maximize per pass**: Prefer completing multiple tasks and milestones per invocation;
   parallelize independent tasks when safe (see Agent Orchestration).
