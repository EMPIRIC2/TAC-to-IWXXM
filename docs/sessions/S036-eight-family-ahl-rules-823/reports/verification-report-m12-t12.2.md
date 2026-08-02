# 08-verify-build — T12.2 report-state matrix (EV-029 / S036)

**Branch**: `evolve/EV-029-eight-family-ahl-rules`  
**Task**: T12.2 — Report-state matrix TC-EV029-006  
**Date**: 2026-08-02

## Deliverables

| Item | Path / detail |
|------|----------------|
| Consolidating pytest | `packages/tac2iwxxm/tests/test_tc_ev029_006_report_state_matrix.py` |
| CI script | `scripts/ci/run_report_state_matrix_smoke.sh` |
| Makefile | `make test-report-state-matrix-smoke` |
| Workflow | `.github/workflows/report-state-matrix-smoke.yml` |

## Matrix coverage

| State | Covered | Notes |
|-------|---------|-------|
| Normal / AMD / COR | METAR…TCA (BBB AHL) + SWXA Normal | `@reportStatus` from BBB |
| CNL | TAF, SIGMET, VA/TC SIGMET, AIRMET | `isCancelReport`; status stays NORMAL |
| NIL | METAR, SPECI, TAF | `nilReason`; status stays NORMAL |
| Gap / N/A | SWXA AMD/COR/CNL/NIL; METAR/SPECI CNL; VAA/TCA CNL/NIL; SIGMET-family NIL | Explicit `_GAP_OR_NA_CELLS` (no silent blanks) |

## Local verification

```
make test-report-state-matrix-smoke  →  38 passed
```

## Spec mapping

- TC-EV029-006 (test-plan / theme map): fixtures + matrix cells Normal/AMD/COR/CNL/NIL
- Pack seeds remain in per-family `test_tc_ev029_007_*` / `test_tc_ev029_005_*`

## Next

**T12.3** — 08-verify-build — lint/typecheck/format/full suites.
