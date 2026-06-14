---
name: 04-tech-plan
description: >
  Interviews the user for technical details: architecture, deployment strategy, test plan
  specifics, integration points, package choices, and architectural decision records. Produces
  an execution plan, dependency inventory, ADRs, deployment plan, and data management plan.
  Template-driven interview with batched questions. Includes deployment strategy planning.
---

# 04 — Technical Planning Interview

Interview the user to produce technical implementation documents: execution plan, dependency
inventory, ADRs, deployment plan, and data management plan.

**Preamble:** [pipeline-preamble.md](../pipeline-preamble.md) — shared conventions for stages 00–17.
**Cross-cutting:** [considerations.md](../considerations.md), [connectivity-gates.md](../connectivity-gates.md).
**State agent:** [workflow-state-manager](../../agents/workflow-state-manager.md) — mandatory read/update.

## Connectivity (stage 04)

Technical plan **must** include executable connectivity work:

| Deliverable | Content |
|-------------|---------|
| `workflow-state.yaml + execution plan artifact` | Tasks: `configure_cors` on each browser-facing FastAPI app; `tests/unit/test_cors_policy.py`; `tests/smoke/test_staging_connectivity.py`; `scripts/deploy/verify_connectivity.sh` |
| `docs/staging-secrets-matrix.md` | `METAR_CORS_ORIGINS`, all `VITE_*`, staging `METAR_STAGING_*_FRONTEND_URL` |
| ADR (if needed) | Defer BFF/gateway (TP-001) → explicit CORS strategy |

Interview: confirm frontend↔API origin map for staging and production.

## Prerequisites

1. **Phase A gate must pass**:
   - 01-requirements `completed` — spec documents exist
   - 02-verify-plan `completed` — specs audited
   - 03-plan-tooling `completed` — plan guardrails installed
2. Required inputs:
   - `docs/feature-list.md` — approved feature scope
   - `docs/spec.md` — approved component architecture
   - `docs/user-journeys.md` — approved caller-facing flows (UJ-NNN)
   - `docs/test-plan.md` — approved test strategy (UJ ↔ TC mapping)
   - `docs/product-audit.md` — audit results
3. Plan tooling must be installed (`.cursor/rules/plan-adherence.mdc` etc.)

## Uncertainty Resolution Protocol

Follow [considerations.md](../considerations.md) §Uncertainty. During technical interviews,
surface:
- **[Decision]**: Multiple valid tech approaches (e.g., REST vs gRPC, SQL vs NoSQL)
- **[Ambiguity]**: Spec section too vague for technical implementation
- **[Contradiction]**: Technical choice conflicts with a product requirement

## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).
**Stage key:** `stages.04-tech-plan`.

Invoke **workflow-state-manager** `read_context` before any other action; `update` after each
substep. **Do not** edit `workflow-state.yaml` directly.


### On invocation — check state

1. Use **workflow-state-manager** context brief for §stages.04-tech-plan (from agent `read_context`).
2. **If `completed`**: Ask: "Reuse existing tech plan, update, or regenerate?"
3. **If `in_progress`**: Report completed substeps. Resume or restart.
4. **If `pending`**: Start fresh.

### Commit-as-you-go

Commit artifacts to an appropriate branch before transitioning to the next stage or
asking the user a blocking question. Branch type per
[workflow-state-reference.md](../workflow-state-reference.md) §Git history.
Record every commit in `workflow-state.yaml` §`git_history.commits` with
`stage: "04-tech-plan"`.

## Delta / feature-addition mode

- **Append** tasks/milestones to `workflow-state.yaml + execution plan artifact`; do not reset completed work.
- Tag new tasks with `evolve_cycle_id` and `feature_ids`.
- New phase/milestone only if scope warrants — user approves via AskQuestion.

## Workflow

### Phase 1 — Detect Existing Toolchain & Template Baseline

Analyze the repository and specs for existing technical choices:

1. **Language & runtime**: From repo files (`pyproject.toml`, `package.json`, etc.)
2. **Existing tooling**: Check for config files (linters, formatters, typecheckers)
3. **Spec-prescribed tools**: Tools already named in product specs take precedence
4. **Gaps**: Surface as `[Decision]` with recommendations per language

**Template baseline** (if template selected): Read `workflow-state.yaml` §template and
[template-registry.md](../template-registry.md). The template pre-decides:

| Choice | API | Worker | Monolith |
|--------|-----|--------|----------|
| Language | Python 3.11+ | Python 3.11+ | Python 3.11+ |
| Platform | Render / Docker / K8s | same | same |
| Entry | `src/app.py` (HTTP) | `src/worker.py` | both |
| DB | Postgres | shared schema | async SQLAlchemy |
| CI/CD | GitHub Actions | GitHub Actions | GitHub Actions |
| Layout | `api/` + `rag/` + `db/` | `jobs/` + `rag/` + `db/` | combined |

These choices are pre-filled. Interview questions focus on domain-specific decisions not
covered by the template (dependencies, data assets, algorithm choices, etc.).

Record all detected/decided toolchain choices.

### Phase 2 — Technical Interview

Interview the user across six topic areas. For each, use template-driven questions
in batches of 3-5.

#### 2.1 — Architecture

Questions derived from spec.md and feature-list.md:

- System architecture pattern (monolith, microservice, serverless, etc.)
- Component interaction patterns (sync/async, event-driven, request-response)
- Data flow between components
- State management approach
- Error handling strategy
- Scalability approach

For each architectural decision, create an ADR:

```markdown
# ADR-001: [Title]

## Status: Accepted

## Context
[What is the issue or decision to be made?]

## Decision
[What was decided and why?]

## Consequences
[What are the trade-offs?]

## Alternatives Considered
[What other options were evaluated?]
```

#### 2.2 — Deployment Strategy

Questions about target deployment:

- Target platform (Modal, Render, AWS, self-hosted, etc.)
- Containerization approach
- GPU/compute requirements — for job templates, map workloads to tiers from
  [deployment-catalog.md](../deployment-catalog.md); document recommended + fallback per stage
- Modal non-GPU cost: CPU ($/core/s), memory ($/GiB/s), volumes ($/GiB/mo + 1 TiB free)
- Scaling strategy (horizontal, vertical, auto-scaling)
- Secrets management
- Data/volume mounting
- CI/CD pipeline
- Rollback strategy
- Monitoring and alerting
- Cost constraints

**This is where deployment planning happens** — not in Stage 12. Stage 12 only
*verifies* that this plan still holds after implementation.

#### 2.3 — Test Plan Details

Drill deeper into test-plan.md:

- Test types to implement (unit, integration, e2e, performance, security)
- Coverage targets per component
- CI/CD test integration
- Test data strategy
- Mock/stub strategy for external services
- Performance benchmarks and thresholds

#### 2.4 — Integration Points

For each external integration in spec.md:

- Protocol (REST, gRPC, WebSocket, message queue)
- Authentication method
- Rate limits and quotas
- Error handling and retry strategy
- Timeout configuration
- API versioning strategy

#### 2.5 — Package Choices

For each dependency category:

- Runtime dependencies with version constraints
- Build/dev dependencies
- Optional dependencies
- Justification for each non-obvious choice
- Known security advisories

#### 2.6 — Data Assets (if applicable)

If the project needs external data (corpus fixtures, datasets, etc.):

- Asset inventory with sources and sizes
- Download and staging strategy
- Verification method (checksums, shape checks)
- Local vs deployment staging
- Authentication requirements

### Phase 3 — Build Execution Plan

Produce `workflow-state.yaml + execution plan artifact` using the template from
[execution-plan-template.md](../build-planner/execution-plan-template.md).

Organize implementation into **phases**, each containing **milestones**, each containing
**tasks** in TDD order (test first, then implementation).

**Template scaffold phase** (if template selected): The first phase must always be:

> **Phase 1: Template Scaffold**
> - M1: Project Scaffold
>   - T1.1 (Config): Clone template repo, replace `{{SERVICE_NAME}}` placeholders,
>     commit initial scaffold
>   - T1.2 (Config): Update `pyproject.toml` / dependency files with project-specific deps
>   - T1.3 (Test): Add initial test for the core logic module (service.py / utils.py)
>   - T1.4 (Config): Configure CI/CD workflow (update deploy_to_modal.yml if needed)

For job templates, Phase 1 also includes:
>   - T1.5 (Config): Select deploy targets per deployment-catalog.md — remove pruned classes from app.py
>   - T1.6 (Config): Configure cache volume name and warmup function

Subsequent phases contain the domain-specific implementation.

Key sections:
- **Current State** — initialized to Phase 1, first milestone, first task
- **Template** — selected template ID, repo, service name, deploy targets (references
  `workflow-state.yaml` §template)
- **Tech Stack Summary** — consolidated tool choices from Phase 1 + 2 (template
  pre-fills platform, language, deploy, CI/CD)
- **Data Dependencies** — which tasks need which data assets
- **Implementation Phases** — phases with milestones, tasks, gate checks
- **Git Strategy** — atomic commits, branch workflow, PR plan
- **Task Tracking** — master task list with statuses and dependency graph
- **Phase Gate Log** — empty, populated during build

#### Task design

Each task must:
- Trace to a spec document section (Spec Source column)
- Have clear dependencies (Depends On column)
- Note data dependencies (Data Deps column)
- Be one of: Test, Code, Config, Docs
- Follow TDD ordering within milestones

### Phase 4 — User Review

Present the technical plan for review using AskQuestion:

**For the phased structure**:
- Approve / Modify / Add a phase

**For each milestone**:
- Approve / Modify / Defer / Split

**For the tech stack** (especially new decisions):
- Approve / Change

**For the deployment plan**:
- Approve / Modify

After review, update all documents with modifications.

### Phase 5 — Back-Add Tech Choices to Specs (Parallel)

For every new tech decision not already in the product specs:

Launch parallel agents (one per spec document that needs updating):
- Each agent receives: target doc, list of changes, citation format
- Resolution Log agent: append new resolutions to appropriate log

### Phase 6 — Generate Additional Documents

Write remaining documents:

1. **`docs/dependency-inventory.md`** — all dependencies with versions and justifications
2. **`docs/adr/`** — one ADR per architectural decision
3. **Deployment plan** (e.g., `docs/deploy.md §Integration` or `docs/deployment-plan.md`)
4. **`docs/spec.md §Data`** (if data assets identified)
5. **`docs/api-contract.md`** (if API endpoints defined)

### Phase 7 — Summary

```
Technical Planning Complete.

Execution plan: workflow-state.yaml + execution plan artifact
  Phases:     [N]
  Milestones: [N]
  Tasks:      [N] ([N] test, [N] code, [N] config)
  Gate checks: [N]

Tech stack:
  Language:    [language] [version]
  Linter:      [tool]
  Formatter:   [tool]
  Typechecker: [tool]
  Test runner: [tool]

Deployment: [platform]
  Strategy: [approach]
  GPU/Compute: [requirements]

Documents generated: [N]
  workflow-state.yaml + execution plan artifact
  docs/dependency-inventory.md
  docs/adr/001-[name].md (x[N])
  docs/[deployment-plan].md
  [additional docs]

ADRs created: [N]
Specs updated: [N] documents back-updated with tech choices

Data dependencies:
  Tasks with data deps: [N]
  Assets needed: [N] ([total size])

Next step: 05-verify-tech
```

**State**: Set status to `completed`.

## Idempotency

On re-invocation:
- If execution-plan.md exists, read and offer reuse/update/regenerate
- Preserve completed/in_progress task statuses
- Merge new hooks rather than overwriting
- Check timestamps on back-added specs

## Handoff checklist (00/01 → execution plan)

Before marking 04-tech-plan `completed`, verify these items are **tasks or ADRs** in
`workflow-state.yaml + execution plan artifact`:

- [ ] Every `[Decision]` / `resolution_id` from `workflow-state.yaml` §decisions_log
- [ ] Every config parameter in config-spec marked **include** vs **exclude** for v1
- [ ] Validation rules aligned with upstream CLI (cross-check 00-context contradictions)
- [ ] User journeys in `docs/user-journeys.md` with E2E tier and planned test modules
- [ ] Modal testing tiers per [ADR-004](../../docs/adr/ADR-004.md) (T0–T3) assigned to stages
- [ ] deploy targets in plan match [deployment-catalog.md](../deployment-catalog.md) and
  `workflow-state.yaml` §template.gpu_tiers (or all ten if unset); drift documented if deferred

## Output Rules

1. **Spec-grounded**: Every task traces to a spec document section.
2. **TDD ordering**: Test tasks precede implementation tasks within milestones.
3. **No orphan decisions**: Every tech choice lives in a spec or ADR.
4. **Deployment planning here**: Deployment strategy is decided in this stage.
5. **Batched interviews**: 3-5 questions per batch, grouped by topic.
6. **ADR for each decision**: Non-obvious tech choices get an ADR.
