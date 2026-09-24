# Nil reasons and the 2025-2 codelist split

Session: EV-1278-nil-reasons. Ticket: #1278. Scale: standard. Gate: closed.

[Corpus: product §F6] [Corpus: domain-profiles] [Corpus: tests]

## Goal

Each nil reason we emit uses the codelist IWXXM 2025-2 Schematron expects. Hrefs that still point at the other list are corrected. 2023-1 output stays on the older href where that line still expects it.

## Out of scope

No new nil tokens. Do not retarget Canada 3.0.0. Do not implement parent #1274. No operator UI change. Do not promote `stage` to `main`.

## What is already true

- Emitters in `packages/tac2iwxxm` mostly write `http://codes.wmo.int/common/nil/...`. Shared constants live on the Annex 3 profile (`NIL_MISSING`, `NIL_NOSIG`, `NIL_NSC`, `NIL_NCD`, `NIL_NOT_OBS`, `NIL_WITHHELD`).
- VONA already writes `http://codes.wmo.int/iwxxm/nil`.
- Space-weather `intensityAndRegion` writes `common/nil` (`nothingOfOperationalSignificance` or `missing`). `locationIndicator` is an `xlink:href` into the space-weather location register when a region is present, not a nil href.
- The official 2025-2 space-weather example still uses `common/nil` on `intensityAndRegion`. The official 2025-2 WAFS example uses `iwxxm/nil` on feature children.
- 2025-2 Schematron splits the check:
  - `IWXXM.nilReasonCheck` requires `http://codes.wmo.int/iwxxm/nil` on `WAFSSignificantWeatherForecast`, `QuantitativeVolcanicAshConcentrationInformation`, `VolcanoObservatoryNoticeForAviation`, `MeteorologicalFeature`, and `MeteorologicalFeatureCollection`.
  - `IWXXM.nilReasonCheckLegacy` requires `http://codes.wmo.int/common/nil` on the report roots `SPECI`, `METAR`, `TAF`, `SIGMET`, `AIRMET`, `TropicalCycloneAdvisory`, `VolcanicAshAdvisory`, and `SpaceWeatherAdvisory`.
  - Both rules test `@nilReason` on that context element. They do not walk every descendant.
- 2023-1 Schematron has one rule, `IWXXM.nilReasonCheck`, on `//iwxxm:*`, and it requires `common/nil`.
- Canada 3.0.0 goldens and emitters stay on `common/nil`. That pin is out of this ticket.

## Emitted nil hrefs

Judged against the two 2025-2 asserts above. Those asserts test `@nilReason` on the named element. Child elements are not that context. Requirements lock: change only a row this table marks rejected.

| Product | Element | Emitted href | 2025-2 result |
|---------|---------|--------------|---------------|
| METAR / SPECI | visibility, rvr, meanRVR, presentWeather, cloud, verticalVisibility, phenomenonTime, weather, trendForecast, observation, airTemperature, dewpointTemperature, qnh | `common/nil` — `missing`, `withheld`, `notObservable`, `notDetectedByAutoSystem`, `nothingOfOperationalSignificance`, `noSignificantChange` | Accepted. The legacy assert names the report root, which we do not nil. Official 2025-2 examples use `common/nil`. |
| TAF | baseForecast | `common/nil/missing` | Accepted. Child of TAF. |
| SIGMET | geometry, directionOfMotion, sequenceNumber, phenomenon, phenomenonTime | `common/nil` — `missing`, `inapplicable`, `nothingOfOperationalSignificance`, `template` | Accepted. Child of SIGMET. |
| SIGMET | aixm maximumLimit, minimumLimit | bare token `unknown` | Not a codes.wmo.int href and not the context of either nil assert. |
| AIRMET | phenomenonTime | `common/nil/missing` | Accepted. Child of AIRMET. |
| TCA | cumulonimbusCloudLocation, remarks, nextAdvisoryTime | `common/nil` — `missing`, `inapplicable` | Accepted. Children of TropicalCycloneAdvisory. |
| VAA | observation, remarks | `common/nil` — `missing`, `inapplicable` | Accepted. Children of VolcanicAshAdvisory. |
| Space weather | intensityAndRegion | `common/nil` — `nothingOfOperationalSignificance`, `missing` | Accepted. Child of SpaceWeatherAnalysis. The official 2025-2 example uses the same `common/nil` href. |
| Space weather | locationIndicator | `xlink:href` into the space-weather location register when a region is present | Accepted. The location assert allows an `xlink:href` from that register or any `@nilReason`. We do not emit a nil href here. |
| Space weather | remarks, nextAdvisoryTime | `common/nil/inapplicable` | Accepted. Children of SpaceWeatherAdvisory. |
| VONA | phenomenonProperty, heightSource, movement | `iwxxm/nil` — `inapplicable`, `unknown` | Accepted. Already the 2025-2 list. The `iwxxm/nil` assert names `VolcanoObservatoryNoticeForAviation` and `MeteorologicalFeature`, and those elements themselves have no `nilReason`. The VONA schema text names these tokens. |
| WAFS, QVACI | not emitted | — | Not applicable. Deferred products. |
| Canada 3.0.0 | densityAltitude | bare token `missing` | Out of this ticket. Leave it. |

No row is rejected, so no emitter changes. The lock test is TC-F6-035.

2023-1 still has one assert, `//iwxxm:*`, requiring `common/nil`. METAR and space weather already emit the same `common/nil` hrefs on 2023-1 as on 2025-2. The 2023-1 VONA for the A7-1 fixture emits no `nilReason`. This session does not add one.

## Success

- A short table lists each emitted nil href, the product, and whether 2025-2 Schematron accepts it.
- Every rejected href in that table is updated, with a test.
- 2023-1 output is unchanged where that line still expects the older href.

## Docs

Delta only: this brief, a nil-href table, and the test plan row for any href that changes. No new feature id.

## UI

No operator surface. Non-deployed UI preview: not applicable.
