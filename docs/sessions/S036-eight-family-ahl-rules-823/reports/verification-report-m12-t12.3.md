# 08-verify-build — T12.3 M12 full suites (EV-029 / S036)

**Branch**: `evolve/EV-029-eight-family-ahl-rules`  
**Task**: T12.3 — 08-verify-build lint/typecheck/format/full suites  
**Tip**: `b43cbb3` ([T12.2] report-state matrix)  
**Date**: 2026-08-02

## Local checks

| Check | Result |
|-------|--------|
| `make format-check` | **PASS** |
| `make lint` | **PASS** |
| `make typecheck` | **PASS** (iwxxm_us partial-unknown warnings only) |
| `make test-product-order-smoke` | **PASS** (11) |
| `make test-report-state-matrix-smoke` | **PASS** (38) |
| husky `validate-ci` + `ci-prepush` (on push) | **PASS** |

## GitHub CI @ `b43cbb3`

| Workflow | Result |
|----------|--------|
| CI/CD Pipeline `30771391289` | **SUCCESS** |
| Report-state matrix smoke | **SUCCESS** |
| Product-order smoke | **SUCCESS** |
| Family quality packs (METAR…SWXA / WMO / AHL COM) | **SUCCESS** |

## Spec mapping

- Execution-plan T12.3 → stage 08-verify-build
- Connectivity: no new FE this task; H4–H5 remain for T12.6 / stage 13 (Examples unlocked)

## Next

**T12.4** — 09-qa delta + 10-e2e smoke (UJ-043).
