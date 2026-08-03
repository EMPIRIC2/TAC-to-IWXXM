# Verification report — M3 F8 → DATABASE_URL — EV-031 / S038

> **Stage**: 08-verify-build (milestone M3 boundary)  
> **Date**: 2026-08-03  
> **Branch**: `evolve/EV-031-platform-independence-842`  
> **Tip**: `426eb92d` (`[T3.3]`)

## Milestone scope

| Task | Status | Commit |
|------|--------|--------|
| T3.1 Worker store/quarantine Postgres tests (TC-F30-003) | completed | `9f8684fd` |
| T3.2 Retarget F8 writers to SQLAlchemy/`DATABASE_URL` | completed | `80318dfc` |
| T3.3 Worker env + deploy docs; drop Supabase DB secrets | completed | `426eb92d` |

## Checks run

| Check | Result |
|-------|--------|
| `make test-unit-worker` / `apps/worker/tests` | **15 passed**, **2 skipped** (integration needs Docker/testcontainers) |
| Pre-commit on T3.x commits | **pass** |
| Static: no `SupabaseRestStore` / `/rest/v1/` on default path | **pass** (TC-F30-003 unit) |
| `render.yaml` worker `DATABASE_URL` | **pass** |

## Notes

- Default writer: `PostgresStore(DATABASE_URL)`; service-role PostgREST removed from worker.
- Schema: Alembic `iwxxm_ingest_results` / `iwxxm_ingest_quarantine` (co-located with sessions).
- Live probe `tests/live/test_t74_worker_ingest_tables.py` retargeted to `DATABASE_URL`.
- ADR-018 amended by ADR-033 / F30 for store auth.

## Next

- **M4 / T4.1** — FE hybrid guest IndexedDB + login auto-upload tests
- Minor PR optional on evolve branch (cycle continues)
