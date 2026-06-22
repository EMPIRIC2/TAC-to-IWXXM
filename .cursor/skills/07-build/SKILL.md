---
name: 07-build
description: >
  Executes the implementation plan task-by-task following TDD ordering, spec-adherence rules,
  and atomic commit conventions. Orchestrates parallel agents for independent tasks, manages
  branches and PRs, invokes 08-verify-build at milestone boundaries, and keeps the execution
  plan in sync with progress. Supports delta mode for feature addition and large changes via
  active 16-evolve cycles only — do not use for net-new features without an evolve cycle.
---

# 07 — Technical Execution (Build)

Execute the execution plan: implement tasks in TDD order, commit atomically, create PRs
at milestone and phase boundaries, and orchestrate parallel agents for independent work.

**Preamble:** [pipeline-preamble.md](../pipeline-preamble.md) — shared conventions for stages 00–19.
**Cross-cutting:** [considerations.md](../considerations.md), [connectivity-gates.md](../connectivity-gates.md).
**State agent:** [workflow-state-manager](../../agents/workflow-state-manager.md) — mandatory read/update.

## Connectivity (stage 07)

Implement and test **all three** layers from connectivity-gates: H0i (integration), H0c (CORS),
and live scripts (for 13). See §Stage 07 in connectivity-gates for task completion criteria.

## Throughput

Treat one agent session as **batch-oriented**: advance the Task Loop as far as
dependencies, data management, branches, and checks allow — across **multiple milestones**.

- **PRs are not session boundaries.** After 08-verify-build passes at a milestone, create
  the minor PR, record it, then **continue** with the next milestone.
- **Same for phase boundaries:** Run the gate check, create the major PR, then proceed.
- **Do not** end the turn after opening a PR unless the user asked for that cadence or
  there is no unblocked next task.
- **AskQuestion** is for ambiguity, `blocked` tasks, or user steering — not a pause
  before every task or milestone.

## Prerequisites

1. **Phase B gate must pass**:
   - 04-tech-plan `completed` — execution plan exists
   - 05-verify-tech `completed` — tech plan audited
   - 06-tech-tooling `completed` — dev tooling installed
2. Required:
   - `workflow-state.yaml + execution plan artifact` with at least one approved phase
   - `.cursor/rules/` — spec-adherence, tdd, atomic-commits, build-execution rules
   - `.cursor/hooks.json` — hooks installed
3. **Data management** (if applicable): Check `docs/spec.md §Data`. Tasks with data
   dependencies are blocked until data is staged. Offer to run data-staging if needed.

## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).
**Stage key:** `stages.07-build`.

Invoke **workflow-state-manager** `read_context` before any other action; `update` after each
substep. **Do not** edit `workflow-state.yaml` directly.


**Detail:** `workflow-state.yaml + execution plan artifact` §Current State — update **both** on every task/milestone change.

### On invocation

1. Read `workflow-state.yaml + execution plan artifact` §Current State
2. Determine active phase, milestone, task
3. Report current position:

```
Execution State:
  Phase:     [N] — [Phase Name]
  Milestone: M[N] — [Milestone Name]
  Task:      T[N.N] — [Task description]
  Progress:  [N] / [N] tasks ([%])

  Ready to work on: T[N.N] — [description]
```

4. Start the Task Loop without AskQuestion unless tasks are `blocked` or the user
   narrowed scope.

## Delta / feature-addition mode

- Implement **only** pending tasks tagged with `evolve_cycle_id` or listed in cycle scope.
- Support multiple Fn in one branch (`evolve/{cycle-id}-{slug}`).
- PR title/body references evolve cycle and feature IDs.

## Workflow

### Phase 1 Scaffold (Template Projects)

If `workflow-state.yaml` §template.id is `utility` or `job`, the first milestone's
first task is the template scaffold. Execute it before entering the normal Task Loop:

1. **Read template registry**: Load [template-registry.md](../template-registry.md)
   §Template Structure Reference for the selected template type
2. **Clone template**: Clone the template repo from
   `https://github.com/Cognitive-Chemistry-Labs/template-modal-{id}.git` into a
   temporary location
3. **Copy structure**: Copy the template's `src/`, `.github/`, `.gitignore`, and
   `README.md` into the project repo (do not overwrite existing files that have
   already been modified by prior pipeline stages)
4. **Replace placeholders**: Replace all `{{SERVICE_NAME}}` occurrences with the value
   from `workflow-state.yaml` §template.service_name
5. **Prune GPU classes** (job template only): Remove GPU class variants not in
   `workflow-state.yaml` §template.gpu_tiers from `src/app.py`
6. **Commit**: `[T1.1] config: scaffold from template-modal-{id}`

After the scaffold commit, continue with remaining Phase 1 tasks (dependency setup,
initial test, CI/CD config) and then enter the normal Task Loop for subsequent phases.

### Task Loop

For each task in order (respecting dependencies):

#### Step 1 — Pre-flight

1. **Read spec source** cited in the task's Spec Source column
2. **Check dependencies**: All tasks in Depends On must be `completed`
3. **Check data deps**: If Data Deps is non-empty, verify assets are staged
4. **Check branch**: Correct milestone branch exists and is checked out
5. **Update state**: Set task to `in_progress` in Task Tracking table

#### Step 2 — Execute

**Test tasks**:
1. Read test plan / acceptance criteria
2. Write test following TDD conventions
3. Run test — should fail (red phase)
4. If test passes without implementation, surface as `[Uncertainty]`

**Code tasks**:
1. Read spec source for component details
2. Implement to make preceding tests pass
3. Run tests — should now pass (green phase)
4. Refactor if needed, keeping tests green

**Browser-facing FastAPI** (ChatRAG, internal write, Modal data-mgmt ASGI):
- Call `deployed-service_shared_schemas.cors.configure_cors` in `create_app`
- Extend `tests/unit/test_cors_policy.py` for new routes if needed
- Add/update `tests/integration` when wiring crosses apps (H0i)
- Task is not complete until **H0c + H0i** pass (see [connectivity-gates.md](../connectivity-gates.md) §Stage 07)

**For all tasks**:
- Follow tech stack from execution plan
- Raise anything unclear via AskQuestion
- If a new dependency is needed, raise as `[Decision]`, back-add to specs
- When any `[Decision]`, `[Ambiguity]`, or `[Contradiction]` is resolved during
  implementation, create an ADR in `docs/adr/` per [considerations.md](../considerations.md)
  §ADR logging. Set the Stage field to `07-build`. Reference the task ID (e.g., T1.3)
  in the ADR's Context section.

#### Step 3 — Post-task checks

1. Run linter on changed files
2. Run typechecker
3. Run full test suite (not just new tests)
4. Fix any failures before proceeding

#### Step 4 — Commit & record

1. Verify correct branch is checked out (create `feat/M{N}-{slug}` if needed)
2. Stage all task-related files
3. Commit: `[T{id}] {type}: {description}`
4. Verify clean state (`git status`)
5. Append to `workflow-state.yaml` §`git_history.commits`:
   ```yaml
   - sha: <short-sha>
     branch: feat/M{N}-{slug}
     message: "[T{id}] {type}: {description}"
     stage: "07-build"
     files_changed: <count>
     timestamp: "<ISO-8601>"
   ```
6. Commit the workflow-state update (same or next commit)

**Never leave uncommitted work.** If an AskQuestion, gate check, or session end
is imminent, commit first. Progress lost to uncommitted work is unrecoverable.

#### Step 5 — Update state

1. Set task to `completed` in Task Tracking, record date
2. Advance Current State to next pending task
3. Report: `Completed T{id}: {description}. Next: T{next_id}`

### Milestone Boundary

When all tasks in a milestone are `completed`:

1. **Invoke [08-verify-build](../08-verify-build/SKILL.md)**: Run all checks via parallel
   agents. 08-verify-build auto-corrects where possible and only blocks on non-trivial
   issues.
2. **Create minor PR** from milestone branch to phase branch:
   - Title: `[M{N}] {Milestone Name}`
   - Body: task list, spec references, check results
3. **Present to user** (PR URL). Do NOT stop the session.
4. Update PR Plan table. Continue Task Loop for next milestone.

### Phase Boundary

When all milestones in a phase are `completed`:

1. **Invoke [08-verify-build](../08-verify-build/SKILL.md)** at phase scope
2. **Run phase gate check**: Verify every criterion in Phase Gate Check section
3. **Record in Phase Gate Log**: Date, result, notes
4. If any gate criterion is unmet, surface as `[Decision]`
5. **Create major PR** from phase branch to main
6. Present to user. Continue executing while unblocked.

## Agent Orchestration

### Parallel task execution

Within a milestone, identify tasks with no unmet dependencies:

1. Build dependency graph from Task Tracking table
2. Identify parallel batch: tasks with all dependencies `completed`
3. Launch Task subagents (`subagent_type: "generalPurpose"`) for each
4. Each agent receives: task definition, spec excerpts, tech stack, branch name
5. Parent agent waits, reviews for consistency, commits each task separately

### Sequential fallback

Chain dependencies (T1.1 → T1.2 → T1.3) execute sequentially in the parent agent.

### User interaction stays in parent

All AskQuestion calls, PR presentations, and gate checks happen in the parent agent.

## Error Handling

### Task failure

1. Set task to `blocked` with blocker description
2. Surface via AskQuestion: fix now / skip / defer
3. If skipping, check and report downstream cascade

### Spec gap

1. Raise as `[Ambiguity]` with what's missing
2. On resolution, back-add to spec
3. Continue with resolved detail

## Idempotency

- Completed tasks are never re-executed
- In-progress tasks resume from current state
- Blocked tasks are re-evaluated (blocker may be resolved)
- Existing branches and PRs are reused

## Validation tasks (required per entry point)

For every Modal `run()` entry point task, include a paired validation task **before**
marking the implementation task complete:

| Check | Spec source |
|-------|-------------|
| Invalid payload → error or `partial_failure` ZIP | config-spec §Validation Rules |
| Upstream minima (e.g. `chunk_size` ≥ 15) | config-spec, upstream CLI |
| Required fields for stage | api-contract, spec.md |

Reference hotfix incidents in `docs/hotfix-log.md` when adding validation — do not
repeat post-deploy surprises (RET-001).

## Output Rules

1. **One task at a time**: Complete, commit, update state before starting next
2. **Tests before code**: Every code task preceded by its test passing red phase
3. **Never skip checks**: Lint, typecheck, tests after every task
4. **Atomic commits**: One commit per task, never bundle
5. **PRs require approval to merge**: Never auto-merge
6. **State always current**: Execution plan reflects true progress at all times
7. **Verify before PR**: Always invoke 08-verify-build at boundaries
8. **Maximize per pass**: Complete many tasks and milestones per invocation
