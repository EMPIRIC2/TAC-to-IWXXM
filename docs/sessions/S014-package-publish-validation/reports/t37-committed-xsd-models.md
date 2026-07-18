# T3.7 — Commit regenerated pydantic models (ADR-027 / F11 acc4)

**Session:** S014 / EV-010  
**Task:** T3.7  
**Date:** 2026-07-18  
**Status:** completed  

## Delivered

| Item | Detail |
|------|--------|
| Regenerated trees | `v2023_1/` (102 py, ~3.8 MiB), `v2025_2/` (103 py, ~3.8 MiB) from pinned `iwxxm.xsd` |
| Stamp | `STATUS.json`, `LAST_RUN.json` |
| Tracked | Removed `v*` / `LAST_RUN.json` from `.gitignore` |
| Adapt helpers | `metar_shared.iwxxm_xsd.adapt` — version discovery, safe leaf import, msgspec/Rust placeholders |
| Optional deps | `metar-shared[xsd]` → pydantic + xsdata-pydantic |
| Smoke isolation | `generate_version(..., out_root=)` so T3.6/T3.7a slow tests do not clobber committed trees |

## Tests

- `packages/shared/tests/test_iwxxm_xsd_adapt.py`
- Existing T3.7a / T3.6 pipeline smokes (temp `out_root`)

## Next

**T3.8a** — backend `/validate` uses Rust SDK (no double heavy-layer run).
