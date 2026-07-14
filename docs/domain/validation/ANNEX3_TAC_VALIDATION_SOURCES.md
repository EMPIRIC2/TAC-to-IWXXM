# Annex 3 / TAC validation — rule sources

**Purpose:** Authoritative URLs for **validating TAC inputs** (templates, business rules, vocabularies) for F6 products under profile **`annex3`**, plus pointers for **`iwxxm_us`**.  
**Ticket:** [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719) · feeds [#698](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/698).  
**Not in scope:** implementing validators; IWXXM XML validation (see [IWXXM_VALIDATION_SOURCES.md](../iwxxm/IWXXM_VALIDATION_SOURCES.md)).

Master catalog: [RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md).

---

## Separation of concerns

| Concern | SoT | Engine consumer |
|---------|-----|-----------------|
| **When / what** must appear in TAC (SARPs, SPECI criteria, TAF periods, SIGMET validity…) | ICAO **Annex 3** (+ Doc **8896** practice) | `tac-validate` |
| **Alphanumeric code forms / groups** | WMO-No. **306 Vol I.1** | `tac-validate` |
| **Coded tokens** (weather, phenomena, nils) | **codes.wmo.int** (+ offline RDF) | `tac-validate` vocab gates |
| **US REMARKS / national differences** | **FMH-1** + NWS instructions + **iwxxm-us** docs | `tac-validate` profile `iwxxm_us` |
| **XML well-formed / XSD / Schematron** | schemas.wmo.int | `iwxxm-validate` (post-convert) |

Historical **GIFTs** METAR grammar is a **gap baseline**, not ongoing SoT (ADR-014).

---

## Normative SARPs & practice (Annex III family)

### ICAO Annex 3

| Field | Value |
|-------|-------|
| Title | Annex 3 — Meteorological Service for International Air Navigation |
| Publisher | ICAO |
| URL | https://store.icao.int/en/annex-3-meteorological-service-for-international-air-navigation-1 |
| Listing | https://store.icao.int/en/annexes/annex-3 |
| Access | **Paywall** — cite only ([ACCESS_AND_CITATION.md](../rules/ACCESS_AND_CITATION.md)) |
| Label | normative |
| Products | METAR · SPECI · TAF · SIGMET · AIRMET · VAA · TCA |

**Use for validation rules that are not “XML encoding”:**

- Report types and issue criteria (e.g. SPECI thresholds)
- Contents of aerodrome observations / forecasts / en-route warnings / advisories
- Observing and reporting obligations that FM 205 / IWXXM XSD **do not** redefine

**WMO-No. 49 Vol II note:** Parts I–II discontinued 31 Dec 2023 — use Annex 3 instead  
https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/aviation/two-stage-discontinuation-of-technical-regulations-wmo-no-49-volume-ii-meteorological-service

### ICAO Doc 8896

| Field | Value |
|-------|-------|
| Title | Manual of Aeronautical Meteorological Practice |
| URL | https://store.icao.int/en/manual-of-aeronautical-meteorological-practice-doc-8896 |
| Access | **Paywall** |
| Label | normative (practice) |
| Use | Harmonized SIGMET/TCA practice, OPMET handling tips feeding operator lint messages |

---

## Alphanumeric templates (WMO Manual on Codes)

| Resource | URL | Role for TAC validation |
|----------|-----|-------------------------|
| WMO-No. 306 Vol **I.1** (Part A alphanumeric) | https://library.wmo.int/idurl/4/35713 | FM templates / code tables for TAC groups |
| Code Table **4678** (machine) | https://codes.wmo.int/306/4678 | Significant weather token inventory |
| WMO-No. 306 Vol **I.3** (FM 205) | https://library.wmo.int/idurl/4/35769 | Points to TAC SARPs elsewhere; **not** primary TAC grammar |

---

## Machine vocabularies (public — preferred for CI)

Validate token **membership** / spellings against registry (not full Annex prose):

| Register | URL | Products |
|----------|-----|----------|
| Present / forecast weather | https://codes.wmo.int/49-2/AerodromePresentOrForecastWeather | METAR SPECI TAF |
| Recent weather | https://codes.wmo.int/49-2/AerodromeRecentWeather | METAR SPECI |
| Cloud amount | https://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome | METAR SPECI TAF |
| Convective type | https://codes.wmo.int/49-2/SigConvectiveCloudType | METAR SPECI (+ hazard space) |
| SIGMET phenomena | https://codes.wmo.int/49-2/SigWxPhenomena | SIGMET |
| AIRMET phenomena | https://codes.wmo.int/49-2/AirWxPhenomena | AIRMET |
| SFC VIS cause | https://codes.wmo.int/49-2/WeatherCausingVisibilityReduction | AIRMET |
| Aviation colour | https://codes.wmo.int/iwxxm/AviationColourCode | VAA |
| Nil reasons | https://codes.wmo.int/common/nil · https://codes.wmo.int/iwxxm/nil | all |

**Conversion pitfall (also a validation hint):** most weather concept `@id`s live under  
`http://codes.wmo.int/306/4678/{TAC}` even when the XSD vocabulary attribute names `49-2/AerodromePresentOrForecastWeather`.

Offline RDF (pin-aligned): `vendor/schemas/iwxxm/IWXXM/rule/codes.wmo.int-*.rdf`.

---

## Official TAC fixtures (accept / reject shapes)

Use WMO official examples as golden TAC for gates — not proprietary corpora:

| Product | Example TAC prefix (`schemas.wmo.int/iwxxm/2025-2/examples/`) |
|---------|----------------------------------------------------------------|
| METAR | `metar-A3-1.tac`, NIL collect, `metar-translation-failed` |
| SPECI | `speci-A3-2.tac` |
| TAF | `taf-A5-1.tac`, cancel `taf-A5-2.tac` |
| SIGMET | `sigmet-A6-1a-TS.tac`, CNL, TC, VA |
| AIRMET | `airmet-A6-1a-TS.tac` |
| VAA | `va-advisory-A7-2.tac` |
| TCA | `tc-advisory-A2-2.tac` |

AHL data type designators (TAC vs IWXXM):  
https://community.wmo.int/en/activity-areas/wis/iwxxm/ahl-icao-data

Additional (informative) pairs: https://github.com/wmo-im/iwxxm-translation

---

## US profile (`iwxxm_us`) — Annex 3 differences

| Resource | URL | Use |
|----------|-----|-----|
| FMH-1 (2019) | https://www.icams-portal.gov/resources/ofcm/fmh/FMH1/fmh1_2019.pdf | Surface obs / METAR REMARKS coding |
| FMH index | https://www.icams-portal.gov/resources/ofcm/fmh/allfmh2.htm | Related handbooks |
| NWS FMH-1 registry | https://codes.nws.noaa.gov/FMH-1 | Machine tables |
| iwxxm-us 3.0 | https://nws.weather.gov/schemas/iwxxm-us/3.0/ | National encode/validate surface |
| MDL data modeling | https://vlab.noaa.gov/web/mdl/data-modeling | Context for US extensions |

GIFTs historically stripped REMARKS — **US profile validation is a first-class gap** this catalog fills.

---

## Product checklist for #698 design Q3

| Product | Minimum normative cite for TAC validation |
|---------|-------------------------------------------|
| METAR | Annex 3 (paywall) **or** registry weather/cloud + official `.tac` examples |
| SPECI | Annex 3 SPECI criteria + same vocab as METAR |
| TAF | Annex 3 / Doc 8896 + examples (AMD/CNL/NIL) |
| SIGMET | Annex 3 + SigWxPhenomena + examples |
| AIRMET | Annex 3 + AirWxPhenomena + VIS-cause |
| VAA | Registry colour codes + VAA examples; Doc 9766 for colour **meanings** (paywall) |
| TCA | Official TCA examples + Annex 3 advisory provisions (paywall) — mark deeper groups TBD if prose unavailable |

If paywalled prose is unavailable in CI, gate on **public vocab + official TAC examples**, and label SARPs-derived lint as “requires Annex 3 licensed reference” in design notes.

---

## Related domain docs

- Implementation layers (post-convert IWXXM): [COMPREHENSIVE_VALIDATION.md](./COMPREHENSIVE_VALIDATION.md)
- Failure taxonomy: [FAILURE_TAXONOMY.md](./FAILURE_TAXONOMY.md)
- IWXXM creation (encode): [IWXXM_CREATION_SOURCES.md](../iwxxm/IWXXM_CREATION_SOURCES.md)
