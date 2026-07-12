# ADR-003: Big-Bang Monorepo Migration

**Status**: Accepted  
**Stage**: 01-requirements  
**Date**: 2026-06-14

## Context

The repository is actively updated but burdened by six git submodules and split GitHub repos
(frontend, GIFTs, iwxxm forks). User wants a single git monorepo with `apps/` + `packages/` +
`vendor/` layout.

Migration strategies: incremental coexistence vs single cutover vs new repo.

## Decision

Execute a **big-bang** migration in one PR on branch `feat/monorepo-big-bang`:

- Remove all submodules
- Move directories to target layout
- Merge auth into backend
- Reorganize tests to `apps/e2e/`
- Update CI, Docker, docs
- Archive legacy GitHub repos after stable deploy

**Non-goal**: no product feature rewrites in the same effort.

## Alternatives Considered

| Option | Rejected because |
|--------|------------------|
| Incremental coexistence | Prolonged dual-path maintenance while repo is active |
| Fresh repo | Loses issue/PR history; user prefers evolving current repo |
| Exploration only | User wants to build — specs lead to implementation |

## Consequences

**Positive**: Fast end-state; no long-lived parallel directory trees; clear team cutover.

**Negative**: Higher merge conflict risk; requires feature freeze; rollback is revert + submodule restore.

## Mitigations

- Golden conversion tests (TC-M003) before merge
- Documented rollback in migration-plan.md
- Merge gate checklist in test-plan.md

## References

- REQ-006, REQ-011, REQ-016
- docs/ops/migration-plan.md
