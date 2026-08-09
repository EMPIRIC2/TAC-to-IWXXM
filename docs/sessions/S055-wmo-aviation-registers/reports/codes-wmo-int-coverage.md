# EV-046 — codes.wmo.int present / cite / cover (Lean)

**Session:** S055-wmo-aviation-registers · **Cycle:** EV-046 · **Date:** 2026-08-08  
**Issue:** [#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889) · Epic [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846)  
**Validated follow-on:** [#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959)  
**Corpus:** [Corpus: product] [Corpus: tests] · domain opt-in

## AC6 — Offline SoT + pin / cadence

| Item | Value |
|------|-------|
| Bundle | `vendor/manifest.json` → `iwxxm-codelists` |
| Upstream | `wmo-im/iwxxm-codelists` tag **`49-2`** @ `b0511b76` |
| Local path | `vendor/schemas/iwxxm-codelists/` |
| Weather membership SoT | `CSV/306/4678/4678_entity.csv` (**402** notations) + `TTL/306/4678/` |
| 49-2 aviation TTL | `TTL/49-2/{register}/*.ttl` |
| SCH / encode RDF (pin) | `vendor/schemas/iwxxm/2025-2/IWXXM/rule/codes.wmo.int-*.rdf` |
| PR CI | **Offline only** — no live HTML fetches |
| Live refresh | Deferred to [#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959) + compose [#882](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/882) |
| URI drift | Compose [#859](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/859) / TC-EV038-008 |

Cadence: refresh with normal vendor sync PRs that bump `iwxxm-codelists` pin; do not scrape `codes.wmo.int` HTML in PR CI.

## AC1 — Present inventory (priority registers)

Vendor counts from `iwxxm-codelists` TTL/CSV + pin RDF (`2025-2`) for `iwxxm/*`:

| Register | Offline members | Disposition |
|----------|-----------------|-------------|
| [49-2/AerodromePresentOrForecastWeather](https://codes.wmo.int/49-2/AerodromePresentOrForecastWeather) | 402 | Present — dual with 306/4678 concept IDs |
| [306/4678](https://codes.wmo.int/306/4678) | 402 (CSV) | **Membership SoT** — live HTML browse incomplete (~101) |
| [49-2/AerodromeRecentWeather](https://codes.wmo.int/49-2/AerodromeRecentWeather) | 26 | Present |
| [49-2/CloudAmountReportedAtAerodrome](https://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome) | 10 | Present |
| [49-2/SigConvectiveCloudType](https://codes.wmo.int/49-2/SigConvectiveCloudType) | 2 (CB, TCU) | Present |
| [49-2/SigWxPhenomena](https://codes.wmo.int/49-2/SigWxPhenomena) | 17 | Present |
| [49-2/AirWxPhenomena](https://codes.wmo.int/49-2/AirWxPhenomena) | 18 | Present |
| [49-2/WeatherCausingVisibilityReduction](https://codes.wmo.int/49-2/WeatherCausingVisibilityReduction) | 19 | Present |
| [49-2/AviationColourCode](https://codes.wmo.int/49-2/AviationColourCode) | 7 | Dual — prefer **`iwxxm/`** for 2025-2 |
| [iwxxm/AviationColourCode](https://codes.wmo.int/iwxxm/AviationColourCode) | 5 (+ register node) | Prefer for VONA/VAA colour |
| [49-2/MeteorologicalFeature](https://codes.wmo.int/49-2/MeteorologicalFeature) | 27 | Dual — `VOLCANIC_ASH` **not** here |
| [iwxxm/MeteorologicalFeature](https://codes.wmo.int/iwxxm/MeteorologicalFeature) | ~28–29 | Prefer; includes `VOLCANIC_ASH` |
| [common/nil](https://codes.wmo.int/common/nil) | 11–12 | Dual SCH with `iwxxm/nil` |
| [iwxxm/nil](https://codes.wmo.int/iwxxm/nil) | 11–12 | Prefer when pin/examples require |
| [49-2/SpaceWxPhenomena](https://codes.wmo.int/49-2/SpaceWxPhenomena) | 8 | Present |
| [49-2/SpaceWxLocation](https://codes.wmo.int/49-2/SpaceWxLocation) | 7 | Present |
| `RESUSPENDED_VOLCANIC_ASH` | — | **404 / obsolete cite** in some XSD docs — track under VONA deepen |

Stable concept pattern: `http://codes.wmo.int/{register}/…/{notation}` (https landings OK for docs).

## AC2 — Cited

| Surface | Change |
|---------|--------|
| `PROVENANCE_MAP.json` | Weather/cloud/nil catalog codes → register landings (not bare root) |
| `ISSUE_CATALOG.md` / `.json` / `catalog_attribution.json` | Regenerated (`make catalog-regen`) |
| `regen_issue_catalog.py` | Attribution prefers `source_url` before note |
| `RULE_SOURCE_URLS.md` | EV-046 pointer + #959 |
| `COVERAGE_MATRIX.md` | Fixture coverage % table (below / linked) |
| Mining notes | EV-046 operational follow-on recorded |

`UNKNOWN_PRODUCT` intentionally retains bare `https://codes.wmo.int/` (`status: N/A`) — not a registry notation check.

## AC3 — Cover (fixture token ∩ register)

Method (Lean / coarse — M1 accepted): extract uppercase TAC tokens from
`packages/tac-validate/tests/fixtures/**/*.tac` (+ `packages/tac2iwxxm/**/*.tac`);
intersect with vendor notations. **Not** encode-path coverage. NilReason URIs rarely
appear as TAC tokens → 0% expected until Validated wiring (#959).

| Product family | Register | Hit / total | % | Sample hits / notes |
|----------------|----------|-------------|---|---------------------|
| METAR/SPECI/TAF | 49-2/AerodromePresentOrForecastWeather | 16 / 402 | **4.0%** | `-RA`, `FG`, `TSRA`, … |
| METAR/SPECI/TAF | 306/4678 | 16 / 402 | **4.0%** | same concept set |
| METAR/SPECI | 49-2/AerodromeRecentWeather | 0 / 26 | **0%** | no `RExx` tokens matched |
| METAR/SPECI/TAF | CloudAmountReportedAtAerodrome | 6 / 10 | **60%** | FEW/SCT/BKN/OVC/… |
| METAR/SPECI/TAF | SigConvectiveCloudType | 1 / 2 | **50%** | CB (TCU gap) |
| SIGMET / VA | SigWxPhenomena | 2 / 17 | **11.8%** | VA, TC |
| VA / VAA / VONA | iwxxm/AviationColourCode | 2 / 6 | **33%** | ORANGE, YELLOW |
| VA / VAA / VONA | iwxxm/MeteorologicalFeature | 1 / 29 | **3.4%** | VOLCANO |
| AIRMET | AirWxPhenomena | 0 / 18 | **0%** | underscore TAC forms not tokenized |
| AIRMET | WeatherCausingVisibilityReduction | 5 / 19 | **26.3%** | FG, BR, … |
| SWXA | SpaceWxLocation | 6 / 7 | **85.7%** | EQN/EQS/… |
| SWXA | SpaceWxPhenomena | 0 / 8 | **0%** | |
| All | common/nil / iwxxm/nil | 0 / 12 | **0%** | nilReason not TAC tokens |
| TCA | (nil only in this method) | 0 / 12 | **0%** | phenomena via other vocab |

### Intentional exclusions (cite + reason)

| Exclusion | Reason |
|-----------|--------|
| Exhaustive 402 weather combinations in fixtures | Combinatorial; quality bars cover representative + negative packs — expand via #959 |
| Live HTML member counts | Incomplete vs CSV; CI uses vendor — [RULE_SOURCE_URLS](../../../domain/rules/RULE_SOURCE_URLS.md) |
| NilReason as TAC tokens | Encoded as IWXXM `xlink:href`, not TAC lexicon — Validated follow-on |
| AIRMET underscore phenomena (`SEV_ICE`, …) | Token heuristic misses `_` forms — gap for #959 |
| Non-aviation trees (bufr4/grib2/wmdr) | Out of scope per #889 |
| `49-2` colour / MetFeature for 2025-2 encode | Prefer `iwxxm/` duals — documented disposition |

## AC4 — Gap report → backlog

| Gap | Disposition |
|-----|-------------|
| Automated TAC∈register membership tests | **Closed** — S059 / EV-050 M1–M2 ([#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959)) |
| Raise weather fixture coverage beyond ~4% of 402 | **Defer+cite** — still ~4.5%; EV-050 OOS exhaustive 402 ([T2.4 delta](../../S059-codes-wmo-validated/reports/fixture-coverage-delta-t2.4.md)) |
| Recent-weather (`RE*`) fixture tokens | **Closed** — EV-050 aggressive packs (representative + sad) |
| AIRMET AirWxPhenomena underscore matching | **Closed** — EV-050 fixtures + normalize |
| SpaceWxPhenomena fixture tokens | **Closed** — composed EFFECT+sev membership path (+ sad); residual notations defer |
| TCU convective type in fixtures | **Closed** — CB+TCU = 100% register |
| URI membership drift vs live | Keep [#859](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/859) |
| Change-notification pipeline | Keep [#882](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/882) |

Post-M2 coverage numbers:
[fixture-coverage-delta-t2.4.md](../../S059-codes-wmo-validated/reports/fixture-coverage-delta-t2.4.md).

## AC5 — Validated waiver

Lean **waives** automated Validated checks (`D-S055-validated=1`). Evidence of waiver +
follow-on: this report + [#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959).
No live HTML CI introduced.

## TC checklist

| TC | Evidence |
|----|----------|
| TC-EV046-001 | Present inventory table above |
| TC-EV046-002 | PROVENANCE / ISSUE_CATALOG URLs |
| TC-EV046-003 | Cover table + exclusions |
| TC-EV046-004 | Gap → #959 + compose links |
| TC-EV046-005 | Waiver + #959 |
| TC-EV046-006 | SoT/pin section + #859/#882 |
