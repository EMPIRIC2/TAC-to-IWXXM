# 09-qa — EV-029 / S036 (delta)

**Date**: 2026-08-02  
**Branch**: `evolve/EV-029-eight-family-ahl-rules`  
**Tip**: `620fa9b` (T12.3) / prior feature tip `b43cbb3` (T12.2)  
**Mode**: delta (M12 T12.4)  
**Scope**: Eight-family AHL/report-state + SWXA quality (UJ-043 / F28 + deepen)

## Blocking

| Check | Result | Notes |
|-------|--------|-------|
| H0c CORS (`tests/unit/test_cors_policy.py`) | **PASS** (6) | Included in UJ-043 smoke batch |
| Format (`make format-check`) | **PASS** | T12.3 / husky |
| Lint (`make lint`) | **PASS** | T12.3 / husky |
| Typecheck (`make typecheck`) | **PASS** | iwxxm_us warnings only |
| Husky `ci-prepush` | **PASS** | On push of `b43cbb3` + `620fa9b` |
| CI/CD @ `b43cbb3` | **SUCCESS** | run `30771391289` |

## Delta suite (UJ-043)

| Suite | Result |
|-------|--------|
| Report-state matrix TC-EV029-006 | **PASS** (38) |
| Product-order smoke TC-EV029-007 | **PASS** (11) |
| AHL API TC-EV029-003 | **PASS** (in batch) |
| Product regression smoke (backend integration) | **PASS** |
| SWXA API smoke TC-F28-005 | **PASS** (2) |
| `make test-swxa-quality` | **PASS** |

**Batch**: 100 passed (CORS + integration smokes + EV-029 matrix/order/AHL).

## Advisory

| Item | Status |
|------|--------|
| H4–H5 staging browser | Deferred to **T12.6 / 13** — FE Examples unlocked (SWXA); not waived |
| Local `test_h0i_connectivity.py` marker collect | Marker config quirk when invoked ad-hoc; H0i covered via CI integration job @ tip |
| tac2iwxxm local cov display 94.57% | CI `Test (tac2iwxxm)` SUCCESS @ tip; husky `ci-prepush` PASS |

## Verdict

**PASS** (delta) — no blocking findings. Proceed to 10-e2e smoke report + T12.5 (11/12).
