# 08-verify-build — T12.1 product-order smoke (EV-029 / S036)

**Branch**: `evolve/EV-029-eight-family-ahl-rules`  
**Task**: T12.1 — Product-order regression smoke TC-EV029-007  
**Date**: 2026-08-02

## Deliverables

| Item | Path / detail |
|------|----------------|
| Consolidating pytest | `packages/tac2iwxxm/tests/test_tc_ev029_007_product_order_smoke.py` |
| CI script | `scripts/ci/run_product_order_smoke.sh` |
| Makefile | `make test-product-order-smoke` |
| Workflow | `.github/workflows/product-order-smoke.yml` |

## Phase B order (locked)

METAR → SPECI → TAF → SIGMET → VA_SIGMET → TC_SIGMET → AIRMET → VAA → TCA → SWXA

Each family: lint → convert → XSD+Schematron on one annex3 accept fixture; adjacency
forbidden-root checks for SIGMET variants / VAA / TCA / SWXA.

## Local verification

```
make test-product-order-smoke  →  11 passed
```

## Spec mapping

- TC-EV029-007 (test-plan / theme map): one accept fixture / family in CI order
- Pack seeds remain in per-family `test_tc_ev029_007_*` / `test_tc_ev029_005_*` / TC-F28

## Next

**T12.2** — Report-state matrix TC-EV029-006 (or child-issue gaps).
