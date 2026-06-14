# Execution Plan Template

Use this template when generating `{output_directory}/execution-plan.md`.

```markdown
# Execution Plan

> **Project**: [Project Name]
> **Generated**: [Date]
> **Skill**: build-planner
> **Specs consumed**: [list of spec files read]

## Current State

Track overall progress. Update this section as work proceeds.

| Field | Value |
|-------|-------|
| **Active phase** | Phase 1: Foundation |
| **Active milestone** | M1: Project Setup |
| **Active task** | T1.1: ... |
| **Tasks completed** | 0 / [total] |
| **Last updated** | [date] |

## Tech Stack Summary

Consolidated from specs and toolchain detection:

| Category | Choice | Source | Spec Reference |
|----------|--------|--------|----------------|
| Language | Python 3.10+ | dependency-inventory.md | §Runtime Dependencies |
| Linter | Ruff | User decision (R8) | — |
| Formatter | Ruff format | User decision (R8) | — |
| Typechecker | Pyright | User decision (R9) | — |
| Test runner | pytest | test-plan.md | §Test Strategy |
| Deployment | Modal | deployment-integration.md | §App Architecture |
| ... | ... | ... | ... |

## Data Dependencies

Assets from `docs/spec.md §Data` that must be staged before tasks can run.
The data-management skill must complete before build-executor starts any task listed below.

| Asset | Type | Size | Staging Status | Needed By Tasks |
|-------|------|------|----------------|-----------------|
| [D1 — e.g., ESM-2 weights] | model_weights | [2.5 GB] | pending | T2.1, T3.1 |
| [D2 — e.g., SAbDab dataset] | dataset | [500 MB] | pending | T1.1, T2.3 |
| ... | ... | ... | ... | ... |

**Data management gate**: All assets with status `pending` must reach `verified` before their
dependent tasks can start. Tasks with no data dependencies can proceed immediately.

## Implementation Phases

Phases are the top-level structure. Each phase groups related milestones and has gate
criteria that must be met before the next phase begins.

### Phase 1: Foundation

**Objective**: Project scaffolding, tooling, and baseline infrastructure.
**Entry gate**: Execution plan approved by user.
**Exit gate**: Project builds, linter/formatter/typechecker pass on empty scaffold, test
runner executes with 0 tests found.

#### Milestones

##### M1: [Milestone Name] — [Priority]

**Goal**: [What this milestone delivers]
**Acceptance criteria**: [From acceptance-criteria.md if available]

###### Tasks (TDD order)

| # | Task | Type | Status | Spec Source | Depends On |
|---|------|------|--------|-------------|------------|
| T1.1 | Write tests for [component] | Test | pending | test-plan.md TC-001 | — |
| T1.2 | Implement [component] | Code | pending | spec.md §Component | T1.1 |
| T1.3 | Write tests for [component B] | Test | pending | test-plan.md TC-002 | — |
| T1.4 | Implement [component B] | Code | pending | spec.md §Component B | T1.3 |
| T1.5 | Integration test for M1 | Test | pending | test-plan.md §Integration | T1.2, T1.4 |

###### Parallelizable tasks

Tasks with `Depends On: —` can be worked on by parallel agents. In M1 above, T1.1 and T1.3
are independent and can run simultaneously via separate Task subagents.

##### M2: [Milestone Name]
...

#### Phase 1 Gate Check

- [ ] All M1 tasks completed
- [ ] All tests passing
- [ ] Linter, formatter, typechecker clean
- [ ] [Additional criteria from specs]

---

### Phase 2: Core Pipeline

**Objective**: Implement the core computational pipeline.
**Entry gate**: Phase 1 gate check passed.
**Exit gate**: Core pipeline executes end-to-end on test data, all unit and integration
tests passing.

#### Milestones
...

#### Phase 2 Gate Check

- [ ] Pipeline runs end-to-end on test data
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Performance within spec thresholds (if defined)

---

### Phase 3: Deployment & Validation

**Objective**: Deploy to target, run validation experiments from the paper.
**Entry gate**: Phase 2 gate check passed.
**Exit gate**: Deployed on Modal, validation experiments reproduce paper results within
acceptance thresholds.

#### Milestones
...

#### Phase 3 Gate Check

- [ ] deployment successful
- [ ] Validation experiments pass acceptance criteria
- [ ] All tests passing (unit + integration + validation)

---

## Git Strategy

### Commit Rules

All commits are **atomic** — each commit does exactly one thing and the codebase passes
linting, typechecking, and all existing tests after every commit.

| Commit type | Scope | Naming convention |
|-------------|-------|-------------------|
| Task commit | One task (T1.1, T1.2, ...) | `[T1.1] test: add tests for [component]` |
| Fix commit | Fix within a task | `[T1.2] fix: correct [description]` |
| Config commit | Tooling / config change | `chore: configure [tool]` |
| Refactor commit | Cleanup within a milestone | `[M1] refactor: [description]` |

### PR Structure

PRs map to milestones and phases. Two levels:

| PR type | Scope | Branch pattern | Review gate |
|---------|-------|----------------|-------------|
| **Minor PR** | One milestone | `feat/M1-[slug]` | All milestone tasks complete, tests pass, lint clean |
| **Major PR** | One phase (rolls up minor PRs) | `phase/1-foundation` | Phase gate check passed |

#### Minor PRs (per milestone)

Each milestone produces one minor PR. The PR:
- Contains all atomic commits for that milestone's tasks
- Targets the phase branch (`phase/N-[slug]`)
- Title: `[M1] [Milestone Name]`
- Body auto-generated from the milestone's task list, spec references, and test results
- Presented to the user for review before merge (merge requires explicit approval)
- **Agent sessions** do not stop here by default: after the PR exists and is recorded, continue
  the next milestone when branch policy allows (see `.cursor/skills/build-executor/SKILL.md`
  §Throughput)

#### Major PRs (per phase)

Each phase produces one major PR that rolls up all minor PRs. The PR:
- Contains all merged minor PRs for that phase
- Targets the main branch
- Title: `Phase N: [Phase Name]`
- Body includes: phase gate check results, milestone summaries, test/lint/typecheck results
- Presented to the user for review before merge (merge requires explicit approval)
- Same **session throughput** expectation as minor PRs when the next phase is not blocked on
  `main` updating

### PR Checklist (auto-generated in PR body)

```markdown
## Checklist
- [ ] All tasks completed (N/N)
- [ ] All tests passing
- [ ] Linter clean
- [ ] Typechecker clean
- [ ] Spec references verified
- [ ] No unresolved `⚠️` markers in changed files
- [ ] Audit decisions respected (no denied statements reintroduced)
```

### Branch Workflow

```
main
 └── phase/1-foundation
      ├── feat/M1-project-setup       → minor PR → phase/1-foundation
      ├── feat/M2-core-dependencies    → minor PR → phase/1-foundation
      └── (all M merged)              → major PR → main
 └── phase/2-core-pipeline
      ├── feat/M3-preprocessing        → minor PR → phase/2-core-pipeline
      └── ...
```

### PR Plan

| PR | Type | Milestone/Phase | Branch | Target | Status |
|----|------|-----------------|--------|--------|--------|
| PR-1 | Minor | M1 | feat/M1-[slug] | phase/1-foundation | pending |
| PR-2 | Minor | M2 | feat/M2-[slug] | phase/1-foundation | pending |
| PR-3 | Major | Phase 1 | phase/1-foundation | main | pending |
| PR-4 | Minor | M3 | feat/M3-[slug] | phase/2-core-pipeline | pending |
| ... | ... | ... | ... | ... | ... |

## Task Tracking

Master task list for quick status overview. Update status as work proceeds.

Statuses: `pending` | `in_progress` | `completed` | `blocked` | `deferred`

| Task | Milestone | Phase | Type | Status | Blocked By | Data Deps | Completed |
|------|-----------|-------|------|--------|------------|-----------|-----------|
| T1.1 | M1 | 1 | Test | pending | — | — | — |
| T1.2 | M1 | 1 | Code | pending | T1.1 | — | — |
| T1.3 | M1 | 1 | Test | pending | — | D2 | — |
| T1.4 | M1 | 1 | Code | pending | T1.3 | D2 | — |
| T1.5 | M1 | 1 | Test | pending | T1.2, T1.4 | — | — |
| ... | ... | ... | ... | ... | ... | ... | ... |

**Note**: Tasks with entries in the Data Deps column cannot start until the referenced
assets have been acquired and verified by the data-management skill. A task is blocked if its
Data Deps assets are not yet `verified` in the Data Dependencies table above.

## Phase Gate Log

Record gate check results as phases complete:

| Phase | Gate Check Date | Result | Notes |
|-------|----------------|--------|-------|
| 1 | — | — | — |
| 2 | — | — | — |
| 3 | — | — | — |

## Hook Configuration

| Hook | Event | Tool | Config File | Purpose |
|------|-------|------|-------------|---------|
| Lint | afterFileEdit | [linter] | [config path] | Catch errors on save |
| Format | afterFileEdit | [formatter] | [config path] | Consistent style |
| Typecheck | afterFileEdit | [typechecker] | [config path] | Type safety |

## Rules to Create

| Rule | File | Scope | Purpose |
|------|------|-------|---------|
| spec-adherence | .cursor/rules/spec-adherence.mdc | Always apply | Enforce spec-checking, phased workflow, gate checks |
| tdd | .cursor/rules/tdd.mdc | Source files | Enforce test-first development |
| atomic-commits | .cursor/rules/atomic-commits.mdc | Always apply | Enforce atomic commits, branch workflow, PR structure |
| build-execution | .cursor/rules/build-execution.mdc | Always apply | Pre-task validation, post-task checks, boundary enforcement, error escalation |

## Open Questions

- [Any remaining questions that surfaced during planning]
```
