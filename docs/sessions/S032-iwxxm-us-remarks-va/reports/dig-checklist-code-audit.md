# Dig checklist code-audit — S032 / EV-025 (T0.2)

**Date**: 2026-07-31  
**Basis**: `iwxxm-us-metar-speci-pdf-mining-notes.md` × `profiles/iwxxm_us.py` × existing `iwxxm_us_golden`  
**Gate C rule**: encode ❌ remaining after M4 **blocks** Gate C (E25-T5=3)

## Encode status (seed for M1–M4)

| Model type | Encode now | Evidence | Work queue |
|------------|------------|----------|------------|
| Addendum (AO2/SLP/`humanReadableText`) | ⚠ partial | `_addendum_extension`; goldens `metar_us_ao2_slp`, etc. | M4.6 deepen residuals |
| AerodromePeakWind | ✅ | `_peak_wind_extension`; `metar_us_pk_wnd` | M4.1 only if deepen gaps |
| AerodromeVariableRVR | ✅ | `_variable_rvr_extension`; TC-EV025-001 | **done** M1 (#810) |
| AerodromeWindShift | ❌ | — | **M4.1** |
| CharacterOfTheSky / CloudTypes | ❌ | — | **M4.2** |
| ConvectiveCloudLocation / Types | ❌ | — | **M4.2** |
| HailstoneSize | ❌ | — | **M4.2** |
| ObservedLightning / Frequency / Type | ✅ | `_parse_lightning_remark` + Addendum VOP; TC-EV025-002 | **done** M2 (#811) |
| VisuallyObservablePhenomena | ✅ lightning | `_vop_addendum_inner`; convection/sky/obscuration still ❌ | **done** M2 lightning (#811); deepen M4 |
| SnowIncrease | ❌ | — | **M3** (#812) |
| FailedSensors / Inoperative / MeteorologicalSensors | ❌ | — | **M3** (#812) |
| Sector / SectorVisibility | ❌ | — | **M4.3** |
| Obscurations | ❌ | — | **M4.3** |
| ObservedAtSecondLocation / SensorLocation / TowerVisibility | ❌ | — | **M4.3** |
| VariableCeilingHeight / Sky / Visibility | ❌ | — | **M4.4** |
| MaxMinTemperatures | ❌/⚠ | not in US profile | **M4.5** |
| ProcessedProperty + statistical codelists | ❌ | — | **M4.5** |
| ObservingSystemType (codelist href) | ⚠ | Addendum `observingSystemType` href | **M4.5** deepen |
| RecentWeather | ⚠ | annex3 overlap likely | **M4.6** if still ❌ for US |
| Addendum residuals (PRESFR/RR, CONTRAIL, `$`, …) | ❌/⚠ | free-text only today | **M4.6** |

## Lane B (#809)

| Stem | Validate | Package golden | Catalog | Queue |
|------|----------|----------------|---------|-------|
| `sigmet-multi-location-VA` | ✅ inventory | ❌ soft M-golden | `wmoReference` | **M5** soft→strict |

## M1–M4 work queue (ordered)

1. **M1** — AerodromeVariableRVR (+ meanRVR withheld) — **done**  
2. **M2** — ObservedLightning* + VisuallyObservablePhenomena (lightning) — **done**  
3. **M3** — SnowIncrease + sensor-outage types  
4. **M4.1** — AerodromeWindShift (+ PeakWind deepen if needed)  
5. **M4.2** — Sky / convective / hail  
6. **M4.3** — Sector / obscuration / second-site / tower  
7. **M4.4** — Variable CIG/SKY/VIS  
8. **M4.5** — Max/min + ProcessedProperty / codelists  
9. **M4.6** — Addendum residuals + RecentWeather deepen  

## Next

`[T1.1]` red goldens for Variable RVR (TC-EV025-001).
