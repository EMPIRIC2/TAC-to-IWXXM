# T5.6 — H0c CORS re-check after msgspec HTTP

**Session:** S014 / EV-010  
**Task:** T5.6  
**Date:** 2026-07-19  
**Status:** completed

## Results

| Suite | Result |
|-------|--------|
| `tests/unit/test_cors_policy.py` + `test_api_cors_config_unit.py` | 29 passed |
| `test_tc_f11_001_cors_after_msgspec.py` | 8 passed |

## Findings

- High-churn routes answer OPTIONS preflight with `POST` under existing `allowed_origins`
- `msgspec_http` introduces **no** CORS env knobs
- `get_cors_origins` has no msgspec branch — still `METAR_CORS_ORIGINS` / config only

## Next

M5 complete → M6 (08–13) or M5 verification report.
