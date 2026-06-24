# ADR-011: Work Sessions Data Access via Supabase JWT Client

## Status: Accepted

## Context

F5 requires per-user METAR work history in Supabase Postgres (`metar_work_sessions`) with
RLS (`auth.uid() = user_id`) and admin read via `is_admin()`. ADR-010 reduced use of
`SUPABASE_SECRET_KEY` — admin and user operations should run through the publishable key with
the caller's JWT so RLS enforces isolation.

The backend already uses this pattern in `packages/auth/src/admin_api.py` (`_get_authed_client`
+ `client.postgrest.auth(access_token)`). An alternative is SQLAlchemy async against
`DATABASE_URL`, which would bypass RLS unless every query sets `request.jwt.claim.sub`.

## Decision

1. **User CRUD** (`/api/v1/work-sessions/*`) — Supabase Python client with forwarded Bearer
   JWT; RLS on `metar_work_sessions` is authoritative.
2. **Admin read** (`GET /admin/work-sessions`) — same JWT client + `require_admin()` guard;
   RLS policy allows `is_admin()` SELECT on all rows.
3. **Retention jobs** (Draft purge, soft-delete hard-delete) — `SECURITY DEFINER` SQL functions
   invoked by pg_cron as `postgres` / service role; no secret key in application code.
4. **Status enforcement** — application layer validates transitions (api-contract.md table);
   partial unique index enforces at most one WIP per user (see ADR-012).
5. **Types** — Pydantic models in `apps/backend/src/schemas/work_session.py`; TypeScript
   interfaces in `packages/shared/src/work-session.ts`; manual parity (same as existing
   `ConversionResponse` pattern in `api.ts`).

## Consequences

- Consistent with ADR-010 and existing admin API patterns.
- Integration tests need Supabase local stack or mocked PostgREST responses.
- No SQLAlchemy ORM models for `metar_work_sessions` in v1 — keeps F5 isolated from
  statistics SQLAlchemy path in `apps/backend/src/services/database.py`.

## Alternatives Considered

| Alternative | Rejected because |
|-------------|------------------|
| SQLAlchemy + service role | Bypasses RLS; increases secret-key blast radius |
| Direct browser Supabase client | Violates F5-R10 / api-contract — backend REST only |
| OpenAPI codegen for TS types | No existing codegen pipeline; overhead for one feature |

## References

- [api-contract.md §Work sessions](../api-contract.md)
- [spec.md §F5](../spec.md)
- [ADR-010](ADR-010-supabase-keys-config-split.md)
- `packages/auth/src/admin_api.py` — `_get_authed_client`
