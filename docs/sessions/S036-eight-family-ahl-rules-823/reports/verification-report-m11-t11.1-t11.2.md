# Verification — M11 T11.1–T11.2 (SWXA / F28 lint bar)

**Session**: S036 / EV-029  
**Date**: 2026-08-02  
**Branch**: `evolve/EV-029-eight-family-ahl-rules`

## Results

| Check | Status |
|-------|--------|
| `pytest packages/tac-validate/tests` | **PASS** (717) |
| TC-F28-001 registry completeness | **PASS** |
| TC-F28-004 / theme SX1 accept+negatives | **PASS** |
| Catalog regen | **PASS** |

## Tasks

| Task | Notes |
|------|-------|
| T11.1 | SWXA accept/negative fixtures + `test_tc_f28_*`; theme **SX1** (avoids SPECI S1) |
| T11.2 | `PRODUCTS`+`SWXA`; registry rows; `_check_swxa`; SPECI S1 product filter |

## Next

**T11.3** — SWXA convert → XSD+SCH (+ golden / `wmoReference`).
