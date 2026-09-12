# Verification report — M2 DO Postgres + Alembic + work-sessions — EV-031 / S038

> **Stage**: 08-verify-build (milestone M2 boundary)  
> **Date**: 2026-08-03  
> **Branch**: `evolve/EV-031-platform-independence-842`  
> **Tip**: `c7c567ab` (`[T2.6]`)

## Milestone scope

| Task | Status | Commit |
|------|--------|--------|
| T2.1 Alembic layout + idempotent upgrade tests | completed | `013d6a16` |
| T2.2 Alembic tree + initial product schema | completed | `8fb8aa4e` |
| T2.3 CI Postgres + `make db-migrate` / `test-alembic` | completed | `a108b584` |
| T2.4 Work-sessions JWT/CRUD contract tests | completed | `9a51f8ea` |
| T2.5 SQLAlchemy + JWKS work-sessions restore | completed | `25504549` |
| T2.6 No PostgREST product writes (TC-F30-001) | completed | `c7c567ab` |

## Checks run

| Check | Result |
|-------|--------|
| Backend unit suite (`fail_under=98`) | **1264+ passed**, **98.00%** |
| TC-EV031-002 layout unit tests | **pass** |
| TC-EV031-002 live double-upgrade | **skipped locally** (Docker unavailable); **CI `test-alembic` job** covers Postgres 16 |
| TC-F31-003 JWT gate + public convert | **pass** |
| H0i work-sessions JWT-gated | **pass** |
| Pre-commit on T2.x commits | **pass** |

## Notes

- Product schema: `tac_work_sessions` (incl. `swxa`) + F8 ingest tables; **no** `auth.users` FK.
- JWT verify for sessions: JWKS-only via `metar_auth` (`SUPABASE_URL` / `SUPABASE_JWKS_URL`).
- Make targets: `make db-migrate`, `make test-alembic`.

## Next

- **M3 / T3.1** — F8 worker store/quarantine against `DATABASE_URL`
- Minor PR optional on evolve branch (cycle continues)
