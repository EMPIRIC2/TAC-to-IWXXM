# Verification report — M3 (S015 / EV-011)

**Date**: 2026-07-19  
**Milestone**: M3 — METAR/SPECI rules R1–R5 + full R8  
**Branch**: `evolve/EV-011-metar-lint-quality`  
**Tip**: `66ac3c5`

## Checks

| Check | Result | Notes |
|-------|--------|-------|
| Format (`make format-check`) | PASS | |
| Lint (`make lint-tac-validate`) | PASS | |
| Typecheck (`make typecheck-py`) | PASS | |
| tac-validate tests | PASS | 291 package tests |
| H0c CORS (`tests/unit/test_cors_policy.py`) | PASS | included in 297 combined run |
| Combined (tac-validate + CORS) | PASS | 297 passed |

## Scope delivered (M3)

| Theme | Tasks | Codes / behavior |
|-------|-------|------------------|
| R1 | T3.1–T3.2 | `ODD_FIELD_ORDER` |
| R2 | T3.3–T3.4 | `INVALID_VISIBILITY` |
| R3 | T3.5–T3.6 | `INVALID_WEATHER` |
| R4 | T3.7–T3.8 | `INVALID_CLOUD_TOKEN`, `CLOUD_CB_OR_TCU` |
| R5 | T3.9–T3.10 | `REMARK_US_EXTENSION`, `INVALID_REMARK` (+ vis scoped before RMK) |
| R8 | T3.11–T3.12 | AUTO/COR/NIL/NOSIG/TEMPO/RVR/VRB·gust info + `INVALID_*` |

## Connectivity artifacts

- `tests/unit/test_cors_policy.py` — green (H0c)
- Staging connectivity scripts present (unchanged this milestone)

## Verdict

**PASS** — M3 gate satisfied; proceed to minor PR then M4 (T4.1 goldens).
