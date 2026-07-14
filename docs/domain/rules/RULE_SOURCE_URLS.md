# Rule source URL catalog

**Status:** living catalog (discovery from [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719)).  
**Updated:** 2026-07-14.  
**Vendor pin:** `vendor/manifest.json` → `iwxxm` **v2025-2**, `iwxxm-codelists` **49-2**, `iwxxm-us` **3.0**.

Thematic companions:

- [ANNEX3_TAC_VALIDATION_SOURCES.md](../validation/ANNEX3_TAC_VALIDATION_SOURCES.md) — Annex 3 / TAC validation
- [IWXXM_CREATION_SOURCES.md](../iwxxm/IWXXM_CREATION_SOURCES.md) — TAC→IWXXM creation
- [IWXXM_VALIDATION_SOURCES.md](../iwxxm/IWXXM_VALIDATION_SOURCES.md) — IWXXM XSD/Schematron
- [COVERAGE_MATRIX.md](./COVERAGE_MATRIX.md) · [ACCESS_AND_CITATION.md](./ACCESS_AND_CITATION.md)

---

## Record template

```text
### {title}
- Publisher:
- URL:                    # prefer permanent / landing that survives version bumps
- Stable concept pattern: # when applicable (codes.wmo.int, namespaces)
- Access:                 # public / register / paywall
- Applies to: products=[…]; profiles=[annex3|iwxxm_us]; role=[validation|conversion|iwxxm-validation]
- Gap vs GIFTs:
- Consumer: tac-validate | tac2iwxxm | iwxxm-validate | UI-decode | bulletin
- Label: normative | normative-vocabulary | normative-schema | …
- Caveats:
```

---

## 1. ICAO — Annex 3 & related manuals (TAC SARPs / practice)

### ICAO Annex 3 — Meteorological Service for International Air Navigation

- **Publisher:** ICAO
- **URL:** https://store.icao.int/en/annex-3-meteorological-service-for-international-air-navigation-1  
  (also listing: https://store.icao.int/en/annexes/annex-3)
- **Edition note:** 21st Edition, August 2025 (verify at store)
- **Access:** **paywall** (ICAO Store); do not redistribute PDF
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA]; profiles=[annex3]; role=[validation]
- **Gap vs GIFTs:** full TAC templates, observation criteria (SPECI), TAF change groups, SIGMET/AIRMET/advisory SARPs — GIFTs was METAR/SPECI-centric and REMARKS-stripped
- **Consumer:** `tac-validate` (primary), UI-decode citations
- **Label:** normative
- **Caveats:** WMO-No. 49 Vol II Parts I–II **discontinued** (2023) → use Annex 3 as SARPs SoT; see [ACCESS_AND_CITATION.md](./ACCESS_AND_CITATION.md)

### ICAO Doc 8896 — Manual of Aeronautical Meteorological Practice

- **Publisher:** ICAO
- **URL:** https://store.icao.int/en/manual-of-aeronautical-meteorological-practice-doc-8896
- **Access:** **paywall**
- **Applies to:** products=[all F6]; profiles=[annex3]; role=[validation]
- **Gap vs GIFTs:** practice guidance for SIGMET harmonization, TCA, OPMET in IWXXM GML form
- **Consumer:** `tac-validate`, UI-decode
- **Label:** normative (practice manual)
- **Caveats:** complements Annex 3; cite chapters, do not mirror text

### ICAO Doc 10003 — Manual on the Digital Exchange of Aeronautical Meteorological Information

- **Publisher:** ICAO
- **URL:** https://store.icao.int/en/manual-on-the-icao-meteorological-information-exchange-model-doc-10003
- **Access:** **paywall**
- **Applies to:** products=[all]; profiles=[annex3]; role=[conversion, iwxxm-validation]
- **Gap vs GIFTs:** translation-centre / IWXXM exchange prose (see also in-repo [ICAO_OPMET_COMPLIANCE.md](../iwxxm/ICAO_OPMET_COMPLIANCE.md))
- **Consumer:** ops / `tac2iwxxm` metadata attrs; `#699` pointer only for prose
- **Label:** normative

### ICAO Doc 9766 — Handbook on the International Airways Volcano Watch (IAVW)

- **Publisher:** ICAO
- **URL:** ICAO Store search “9766” (store landing varies by edition)
- **Access:** **paywall** / member channels
- **Applies to:** products=[VAA]; role=[validation, conversion]
- **Advice:** AviationColourCode registry already public: https://codes.wmo.int/iwxxm/AviationColourCode
- **Consumer:** `tac2iwxxm`, UI-decode
- **Label:** normative (colour meanings); use registry for machine IDs

---

## 2. WMO Manual on Codes & technical regs

### WMO-No. 306 Vol. I.1 — Manual on Codes (alphanumeric / Part A)

- **Publisher:** WMO
- **URL:** https://library.wmo.int/idurl/4/35713  
  (record: https://library.wmo.int/records/item/35713-manual-on-codes-volume-i-1-international-codes)
- **Access:** WMO e-Library (often captcha); public catalog; **do not commit PDF**
- **Applies to:** products=[METAR,SPECI,TAF,…]; profiles=[annex3]; role=[validation]
- **Gap vs GIFTs:** FM templates / Code Table **4678** significant weather (canonical TAC weather IDs)
- **Consumer:** `tac-validate`, `tac2iwxxm` (href `http://codes.wmo.int/306/4678/{TAC}`)
- **Label:** normative
- **Machine vocabulary mirror:** https://codes.wmo.int/306/4678

### WMO-No. 306 Vol. I.3 (2023) — Manual on Codes Part D / FM 205 IWXXM

- **Publisher:** WMO
- **URL:** https://library.wmo.int/idurl/4/35769
- **Access:** WMO e-Library (captcha friction)
- **Applies to:** products=[all F6]; profiles=[annex3]; role=[conversion]
- **Gap vs GIFTs:** printed requirements classes for TAF/SIGMET/AIRMET/TCA/VAA NIL–CNL + packages
- **Consumer:** `tac2iwxxm`, `iwxxm-validate` (prose ↔ schema)
- **Label:** normative
- **Working notes:** [WMO-306-vI-3-2023-mining-notes.md](../iwxxm/WMO-306-vI-3-2023-mining-notes.md)
- **Caveats:** FM **205-2023-1** defers machine detail to online schemas (often **2023-1**); runtime pin is **2025-2**

### WMO-No. 49 Vol. II — Meteorological Service for International Air Navigation

- **Publisher:** WMO (historical)
- **Discontinuation:** https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/aviation/two-stage-discontinuation-of-technical-regulations-wmo-no-49-volume-ii-meteorological-service
- **Access:** Parts I–II discontinued **31 Dec 2023** → **use ICAO Annex 3**
- **Applies to:** role=[validation] (historical cite only)
- **Label:** historical (SARPs moved to Annex 3)
- **Caveat:** Linked Data register path **`49-2`** on codes.wmo.int remains the **vocabulary** namespace — distinct from the discontinued regulation text

### WMO aviation resource hub

- **URL:** https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/aviation/aviation-resources-technical-regulations-guidance-and-other-reference-materials
- **Role:** landing for current regs / Annex 3 pointers
- **Label:** informative index

---

## 3. WMO Codes Registry (vocabularies)

### codes.wmo.int (root)

- **Publisher:** WMO Codes Registry
- **URL:** https://codes.wmo.int/
- **Stable concept pattern:** `http://codes.wmo.int/{register}/{…}/{notation}`
- **Access:** public Linked Data (TTL/RDF/XML/JSON-LD/CSV); no registration
- **Applies to:** products=[all F6]; profiles=[annex3, iwxxm_us]; role=[validation, conversion]
- **Gap vs GIFTs:** machine enumerations + nilReasons GIFTs did not systematically encode
- **Consumer:** `tac-validate`, `tac2iwxxm`, `iwxxm-validate`, UI-decode
- **Label:** normative-vocabulary
- **Offline:** `vendor/schemas/iwxxm/IWXXM/rule/codes.wmo.int-*.rdf` + bundle `iwxxm-codelists`

### IWXXM register (`_iwxxm`)

- **URL:** https://codes.wmo.int/iwxxm
- **Stable pattern:** `http://codes.wmo.int/iwxxm/{AviationColourCode|MeteorologicalFeature|nil}/{notation}`
- **Access:** public
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA]; role=[validation, conversion]
- **Gap vs GIFTs:** VAA colour + MetFeature; aviation nils (NOSIG/NSC/NSW/NCD)
- **Consumer:** `tac2iwxxm`, `iwxxm-validate`, UI-decode
- **Label:** normative-vocabulary
- **Caveats:** Prefer **`iwxxm/AviationColourCode`** over `49-2/AviationColourCode` for 2025-2; prefer example-aligned **`iwxxm/nil`** vs converter’s current `common/nil/missing`; `RESUSPENDED_VOLCANIC_ASH` cited in some XSD docs but **404** on registry (2026-07-14)

### WMO No. 49 Vol II code lists (`49-2`)

- **URL:** https://codes.wmo.int/49-2
- **Key subregisters:**
  - https://codes.wmo.int/49-2/AerodromePresentOrForecastWeather
  - https://codes.wmo.int/49-2/AerodromeRecentWeather
  - https://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome
  - https://codes.wmo.int/49-2/SigConvectiveCloudType
  - https://codes.wmo.int/49-2/SigWxPhenomena
  - https://codes.wmo.int/49-2/AirWxPhenomena
  - https://codes.wmo.int/49-2/WeatherCausingVisibilityReduction
- **Access:** public
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET,AIRMET]; role=[validation, conversion]
- **Gap vs GIFTs:** SIGMET/AIRMET phenomena entire product; correct present-weather **concept IDs** often under **`306/4678/{TAC}`** even when vocabulary attr says `49-2/…`
- **Consumer:** `tac2iwxxm`, `tac-validate`, Schematron RDF
- **Label:** normative-vocabulary

### Common / nil / quantity-kind

- **URL:** https://codes.wmo.int/common · https://codes.wmo.int/common/nil
- **Access:** public
- **Applies to:** all products; role=[conversion, iwxxm-validation]
- **Label:** normative-vocabulary

### Code Table 4678 (significant weather)

- **URL:** https://codes.wmo.int/306/4678
- **Access:** public
- **Applies to:** METAR, SPECI, TAF (present/forecast weather hrefs)
- **Gap vs GIFTs:** URI pattern for weather groups (avoid tribal GIFTs hrefs)
- **Consumer:** `tac2iwxxm`
- **Label:** normative-vocabulary

---

## 4. IWXXM schemas, Schematron, guidance, examples

### wmo-im/iwxxm (source) + schemas.wmo.int (publish)

- **Publisher:** WMO TT-AvXML
- **URL:** https://github.com/wmo-im/iwxxm (tag **`v2025-2`**)  
  Publish: https://schemas.wmo.int/iwxxm/2025-2/
- **Namespace:** `http://icao.int/iwxxm/2025-2`
- **Access:** public HTTP + GitHub; no registration
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA,…]; profiles=[annex3]; role=[conversion, iwxxm-validation]
- **Gap vs GIFTs:** multi-product XSDs/examples/Schematron; runwayState **removed** in 2025-2 RC1
- **Consumer:** `tac2iwxxm`, `iwxxm-validate`, fixtures
- **Label:** normative-schema
- **Vendor:** `vendor/schemas/iwxxm`
- **Detail:** [IWXXM_VALIDATION_SOURCES.md](../iwxxm/IWXXM_VALIDATION_SOURCES.md)

### TAC-to-XML encoding guidance

- **URL:** https://github.com/wmo-im/iwxxm/blob/v2025-2/IWXXM/examples/TAC-to-XML-Guidance.txt  
  Also: https://schemas.wmo.int/iwxxm/2025-2/examples/
- **Access:** public
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA,SWX]; role=[conversion]
- **Gap vs GIFTs:** nilReason map for NOSIG/NSC/NSW/NCD/NIL/CNL/STNR/…
- **Consumer:** `tac2iwxxm`, `tac-validate`, UI-decode
- **Label:** normative-conversion-notes
- **Detail:** [IWXXM_CREATION_SOURCES.md](../iwxxm/IWXXM_CREATION_SOURCES.md)

### Official TAC↔IWXXM example pairs

- **URL:** https://schemas.wmo.int/iwxxm/2025-2/examples/
- **Access:** public
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA,VONA,SWX]; role=[conversion-fixtures, validation-fixtures]
- **Gap vs GIFTs:** CNL/NIL/collect/`translationFailedTAC` pairs; TC+VA SIGMET
- **Consumer:** golden encode/validate, e2e samples
- **Label:** normative-examples

### IWXXM AHL / bulletin headings

- **URL:** https://community.wmo.int/en/activity-areas/wis/iwxxm/ahl-icao-data
- **Access:** public
- **Applies to:** products=[all F6]; role=[bulletin-validation, conversion]
- **Gap vs GIFTs:** TAC T1T2 (`SA`/`SP`/…) ↔ IWXXM T1T2 (`LA`/`LP`/…) + AMHS filename pattern
- **Consumer:** `tac-validate`, bulletin encode, F8 worker
- **Label:** normative-exchange

### Sibling repos (already vendored)

| Repo | URL | Role | Label |
|------|-----|------|-------|
| iwxxm-codelists | https://github.com/wmo-im/iwxxm-codelists | RDF → codes.wmo.int | normative-vocabulary |
| iwxxm-modelling | https://github.com/wmo-im/iwxxm-modelling | UML / generation | informative (tooling) |
| iwxxm-translation | https://github.com/wmo-im/iwxxm-translation | Extra TAC/XML pairs + translator list | **informative** (README: no official WMO/ICAO status) |

### WMO community IWXXM home

- **URL:** https://community.wmo.int/en/activity-areas/wis/iwxxm  
  (short form often seen: https://community.wmo.int/iwxxm)
- **Access:** public
- **Applies to:** products=[all F6]; role=[iwxxm-validation, conversion] (index + **compatibility table** package×Annex 3)
- **Consumer:** F4 version policy, ops citations
- **Label:** informative index
- **Caveats:** Prefer this for human-readable amendment↔package tables; runtime validate against vendor pin **v2025-2**

### PPT-02 IWXXM Framework (ESAF workshop, TT-AvData)

- **Publisher:** WMO TT-AvData (B.L. Choy); ICAO ESAF workshop materials
- **URL:** https://www.icao.int/filebrowser/download/26741?fid=26741
- **Access:** public filebrowser (**Cloudflare challenge** for automated fetch); do not commit PDF
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA,WAFS,QVACI]; profiles=[annex3]; role=[conversion, iwxxm-validation, bulletin] (overview)
- **Gap vs GIFTs:** METAR >4 RVR / 0.1 °C; SIGMET >7 polygon points; IWXXM-only WAFS/QVA; ROC translation attrs; AMHS/FTBP + AHL
- **Consumer:** `tac2iwxxm`, `iwxxm-validate`, bulletin, UI-decode
- **Label:** **informative**
- **Caveats:** Workshop briefing — **not** encode/validate SoT; several slides are figures only. Local extract: `.local/reference/ppt-02-iwxxm-framework-wmo/`
- **Detail:** [PPT-02-IWXXM-Framework-WMO-mining-notes.md](../iwxxm/PPT-02-IWXXM-Framework-WMO-mining-notes.md)
- **Mined:** 2026-07-14 · pin v2025-2

---

## 5. National — US profile (FMH-1 / iwxxm-us)

### Federal Meteorological Handbook No. 1 (FMH-1)

- **Publisher:** OFCM / ICAMS
- **URL:** https://www.icams-portal.gov/resources/ofcm/fmh/FMH1/fmh1_2019.pdf  
  Index: https://www.icams-portal.gov/resources/ofcm/fmh/allfmh2.htm
- **Access:** public PDF (US federal handbook)
- **Applies to:** products=[METAR,SPECI]; profiles=[**iwxxm_us**]; role=[validation]
- **Gap vs GIFTs:** **entire REMARKS / US national content** (GIFTs stripped RMK)
- **Consumer:** `tac-validate` (US), `tac2iwxxm` extension map
- **Label:** normative (national)

### NWS Codes Registry — FMH-1 tables

- **URL:** https://codes.nws.noaa.gov/FMH-1
- **Access:** public Linked Data
- **Applies to:** profiles=[iwxxm_us]; role=[validation, conversion]
- **Label:** normative-vocabulary (national)

### United States’ Extensions to IWXXM (iwxxm-us 3.0)

- **Publisher:** NOAA / NWS MDL
- **URL:** https://nws.weather.gov/schemas/iwxxm-us/  
  Package: https://nws.weather.gov/schemas/iwxxm-us/3.0/  
  Examples: https://nws.weather.gov/schemas/iwxxm-us/3.0/examples/  
  Archive (vendor pin): https://nws.weather.gov/schemas/iwxxm-us/3.0/iwxxm-us-3.0-schemas.tgz
- **Namespace:** `http://www.weather.gov/iwxxm-us/3.0`
- **Access:** public
- **Applies to:** products=[AIRMET,METAR,SIGMET,SPECI,TAF] (FAA five); profiles=[**iwxxm_us**]; role=[conversion, iwxxm-validation]
- **Gap vs GIFTs:** US `extension` blocks; not in historical GIFTs
- **Consumer:** `tac2iwxxm`, `iwxxm-validate` (combined catalogs)
- **Label:** normative-schema (national)
- **MDL context:** https://vlab.noaa.gov/web/mdl/data-modeling
- **Vendor:** `vendor/schemas/iwxxm-us`

---

## 6. Historical GIFTs (gap baseline only)

- **Label:** historical-GIFTs
- **Role:** baseline of what was **not** covered (non-METAR F6, REMARKS, iwxxm-us, deep TAF CNL/NIL)
- **Do not** use as ongoing rule SoT (ADR-014 / F6 cutover)
- **Consumer:** gap columns in [COVERAGE_MATRIX.md](./COVERAGE_MATRIX.md) only

---

## What this catalog does *not* replace

| Need | Still elsewhere |
|------|-----------------|
| Full Annex 3 / Doc 8896 prose | Paywalled ICAO PDFs (cite only) |
| Active machine validation for pin | `vendor/schemas/iwxxm` + [IWXXM_VALIDATION_SOURCES.md](../iwxxm/IWXXM_VALIDATION_SOURCES.md) |
| Package API design | #698 / #699 |
| Converter implementation | #693 / `packages/tac2iwxxm` |

## Related tickets

| Ticket | Boundary |
|--------|----------|
| [#698](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/698) | TAC validation package — consumes this catalog |
| [#699](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/699) | IWXXM validation package — schema release pointers |
| [#693](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/693) | Converter — conversion citations |
| [#702](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/702) / [#714](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/714) | Decode / F7 UX provenance |
