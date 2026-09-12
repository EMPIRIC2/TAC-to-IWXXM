# 10-e2e smoke — S036 / EV-029 (UJ-043)

**Date**: 2026-08-02  
**Mode**: smoke (Standard; T12.4)  
**Tip**: `620fa9b` / feature tip `b43cbb3`

| Tier | Journey / TC | Evidence | Result |
|------|--------------|----------|--------|
| T0 | UJ-043 / TC-EV029-006 | `make test-report-state-matrix-smoke` (38) | **PASS** |
| T0 | UJ-043 / TC-EV029-007 | `make test-product-order-smoke` (11) | **PASS** |
| T0 | UJ-043 / TC-EV029-003 | `test_tc_ev029_003_ahl_api.py` | **PASS** |
| T0 | UJ-043 / TC-F28-001..006 | `make test-swxa-quality` | **PASS** |
| T1 | TC-F28-005 API | `apps/backend/tests/integration/test_tc_f28_005_swxa_smoke.py` | **PASS** |
| T1 | Product regression | `test_product_regression_smoke.py` | **PASS** |
| T2 H4–H5 | TC-EV029-008 / FE Examples | SWXA catalog unlocked @ T11.7 | **Deferred → T12.6 / 13** |
| T3 browser | Live UJ | — | **N/A** this task |

## Combined smoke batch

```
CORS + SWXA API + product regression + TC-EV029-003/006/007 → 100 passed
```

## Verdict

**PASS** smoke — package + API T0/T1 green for UJ-043. Playwright live H4–H5 reserved for
deploy smoke (Examples unlock). No new Playwright delta required for T12.4.
