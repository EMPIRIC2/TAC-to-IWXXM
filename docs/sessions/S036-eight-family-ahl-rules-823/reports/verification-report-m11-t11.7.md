# Verification — M11 T11.7 (TC-F28-005 SWXA product-path smoke)

> **Date**: 2026-08-02  
> **Branch**: `evolve/EV-029-eight-family-ahl-rules`  
> **Cycle**: EV-029 / S036  
> **Spec**: TC-F28-005; UJ-043; F28 AC6

## Scope

| Surface | Deliverable |
|---------|-------------|
| API | Integration smoke: `product=swxa` lint + convert + lint-issue-catalog |
| FE Examples | Unlock `spacewx-A7-3` as `wmoReference` (S02.L1); A7-4/A7-5 deferred |
| Inventory | Register `spacewx-A7-3`; defer A7-4/A7-5; include `spacewx-` in happy-path filter |

## Results

| Check | Status |
|-------|--------|
| `test_tc_f28_005_swxa_smoke.py` (2) | **PASS** |
| `test_tc_ev027_001_002_inventory_catalog.py` (4) | **PASS** |
| `examplesCatalog.test.ts` (22) | **PASS** |
| Root `iwxxm:SpaceWeatherAdvisory` on convert | **PASS** |
| Catalog includes `MISSING_SWXC` | **PASS** |
| FE single-seed SWXA only | **PASS** |

## Notes

- H4–H5 live browser deferred to **13-deploy-smoke** (FE Examples unlocked → no longer waived).
- Next: **T12.1** product-order regression smoke (TC-EV029-007).
