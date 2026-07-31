# Dig checklist refresh — S032 / EV-025 (T4.7)

**Date**: 2026-07-31  
**Gate**: E25-T5=3 — any dig ❌ **encode** residual blocks Gate C  
**Verdict**: **Lane A encode rows ✅** — no Gate C encode blockers from dig type table

## Lane A encode audit (post M4.1–M4.6)

| Dig type / cluster | Encode | Notes |
|--------------------|--------|-------|
| Addendum container (AO/SLP/text) | ✅ | M4.5–M4.6 |
| AerodromePeakWind | ✅ | prior + M4.1 |
| AerodromeVariableRVR | ✅ | M1 #810 |
| AerodromeWindShift | ✅ | M4.1 |
| CharacterOfTheSky / CloudTypes | ✅ | M4.2 |
| ConvectiveCloud* | ✅ | M4.2 |
| HailstoneSize | ✅ | M4.2 |
| Failed/Inoperative/MeteorologicalSensors | ✅ | M3 #812 |
| MaxMinTemperatures | ✅ | M4.5 |
| Obscurations | ✅ | M4.3 |
| ObservedLightning* | ✅ | M2 #811 |
| ObservedAtSecondLocation / TowerVisibility | ✅ | M4.3 |
| ObservingSystemType | ✅ | M4.5 |
| ProcessedProperty + statistical | ✅ | M4.5 (P/6/7) |
| RecentWeather | ✅ | M4.6 |
| Sector / SectorVisibility | ✅ | M4.3 |
| SnowIncrease | ✅ | M3 #812 |
| Variable CIG / SKY / VIS | ✅ | M4.4 |
| PRESFR/RR + flags (`$`/CONTRAILS/AURORA/NOSPECI) | ✅ | M4.6 |
| VisuallyObservablePhenomena | ✅ | M2+#M4.2+#M4.3 |

## Soft residuals (do **not** block Gate C encode)

| Item | Status | Disposition |
|------|--------|-------------|
| `pressureTendency3hr` / `5appp` | not yet structured | Optional deepen — free-text never-drop; not a dig ❌ row after Addendum ✅ |
| `snowDepth` alone (non-SNINCR) | not yet structured | Optional; SNINCR path ✅ |
| `firstObservation` / `lastObservation` / `durationOfSunshine` | rare TAC | Optional; not dig ❌ blockers |
| ObservingSystemMetadata | unused (PDF) | Skip |
| Validate / SCH | ⚠ | M6 TC-EV025-010 |

## Lane B

| Item | Status |
|------|--------|
| #809 `sigmet-multi-location-VA` soft→strict | **M5** soft ✅; equality/`wmoPass` deferred (T5.3) |

## Gate C encode (Lane A)

**PASS** for dig ❌ encode closeout — proceed to M5 (#809) then M6/M7.
