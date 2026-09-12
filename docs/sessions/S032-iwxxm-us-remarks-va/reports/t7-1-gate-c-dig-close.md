# Dig ❌→✅ final audit — S032 / EV-025 (T7.1)

**Date**: 2026-07-31  
**Gate**: E25-T5=3 — any dig ❌ **encode** residual blocks Gate C  
**Verdict**: **PASS** — no dig ❌ encode residuals remain; Lane B soft-compare green; equality/`wmoPass` deferred per TC-EV025-009

## Lane A — dig encode closeout

Reaffirms T4.7: all dig-checklist encode rows ✅ (VariableRVR, Lightning/VOP, SnowIncrease/sensors, WindShift, sky/convective/hail, sector/obscuration/tower, variable CIG/SKY/VIS, MaxMin/ProcessedProperty, Addendum residuals/RecentWeather). Soft non-❌ residuals unchanged (optional free-text deepen only).

## Lane B — #809

| Item | Status |
|------|--------|
| Soft-compare (TC-EV025-008) | ✅ green — dual `analysisCollection`, OBS+FCST, volcano |
| ADR-032 equality / `wmoPass` (TC-EV025-009) | ❌ not yet — catalog stays `wmoReference`; FIXTURE_GAPS note |
| Does equality gap block Gate C? | **No** — S02.M1 allows soft first; dig ❌ encode gate is Lane A only |

## M6 deepen / validate

| TC | Status |
|----|--------|
| TC-EV025-005 US out of WMO menu | ✅ |
| TC-EV025-006/007 diagnostics + `humanReadableText` | ✅ |
| TC-EV025-010 combined-catalog validate smoke | ✅ (no SCH blocking; S02.L1 N/A) |

## Gate C encode decision

**PASS** — proceed to T7.2 (`08-verify-build` + `10-e2e` smoke). Deploy (T7.3 / 13) only when API convert/validate ships.
