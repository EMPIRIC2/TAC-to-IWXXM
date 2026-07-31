# Mining notes — IWXXM-US METAR/SPECI PDF + MDL (#773)

> **Transitory** — not SoT.  
> **Cycle**: S031 / EV-024 · **Date mined**: 2026-07-30  
> **Skills**: extract-pdf-to-repo + mine-domain-sources  
> **Local**: `.local/reference/iwxxm-us-metar-speci-pdf/` (gitignored)  
> **Vendor pin**: `vendor/schemas/iwxxm-us` **3.0**

## Sources

| Item | URL / path | Label |
|------|------------|-------|
| METAR and SPECI.pdf | VLab → documents/…/METAR+and+SPECI.pdf (v3.0 model docs; 23 Dec 2022) | normative-conversion-notes (US) |
| VLab Data Modeling | https://vlab.noaa.gov/web/mdl/data-modeling | informative index |
| nws.weather.gov iwxxm-us 3.0 | https://nws.weather.gov/schemas/iwxxm-us/3.0/ | normative-schema |
| NOAA-MDL/iwxxm-us-modelling | https://github.com/NOAA-MDL/iwxxm-us-modelling | informative tooling |
| Vendor pin | `vendor/schemas/iwxxm-us/3.0/*.xsd` | runtime SoT |
| FMH-1 dig (prior) | [fmh1-2019-mining-notes.md](./fmh1-2019-mining-notes.md) | TAC RMK syntax |

**Boundary:** USWX (non–Annex 3) out of product scope. Do **not** mix US examples into WMO sample menu (UJ-039 / E24-C).

## Type × TAC × encode × validate checklist

Status seed from PDF TOC + pin XSD vs known F6.b / F15 work (engine gaps → child issues).

| Model type | Likely TAC / RMK | Encode (F6.b) | Validate (iwxxm-us) | Fixture | Notes |
|------------|------------------|---------------|---------------------|---------|-------|
| Addendum | AO1/AO2, SLP, PRESFR/RR, snow, CONTRAIL, AURORA, FROPA flags, sunshine, `$`, text | ⚠ partial | ⚠ | ⚠ | Container; AO2/SLP often started |
| AerodromePeakWind | PK WND | ⚠ / ✅ theme | ⚠ | ⚠ | F15 deepen cited AO2/SLP/PK WND |
| AerodromeVariableRVR | Variable RVR | ✅ | ⚠ | ✅ | S032/#810 — meanRVR withheld; TC-EV025-001 |
| AerodromeWindShift | WSHFT / FROPA | ⚠ | ⚠ | ❌ | |
| CharacterOfTheSky / CloudTypes | Sky character RMK | ❌ | ⚠ | ❌ | |
| ConvectiveCloudLocation / Types | CB/TCU location/motion | ❌/⚠ | ⚠ | ❌ | |
| FailedSensors / InoperativeSensors / MeteorologicalSensors | Sensor outage | ❌ | ⚠ | ❌ | |
| HailstoneSize | GR size | ❌ | ⚠ | ❌ | |
| MaxMinTemperatures | 1/6-hr max/min | ⚠ | ⚠ | ❌ | |
| Obscurations | Obscuration layers | ❌ | ⚠ | ❌ | |
| ObservedLightning / Frequency / Type | Lightning RMK | ✅ | ⚠ | ✅ | S032/#811 — TC-EV025-002; PDF sample shapes |
| ObservedAtSecondLocation / SensorLocation / TowerVisibility | Second-site / tower | ❌ | ⚠ | ❌ | |
| RecentWeather | RE… | ⚠ | ⚠ | ❌ | May overlap WMO recent |
| Sector / SectorVisibility | Sector vis | ❌ | ⚠ | ❌ | |
| SnowIncrease | Snow depth increase | ❌ | ⚠ | ❌ | |
| ProcessedProperty + statistical codelists | PNO / stats | ❌ | ⚠ | ❌ | |
| VariableCeilingHeight / Sky / Visibility | Variable CIG/SKY/VIS | ❌ | ⚠ | ❌ | |
| VisuallyObservablePhenomena | Lightning+convection+sky+obscuration bundle | ✅ lightning | ⚠ | ✅ | S032/#811 — lightning via Addendum; convection/sky/obscuration → M4 |
| Codelists (ObservingSystemType, Pressure*, QualitativeDistance, Statistical*) | FMH-1 / NWS codes URIs | ⚠ | ⚠ | ❌ | Prefer codes.nws.noaa.gov hrefs from PDF |

**Legend:** ✅ encoded/tested · ⚠ partial / unconfirmed · ❌ missing — refine in M4/M7 children after code audit.

## Durable catalog rows (promote)

See RULE_SOURCE_URLS §National — add/enrich:

1. METAR and SPECI.pdf (VLab document UUID path)
2. TAF.pdf companion (listed on VLab — extract deferred unless needed this cycle)
3. NOAA-MDL/iwxxm-us-modelling
4. Enrich existing VLab + nws.weather.gov rows

## Child-issue seeds

| Gap | Suggested focus |
|-----|-----------------|
| Variable RVR encode + meanRVR withheld | tac2iwxxm + goldens |
| Lightning / VisuallyObservablePhenomena pack | tac2iwxxm + tac-validate US REMARKS |
| SnowIncrease / sensor outage remarks | lint + encode |
| Combined catalog expectations for extension blocks | iwxxm-validate |
| AWC live IWXXM vs nws examples drift | fixtures |

## Vendor drift (read-only)

Pin `3.0` XSD types align with PDF TOC type names (`Addendum`, `AerodromePeakWind`, …). No sync ticket opened this pass — re-check if published tarball SHA drifts from `vendor/schemas/iwxxm-us`.
