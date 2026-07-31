# Guidance + Schematron assert gap list — S031 / EV-024 (T4.2)

**Date**: 2026-07-30  
**Pin**: IWXXM **v2025-2** (`vendor/schemas/iwxxm/2025-2/IWXXM/`)  
**Sources**: `examples/TAC-to-XML-Guidance.txt` · `rule/iwxxm.sch` (165 patterns)  
**Purpose**: Re-scrape → seed **child issues** (TC-EV024-008). No engine encode rewrite in this cycle.

## Schematron inventory (pin)

| Prefix | Pattern count | Product / shared |
|--------|---------------|------------------|
| METAR_SPECI | 43 | METAR/SPECI |
| AIRMET | 20 | AIRMET |
| Common | 18 | Shared aerodrome / report |
| SIGMET | 15 | General SIGMET |
| VolcanicAshAdvisory | 14 | VAA |
| TAF | 14 | TAF |
| TropicalCycloneAdvisory | 10 | TCA |
| WAFSSignificantWeatherForecast | 7 | WAFS (roadmap) |
| MeteorologicalFeature | 6 | MetFeature embeds |
| SpaceWeatherAdvisory | 5 | SWX (roadmap) |
| VolcanicAshSIGMET | 4 | VA SIGMET |
| IWXXM | 3 | Extension / nilReason |
| TropicalCycloneSIGMET | 3 | TC SIGMET (#738) |
| VolcanoObservatoryNoticeForAviation | 3 | VONA (roadmap) |
| **Total** | **165** | |

Full id list: extract via `sch:pattern/@id` on pin `iwxxm.sch` (do not hand-edit vendor).

## Guidance topics (pin `TAC-to-XML-Guidance.txt`)

| Section | Topics (abbreviated) | Prior theme coverage | Gap / child seed |
|---------|----------------------|----------------------|------------------|
| All reports | `reportStatus`; 2-D CRS (`srsName`/`srsDimension`/`axisLabels`) | F20/F23 **C1** convert-only deferred | Keep deferred — no TAC lint surface |
| METAR/SPECI | NIL; CAVOK; CLRD; NSC; NCD; NOSIG; NSW; R88/R99; SNOCLO; `//` wx; VV///; `//////` clouds; CLR/SKC; runway depth; BECMG/TEMPO trend; nilReason quantities; wind variation; missing RVR | F15 R1–R8 closed; runway-state / sea largely out | Residual: CLRD/SNOCLO/R88 depth if not in registry; sea-state SCH vs lint |
| TAF | NIL; CNL; CAVOK; NSC; NSW; VV/// (omit); TX/TN pairs | F20 T1–T4 | Residual: multi TX/TN pair edge (#735 survivors if any) |
| AirspaceVolume / FL | `aixm:AirspaceVolume`; FLnnn / M / FT; TOP ABV / BLW | F23 G1 residual TOP ABV/BLW light | Child if encode still light vs Guidance |
| AIRMET and SIGMET | CNL; point lat/lon; NO VA EXP; STNR | F23/F24 closed themes | Multi-location VA geometry fidelity (**new**) |
| Volcanic Ash Advisory | UNKNOWN/UNNAMED; NOT PROVIDED; NO VA EXP; NIL remarks; NO FURTHER ADVISORIES | F26 V1–V3 closed | Cite only unless #800 residual |
| Tropical Cyclone Advisory | UNNAMED; NIL CB; NO MSG EXP; &lt;34 kt; no-longer-TC | F27 T1–T3 closed | Cite only |
| Space Weather Advisory | DAYSIDE; NOT AVBL; NO SWX EXP; NIL; NO FURTHER | #740 roadmap | Defer with product |

## Stem × wire gaps (from #804 matrix)

| Stem | Validate XML | Convert golden | Sample menu | Child / ticket |
|------|--------------|----------------|-------------|----------------|
| In-scope happy-path (METAR/SPECI/TAF/SIGMET/AIRMET/VAA/TCA passers) | ✅ CI | ✅ where F25/F23/… | ✅ `wmoPass` | — |
| `sigmet-VA-EGGX` | ✅ | ⚠ package golden (F23) | ✅ `wmoReference` | Deepen only if equality fails under defaults |
| `sigmet-multi-location-VA` | ✅ (M6 inventory) | ❌ not M-golden | ✅ `wmoReference` | **File child** — multi-location VA encode |
| `sigmet-A6-2-TC` | ✅ | D | D | #738 |
| `*-translation-failed*` / NIL-collect | ✅ quarantine / shape | — / D | — | #800 survivors |
| SWX / VONA / WAFS / QVACI | D | D | D | #740 / #741 / roadmap |

## US / MDL (#773) → children (not Guidance)

See [iwxxm-us-metar-speci-pdf-mining-notes.md](../../../domain/mining/iwxxm-us-metar-speci-pdf-mining-notes.md) checklist. Priority clusters for issues:

1. Variable RVR / meanRVR withheld  
2. Lightning + VisuallyObservablePhenomena  
3. SnowIncrease / sensor outage remarks  
4. Combined iwxxm-us validate expectations for extension blocks  

## Explicit non-gaps this cycle

- Hand-edit `vendor/schemas/*`  
- Big-bang encode rewrite  
- #806 WIS2 (OOS)  
- Committing `.local/` PDF/clones  
