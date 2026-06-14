---
name: build-planner
description: >
  Creates an execution plan from audited doc-planner specs, gets user approval
  (approve/deny/modify), sets up hooks for linting, formatting, and typechecking, and writes
  rules enforcing spec-adherence and TDD. Runs after doc-planner and audit-docs. Use when the
  user wants to move from documentation/specs to implementation, set up dev tooling hooks,
  create an execution plan, or establish coding standards from specs.
---

# Build Planner

Create an execution plan from specs, configure dev tooling hooks, and establish rules that
enforce spec-adherence and test-driven development.

**Cross-cutting:** [considerations.md](../considerations.md).

## Prerequisites

This skill requires **doc-planner** and **audit-docs** (and therefore **gather-context**)
to have been run first.

1. Check if `{output_directory}/execution-plan.md` exists.
   - **If it exists**: Read it. Ask the user whether to reuse, update, or regenerate.
2. Check that doc-planner output exists (at minimum: `research-brief.md` and the mandatory
   `deployment-integration.md`). If missing, inform the user and invoke doc-planner first.
3. Read `workflow-state.yaml` §`stages.audit-docs` (and legacy `docs/audit-state.md` if present).
   - **If audit-docs not `completed`**: Inform the user that audit-docs has not finished.
     Ask: "Run audit-docs first, or proceed with unaudited specs?" If proceeding unaudited,
     flag in the execution plan as `⚠️ Built from unaudited specs` and log in `issue_log`.
4. If audit-docs was completed, read `audit-decisions.md` for any denied or modified
   statements — these corrections are already applied to the source docs, but the decision
     log provides context for planning decisions.

## State management

**Canonical:** repo-root [`workflow-state.yaml`](../../workflow-state.yaml) §`stages.build-planner`.
Rules: [workflow-state-reference.md](../workflow-state-reference.md).

On invocation: read §`stages.build-planner`. When `workflow-state.yaml + execution plan artifact` is approved, set
`status: completed`, record `completed_at`, and append the plan to `artifacts`. Pipeline path
uses `04-tech-plan` instead — then keep `stages.build-planner.status: skipped`.

## Uncertainty Resolution Protocol

Follow [gather-context — Uncertainty Resolution Protocol](../gather-context/SKILL.md#uncertainty-resolution-protocol)
and [considerations.md](../considerations.md). During planning, extend the Resolution Log from
doc-planner; back-add approved tech choices per Phase 5.

## Agent Orchestration

Several phases in this skill contain independent work that should be parallelized using the
Task tool to launch concurrent subagents. The orchestration map:

```
Phase 1 — Load & Validate Specs ─────────── sequential (parent agent)
Phase 2 — Detect Toolchain ──────────────── sequential (parent agent)
Phase 3 — Build Execution Plan ──────────── sequential (parent agent)
Phase 3.5 — Verify Workflow ─────────────── sequential (parent agent)
Phase 4 — User Review ───────────────────── sequential (parent agent, needs user)
Phase 5 — Back-Add Tech Choices ─────────── ★ parallel (one agent per spec doc to update)
Phase 6+7 — Create Hooks & Rules ────────── ★ parallel (hooks agent + rules agent)
Phase 8 — Suggest Improvements ──────────── sequential (parent agent, needs full context)
Phase 9 — Summary ───────────────────────── sequential (parent agent)
```

### Parallelization rules

1. **Launch via Task tool**: Use `subagent_type: "generalPurpose"` for each parallel work
   unit. Run them in a single message with multiple Task tool calls.
2. **Context handoff**: Each subagent receives the specific slice of context it needs — not
   the full execution plan. Include only the relevant spec excerpts and tech choices.
3. **Merge results**: Parent agent waits for all subagents, then merges their outputs.
   Conflicts (e.g., two agents chose different naming conventions) are surfaced to the user
   as `[Contradiction]` via AskQuestion.
4. **Never parallelize user-facing phases**: Phases 4, 8, and any AskQuestion interactions
   stay in the parent agent. Users see one conversation, not multiple.

### Implementation-time parallelization

When the execution plan is used during implementation, tasks within a milestone that have
no dependency on each other can be worked on in parallel by separate agents. The dependency
graph is in the Task Tracking table (Depends On column). Rules:

- Tasks with `Depends On: —` in the same milestone can run in parallel
- Parallel agents share the **same** milestone branch and must touch disjoint files (see
  `build-execution.mdc` §Parallel Agent Coordination)
- Test tasks for independent components can be written simultaneously
- Parent agent merges results and verifies consistency before the milestone PR
- **Throughput:** [build-executor](../build-executor/SKILL.md) should advance many tasks and
  milestones per invocation when unblocked, not stop after a single PR

## Workflow

### Phase 1 — Load & Validate Specs

Read all doc-planner outputs from the output directory. At minimum, expect:

| Document | Required | Used for |
|----------|----------|----------|
| `research-brief.md` | Yes | Cross-ref matrix, resolution log, agent reports, data asset inventory |
| `deployment-integration.md` | Yes | Deployment architecture, GPU strategy (vs [deployment-catalog.md](../deployment-catalog.md)), pipeline mapping, volume layout |
| `data-management-plan.md` | Yes | Data asset inventory, download methods, staging strategies, task dependencies |
| `feature-list.md` | If exists | Implementation scope and ordering |
| `spec.md` | If exists | Component details, data flow, constraints |
| `config-spec.md` | If exists | Configuration surface, defaults |
| `user-journeys.md` | If exists | Caller-facing UJ-NNN flows; E2E tier; feeds test-plan and 10-e2e |
| `test-plan.md` | If exists | Test strategy, test cases, metrics (UJ ↔ TC mapping) |
| `dependency-inventory.md` | If exists | Runtime/build deps, hardware |
| `roadmap.md` | If exists | Phasing and priorities |
| `acceptance-criteria.md` | If exists | Pass/fail conditions |

For each document read, extract:
- **Tech choices** already made (languages, frameworks, libraries, tools)
- **Constraints** (hardware, performance targets, compatibility)
- **Open questions** and `⚠️ Needs human input` gaps
- **Pipeline stages** and their implementation order

If any spec contains unresolved gaps that block planning, surface them now via AskQuestion.

### Phase 2 — Detect Toolchain

Analyze the repository and specs to determine the project's toolchain:

1. **Language & runtime**: From `dependency-inventory.md`, `research-brief.md`, or repo files
   (`pyproject.toml`, `package.json`, `Cargo.toml`, etc.)
2. **Existing tooling**: Check the repo for existing config files:
   - Linters: `ruff.toml`, `.flake8`, `.eslintrc.*`, `clippy.toml`, `.Rlintr`
   - Formatters: `pyproject.toml [tool.black]`, `.prettierrc`, `rustfmt.toml`
   - Typecheckers: `pyrightconfig.json`, `mypy.ini`, `tsconfig.json`
   - Test runners: `pytest.ini`, `conftest.py`, `jest.config.*`, `vitest.config.*`
3. **Spec-prescribed tools**: If the specs name specific tools, those take precedence.
4. **Gaps**: If the specs don't prescribe a tool for a required category, surface it as a
   **[Decision]** via AskQuestion with recommendations based on the detected language:

```
prompt: "[Decision] No linter is specified in the specs. The project is Python-based.
  Which linter should we use?"

options:
  1. "Ruff — fast, covers linting + formatting, recommended for new Python projects"
  2. "Flake8 + Black — traditional combination"
  3. "Let me specify a different tool"
  4. "Let me explain / provide more context"
```

Record all toolchain decisions. Any new decisions become tech choices that get back-added to
specs in Phase 5.

### Phase 3 — Build Execution Plan

Produce a structured execution plan at `{output_directory}/execution-plan.md`.

The plan organizes implementation into **milestones** derived from the specs. Each milestone
contains **tasks** ordered to support test-driven development (test first, then implementation).

#### Execution Plan structure

Read the full template from [execution-plan-template.md](execution-plan-template.md).

Key sections in the template:
- **Current State** — active phase/milestone/task tracker
- **Tech Stack Summary** — consolidated tool choices
- **Data Dependencies** — which tasks need which data assets (from data-management-plan.md)
- **Implementation Phases** — phases with milestones, tasks (TDD order), and gate checks
- **Git Strategy** — atomic commit rules, minor/major PR structure, branch workflow, PR plan
- **Task Tracking** — master task list with statuses (includes Data Deps column)
- **Phase Gate Log** — gate check records
- **Hook/Rules Configuration** — what to set up

#### Data dependency mapping

When building the task list, cross-reference `docs/spec.md §Data` §Dependencies to
annotate which tasks require which data assets. Add a **Data Deps** column to the Task
Tracking table. Tasks with data dependencies cannot start until the data-management skill has
acquired and verified those assets.

The execution plan should include a note in Phase 1 or as a pre-phase gate: "Data management
must complete before tasks with data dependencies can begin. Run the data-management skill
after this plan is approved."

### Phase 3.5 — Verify or Create Implementation Workflow

Check whether the execution plan already contains a valid implementation workflow:

1. **If `execution-plan.md` exists** (re-run scenario):
   - Read the Current State section — determine which phase/milestone/task is active.
   - Validate the Task Tracking table — check that statuses are consistent (no `completed`
     task with a pending dependency, no `in_progress` task in a phase whose gate hasn't been
     entered).
   - Verify Phase Gate Log — check that completed phases have a gate check recorded.
   - If anything is inconsistent, surface it as `[Ambiguity]` via AskQuestion and repair.
   - Ask the user: "Resume from current state, or regenerate the workflow?"

2. **If no workflow exists** (first run):
   - The workflow was just created in Phase 3. Verify it has:
     - At least 2 implementation phases with gate criteria
     - Every milestone has at least one task
     - Every code task has a preceding test task (TDD ordering)
     - All tasks appear in both the milestone detail and the Task Tracking table
     - Current State section is initialized to Phase 1, first milestone, first task
   - If validation fails, repair the plan before presenting to the user.

3. **Sync with TodoWrite**: When implementation begins, tasks from the execution plan should
   be loaded into the Cursor TodoWrite tool for in-session tracking. The execution plan remains
   the persistent source of truth on disk; TodoWrite provides ephemeral session tracking.

### Phase 4 — User Review

Present the execution plan to the user for review. Use AskQuestion for each section:

**For the phased structure**, present the overall phase breakdown with options:
- **Approve** — phases and gate criteria look good
- **Modify** — user will adjust phase boundaries, gate criteria, or ordering
- **Add a phase** — user wants to insert an additional phase

**For each milestone**, present with options:
- **Approve** — proceed as planned
- **Modify** — user will adjust scope, ordering, or tasks
- **Defer** — move to a later phase
- **Split** — break into smaller milestones

**For the tech stack**, present each tool choice (especially new decisions not already in
specs) with options:
- **Approve** — use this tool
- **Change** — user will specify an alternative

**For hook configuration**, present with options:
- **Approve all** — set up all hooks
- **Select hooks** — user picks which hooks to enable
- **Skip hooks** — no hooks for now

After review, summarize:

```
Execution Plan Review Complete.
  Phases:      [N] approved, [N] modified
  Milestones:  [N] approved, [N] modified, [N] deferred
  Tech choices: [N] confirmed, [N] changed
  Hooks:       [approved/partial/skipped]
```

Update `execution-plan.md` with any modifications.

### Phase 5 — Back-Add Tech Choices to Specs ★ parallel

For every new tech decision made during Phases 2–4 that is not already in the specs:

1. **Group updates by target document** — collect all changes destined for the same file.
2. **Launch parallel agents** — one Task subagent per spec document that needs updating.
   Each agent receives: the target document path, the list of changes to apply, and the
   citation format (`(per build-planner R[N])`).
3. **Resolution Log agent** — in parallel with the spec agents, launch one agent to append
   all new resolutions to `research-brief.md`.
4. **Merge** — parent agent waits for all agents, verifies no conflicts, and confirms the
   updates.

This ensures specs remain the single source of truth and downstream re-runs produce consistent
results.

### Phase 6+7 — Create Hooks & Rules ★ parallel

Phases 6 and 7 are independent and run as parallel subagents launched in a single message:

**Agent A — Hooks**: Creates the hook infrastructure:
- `.cursor/hooks.json` — hook definitions for linting, formatting, and typechecking
- `.cursor/hooks/lint.sh`, `format.sh`, `typecheck.sh` — one script per hook
- Hooks fire on `afterFileEdit`, scoped to project source patterns (e.g., `**/*.py`)
- Each script reads `filePath` from stdin JSON, runs the tool, returns `additional_context`
  with errors or empty on success. Exits 0 always (lint errors go in context, not exit code).
- Makes all scripts executable

**Agent B — Rules**: Creates the rule files (see [rules-reference.md](rules-reference.md)
for full content of each rule):

1. **`.cursor/rules/spec-adherence.mdc`** — always-apply: spec verification, phased workflow,
   tech choices, question-raising, back-adding decisions, task bookkeeping
2. **`.cursor/rules/tdd.mdc`** — source-file scoped: test-first, coverage, naming, no skipping
3. **`.cursor/rules/atomic-commits.mdc`** — always-apply: atomic commits, branch workflow,
   minor/major PRs, PR Plan tracking
4. **`.cursor/rules/build-execution.mdc`** — always-apply: governs how build-executor operates
   (pre-task validation, post-task verification, milestone/phase boundaries, parallel agent
   coordination, error escalation)

**Agent C — Build hooks**: Creates build-execution-specific hooks alongside the dev tooling
hooks:

| Hook | Event | Purpose |
|------|-------|---------|
| `pre-task-check.sh` | `preToolUse` (Write) | Verify the active task's spec source has been read before writing implementation files |
| `post-test-sync.sh` | `afterShellExecution` (test commands) | After test runs, update execution-plan.md task status if tests pass/fail |
| `pr-checklist.sh` | `preToolUse` (Shell, git push) | Before pushing, verify PR checklist criteria are met (all tasks complete, checks pass) |

Build hooks are merged into the same `.cursor/hooks.json` alongside dev tooling hooks.

### Phase 8 — Suggest Improvements

Before finalizing, review the full execution plan, specs, audit decisions, and resolution
log to identify potential improvements. Analyze:

1. **Spec gaps**: Sections in the execution plan that rely on thin evidence or have multiple
   `⚠️ Needs human input` markers. Suggest whether a deeper investigation or an additional
   spec document would help.

2. **Toolchain opportunities**: Based on the tech stack and pipeline, suggest tools or
   practices not currently in the plan that could improve quality, speed, or reliability.
   Examples: CI/CD pipeline setup, pre-commit hooks, containerized dev environments,
   documentation generation, code coverage thresholds.

3. **Architecture risks**: Patterns in the execution plan that could cause problems at scale
   or during deployment — e.g., tight coupling between components, missing error handling
   strategies, no retry/fallback in the Modal integration, missing monitoring.

4. **Milestone ordering**: Opportunities to reorder milestones or tasks for better risk
   reduction — e.g., moving high-uncertainty tasks earlier so blockers surface sooner.

5. **Test coverage gaps**: Components or pipeline stages in the specs that lack corresponding
   test cases in the test plan. Suggest additions.

6. **Process improvements**: Observations about the skill pipeline itself — e.g., specs that
   could be consolidated, audit decisions that suggest a spec needs rework, or recurring
   question patterns that indicate an under-specified area.

Present improvements to the user via AskQuestion:

```
prompt: "Build planner identified [N] potential improvements. Review them?"

options:
  1. "Review and apply improvements now"
  2. "Show me the list — I'll decide which to apply"
  3. "Skip — proceed with the current plan"
```

If the user reviews, present each improvement individually:

```
prompt: "[Improvement 1 of N] Spec gap: The Deployment Integration Plan's cost estimation 
  section has 4 placeholder values. A quick check of Modal's pricing page could fill 
  these in now, avoiding guesswork during implementation."

options:
  1. "Apply — fill in the cost estimates now"
  2. "Note it — add a TODO but proceed"
  3. "Skip — not important"
  4. "Let me explain / provide more context"
```

For each accepted improvement:
- Apply it immediately (update the relevant spec, plan, or rule)
- Log it in the execution plan under a new **Improvements Applied** section
- Back-add to specs if the improvement changes a tech choice or adds a dependency

Append an **Improvements** section to `execution-plan.md`:

```markdown
## Improvements

### Applied

| # | Category | Description | Action Taken |
|---|----------|-------------|--------------|
| I1 | Spec gap | Cost estimates filled in deployment-integration.md | Updated §Cost Estimation |
| I2 | Toolchain | Added pre-commit hook for Ruff | Added to hooks.json |

### Noted (TODOs)

| # | Category | Description | When to Address |
|---|----------|-------------|-----------------|
| I3 | Test coverage | No tests for postprocessing stage | During M2 implementation |

### Declined

| # | Category | Description | Reason |
|---|----------|-------------|--------|
| I4 | Architecture | Suggested retry logic for Modal | User: "Not needed for research tool" |
```

### Phase 9 — Summary

Report completion:

```
Build Planner Complete.

Execution plan written to: workflow-state.yaml + execution plan artifact
  Phases:     [N] implementation phases defined
  Milestones: [N] ([N] approved, [N] deferred)
  Total tasks: [N] ([N] test tasks, [N] code tasks)
  Gate checks: [N] phase gates defined

Hooks created:
  .cursor/hooks.json — [N] hooks configured
  .cursor/hooks/lint.sh — [linter tool]
  .cursor/hooks/format.sh — [formatter tool]
  .cursor/hooks/typecheck.sh — [typechecker tool]

Rules created:
  .cursor/rules/spec-adherence.mdc — always-apply
  .cursor/rules/tdd.mdc — scoped to [source patterns]
  .cursor/rules/atomic-commits.mdc — always-apply
  .cursor/rules/build-execution.mdc — always-apply

Git strategy:
  Branch workflow: milestone → phase → main
  Minor PRs planned: [N] (one per milestone)
  Major PRs planned: [N] (one per phase)
  Commit convention: [task-id] type: description

Specs updated: [N] documents back-updated with new tech choices

Improvements: [N] suggested, [N] applied, [N] noted as TODOs, [N] declined

Data dependencies:
  Tasks with data deps: [N] (require data-staging to complete first)
  Data assets needed:   [N] ([total size])

Implementation workflow:
  Current phase: Phase 1 — Foundation
  First task:    T1.1 — [task description]
  Phase 1 gate:  [N] criteria to satisfy before Phase 2

Next step: run data-staging to acquire and verify data assets, then invoke build-executor.
```

## Next Step — Data Staging, then Build Executor

After build-planner completes:

1. **Data management**: Run the [data-staging](../data-management/SKILL.md) skill to acquire,
   verify, and stage all corpus fixtures, datasets, and checkpoints identified in
   `docs/spec.md §Data`. This must complete before build-executor starts any task
   that has data dependencies.

2. **Build executor**: The [build-executor](../build-executor/SKILL.md) skill then executes
   the plan: implements tasks in TDD order, commits atomically, opens PRs at milestone and
   phase boundaries (merge stays user-approved), and keeps working across milestones in one
   session when practical. It orchestrates parallel agents for independent work.

## Idempotency

This skill is idempotent. On re-invocation:

1. **Execution plan & workflow**: If `execution-plan.md` exists, read it and ask the user
   whether to reuse, update (merge changes), or regenerate. If reusing, validate the
   workflow state (Phase 3.5) — verify task statuses, phase gates, and dependencies are
   consistent. Repair any inconsistencies.
2. **Task progress**: Preserve all `completed` and `in_progress` task statuses. Only reset
   `pending` tasks if the user explicitly requests regeneration.
3. **Phase gates**: Preserve the Phase Gate Log. On update, re-evaluate gate criteria against
   current task statuses and flag any gates that should now be marked as passed.
4. **Hooks**: If `.cursor/hooks.json` exists, read it and merge new hooks rather than
   overwriting. Preserve any user-added hooks.
5. **Rules**: If rule files exist, read them and update in place rather than overwriting.
   Preserve any user modifications.
6. **Back-added specs**: Check timestamps — only update specs that have changed since the
   last run.

## Output Rules

1. **Spec-grounded**: Every task in the execution plan must trace to a spec document. Cite
   the source (e.g., `spec.md §Component Details`, `test-plan.md TC-003`).
2. **TDD ordering**: Within each milestone, test tasks always precede their corresponding
   implementation tasks.
3. **No orphan decisions**: Every tech choice lives in a spec. If it's not in a spec, it
   gets back-added before the skill completes.
4. **Hooks are non-blocking**: Hook scripts should report errors as context, not block the
   agent. Lint errors inform; they don't prevent edits.
5. **Rules are enforceable**: Rule content must be concrete and actionable — no vague
   guidance like "write good code".
