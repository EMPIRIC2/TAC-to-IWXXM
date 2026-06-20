# ADR-002: Merge Auth Microservice Into Backend API

**Status**: Accepted  
**Stage**: 01-requirements  
**Date**: 2026-06-14

## Context

Authentication runs as a separate FastAPI service (`auth/`) proxying Supabase. Docker Compose
and Render deploy three services (frontend, backend, auth). The user indicated auth does not
need its own top-level directory as a deployable — it can be a **package** consumed by backend.

## Decision

Extract auth logic into `packages/auth` (library). Mount auth routes on `apps/backend`.
Deploy **two** Render services: API (backend + auth) and static frontend.

Preserve `/auth/*` URL paths for frontend compatibility.

## Alternatives Considered

| Option | Rejected because |
|--------|------------------|
| Separate auth service (status quo) | Extra deployable; cross-service latency; user preference |
| Inline only (no package) | Harder to test auth in isolation |
| Frontend → Supabase direct only | Existing middleware adds server-side validation |

## Consequences

**Positive**: Simpler ops; single CORS origin for API+auth; lower Render cost.

**Negative**: Backend image grows slightly; auth scaling tied to API scaling; migration work in big-bang PR.

## References

- REQ-004, REQ-009, REQ-010
- docs/api-contract.md
