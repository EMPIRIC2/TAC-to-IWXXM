# IWXXM creation (TAC → IWXXM) — rule sources

**Purpose:** Authoritative URLs and mappings for **creating** IWXXM XML from TAC under F6 (`packages/tac2iwxxm`).  
**Ticket:** [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719) · feeds [#693](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/693).  
**Vendor pin:** `iwxxm` **v2025-2** · namespace `http://icao.int/iwxxm/2025-2`.

Companions: [ANNEX3_TAC_VALIDATION_SOURCES.md](../validation/ANNEX3_TAC_VALIDATION_SOURCES.md) (input rules) · [IWXXM_VALIDATION_SOURCES.md](./IWXXM_VALIDATION_SOURCES.md) (output checks) · [WMO-306-vI-3-2023-mining-notes.md](./WMO-306-vI-3-2023-mining-notes.md) · [PPT-02-IWXXM-Framework-WMO-mining-notes.md](./PPT-02-IWXXM-Framework-WMO-mining-notes.md) (informative workshop overview) · [ICAO-Doc-10003-draft-2014-mining-notes.md](./ICAO-Doc-10003-draft-2014-mining-notes.md) (historical Doc 10003 Advance 2014 — not encode SoT).

---

## SoT stack for encode (recommended order)

1. **Official examples** for structure + product roots — `https://schemas.wmo.int/iwxxm/2025-2/examples/`
2. **`TAC-to-XML-Guidance.txt`** for TAC token → nilReason / omission rules
3. **codes.wmo.int** for `xlink:href` / `nilReason` enumerations
4. **WMO-No. 306 Vol I.3 FM 205** (esp. 205-2018 tables) for NIL/CNL & requirements-class prose
5. **Product XSD** constraints for required elements/attrs
6. **iwxxm-us** only when profile = `iwxxm_us` (`extension` content)

Do **not** treat historical GIFTs as SoT for non-METAR products or REMARKS.

---

## Primary public landings

| Resource | URL | Label |
|----------|-----|-------|
| Schema publish root | https://schemas.wmo.int/iwxxm/2025-2/ | normative-schema |
| GitHub source (tag v2025-2) | https://github.com/wmo-im/iwxxm | normative-schema |
| TAC→XML guidance | https://github.com/wmo-im/iwxxm/blob/v2025-2/IWXXM/examples/TAC-to-XML-Guidance.txt | normative-conversion-notes |
| Examples directory | https://schemas.wmo.int/iwxxm/2025-2/examples/ | normative-examples |
| Codes registry | https://codes.wmo.int/ | normative-vocabulary |
| FM 205 Manual I.3 | https://library.wmo.int/idurl/4/35769 | normative |
| AHL headings | https://community.wmo.int/en/activity-areas/wis/iwxxm/ahl-icao-data | normative-exchange |
| Community IWXXM + compatibility table | https://community.wmo.int/en/activity-areas/wis/iwxxm | informative index |
| Extra fixtures | https://github.com/wmo-im/iwxxm-translation | informative |
| US extensions | https://nws.weather.gov/schemas/iwxxm-us/3.0/ | normative-schema (national) |
| PPT-02 IWXXM Framework (workshop) | https://www.icao.int/filebrowser/download/26741?fid=26741 | informative |

Local vendor mirrors: `vendor/schemas/iwxxm`, `iwxxm-translation`, `iwxxm-us`.

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

---

## Conversion highlights (all F6)

Full tables: `TAC-to-XML-Guidance.txt` + FM 205-2018 (mining notes). Summary:

### Shared

| TAC / ops | IWXXM |
|-----------|-------|
| NORMAL / AMD / COR | `@reportStatus` = NORMAL \| AMENDMENT \| CORRECTION |
| Geometry | Horizontal CRS; `srsName` + `srsDimension="2"` + `axisLabels` |
| Convert failure | `@translationFailedTAC` + minimum fields (see failed examples) |

### METAR / SPECI

| TAC | IWXXM |
|-----|-------|
| NIL | empty observation + `…/nil/missing` |
| CAVOK | `@cloudAndVisibilityOK=true`; omit vis/RVR/weather/cloud |
| NSC | empty cloud + `nothingOfOperationalSignificance` |
| NCD (AUTO) | empty cloud + `notDetectedByAutoSystem` |
| NOSIG | trendForecast + `noSignificantChange` |
| NSW | weather + `nothingOfOperationalSignificance` |
| Present weather `//` | `notObservable` |
| Sensor-failed quantities | `xsi:nil`, `uom=N/A`, `notObservable` |
| Weather groups | prefer `http://codes.wmo.int/306/4678/{TAC}` hrefs |

⚠️ **Runway state** (`CLRD`, deposits, SNOCLO…): guidance still mentions `AerodromeRunwayState`, but **IWXXM 2025-2 RC1 removed** runway-state types from METAR — **do not encode** for the current pin until model/guidance re-align.

### TAF

| TAC | IWXXM |
|-----|-------|
| CNL | `@isCancelReport=true` + `cancelledReportValidPeriod`; omit validPeriod / forecasts |
| NIL | empty `baseForecast` + `missing` |
| `VV///` | verticalVisibility **absent** (differs from METAR) |
| TX/TN | max/min temperatures in pairs |

### SIGMET / AIRMET

| TAC | IWXXM |
|-----|-------|
| Phenomenon | `phenomenon/@xlink:href` → SigWxPhenomena / AirWxPhenomena |
| CNL | `@isCancelReport=true` + cancelled seq/period; omit phenomenon + analysis |
| STNR | `speedOfMotion=0`; direction `inapplicable` |
| Single point | `gml:CircleByCenterPoint` radius **0** |
| NO VA EXP | empty VA member + `nothingOfOperationalSignificance` |

### TCA / VAA

| Product | Key encodings |
|---------|----------------|
| TCA | `UNNAMED`; remarks / nextAdvisoryTime nils; metce TropicalCyclone |
| VAA | colour → `iwxxm/AviationColourCode/{GREEN\|YELLOW\|ORANGE\|RED\|UNASSIGNED}`; unknown location/elev → `unknown` |

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
| FMH-1 REMARKS | https://www.icams-portal.gov/resources/ofcm/fmh/FMH1/fmh1_2019.pdf |

Encode national content in IWXXM **`extension`** blocks per MDL / iwxxm-us — do not invent elements in the ICAO namespace.

---

## Translation metadata (OPMET centres)

When emitting translation-centre attributes, align with **published** Doc 10003 / project guide + pin schema:

- **Machine SoT:** vendored `common.xsd` attrs (`translationCentreName`, `translationCentreDesignator`, `translationTime`, `translatedBulletinID`, `translatedBulletinReceptionTime`, `permissibleUsage`, …) on IWXXM **v2025-2**
- In-repo ops guide: [ICAO_OPMET_COMPLIANCE.md](./ICAO_OPMET_COMPLIANCE.md) (cites Doc 10003 §7 — **not** present in Advance 2014 draft; verify against purchased edition)
- Doc 10003 store: https://store.icao.int/en/manual-on-the-icao-meteorological-information-exchange-model-doc-10003 (**paywall**)
- Lineage / FAQ only: [ICAO-Doc-10003-draft-2014-mining-notes.md](./ICAO-Doc-10003-draft-2014-mining-notes.md) — early ROC convert-at-centre FAQ; Ch.5 metadata empty
- Workshop reminder (informative): [PPT-02…](./PPT-02-IWXXM-Framework-WMO-mining-notes.md) — set `translatedBulletinID` / `translationCentreName` (etc.) when a **third party / ROC** translates TAC→IWXXM; **omit** those attributes when the producing organization translates itself.

### Schema capacity vs TAC template (informative)

PPT-02 (2025-10-22) notes that some IWXXM reports can carry more than classic TAC templates allow (e.g. METAR **>4 RVRs**, temperature to **0.1 °C**, SIGMET polygons **>7 points**). Encode against **XSD + official examples** for the pin; do not clamp to TAC presentation limits when the message is native IWXXM or guidance permits richer content.

---

## Suggested encode citation block (for #693 docs)

```text
Product: {METAR|…}
Profile: annex3 | iwxxm_us
IWXXM line: 2025-2 (vendor/manifest.json)
Structure SoT: schemas.wmo.int/iwxxm/2025-2/examples/{pair}
Token mapping: TAC-to-XML-Guidance.txt + FM 205-2018 notes
Vocabulary: codes.wmo.int/{…}
Validate output with: iwxxm-validate against vendor schemas
```
