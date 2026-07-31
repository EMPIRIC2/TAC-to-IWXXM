# IWXXM conversion (TAC → IWXXM)

**Purpose:** Authoritative URLs and mappings for **creating** IWXXM XML from TAC under F6 (`packages/tac2iwxxm`).  
**Ticket:** [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719) · feeds [#693](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/693).  
**Vendor pin:** `iwxxm` **v2025-2** · namespace `http://icao.int/iwxxm/2025-2`.

Hub: [README.md](README.md) · Companions: [TAC_VALIDATION.md](TAC_VALIDATION.md) · [IWXXM_VALIDATION.md](IWXXM_VALIDATION.md).  
Source digs (not SoT): [mining/](mining/) — especially Tier A, FM 205 ([2023](mining/WMO-306-vI-3-2023-mining-notes.md); historical [2019/upd-2021 **1–272 complete**](mining/WMO-306-vI-3-2019-upd-2021-mining-notes.md) · #798 — 3.0 nilReason + D-* landings corroborate Guidance below), OPMET Guidelines, modelling, [Annex 3](mining/icao-annex-3-mining-notes.md) (dual TAC+IWXXM **shall** obligation only — encoding still 306 I.3 / Doc 10003 / pin), [APAC IWXXM FAQs 3rd](mining/icao-apac-iwxxm-faqs-3rd-2025-mining-notes.md) (informative encode gotchas · #797).

---

## SoT stack for encode (recommended order)

1. **Official examples** for structure + product roots — `https://schemas.wmo.int/iwxxm/2025-2/examples/`
2. **`TAC-to-XML-Guidance.txt`** for TAC token → nilReason / omission rules (vendor: `2025-2/IWXXM/examples/`)
3. **codes.wmo.int** for `xlink:href` / `nilReason` enumerations (prefer URI family used in official example for that product: usually `common/nil` for classic F6; `iwxxm/nil` + `iwxxm/*` lists where XSD `vocabulary=` says so)
4. **WMO-No. 306 Vol I.3 FM 205** — for package selection / requirements prose prefer pin `documentation/manual/FM205.adoc` (**FM 205-2025-2**) over 2023 PDF tables that stop at 2023-1
5. **Product XSD** constraints for required elements/attrs
6. **iwxxm-us** only when profile = `iwxxm_us` (`extension` content)

Do **not** treat historical GIFTs as SoT for non-METAR products or REMARKS.  
Do **not** emit `runwayState` for pin **2025-2** (removed in RC1) even if Guidance still mentions CLRD/SNOCLO/R88/R99.

---

## Conversion strategy

Pipeline placement: **stage 2** of the domain E2E flow ([README.md](README.md)
§End-to-end strategy). Prerequisites: TAC lint passed (or explicit quarantine path).
Output: IWXXM XML for the **vendored** year line, then [IWXXM_VALIDATION.md](IWXXM_VALIDATION.md).

### Decision order (every encode)

1. **Select product root** from the Product → IWXXM root table below (do not reuse METAR
   structure for TAF/SIGMET/…).
2. **Select profile:** `annex3` default; `iwxxm_us` only for national `extension` content.
3. **Match an official example pair** (`…/examples/{prefix}.{tac,xml}`) for overall shape.
4. **Apply TAC-to-XML-Guidance** token → nilReason / omission rules (tables below).
5. **Emit vocab `xlink:href`s** from `codes.wmo.int` using the URI family in the official
   example for that product (usually `306/4678/{TAC}` for weather; `common/nil` for classic
   F6 nils; `iwxxm/*` when XSD `vocabulary=` says so).
6. **Respect pin schema deletions** (e.g. no `runwayState` on 2025-2) even if Guidance lags.
7. **On convert failure:** emit minimum quarantine shell + `@translationFailedTAC` (see
   official `*-translation-failed` examples) — do not invent a half-valid product body.
8. **Validate** with `iwxxm-validate` against vendor XSD+SCH before treating output as ready.

### Encode vs validate vs Annex 3

| Concern | Belongs in | Not in conversion |
|---------|------------|-------------------|
| SPECI/TAF **when** to issue | `tac-validate` / Annex 3 | — |
| Token → element / nilReason | **here** (Guidance + examples) | — |
| Required XSD elements / types | Product XSD (checked post-encode) | Do not re-implement as ad-hoc XML |
| Schematron business rules | `iwxxm-validate` | Do not duplicate SCH in encode |
| Dual TAC+IWXXM dissemination obligation | Annex 3 (ops) | Encoding recipes stay WMO pin |

### Golden-corpus strategy

| Priority | Source | Use |
|----------|--------|-----|
| **P0** | Official `schemas.wmo.int/iwxxm/2025-2/examples/` TAC+XML pairs | CI convert golden; structure SoT |
| **P1** | Same dir `TAC-to-XML-Guidance.txt` | nilReason / omission cookbook |
| **P2** | `iwxxm-translation` Amd79-80-2023 TAC inputs | Informative regression (METAR/TAF/VAA/TCA only) — convert to **pin 2025-2**, then XSD+SCH; **no** XML byte-match to suite’s **2023-1** fixtures ([parity dig](mining/iwxxm-translation-parity-mining-notes.md) · #797) |
| **P3** | AWC Data API `format=iwxxm` | Live smoke only — not encode SoT |

### Product encode playbook (F6 quick apply)

| Product | Structure SoT | Token / nil SoT | Post-encode |
|---------|---------------|-----------------|-------------|
| METAR / SPECI | `metar-A3-*` / `speci-A3-*` | Guidance METAR tables; no `runwayState` on 2025-2 | `metarSpeci.xsd` + SCH |
| TAF | `taf-A5-1` / cancel `taf-A5-2` | CNL/`isCancelReport`; `VV///` **absent** (≠ METAR) | `taf.xsd` + SCH |
| SIGMET / AIRMET | `sigmet-A6-*` / `airmet-A6-*` | SigWx / AirWx hrefs; volume helpers | `sigmet.xsd` / `airmet.xsd` + SCH |
| VAA | `va-advisory-A7-2` | Colour → registry; UNKNOWN/NOT GIVEN/NIL → Guidance nils; METCE `Volcano` | `volcanicAshAdvisory.xsd` + SCH |
| TCA | `tc-advisory-A2-2` | Issue gate ≥34 kt is **TAC** concern; CB NIL → `missing`; METCE `TropicalCyclone` | `tropicalCycloneAdvisory.xsd` + SCH |
| US METAR/SPECI | Official WMO body + **iwxxm-us** examples | FMH RMK → `extension` only | WMO pin + iwxxm-us catalogs |

**Apply after TAC lint checklists:** [TAC_VALIDATION.md](TAC_VALIDATION.md) A3-2 / A5-1 /
A6 / A2-1 / A2-2 tables gate **shape**; this playbook gates **encode**.

**VAA colour encode (do not invent hrefs):**

| TAC colour token | Encode |
|------------------|--------|
| RED / ORANGE / YELLOW / GREEN | `http://codes.wmo.int/iwxxm/AviationColourCode/{…}` |
| UNKNOWN / NOT GIVEN / NIL | Registry UNASSIGNED and/or `nilReason` per Guidance + official VAA examples — **never** invent a colour concept URI |

### Quarantine / partial-translation strategy

On convert failure (OPMET Guidelines §5.3.3 + official `*-translation-failed` examples):

| Rule | Detail |
|------|--------|
| Emit | Product-typed IWXXM **shell** (no invented MET body) + original TAC on `@translationFailedTAC` |
| Min identity | Product type (+ COR/AMD where applicable) + CCCC + time (METAR/TAF); SIGMET/AIRMET: CCCC + VALID; VAA: DTG+VAAC; TCA: DTG+TCAC — see Guidelines dig |
| `permissibleUsage` | Prefer `OPERATIONAL` when test/exercise mapping is uncertain so humans can recover TAC |
| Then | Still attempt XSD (shell) / SCH min-field asserts; do not pretend a full valid product |

Full Guidance paraphrase tables: §Conversion highlights below.

---

## Primary public landings

| Resource | URL | Label |
|----------|-----|-------|
| Schema publish root | https://schemas.wmo.int/iwxxm/2025-2/ | normative-schema |
| METCE foundation (TC/VA types) | https://schemas.wmo.int/metce/1.2/ | normative-schema — [mining](mining/schemas-wmo-int-metce-mining-notes.md) |
| OPM foundation (observable-property scaffolding) | https://schemas.wmo.int/opm/1.2/ | normative-schema — transitive via METCE Process only; **not** F6 encode SoT — [mining](mining/schemas-wmo-int-opm-mining-notes.md) |
| SAF (Simple Aeronautical Features) | https://schemas.wmo.int/saf/ | **historical** — IWXXM **1.x** aerodrome/airspace only; obsolete since 2.0RC1; pin **2025-2** uses **AIXM 5.1.1** via `common.xsd` — do **not** emit `saf:` — [mining](mining/schemas-wmo-int-saf-mining-notes.md) |
| GitHub source (tag v2025-2) | https://github.com/wmo-im/iwxxm | normative-schema |
| TAC→XML guidance | https://github.com/wmo-im/iwxxm/blob/v2025-2/IWXXM/examples/TAC-to-XML-Guidance.txt | normative-conversion-notes |
| Examples directory | https://schemas.wmo.int/iwxxm/2025-2/examples/ | normative-examples |
| Codes registry | https://codes.wmo.int/ | normative-vocabulary |
| FM 205 Manual I.3 | https://library.wmo.int/idurl/4/35769 | normative |
| FM 205 working AsciiDoc (pin) | `vendor/schemas/iwxxm/documentation/manual/FM205.adoc` (**FM 205-2025-2**) | normative-conversion-notes (package-aligned) |
| AHL headings | https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/wmo-information-system-wis/about-manual-gts/ahls-aviation-data-over-icao-afs | normative-exchange |
| WIS2 aviation publish (ops) | https://github.com/wmo-im/wis2-cookbook (`publishing-aviation-data.adoc`) · https://github.com/wmo-im/wis2-guide §2.8.1.1 · WTH https://github.com/wmo-im/wis2-topic-hierarchy | informative / normative-exchange (topics) — [Tier B](mining/wmo-im-tier-b-mining-notes.md) |
| Community IWXXM + compatibility table | https://community.wmo.int/en/activity-areas/wis/iwxxm (**404** 2026-07-14 — see catalog) | informative index |
| Extra fixtures | https://github.com/wmo-im/iwxxm-translation | informative — tip Amd79-80-2023 / suite IWXXM **2023-1**; [parity dig](mining/iwxxm-translation-parity-mining-notes.md) |
| Live TAC/IWXXM (US centre) | https://aviationweather.gov/data/api/ | informative — [mining](mining/awc-data-api-mining-notes.md) |
| US extensions | https://nws.weather.gov/schemas/iwxxm-us/3.0/ | normative-schema (national) |
| PPT-02 IWXXM Framework (workshop) | https://www.icao.int/filebrowser/download/26741?fid=26741 | informative |
| OPMET IWXXM Exchange Guidelines (5th Ed.) | https://www.icao.int/sites/default/files/METP/Documents/Guidlines-for-the-Implementation-of-OPMET-Data-Exchange-using-IWXXM_5th-Edition.pdf | normative-exchange |
| ICAO APAC IWXXM FAQs (3rd Ed., Mar 2025) | https://www.icao.int/sites/default/files/APAC/Documents/edocs/MET/2025-03_IWXXM-FAQs_3rd-Ed.pdf | informative — NSC/cloud, `translationFailedTAC`, translationCentre, COLLECT; [mining](mining/icao-apac-iwxxm-faqs-3rd-2025-mining-notes.md) · #797 |
| EUR Doc 014 SIGMET/AIRMET Guide (5th Ed. 2023) | https://www.icao.int/sites/default/files/EURNAT/Documents/EUR%20and%20Nat%20Docs/EUR%20Documents/EUR%20Documents/014%20-%20EUR%20SIGMET%20and%20AIRMET%20Guide/EUR-Doc-14-EN-5th-Ed-2023-rev-Dec23-clean.pdf | normative-conversion-notes (regional TAC/AHL; [mining](mining/icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md)) |

Local vendor mirrors: `vendor/schemas/iwxxm`, `iwxxm-modelling` (UML generators only), `iwxxm-translation`, `iwxxm-us`.

---

## Product → IWXXM root & package (2025-2)

| TAC product | IWXXM root | XSD | Package ver (2025-2) | Official example prefix |
|-------------|------------|-----|----------------------|-------------------------|
| METAR | `iwxxm:METAR` | `metarSpeci.xsd` | 3.2.0 | `metar-A3-1` |
| SPECI | `iwxxm:SPECI` | `metarSpeci.xsd` | 3.2.0 | `speci-A3-2` |
| TAF | `iwxxm:TAF` | `taf.xsd` | 3.0.2 | `taf-A5-1` / cancel `taf-A5-2` |
| SIGMET | `iwxxm:SIGMET` | `sigmet.xsd` | 4.0.2 | `sigmet-A6-1a-TS` |
| SIGMET TC | `iwxxm:TropicalCycloneSIGMET` | `sigmet.xsd` | 4.0.2 | `sigmet-A6-2-TC` |
| SIGMET VA | `iwxxm:VolcanicAshSIGMET` | `sigmet.xsd` | 4.0.2 | `sigmet-VA-EGGX` |
| AIRMET | `iwxxm:AIRMET` | `airmet.xsd` | 3.1.2 | `airmet-A6-1a-TS` |
| TCA | `iwxxm:TropicalCycloneAdvisory` | `tropicalCycloneAdvisory.xsd` | 3.1.1 | `tc-advisory-A2-2` |
| VAA | `iwxxm:VolcanicAshAdvisory` | `volcanicAshAdvisory.xsd` | 3.2.0 | `va-advisory-A7-2` |

Annex 3 amendment ↔ older package lineage (FM 205-2023-1.2.4) is tabulated in the mining notes; **runtime encode/validate against v2025-2**.  
ICAO Annex 3 (App 2/3/5/6) requires F6 products **shall** be exchanged in IWXXM GML **in addition to** TAC — it does **not** define nilReason / GML recipes ([mining/icao-annex-3-mining-notes.md](mining/icao-annex-3-mining-notes.md)). Table **A3-2** footnote (pass 2): temporarily missing TAC groups use `/` and must be marked missing in the IWXXM version — still resolve href/`nilReason` from Guidance + pin schemas.

---

## Conversion highlights (all F6)

Full tables: vendor `TAC-to-XML-Guidance.txt` + FM 205-2025-2 AsciiDoc. Summary below
(paraphrase only — prefer official Guidance wording when implementing).

### Shared (all reports)

| TAC / ops | IWXXM |
|-----------|-------|
| NORMAL / AMD / COR | `@reportStatus` = NORMAL \| AMENDMENT \| CORRECTION |
| Geometry | Horizontal CRS only; `srsName` + `srsDimension="2"` + non-empty `axisLabels` |
| Convert failure | `@translationFailedTAC` + minimum fields (see failed examples) |
| Sensor-failed quantities | `xsi:nil="true"`, `uom="N/A"`, `nilReason=…/notObservable` |

### METAR / SPECI

| TAC | IWXXM |
|-----|-------|
| NIL | empty observation + `…/nil/missing` |
| CAVOK | `@cloudAndVisibilityOK=true`; omit vis/RVR/weather/cloud |
| NSC | empty cloud + `nothingOfOperationalSignificance` — **do not** also emit layered cloud amount/base (APAC FAQ §14.3; #797) |
| NCD (AUTO) | empty cloud + `notDetectedByAutoSystem` |
| Missing present weather (no WX group) | Follow `TAC-to-XML-Guidance.txt` nil/omission; cross-check iwxxm-translation examples (FAQ §3.2) — prefer example URI family (`common/nil` vs `iwxxm/nil`) |
| NOSIG | trendForecast + `noSignificantChange` |
| NSW | weather + `nothingOfOperationalSignificance` |
| Present weather `//` | `notObservable` |
| `VV///` (obs, sensor fail) | verticalVisibility nil + `notObservable` |
| Cloud `//////` (± CB/TCU) | layer amount/base nil → `notObservable` or `notDetectedByAutoSystem` |
| Cloud amount `///hhh` / base `BBBxxx` gaps | amount or base nil with same nilReasons |
| Cloud type `///` (AUTO) | cloudType + `notObservable` |
| CLR / SKC (no CAVOK) | cloud base + `inapplicable` |
| RVR missing, vis < 1500 m, no sensors | empty `rvr` + `missing` + `xsi:nil` |
| RVR sensors inoperative, vis < 1500 m | empty `rvr` + `notObservable` + `xsi:nil` |
| Wind variation `dndnVdxdx` | map clockwise extreme → `extremeClockwiseWindDirection` (TAC `dxdxdx`) |
| BECMG/TEMPO trend without TL/AT/FM | phenomenonTime + `missing` (or `unknown` when uncertain) |
| Weather groups | prefer `http://codes.wmo.int/306/4678/{TAC}` hrefs |

⚠️ **Runway state** (`CLRD`, deposits, SNOCLO, R88/R99…): Guidance still mentions
`AerodromeRunwayState`, but **IWXXM 2025-2 RC1 removed** runway-state types from METAR —
**do not encode** for the current pin until model/guidance re-align.

### TAF

| TAC | IWXXM |
|-----|-------|
| CNL | `@isCancelReport=true` + `cancelledReportValidPeriod`; omit validPeriod / forecasts |
| NIL | empty `baseForecast` + `missing` |
| CAVOK / NSC / NSW | same nil/omit pattern as METAR (weather element name may differ) |
| `VV///` | verticalVisibility **absent** (no nilReason) — **differs from METAR** |
| TX/TN | max/min temperatures in pairs (Annex 3); may repeat a single extreme in both groups |

### Airspace volume (SIGMET / AIRMET geometry helpers)

| TAC | IWXXM (`aixm:AirspaceVolume`) |
|-----|------------------------------|
| Single level FLnnn / nnnnM / nnnnFT | same value in `lowerLimit` and `upperLimit` |
| TOP ABV FLnnn | `upperLimit=nnn`; `maximumLimit` nil + `unknown` |
| TOP BLW FLnnn | `upperLimit` nil + `unknown`; `maximumLimit=nnn` |

### SIGMET / AIRMET

| TAC | IWXXM |
|-----|-------|
| Phenomenon | `phenomenon/@xlink:href` → SigWxPhenomena / AirWxPhenomena |
| CNL | `@isCancelReport=true` + cancelled seq/period; omit phenomenon + analysis |
| STNR | `speedOfMotion=0`; direction `inapplicable` |
| Single point | `gml:CircleByCenterPoint` radius **0** |
| NO VA EXP | empty VA member + `nothingOfOperationalSignificance` |
| Prefer polygon TAC; “S OF” / “W OF” / “ENTIRE FIR” | Close geometry with FIR boundary intersection when Annex 3 allows relative phrases (APAC FAQ §3.3; wiki [Geospatial objects in IWXXM](https://github.com/wmo-im/iwxxm/wiki/Geospatial-objects-in-IWXXM) — `issuingAirTrafficServicesRegion` / FIR as `aixm:Airspace` + optional `gml:PolygonPatch`) — engine deepen tracked under #797 / #738 |

### TCA / VAA

| Product | Key encodings |
|---------|----------------|
| TCA | Issue when forecast max 10-min mean wind ≥ **34 kt** (Annex 3 App 2 §5.1.1); Table **A2-2**. Encode: `UNNAMED`; NIL CB → `cumulonimbusCloudLocation` + `missing`; NIL remarks / `NO MSG EXP` → `inapplicable`; wind < 34 kt forecast → `nothingOfOperationalSignificance`; no-longer-TC position → `inapplicable`; cyclone via **`metce:TropicalCyclone`** |
| VAA | Table **A2-1** + §3.1.2 shall IWXXM. Colour → `iwxxm/AviationColourCode/{GREEN\|YELLOW\|ORANGE\|RED\|UNASSIGNED}` (TAC UNKNOWN/NOT GIVEN/NIL → registry/nilReason per Guidance — **no** invented colour hrefs); MetFeature ash → `iwxxm/MeteorologicalFeature/VOLCANIC_ASH` when vocabulary requires it (**not** present on `49-2/MeteorologicalFeature` — [codes dig](mining/codes-wmo-int-aviation-mining-notes.md)); UNKNOWN/UNNAMED volcano; unknown location/elev/state/eruptionDetails → `unknown`; NIL remarks / no further advisories → `inapplicable`; ash OBS/FCST status enums; volcano via **`metce:Volcano`** (`VolcanoPropertyType` on 2025-2) |
| SIGMET TC / VA | Same METCE types on `tropicalCyclone` / `eruptingVolcano` properties in `sigmet.xsd` |

### Space weather (beyond F6 core — informative)

Present on **2025-2** (`spaceWxAdvisory.xsd`). Guidance: `DAYSIDE` → sub-solar
`CircleByCenterPoint` (~10100 km radius); `NO SWX EXP` / `NOT AVBL` / NIL remarks /
`NO FURTHER ADVISORIES` nil patterns. Not an F6 release gate unless ops expands scope.

Nil URI note: guidance/FM tables often use **`http://codes.wmo.int/common/nil/...`**; IWXXM examples also use **`iwxxm/nil`**. Prefer pin-aligned examples + Schematron; avoid over-using only `missing`.

---

## Codelist consumers already in-repo (evidence)

| Consumer | Usage |
|----------|--------|
| `packages/tac2iwxxm` | `common/nil/missing`; CloudAmount; SigWx / AirWx (`profiles/annex3*.py`) |
| Vendor RDF | Offline snapshots for Schematron |
| Backend helper | Optional online `codes.wmo.int` (`codelist_parser.py`) |

**Known encode gaps vs guidance:** aviation nilReasons (NOSIG/NSC/NSW/NCD/notObservable) often stubbed as `missing` — see #719 comments / coverage matrix.

---

## US profile creation

| Resource | URL |
|----------|-----|
| iwxxm-us schemas | https://nws.weather.gov/schemas/iwxxm-us/3.0/ |
| US examples | https://nws.weather.gov/schemas/iwxxm-us/3.0/examples/ |
| FMH-1 REMARKS | https://www.icams-portal.gov/resources/ofcm/fmh/FMH1/fmh1_2019.pdf · [mining](mining/fmh1-2019-mining-notes.md) |

Encode national content in IWXXM **`extension`** blocks per MDL / iwxxm-us — do not invent elements in the ICAO namespace.

**FMH-1 encode hints (profile `iwxxm_us` only):**

| TAC (US) | Encode stance |
|----------|---------------|
| Body units SM / FT / KT / `Axxxx` | Parse with US unit rules; GML quantities still use pin UOMs |
| Missing body group | FMH omits group — do **not** invent Annex 3 `/` nilReasons for absent US groups |
| `RMK …` (§12.7) | **Never drop**; map additive/plain remarks into **iwxxm-us** `extension` (AO1/AO2, SLP, `T…`, `$`, PK WND, …) |
| SKC / CLR | US clear-sky tokens — not interchangeable with NSC/NCD without profile rules |

**Structured `RMK` → iwxxm-us elements (vendored 3.0):**

| Prefer element | When TAC has |
|----------------|--------------|
| `observingSystemType` | AO1 / AO2 → `codes.nws.noaa.gov/FMH-1/ObservingSystemType` |
| `AerodromePeakWind` | PK WND |
| `AerodromeVariableRVR` | Variable RVR body group `R…/minVmax` (FT); meanRVR withheld (`nilReason` withheld) — S032 / #810 |
| `VisuallyObservablePhenomena` / `ObservedLightning` | FMH-1 lightning REMARKS (`LTG` / `OCNL|FRQ|CONS` + type + `DSNT|VC` + sector) — S032 / #811 |
| `SnowIncrease` / `InoperativeSensors` / `FailedSensors` | FMH-1 `SNINCR ii/dd` + sensor-NO (`CHINO`/`RVRNO`/…) — S032 / #812 |
| `AerodromeWindShift` | WSHFT |
| `pressureChangeIndicator` | PRESRR / PRESFR |
| `seaLevelPressure` | SLPppp / SLPNO |
| `snowDepth` / `snowIncrease` | snow depth / SNINCR |
| `maxMinTemperatures` | FMH-1 additive ``1snTTT`` / ``2snTTT`` (6-h) · ``4snTTTsnTTT`` (24-h) — S032/M4.5 |
| `processedQuantity` | precip additive ``Prrrr`` / ``6RRRR`` / ``7R24…`` (+ statistical codelist hrefs) — S032/M4.5 |
| `pressureTendency*` | additive ``5appp`` families (residual / deepen) |
| `maintenanceIndicator` | `$` |
| `Remarks` / `humanReadableText` | anything else kept verbatim |

Validate US output with **combined** WMO pin + iwxxm-us catalogs
([IWXXM_VALIDATION.md](IWXXM_VALIDATION.md)). Full token inventory:
[mining/fmh1-2019-mining-notes.md](mining/fmh1-2019-mining-notes.md).

GIFTs stripping REMARKS is a **historical gap**, not allowed behavior for `iwxxm_us`.

---

## Translation metadata (OPMET centres)

When emitting translation-centre attributes, align with **published** Doc 10003 / project guide + pin schema:

- **Machine SoT:** vendored `common.xsd` attrs on IWXXM **v2025-2**: `reportStatus`, `permissibleUsage` (+ optional `permissibleUsageReason` / `permissibleUsageSupplementary`), `translatedBulletinID`, `translatedBulletinReceptionTime`, `translationCentreDesignator`, `translationCentreName`, `translationTime`, `translationFailedTAC`
- **Official quarantine goldens:** `vendor/schemas/iwxxm/IWXXM/examples/*-translation-failed.xml` (METAR/TAF/AIRMET/VAA/TCA/SWX + `sigmet-translation-failed-collect`) — each sets the full translation* attr set above with `@translationFailedTAC` holding the original TAC shell (no MET body). Use as encode shape SoT; fictional `YUZZ` / `TTAAiiCCCYYGGgg` are placeholders.
- **Public ops SoT:** [OPMET IWXXM Exchange Guidelines 5th Ed.](mining/OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md) — Translation Centre bulletin basis (§4.1.3 / §5.3); identify centre + translation time when translating; `permissibleUsage` TEST/EXERCISE rules; partial-translation shell + min fields (§5.3.3); COLLECT aggregation + UUIDv4 `gml:id` guidance (§5.2)
- **APAC FAQ (informative, Mar 2025):** [mining/icao-apac-iwxxm-faqs-3rd-2025-mining-notes.md](mining/icao-apac-iwxxm-faqs-3rd-2025-mining-notes.md) — reinforce: do **not** put operational TAC in XML comments (§4.1); on unreliable convert use `@translationFailedTAC` (§8.6); emit `translationCentreDesignator` / `translationCentreName` only when translating **on behalf of another State** (§14.5) — omit for in-State producer self-translate; multi-version COLLECT must declare `http://icao.int/iwxxm/{version}` per group (§14.7). Engine/ops backlog: #797. Same no-partial-translate rule appears in Manual I.3 FM 205-16 (p.166) and FM 205-2018 Report (p.222) — [historical dig](mining/WMO-306-vI-3-2019-upd-2021-mining-notes.md) · #798.
- In-repo ops guide: [ICAO_OPMET_COMPLIANCE.md](iwxxm/ICAO_OPMET_COMPLIANCE.md) (cites Doc 10003 §7 — **not** present in Advance 2014 draft; Guidelines §7 is ROC/RODB *exchange* stats — complementary)
- Doc 10003 store: https://store.icao.int/en/manual-on-the-icao-meteorological-information-exchange-model-doc-10003 (**paywall**)
- Lineage / FAQ only: [mining/ICAO-Doc-10003-draft-2014-mining-notes.md](mining/ICAO-Doc-10003-draft-2014-mining-notes.md) — early ROC convert-at-centre FAQ; Ch.5 metadata empty
- Workshop reminder (informative): [PPT-02…](mining/PPT-02-IWXXM-Framework-WMO-mining-notes.md) — set translation attrs when a **third party / ROC** translates TAC→IWXXM; **omit** them when the producing organization translates itself. Slide 9 example retains failed TAC in `translationFailedTAC` (e.g. `METAR YUDO 221630Z INVALID`) and uses placeholder bulletin id `TTAAiiCCCYYGGgg`.

### Schema capacity vs TAC template (informative)

PPT-02 (2025-10-22) notes that some IWXXM reports can carry more than classic TAC templates allow (e.g. METAR **>4 RVRs**, temperature to **0.1 °C**, SIGMET polygons **>7 points**). New products may be **IWXXM-only** (no TAC path): WAFS Significant Weather Forecast, Quantitative Volcanic Ash (QVA) Concentration Information (and VONA on the 2025-2 package line). Encode against **XSD + official examples** for the pin; do not clamp to TAC presentation limits when the message is native IWXXM or guidance permits richer content.

### Round-trip (IWXXM → TAC) — out of reference-set SoT

Official `examples/*.tac` + `*.xml` pairs and `TAC-to-XML-Guidance.txt` are **encode-direction** artifacts. There is **no** F6-wide WMO “XML-to-TAC Guidance” in the 2025-2 package. Do not invent a reverse SoT from AWC or GIFTs. Optional semantic compare of converter output against official XML is the supported regression path; any IWXXM→TAC round-trip remains **product-specific / out of domain release gate** until an authoritative reverse mapping is adopted.

APAC FAQ §8.3 (informative): TAC→IWXXM translation under agreement is allowed; **IWXXM→TAC is not permitted** when the original TAC from the source is available — aligns with “no reverse SoT” above.

### Package versions on supported lines (informative)

Deck + community Wayback compatibility table + vendor check (see [VERSION_SUPPORT_POLICY Appendix A](iwxxm/VERSION_SUPPORT_POLICY.md#appendix-a--package--iwxxm-line-matrix-informative); [Wayback dig](mining/community-wmo-iwxxm-wayback-mining-notes.md)): on **2025-2**, METAR/SPECI **3.2.0**, TAF **3.0.2**, SIGMET **4.0.2**, AIRMET **3.1.2**, TCA **3.1.1**, VAA **3.2.0**, SWX **3.1.0**, WAFS **1.2.0**, QVACI/VONA **1.0.0**; on **2023-1**, METAR/SPECI **3.1.0**, TAF **3.0.1**, SIGMET **4.0.1**, … (QVACI/VONA absent).

---

## Suggested encode citation block (for #693 docs)

```text
Product: {METAR|…}
Profile: annex3 | iwxxm_us
IWXXM line: 2025-2 (vendor/manifest.json)
Structure SoT: schemas.wmo.int/iwxxm/2025-2/examples/{pair}
Token mapping: TAC-to-XML-Guidance.txt + FM 205-2025-2 (pin AsciiDoc) / examples
Vocabulary: codes.wmo.int/{…}
Validate output with: iwxxm-validate against vendor schemas (XSD + Schematron)
```

**Out of SoT:** product-wide **IWXXM→TAC** round-trip — no F6 official reverse cookbook;
some products are IWXXM-only (WAFS / QVA / VONA on the 2025-2 line).