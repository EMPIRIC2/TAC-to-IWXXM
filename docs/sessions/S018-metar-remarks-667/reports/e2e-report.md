# E2E Behavior Report — S018 / EV-013 (#667)

> Generated: 2026-07-20  
> Mechanism: **library** (tac2iwxxm) + package edge TCs  
> Scope: UJ-026 (new), UJ-010 (regression)  
> Journeys tested: 2 (cycle-scoped)

## Summary

| # | Journey | Mechanism | T0 | T2 connectivity | T3 browser | Status |
|---|---------|-----------|----|-----------------|------------|--------|
| 1 | UJ-026 METAR REMARKS retain / exclusion | library | PASS | deferred → 13 | N/A | PASS (T0) |
| 2 | UJ-010 Malformed US REMARKS | library | PASS | deferred → 13 | N/A | PASS (T0) |

Mocks/package T0 ≠ production UI connected — T2/T3 recorded separately per connectivity-gates §Stage 10.

## Journey → test mapping

| Journey | Test module | Notes |
|---------|-------------|-------|
| UJ-026 | `packages/tac2iwxxm/tests/test_issue_667_metar_remarks.py` | TC-F6-013; no `tests/e2e/test_uj026.py` (library journey — package tests are SoT) |
| UJ-010 | `packages/tac2iwxxm/tests/test_tc_f6_010_011_012_edge.py::test_tc_f6_012_*` | Malformed REMARKS → `MALFORMED_REMARKS` |

**Waiver:** Repo uses `apps/e2e/` Playwright for UI UJs and package pytest for F6 convert journeys.
No `tests/e2e/test_uj*.py` tree. Documented here instead of inventing a parallel harness.

## Journey details

### UJ-026: METAR REMARKS retain / exclusion (#667)

- **Feature**: F6 deepen (EV-013)
- **Mechanism**: library (`tac2iwxxm.convert` / `parse_metar_speci`)
- **Steps**:
  1. annex3 + RMK → `ok` + `REMARKS_EXCLUDED` (info) — PASS
  2. annex3 without RMK → no `REMARKS_EXCLUDED` — PASS
  3. iwxxm_us unparsed remainder → `humanReadableText` — PASS
  4. T/P parsed to IR + retained in free-text — PASS
  5. structured-only AO2/SLP → no empty `humanReadableText` — PASS
  6. SPECI annex3 exclusion + span — PASS
  7. plain-language-only / escape / peak-wind coexistence — PASS
- **Evidence**: 12/12 in `test_issue_667_metar_remarks.py`; live REPL: `annex3 True ['REMARKS_EXCLUDED']`, us XML contains `VIRGA`

### UJ-010: Malformed US REMARKS

- **Feature**: F6
- **Mechanism**: library
- **Steps**:
  1. iwxxm_us + malformed AO/SLP/PK → `MALFORMED_REMARKS` — PASS (`test_tc_f6_012`)
- **Evidence**: included in 15/15 combined UJ-026+edge run

## T2 / T3

| Tier | Status | Notes |
|------|--------|-------|
| T2 (H1–H5) | **Deferred** | Owned by 13-deploy-smoke after merge; convert issues surface via `/api/v1/convert` |
| T3 live browser | **Not run** | No UI-only acceptance for #667 this cycle |

## Playwright

Not required for UJ-026 T0 (package). Full `make test-e2e-playwright` not executed in this stage
(no local stack spun). CI E2E Smoke on feat branch #750: SUCCESS.
