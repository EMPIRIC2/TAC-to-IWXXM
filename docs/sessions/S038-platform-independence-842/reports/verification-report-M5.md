# Verification report — M5 Supabase → DO migrate — EV-031 / S038

> **Stage**: 08-verify-build (milestone M5 boundary)  
> **Date**: 2026-08-03  
> **Branch**: `evolve/EV-031-platform-independence-842`  
> **Tip**: `e2e43a83` (`[T5.4]`)

## Milestone scope

| Task | Status | Commit |
|------|--------|--------|
| T5.1 Finalize table/column map in ops migrate doc | completed | `c5f2bfc8` |
| T5.2 Verify script: row counts / sample checksum | completed | `7bde343c` |
| T5.3 Migrate dry-run / apply runner (SQL export; optional pg_dump) | completed | `42179df3` |
| T5.4 Post-migrate session CRUD + Auth-only Supabase (TC-EV031-004 / TC-F30-002) | completed | `e2e43a83` |

## Checks run

| Check | Result |
|-------|--------|
| `make validate-fast` (pre T5.4 commit) | **pass** |
| M5 migrate unit tests (`test_run_*` + `test_verify_*`) | **11 passed** |
| M5 post-migrate CRUD / TC-F30-002 | **6 passed** |
| H0c `tests/unit/test_cors_policy.py` | **pass** |
| `make format-check` | **pass** |

## Connectivity artifacts

| Artifact | Present |
|----------|---------|
| `tests/unit/test_cors_policy.py` | yes |
| `scripts/deploy/verify_connectivity.sh` | yes |
| Live H4–H5 | deferred to T7.2 / M7 |

## Ops note (live cut)

- Tooling: `make migrate-supabase-to-do MODE=dry-run|apply VERIFY=1`
- Safety: runner refuses same-DB source/target (current `.env` `DATABASE_URL` is still Supabase pooler).
- **Live dry-run/apply** requires `MIGRATE_SOURCE_DATABASE_URL` + `MIGRATE_TARGET_DATABASE_URL` (DO Postgres) before production cut.

## Next

- **M6 / T6.1** — DOKS manifests/Helm/Blueprint: API + FE static + worker; secrets
- Minor PR optional on evolve branch (cycle continues)
