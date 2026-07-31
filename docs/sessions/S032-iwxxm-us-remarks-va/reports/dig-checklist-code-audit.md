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
| AerodromeWindShift | ✅ | `_wind_shift_extension`; TC-EV025-004 WSHFT/FROPA | **done** M4.1 |
| CharacterOfTheSky / CloudTypes | ✅ | `_character_of_the_sky_xml`; TC-EV025-004 `8/` | **done** M4.2 |
| ConvectiveCloudLocation / Types | ✅ | `_convective_cloud_xml`; TC-EV025-004 CB/TS | **done** M4.2 |
| HailstoneSize | ✅ | `_hailstone_size_addendum_inner`; TC-EV025-004 GR | **done** M4.2 |
| ObservedLightning / Frequency / Type | ✅ | `_parse_lightning_remark` + Addendum VOP; TC-EV025-002 | **done** M2 (#811) |
| VisuallyObservablePhenomena | ✅ L/C/sky/obsc | `_vop_addendum_inner`; obscuration ✅ | **done** M2+#M4.2+#M4.3 |
| SnowIncrease | ✅ | `_snow_increase_addendum_inner`; TC-EV025-003 | **done** M3 (#812) |
| FailedSensors / Inoperative / MeteorologicalSensors | ✅ | `_inoperative_sensors_extension`; CHINO/… | **done** M3 (#812) |
| Sector / SectorVisibility | ✅ | `_visibility_us_extension`; TC-EV025-004 VIS n DIR | **done** M4.3 |
| Obscurations | ✅ | VOP obscuration; TC-EV025-004 FU BKNhhh | **done** M4.3 |
| ObservedAtSecondLocation / SensorLocation / TowerVisibility | ✅ | Addendum + vis ext; TC-EV025-004 CIG/VIS RWY / TWR VIS | **done** M4.3 |
| VariableCeilingHeight / Sky / Visibility | ✅ | CloudLayer + vis ext; TC-EV025-004 CIG/SKY/VIS V | **done** M4.4 |
| MaxMinTemperatures | ✅ | `_max_min_temperatures_addendum_inner`; TC-EV025-004 `1`/`2`/`4` | **done** M4.5 |
| ProcessedProperty + statistical codelists | ✅ | `_processed_quantity_addendum_inner`; P/6/7 precip | **done** M4.5 |
| ObservingSystemType (codelist href) | ✅ | Addendum `observingSystemType` AO1/AO2 href | **done** M4.5 |
| RecentWeather | ⚠ | annex3 overlap likely | **M4.6** if still ❌ for US |
| Addendum residuals (PRESFR/RR, CONTRAIL, `$`, …) | ❌/⚠ | free-text only today | **M4.6** |

## Lane B (#809)

| Stem | Validate | Package golden | Catalog | Queue |
|------|----------|----------------|---------|-------|
| `sigmet-multi-location-VA` | ✅ inventory | ❌ soft M-golden | `wmoReference` | **M5** soft→strict |

## M1–M4 work queue (ordered)

1. **M1** — AerodromeVariableRVR (+ meanRVR withheld) — **done**  
2. **M2** — ObservedLightning* + VisuallyObservablePhenomena (lightning) — **done**  
3. **M3** — SnowIncrease + sensor-outage types — **done**  
4. **M4.1** — AerodromeWindShift (+ PeakWind deepen if needed) — **done**
5. **M4.2** — Sky / convective / hail — **done**
6. **M4.3** — Sector / obscuration / second-site / tower — **done**
7. **M4.4** — Variable CIG/SKY/VIS — **done**
8. **M4.5** — Max/min + ProcessedProperty / codelists — **done**
9. **M4.6** — Addendum residuals + RecentWeather deepen  

## Next

`[T4.6]` Addendum residuals (AO1/flags/text not yet structured) + RecentWeather deepen if ❌.
