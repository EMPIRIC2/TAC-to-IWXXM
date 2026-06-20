# ADR-007: Universal 95% Coverage Gate

## Status: Accepted

## Context

The legacy repo enforces 95% coverage on the backend via Makefile and Codecov. The monorepo
adds new workspace members (packages/gifts, packages/auth, packages/shared, apps/frontend)
that previously had uneven or no coverage enforcement.

## Decision

Enforce **95% line coverage** on all Python packages and apps:

- `packages/gifts`
- `packages/auth`
- `packages/shared` (when code present)
- `apps/backend`

Enforce **95% statement coverage** on `apps/frontend` via Vitest coverage thresholds.

CI fails if any workspace member falls below 95%. Coverage config added in Phase 1 (T1.9).

## Consequences

- Migration may require additional tests in gifts and auth packages to reach threshold.
- Frontend may need Vitest coverage uplift (currently has coverage tooling but no 95% gate).
- CI runtime increases slightly due to broader coverage collection.

## Alternatives Considered

- **Keep 95% backend only**: Rejected — user requested universal 95%.
- **Relax to 90% during migration**: Rejected — user chose strict 95% everywhere.
- **Remove coverage gate**: Rejected — regression risk too high for big-bang migration.
