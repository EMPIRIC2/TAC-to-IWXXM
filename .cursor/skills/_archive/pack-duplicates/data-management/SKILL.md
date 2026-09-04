---
name: data-management
description: >
  Prepares database schema, seed data, and fixtures before build-executor runs tasks that need
  real data. Reads data requirements from docs/spec.md §Data, applies migrations, loads fixtures,
  verifies integrity, and documents local/staging procedures. Use when implementation or deploy
  needs a populated {{DATA_STORE}} or verified migrations.
---

# Data Management

Prepare **schema**, **seed data**, and **fixtures** so build-executor and integration tests can
run without manual setup.

## Purpose

Typical dependencies:

1. **Schema** — migrations applied (`{{MIGRATION_COMMAND}}`)
2. **Fixtures** — dev/staging seed data and optional eval sets
3. **Verification** — row counts, FK integrity, constraint checks
4. **Documentation** — how to reset local DB and re-seed

This skill bridges **04-tech-plan** (data section in `docs/spec.md`) and **07-build**.

## Connectivity note

Data-management enables server-side integration tests (H0i/H2). It does **not** replace browser
connectivity gates (H4–H5) when a frontend exists. See [connectivity-gates.md](../connectivity-gates.md).

## Prerequisites

1. `docs/spec.md` §Data (from doc-planner or 04-tech-plan)
2. `docs/deploy.md` §Integration — DB URL pattern, migration hook
3. Execution plan artifact in `workflow-state.yaml` — tasks listing data deps

## State management

**Canonical:** repo-root `workflow-state.yaml` §`stages.data-management`.
Rules: [workflow-state-reference.md](../workflow-state-reference.md).

## Workflow (summary)

### Phase 1 — Parse requirements

Extract from spec: migrations, fixtures, eval sets, external data sources.

### Phase 2 — Local database

- Start {{DATA_STORE}} (Docker Compose or existing)
- Run `{{MIGRATION_COMMAND}}`
- Confirm required extensions installed

### Phase 3 — Seed data

- Run `{{STAGING_COMMAND}}` or documented seed scripts
- Record row counts in workflow-state artifacts

### Phase 4 — Verify

- Run verification script or queries: row counts, orphan checks
- Optional: run eval expectations (ids only, not LLM judge)

### Phase 5 — Staging notes

- Document staging migrate + seed policy (no production PII unless approved)
- Align with `docs/deploy.md` §Integration CI hooks

## AskQuestion triggers

| Category | Example |
|----------|---------|
| **Decision** | Local vs remote {{DATA_STORE}} for staging |
| **Blocker** | `{{CONFIG_PREFIX}}_DATABASE_URL` missing |
| **Ambiguity** | Which fixture revision pins schema version |

## References

- `docs/spec.md` §Data
- `docs/deploy.md`
- [connectivity-gates.md](../connectivity-gates.md)
