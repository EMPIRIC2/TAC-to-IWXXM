# Verification report — M4 FE hybrid + F22 deepen — EV-031 / S038

> **Stage**: 08-verify-build (milestone M4 boundary)  
> **Date**: 2026-08-03  
> **Branch**: `evolve/EV-031-platform-independence-842`  
> **Tip**: `389a3b24` (`[T4.5]`)

## Milestone scope

| Task | Status | Commit |
|------|--------|--------|
| T4.1 Vitest/Playwright: guest notice, auto-upload, privacy gates | completed | `8f770ba5` |
| T4.2 Restore optional Auth FE client + login UX | completed | `0dbd45bc` |
| T4.3 Auto-upload local drafts; server session lists | completed | `588b87c4` |
| T4.4 F22 deepen: gate guest IndexedDB; disclose Auth cookies | completed | `a44c3a40` |
| T4.5 `/config.json` Auth bootstrap + DOKS FE CORS placeholder | completed | `389a3b24` |

## Checks run

| Check | Result |
|-------|--------|
| `make format-check` | **pass** |
| `make typecheck` | **pass** (0 errors; known tac2iwxxm US profile warnings) |
| `make validate-fast` (pre-commit / T4.4–T4.5) | **pass** |
| H0c `tests/unit/test_cors_policy.py` | **6 passed** |
| Config contract `tests/test_frontend_env_configuration.py` | **10 passed** |
| M4 FE Vitest (privacy, hybrid sessions, runtime-config, lists) | **71 passed** (8 files) |

## Connectivity artifacts

| Artifact | Present |
|----------|---------|
| `tests/unit/test_cors_policy.py` | yes |
| `scripts/deploy/verify_connectivity.sh` | yes |
| Live H4–H5 | deferred to T7.2 / M7 |

## Notes

- Guest IndexedDB writes honor `workHistoryLocal`; Auth cookies disclosed in F22 inventory.
- `config/prod.json` keeps Render `api.baseUrl` / `liveE2e`; DOKS FE placeholder only in `corsOrigins`.
- `prepare-config.sh` requires `api.baseUrl` + `supabase.url`; injects publishable key.

## Next

- **M5 / T5.1** — Finalize table/column map in `ops/supabase-to-do-postgres-migration.md`
- Minor PR optional on evolve branch (cycle continues)
