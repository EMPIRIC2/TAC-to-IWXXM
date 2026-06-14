# Supported Document Types

## Standing docs (minimal export set)

Generate and maintain **only** these committed files in `docs/`:

| File | Purpose |
|------|---------|
| `spec.md` | Architecture, roadmap, data, glossary |
| `feature-list.md` | Features + acceptance bullets |
| `user-journeys.md` | Caller journeys (UJ-NNN) |
| `test-plan.md` | Test matrix + QA gates |
| `api-contract.md` | HTTP/API surface |
| `dependency-inventory.md` | Dependencies and licenses |
| `risk-register.md` | Risks and mitigations |
| `deploy.md` | Checklist + integration + runbook (merged) |
| `adr/README.md` | ADR process + index |

**Ephemeral** (workflow-state.yaml §`artifacts`, not standing docs): execution-plan,
config-spec, research-brief, context-brief, qa-report, deploy-report, bug-reports.

Merged sources (do not generate as separate files): `roadmap.md`, `glossary.md`,
`data-management-plan.md`, `deployment-integration.md`, `deploy-checklist.md`,
`staging-runbook.md`, `acceptance-criteria.md`.

---

Reference catalog of document types the doc-planner skill can generate.
Each entry defines when the document is relevant, its file path convention, and a template.

---

## 1. Roadmap

**When relevant**: Always — every project benefits from a phased plan.
**Path**: `docs/roadmap.md`

```markdown
# Roadmap

## Vision
One-paragraph statement of where this project is headed.

## Phases

### Phase 1: [Name] (Target: [date or milestone])
- [ ] Goal 1
- [ ] Goal 2

### Phase 2: [Name]
- [ ] Goal 1
- [ ] Goal 2

## Non-Goals
Things explicitly out of scope for the foreseeable future.

## Open Questions
Unresolved decisions that affect the roadmap.
```

---

## 2. Feature List

**When relevant**: Project has identifiable capabilities, pipeline stages, or modes of operation.
**Path**: `docs/feature-list.md`

```markdown
# Feature List

| # | Feature | Status | Description | Source |
|---|---------|--------|-------------|--------|
| 1 | ... | Implemented / Planned / Experimental | ... | [Paper §X] or [Repo: file] |

## Feature Details

### F1: [Feature Name]
- **What it does**: ...
- **Inputs**: ...
- **Outputs**: ...
- **Key parameters**: ...
- **Limitations**: ...
```

---

## 3. User Journeys

**When relevant**: **Always — mandatory for every project with caller-facing behavior** (API,
CLI, library entry points, or HTTP API). Describes what a **caller** does end-to-end
—not internal module tests. Each journey maps to a feature in `feature-list.md`, entry points
in `api-contract.md` (when present), test cases in `test-plan.md`, and E2E verification in
stage 10-e2e / 11-verify-impl.

**Path**: `docs/user-journeys.md`

**Generation order**: After `feature-list.md` and `spec.md` (and `api-contract.md` when
applicable); before `test-plan.md` so the test plan can reference journey IDs (UJ-001, …).

```markdown
# User Journeys

> **Project**: [name]
> **Source**: [feature-list.md], [api-contract.md], [requirements-decisions.md or research-brief]
> **Last updated**: [date]

Product-facing journeys describe what a **caller** does — not internal module tests.
Each journey maps to automated E2E tests (`tests/e2e/`) and a stage **11-verify-impl**
interview prompt.

## Journey Index

| ID | Journey | Entry point | Feature | E2E tier |
|----|---------|-------------|---------|----------|
| UJ-001 | ... | ... | F# | local / live / both |

**E2E tier** (define per project): e.g. **local** (TestClient + test DB), **live** (staging URL).

## Journey Details

### UJ-001: [Journey title]

**Actor**: [who invokes the system]

**Goal**: [outcome in one sentence]

**Steps**:

1. ...
2. ...

**Acceptance**: [Link to acceptance-criteria.md §feature or inline criteria]

**Automated tests**: `tests/e2e/test_uj001_*.py` (tiers)

**Interview (11)**: "[Question for human verification in 11-verify-impl]"
```

---

## 4. Test Plan

**When relevant**: Paper describes validation experiments, or repo has test infrastructure.
**Path**: `docs/test-plan.md`

Must cross-reference `docs/user-journeys.md` (UJ-IDs) in a **User Journeys (E2E)** section;
each TC-ID should map to at least one journey where applicable.

```markdown
# Test Plan

## Scope
What this test plan covers and what it excludes.

## User Journeys (E2E)

Product-facing journeys are defined in [user-journeys.md](user-journeys.md) (UJ-001–…).
Map each journey to test modules and TC-IDs.

## Test Strategy

| Level | Framework | Scope | Run Command |
|-------|-----------|-------|-------------|
| Smoke | ... | Basic pipeline execution | `...` |
| Unit | ... | Individual components | `...` |
| Integration | ... | End-to-end pipeline | `...` |
| Validation | ... | Reproduce paper results | `...` |

## Test Cases

### TC-001: [Name]
- **Objective**: ...
- **Input**: ...
- **Expected output**: ...
- **Pass criteria**: ...
- **Source**: [Paper §X] or [Repo: test file]

## Test Data
Where to obtain test datasets and fixtures.

## Metrics & Thresholds

| Metric | Threshold | Context |
|--------|-----------|---------|
| ... | ... | ... |
```

---

## 5. Architecture Decision Records (ADRs)

**When relevant**: Paper or repo reveals significant design choices with alternatives considered.
**Path**: `docs/adr/NNN-[slug].md`

```markdown
# ADR-NNN: [Title]

## Status
Accepted | Proposed | Deprecated | Superseded by ADR-XXX

## Context
What problem or decision point prompted this record.

## Decision
What was decided and why.

## Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|-------------|------|------|--------------|
| ... | ... | ... | ... |

## Consequences
What follows from this decision — both positive and negative.

## References
- [Paper §X], [Repo: file:lines]
```

---

## 6. Technical Specification

**When relevant**: Complex pipeline or algorithm that needs detailed documentation beyond
what the paper provides.
**Path**: `docs/spec.md`

```markdown
# Technical Specification

## Overview
What this software does at a technical level.

## System Architecture
High-level component diagram (describe in text or reference a diagram).

## Component Details

### [Component Name]
- **Purpose**: ...
- **Inputs**: ...
- **Outputs**: ...
- **Algorithm**: ...
- **Dependencies**: ...

## Data Flow
How data moves through the system, stage by stage.

## Constraints & Assumptions
Hard constraints the design operates under.
```

---

## 7. Configuration Spec

**When relevant**: Repo has config files, environment variables, or tunable parameters.
**Path**: `docs/config-spec.md`

```markdown
# Configuration Specification

## Configuration Files

### [filename]
- **Format**: YAML / TOML / JSON / INI
- **Location**: `path/to/file`

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| ... | ... | ... | ... | ... |

## Environment Variables

| Variable | Type | Default | Required | Description |
|----------|------|---------|----------|-------------|
| ... | ... | ... | ... | ... |

## CLI Flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| ... | ... | ... | ... |

## Precedence
CLI flags > Environment variables > Config file > Defaults

## Recommended Defaults from Paper

| Parameter | Recommended Value | Paper Reference |
|-----------|-------------------|-----------------|
| ... | ... | [Paper §X] |
```

---

## 8. Dependency Inventory

**When relevant**: Always — every project has dependencies worth tracking.
**Path**: `docs/dependency-inventory.md`

```markdown
# Dependency Inventory

## Runtime Dependencies

| Package | Version | Purpose | License | Source |
|---------|---------|---------|---------|--------|
| ... | ... | ... | ... | [Repo: requirements.txt] |

## Build Dependencies

| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| ... | ... | ... | ... |

## Hardware Requirements

| Resource | Minimum | Recommended | Context |
|----------|---------|-------------|---------|
| GPU | ... | ... | ... |
| RAM | ... | ... | ... |
| Disk | ... | ... | ... |

## External Services / Data

| Resource | URL | Required | Purpose |
|----------|-----|----------|---------|
| ... | ... | Yes/No | ... |
```

---

## 9. Acceptance Criteria

**When relevant**: Project has measurable outcomes defined in the paper or issue tracker.
**Path**: `docs/acceptance-criteria.md`

```markdown
# Acceptance Criteria

## Per-Feature Criteria

### [Feature Name]
- [ ] Criterion 1: [measurable condition]
- [ ] Criterion 2: [measurable condition]
- **Source**: [Paper §X] or [Repo: file]

## Quantitative Benchmarks

| Benchmark | Metric | Target | Dataset | Paper Reference |
|-----------|--------|--------|---------|-----------------|
| ... | ... | ... | ... | ... |

## Qualitative Criteria
Non-numeric conditions that must be met.
```

---

## 10. Glossary

**When relevant**: Domain-specific terminology that could confuse contributors
(especially common in scientific software).
**Path**: `docs/glossary.md`

```markdown
# Glossary

| Term | Definition | Context |
|------|------------|---------|
| ... | ... | Used in [component/paper section] |
```

---

## 11. Risk Register

**When relevant**: Project has known failure modes, security concerns, or operational risks
mentioned in the paper or visible in the codebase.
**Path**: `docs/risk-register.md`

```markdown
# Risk Register

| # | Risk | Likelihood | Impact | Mitigation | Status |
|---|------|-----------|--------|------------|--------|
| R1 | ... | High/Med/Low | High/Med/Low | ... | Open/Mitigated |

## Risk Details

### R1: [Risk Name]
- **Description**: ...
- **Trigger**: What would cause this risk to materialize
- **Mitigation plan**: ...
- **Owner**: ⚠️ Needs human input
- **Source**: [Paper §X] or [Repo: file]
```

---

## 12. API Contract

**When relevant**: Repo exposes a REST, gRPC, CLI, or library API.
**Path**: `docs/api-contract.md`

```markdown
# API Contract

## Endpoints / Entry Points

### [Endpoint or Function]
- **Method / Signature**: ...
- **Input**: ...
- **Output**: ...
- **Errors**: ...
- **Example**: ...

## Data Models

### [Model Name]
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| ... | ... | ... | ... |
```

---

## 13. Migration Plan

**When relevant**: Software requires data migration, version upgrades, or environment transitions.
**Path**: `docs/migration-plan.md`

```markdown
# Migration Plan

## From → To
Describe the starting state and target state.

## Pre-Migration Checklist
- [ ] ...

## Steps

| # | Step | Command / Action | Rollback |
|---|------|-----------------|----------|
| 1 | ... | ... | ... |

## Post-Migration Validation
How to verify the migration succeeded.

## Risks
What could go wrong and how to recover.
```

---

## 14. Data Management Plan

**When relevant**: **Always — mandatory for deployed service.** Schema migrations, seed corpus, eval
fixtures, and verification before RAG integration tests. Consumed by the data-management skill
before build-executor begins implementation.
**Path**: `docs/spec.md §Data`

```markdown
# Data Management Plan

## Overview
What data assets the project needs and why they must be staged before the pipeline runs.

### Total Data Budget

| Metric | Value |
|--------|-------|
| Total assets | [N] |
| Total size (local) | [X GB] |
| Auth-gated assets | [N] |

## Asset Inventory

| # | Asset | Type | Size | Source | Auth | Needed By |
|---|-------|------|------|--------|------|-----------|
| D1 | ... | corpus_fixture / migration / eval_set | ... | ... | gated / none | [task IDs] |

## Sources
Per-asset download instructions, authentication, and references.

## Verification
Checksums, size checks, format validation per asset.

## Local Paths
Where each asset goes for local development, .gitignore entries.

## Staging environments
Local Docker Postgres, staging seed policy, production (no dev fixtures).

## Quick Start
Commands to download and verify all assets for a new developer.

## Dependencies
Which execution plan tasks depend on which assets; minimum viable subset for testing.

## Open Questions
Unresolved decisions about data sources, versions, or strategies.
```

---

## 15. Deployment Integration Plan

**When relevant**: **Always — mandatory for deployed service.** API + worker deploy, Postgres/pgvector,
secrets, CI/CD, observability, and DB migration hooks per deployment-catalog.md.
**Path**: `docs/deploy.md §Integration`

```markdown
# Deployment Integration Plan

## Overview
deployed service API, worker, and database deployment.

## Services
API, worker, Postgres (+ pgvector), optional object storage.

## Database
Connection, migrations, extensions, pool sizing.

## Secrets & Environment
Platform secrets; `DATABASE_URL`, embedding/LLM keys.

## Entrypoints & Triggers
CLI entrypoints, web endpoints, cron schedules.

## Pipeline Mapping

| Component | Implementation | Deploy unit | Notes |
|-----------|----------------|-------------|-------|
| ingest | [src/jobs/] | worker | ... |
| query | [src/api/] | api | ... |

## Scaling & Performance
Query p95, ingest throughput, connection pool limits.

## Migration Checklist
Alembic revisions, seed corpus, smoke H3.

## Cost Estimation

| Resource | Unit Cost | Est. Usage / Run | Est. Cost / Run |
|----------|----------|-----------------|-----------------|
| ... | ... | ... | ... |

## Open Questions
Unresolved decisions about deployment target or vector store.
```
