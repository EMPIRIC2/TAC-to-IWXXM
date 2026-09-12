# E2E report — S032 / EV-025 (10-e2e smoke / T7.2)

**Date**: 2026-07-31  
**Mode**: smoke (Lean+build)  
**Verdict**: **PASS**

## Journeys exercised (library / in-process)

| Journey | Mechanism | Result |
|---------|-----------|--------|
| UJ-040 US REMARKS encode | pytest TC-EV025-001..007 / 010 | PASS |
| UJ-041 VA multi-location soft | TC-EV025-008 soft-compare | PASS |
| UJ-041 catalog tier | TC-EV025-009 stays `wmoReference` | PASS |
| UJ-039 US out of WMO menu | Vitest TC-EV025-005 | PASS |
| F23 SIGMET catalog smoke | backend integration | PASS |

## Tiers

| Tier | Status |
|------|--------|
| T0 in-process UJ | PASS |
| T1 H0i integration | PASS (SIGMET catalog smoke) |
| T2 / T3 live browser | N/A this smoke — 13 when ships; no UI change (E25-ui=1) |

## Notes

No Playwright required for this cycle (UI N/A). Deploy smoke deferred to T7.3 when convert ships on Render.
