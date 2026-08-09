# Rule source URL catalog

**Status:** living catalog (discovery from [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719)).  
**Updated:** 2026-07-30 (… · WMO-306 I.3 2019/upd-2021 dig **1–272 complete** · #798).  
**Vendor pin:** `vendor/manifest.json` → `iwxxm` **v2025-2**, `iwxxm-codelists` **49-2**, `iwxxm-us` **3.0**.

**Inventory pass:** [mining/iwxxm-2025-2-reference-set-mining-notes.md](../mining/iwxxm-2025-2-reference-set-mining-notes.md)

**How to apply URLs:**

1. Filter by **Applies to** (`products`, `profiles`, `role`).
2. Open the matching **canonical strategy** ([README.md](./README.md) role table + **apply playbooks**).
3. Prefer **public / machine** rows for CI; keep paywall rows cite-only.
4. On conflict → **defer to latest** pin (`vendor/manifest.json` / `schemas.wmo.int/iwxxm/<pin>/`).
5. GIFTs / AWC / translation extras never override Annex 3 or normative-schema.

Canonical companions:

- [TAC_VALIDATION.md](../TAC_VALIDATION.md) — TAC / Annex 3 validation
- [IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) — TAC→IWXXM conversion
- [IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) — IWXXM XSD/Schematron
- [COVERAGE_MATRIX.md](./COVERAGE_MATRIX.md) (incl. G1–G7 gates) · [ACCESS_AND_CITATION.md](./ACCESS_AND_CITATION.md) · [README.md](./README.md)
- Hub: [../README.md](../README.md) · Mining digs: [../mining/](../mining/)

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
- **Edition note:** Store may list **21st Edition, August 2025** — verify before citing. **Local dig (2026-07-14):** Twentieth Edition, July 2018 + amendments through **No. 81** (applicable 28 Nov 2024); `.local/reference/icao-annex-3/` (gitignored)
- **Access:** **paywall** (ICAO Store); do not redistribute PDF
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA]; profiles=[annex3]; role=[validation] (also frames dual TAC+**IWXXM GML** dissemination obligation → Doc 10003 / WMO-No. 306 Vol I.3 Part D for encoding)
- **Gap vs GIFTs:** full TAC templates (Tables A3-2 / A5-1 / A6-1A / A2-1/2), SPECI shall vs Rec thresholds (App 3 §2.3), CAVOK, TREND (2 h), TAF FM/BECMG/TEMPO/PROB, SIGMET/AIRMET phenomena+validity — GIFTs was METAR/SPECI-centric and REMARKS-stripped
- **Consumer:** `tac-validate` (primary), UI-decode citations
- **Label:** normative
- **Caveats:** WMO-No. 49 Vol II Parts I–II **discontinued** (2023) → use Annex 3 as SARPs SoT; see [ACCESS_AND_CITATION.md](./ACCESS_AND_CITATION.md). Foreword prose still linking Annex 3 to 49 Vol II is **historical** relative to that discontinuation. SPECI vs TAF Recommended vis steps are **not identical** — do not merge lint tables.
- **Mined:** 2026-07-14 (pass 2 deeper) · [mining/icao-annex-3-mining-notes.md](../mining/icao-annex-3-mining-notes.md)

### ICAO Doc 8896 — Manual of Aeronautical Meteorological Practice

- **Publisher:** ICAO
- **URL:** https://store.icao.int/en/manual-of-aeronautical-meteorological-practice-doc-8896
- **Access:** **paywall**
- **Applies to:** products=[all F6]; profiles=[annex3]; role=[validation]
- **Gap vs GIFTs:** practice guidance for SIGMET harmonization, TCA, OPMET in IWXXM GML form
- **Consumer:** `tac-validate`, UI-decode
- **Label:** normative (practice manual)
- **Caveats:** complements Annex 3; cite chapters, do not mirror text

### ICAO EUR Doc 014 — EUR SIGMET and AIRMET Guide (5th Ed. 2023)

- **Publisher:** ICAO EUR/NAT (EASPG METG)
- **URL:** https://www.icao.int/sites/default/files/EURNAT/Documents/EUR%20and%20Nat%20Docs/EUR%20Documents/EUR%20Documents/014%20-%20EUR%20SIGMET%20and%20AIRMET%20Guide/EUR-Doc-14-EN-5th-Ed-2023-rev-Dec23-clean.pdf
- **Landing:** http://www.icao.int/EURNAT/Pages/welcome.aspx (EUR Documents → 014 – EUR SIGMET and AIRMET Guide)
- **Access:** **public**
- **Applies to:** products=[SIGMET,AIRMET]; profiles=[annex3]; role=[validation, conversion, bulletin]
- **Gap vs GIFTs:** entire SIGMET/AIRMET products; AHL `WS`/`WV`/`WC`/`WA` ↔ IWXXM `LS`/`LV`/`LY`/`LW`; CNL; no `COR`; EUR TAC examples (App C)
- **Consumer:** `tac-validate`, `tac2iwxxm`, bulletin, UI-decode
- **Label:** normative-conversion-notes (regional guide; Annex 3 remains SARPs SoT)
- **Caveats:** Complements Annex 3 App 6 / Table A6-1A — do not override SARPs. IWXXM formatting defers to `schemas.wmo.int/iwxxm/<pin>/` (vendor manifest **v2025-2**). Space weather out of scope. EU Reg 2017/373 AMC sequence-number form is regional. Local extract: `.local/reference/icao-eur-doc-14-sigmet-airmet-2023/` (90/90 pages verified 2026-07-20).
- **Mined:** 2026-07-20 · [mining/icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md](../mining/icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md)

### ICAO Doc 10003 — Manual on the Digital Exchange of Aeronautical Meteorological Information

- **Publisher:** ICAO
- **URL:** https://store.icao.int/en/manual-on-the-icao-meteorological-information-exchange-model-doc-10003
- **Access:** **paywall**
- **Applies to:** products=[all F6 + ops]; profiles=[annex3]; role=[conversion, iwxxm-validation, bulletin]
- **Gap vs GIFTs:** translation-centre / IWXXM exchange prose (see also in-repo [ICAO_OPMET_COMPLIANCE.md](../iwxxm/ICAO_OPMET_COMPLIANCE.md))
- **Consumer:** ops / `tac2iwxxm` metadata attrs; `#699` pointer only for prose
- **Label:** normative
- **Caveats:** Cite the **published** edition for § translation-centre / ops prose. An Advance 2014 unedited draft (Amd 76 / IWXXM v1 era) was mined 2026-07-14 — local only under `.local/reference/icao-doc-10003-draft-en/`; tracked notes: [mining/ICAO-Doc-10003-draft-2014-mining-notes.md](../mining/ICAO-Doc-10003-draft-2014-mining-notes.md). That draft lacks §7, AIRMET/VAA/TCA, and COLLECT bulletins; do not use it as runtime SoT. For **public** AMHS/FTBP, COLLECT, partial-translation, and ROC validation-statistics implementation guidance, prefer [OPMET IWXXM Exchange Guidelines 5th Ed.](../mining/OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md) — complementary, not a substitute for Doc 10003.
- **Mined:** 2026-07-14

### ICAO Doc 10003 — Advance 2014 Edition (unedited draft)

- **Publisher:** ICAO (unedited advance)
- **URL:** store landing above (final); local extracts `.local/reference/icao-doc-10003-draft-en/` (gitignored)
- **Access:** draft PDF local-only; **not authoritative** (PDF p.1 notice)
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET]; profiles=[annex3]; role=[conversion, iwxxm-validation] (historical)
- **Gap vs GIFTs:** SWIM/IWXXM+SAF architecture; early present/recent-weather encode lists; ROC convert FAQ — no F6 advisories
- **Consumer:** design / lineage only (not CI validate pin)
- **Label:** informative / historical
- **Caveats:** Namespaces `icao.int/iwxxm/1.0RC2`; FAQ “no bulletin schema” superseded by COLLECT / `iwxxm-collect.xsd`
- **Mined:** 2026-07-14 · [mining/ICAO-Doc-10003-draft-2014-mining-notes.md](../mining/ICAO-Doc-10003-draft-2014-mining-notes.md)

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
- **Working notes:** [mining/WMO-306-vI-3-2023-mining-notes.md](../mining/WMO-306-vI-3-2023-mining-notes.md)
- **Caveats:** FM **205-2023-1** defers machine detail to online schemas (often **2023-1**); runtime pin is **2025-2**

### WMO-No. 306 Vol. I.3 (2019 ed., upd. 2021) — historical Part D PDF

- **Publisher:** WMO
- **URL:** WMO e-Library (ISBN 978-92-63-10306-2); standing cites prefer later 2023 entry https://library.wmo.int/idurl/4/35769
- **Access:** e-Library captcha / local PDF — **do not commit**
- **Applies to:** products=[all F6 + bulletin + SWX scope]; profiles=[annex3]; role=[conversion] (historical)
- **Gap vs GIFTs:** Full dig 1–272: COLLECT; METCE volcano/TC; IWXXM 1.1–3.0 NIL–CNL / NOSIG / field nilReasons; SAF→AIXM; AIRMET/TCA/VAA/SWX; `translationFailedTAC`; CRS 2-D; Extension; D-1…D-10 (4678 / SigWx / CloudAmount)
- **Consumer:** `tac2iwxxm`, `iwxxm-validate` (vocab landings), dissemination (COLLECT)
- **Label:** normative (historical)
- **Working notes:** [mining/WMO-306-vI-3-2019-upd-2021-mining-notes.md](../mining/WMO-306-vI-3-2019-upd-2021-mining-notes.md)
- **Caveats:** Dig **complete**; App B package map stops at IWXXM **3.0** — superseded by 2023 dig + vendor **v2025-2** / `FM205.adoc`; SAF = 1.1 lineage only; 2.1 NOSIG→`inapplicable` deferred vs pin `noSignificantChange`; 3.0 runway-state historical vs 2025-2 removal; prefer live codes.wmo.int / vendor RDF over printed bufr4 path quirks in D-8

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
- **Drift check (#859 / TC-EV038-008):** `make codelist-uri-drift` — SCH RDF ↔ CSV URI
  membership (non-flake); optional `--live` RDF (never HTML). Cadence + disposition:
  [RELEASE_LINE_ADOPTABILITY §codes.wmo.int URI drift](../iwxxm/RELEASE_LINE_ADOPTABILITY.md).
  Cite-ready URIs hand off to [#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889).
- **Refresh:** aviation inventory re-checked 2026-07-30 — [mining/codes-wmo-int-aviation-mining-notes.md](../mining/codes-wmo-int-aviation-mining-notes.md)
- **S055 / EV-046 (#889 Lean):** present/cite/cover —
  [codes-wmo-int-coverage.md](../../sessions/S055-wmo-aviation-registers/reports/codes-wmo-int-coverage.md);
  ISSUE_CATALOG weather/cloud/nil rows cite register landings; pin
  `vendor/manifest.json` → `iwxxm-codelists` tag `49-2`. **Validated** deferred to
  [#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959); compose
  [#859](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/859) /
  [#882](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/882).

### IWXXM register (`_iwxxm`)

- **URL:** https://codes.wmo.int/iwxxm
- **Stable pattern:** `http://codes.wmo.int/iwxxm/{AviationColourCode|MeteorologicalFeature|nil}/{notation}`
- **Access:** public Linked Data HTML (request with `Accept: text/html` — bare HEAD/GET without Accept may **404**)
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA]; role=[validation, conversion]
- **Gap vs GIFTs:** VAA colour + MetFeature; aviation nils (NOSIG/NSC/NSW/NCD)
- **Consumer:** `tac2iwxxm`, `iwxxm-validate`, UI-decode
- **Label:** normative-vocabulary
- **Caveats:** Prefer **`iwxxm/AviationColourCode`** over `49-2/AviationColourCode` for 2025-2; prefer example-aligned **`iwxxm/nil`** vs converter’s current `common/nil/missing`; **`iwxxm/MeteorologicalFeature/VOLCANIC_ASH`** is not on `49-2/` (live 2026-07-30); `RESUSPENDED_VOLCANIC_ASH` cited in some XSD docs but **404** on registry (2026-07-14)
- **Mined:** 2026-07-14 (Accept / link-check); member-set refresh 2026-07-30 — [codes dig](../mining/codes-wmo-int-aviation-mining-notes.md)

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
- **Access:** public Linked Data; HTML browse may show a **subset** (~101 links observed 2026-07-30)
- **Applies to:** METAR, SPECI, TAF (present/forecast weather hrefs)
- **Gap vs GIFTs:** URI pattern for weather groups (avoid tribal GIFTs hrefs)
- **Consumer:** `tac2iwxxm`, `tac-validate`
- **Label:** normative-vocabulary
- **Offline SoT:** `vendor/schemas/iwxxm-codelists/CSV/306/4678/4678_entity.csv` (**402** stable notations) + TTL entities under `TTL/306/4678/`
- **Caveats:** Prefer vendor CSV/RDF for membership gates; Manual on Codes wins if CSV ≠ Manual (codelists README); do not gate CI on live HTML count — [codes dig](../mining/codes-wmo-int-aviation-mining-notes.md)

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
- **Detail:** [IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md)

### TAC-to-XML encoding guidance

- **URL:** https://github.com/wmo-im/iwxxm/blob/v2025-2/IWXXM/examples/TAC-to-XML-Guidance.txt  
  Also: https://schemas.wmo.int/iwxxm/2025-2/examples/
- **Access:** public
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA,SWX]; role=[conversion]
- **Gap vs GIFTs:** nilReason map for NOSIG/NSC/NSW/NCD/NIL/CNL/STNR/…
- **Consumer:** `tac2iwxxm`, `tac-validate`, UI-decode
- **Label:** normative-conversion-notes
- **Detail:** [IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md)

### WMO METCE (foundation meteorology schema)

- **Publisher:** WMO
- **URL:** https://schemas.wmo.int/metce/  
  Runtime import used by IWXXM **v2025-2:** https://schemas.wmo.int/metce/1.2/metce.xsd
- **Stable concept pattern:** namespace `http://def.wmo.int/metce/2013`; package versions under `/metce/{1.0|1.1|1.2}/`
- **Access:** public
- **Applies to:** products=[SIGMET,VAA,TCA]; profiles=[annex3]; role=[iwxxm-validation, conversion]
- **Gap vs GIFTs:** TropicalCyclone / Volcano / EruptingVolcano feature types for advisories and TC/VA SIGMET — outside GIFTs METAR encoder
- **Consumer:** `tac2iwxxm`, `iwxxm-validate`
- **Label:** normative-schema
- **Caveats:** Prefer vendor `externalSchema/.../metce/1.2/` (published 1.2 content; XSD EOL differs CRLF vs LF). GitHub [wmo-im/metce](https://github.com/wmo-im/metce) is historical tip only. METCE Schematron (`rule/metce.sch`) covers MeasurementContext / RangeBounds — not cyclone/volcano naming. Historical docs may cite metce **1.0**; pin imports **1.2**.
- **Detail:** [mining/schemas-wmo-int-metce-mining-notes.md](../mining/schemas-wmo-int-metce-mining-notes.md)
- **Mined:** 2026-07-14 · METCE 1.2 · iwxxm pin v2025-2 · #719

### WMO OPM (Observable Property Model)

- **Publisher:** WMO
- **URL:** https://schemas.wmo.int/opm/  
  Runtime import used by METCE **1.2** (not by IWXXM product XSDs): https://schemas.wmo.int/opm/1.2/opm.xsd
- **Stable concept pattern:** namespace `http://def.wmo.int/opm/2013`; package versions under `/opm/{1.0|1.1|1.2}/`
- **Access:** public
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA]; profiles=[annex3]; role=[iwxxm-validation]
- **Gap vs GIFTs:** Observable-property scaffolding only — no `opm:` elements in classic F6 2025-2 examples
- **Consumer:** `iwxxm-validate`
- **Label:** normative-schema
- **Caveats:** Prefer vendor `externalSchema/.../opm/1.2/` (published 1.2 content; main XSDs EOL differs CRLF vs LF). GitHub [wmo-im/opm](https://github.com/wmo-im/opm) is **archived** historical tip. Do not use OPM as TAC→IWXXM encode SoT. `StatisticalFunctionCode` vocabulary is GRIB2 `codes.wmo.int/grib2/codeflag/4.10` (not IWXXM aviation lists). Published `OPM.COP1` Schematron assert XPath is malformed (`{if(...)}`). Historical docs may cite opm **1.0**; METCE pin path uses **1.2**.
- **Detail:** [mining/schemas-wmo-int-opm-mining-notes.md](../mining/schemas-wmo-int-opm-mining-notes.md)
- **Mined:** 2026-07-14 · OPM 1.2 · iwxxm pin v2025-2 · #719

### WMO SAF (Simple Aeronautical Features) — historical

- **Publisher:** WMO
- **URL:** https://schemas.wmo.int/saf/  
  Packages: https://schemas.wmo.int/saf/1.0/ · https://schemas.wmo.int/saf/1.1/  
  (**No** `/saf/1.2/`; **not** imported by IWXXM **v2025-2**)
- **Stable concept pattern:** namespaces `http://icao.int/saf/{1.0|1.1}`
- **Access:** public
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET,AIRMET] under IWXXM **1.x** only; profiles=[annex3]; role=[iwxxm-validation]
- **Gap vs GIFTs:** Historical aerodrome / runway / airspace / unit feature model — superseded before F6 pin
- **Consumer:** `iwxxm-validate` (lineage / IWXXM 1.x docs only)
- **Label:** historical
- **Caveats:** Obsolete since IWXXM **2.0RC1** (2016-04) per vendor README. Successor for pin **2025-2** = **AIXM 5.1.1** via `common.xsd` (`aixm:AirportHeliport` / `Airspace` / …) + Eurocontrol AIXM_WX profiling. Vendor XSD+SCH+ReleaseNotes **byte-identical** to publish; `examples/` published only (not in vendor embed). GitHub [wmo-im/saf](https://github.com/wmo-im/saf) **archived**. Do **not** emit `saf:` under current pin.
- **Detail:** [mining/schemas-wmo-int-saf-mining-notes.md](../mining/schemas-wmo-int-saf-mining-notes.md)
- **Mined:** 2026-07-14 · SAF 1.0–1.1 · iwxxm pin v2025-2 · #719

### OGC TimeseriesML (TSML) — schemas.wmo.int mirror

- **Publisher:** Open Geospatial Consortium (content); WMO hosts [schemas.wmo.int/tsml](https://schemas.wmo.int/tsml/)
- **URL:** https://schemas.wmo.int/tsml/  
  Package: https://schemas.wmo.int/tsml/1.0/  
  Prefer instance `schemaLocation`: http://schemas.opengis.net/tsml/1.0/timeseriesML.xsd
- **Stable concept pattern:** namespace `http://www.opengis.net/tsml/1.0`; requirements `http://www.opengis.net/spec/timeseriesml/1.0/req/…`
- **Access:** public
- **Applies to:** products=[]; profiles=[]; role=[] (**not** F6 `iwxxm-validation` / `conversion`)
- **Gap vs GIFTs:** N/A — hydrology/climate timeseries (TVP / DomainRange), not aviation TAC→IWXXM
- **Consumer:** none (discovery / non-F6 only)
- **Label:** normative-schema (OGC TimeseriesML 1.0)
- **Caveats:** Landing has **1.0 only** (OGC 15-042r3 → 1.0.0). IWXXM **v2025-2** does **not** import TSML; no vendor `externalSchema/.../tsml/`. Sampled XSD/SCH/examples are byte-identical to `schemas.opengis.net/tsml/1.0/`. Do not confuse TSML `PointMetadata/nilReason` with IWXXM aviation `codes.wmo.int` nils. Standard landing: [ogc.org/standards/tsml](https://www.ogc.org/standards/tsml/).
- **Detail:** [mining/schemas-wmo-int-tsml-mining-notes.md](../mining/schemas-wmo-int-tsml-mining-notes.md)
- **Mined:** 2026-07-14 · TSML 1.0 · iwxxm pin v2025-2 · #719

### WMO schemas.wmo.int/rule (centralized Schematron index)

- **Publisher:** WMO
- **URL:** https://schemas.wmo.int/rule/  
  Packages: https://schemas.wmo.int/rule/1.0/ · [1.1](https://schemas.wmo.int/rule/1.1/) · [1.2](https://schemas.wmo.int/rule/1.2/)
- **Stable concept pattern:** `/rule/{1.0|1.1|1.2}/*.sch` (package numbers — **not** IWXXM year lines)
- **Access:** public
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET] under 1.x `iwxxm.sch` only; METCE/OPM/COLLECT via `/rule/1.2/` mirror; profiles=[annex3]; role=[iwxxm-validation]
- **Gap vs GIFTs:** Historical IWXXM **1.0/1.1** pattern set (63 rules); no AIRMET/VAA/TCA/VONA/SWX; includes runway-state rules removed in 2025-2
- **Consumer:** `iwxxm-validate` (lineage / discovery only)
- **Label:** historical (`iwxxm.sch` / `saf.sch` under 1.0–1.1); normative-schema **mirror** only for `/rule/1.2/{metce,opm,collect}.sch`
- **Caveats:** **Do not** validate pin XML against `/rule/1.0|1.1/iwxxm.sch`. Runtime SoT remains `https://schemas.wmo.int/iwxxm/<pin>/rule/iwxxm.sch` + vendor. `/rule/1.2/` dropped product IWXXM SCH; foundation files are byte-identical to package-local `…/rule/` (prefer those URLs / vendor embeds). No vendor tree at `externalSchema/.../schemas.wmo.int/rule/`.
- **Detail:** [mining/schemas-wmo-int-rule-mining-notes.md](../mining/schemas-wmo-int-rule-mining-notes.md)
- **Mined:** 2026-07-14 · rule packages 1.0–1.2 · iwxxm pin v2025-2 · #719

### Official TAC↔IWXXM example pairs

- **URL:** https://schemas.wmo.int/iwxxm/2025-2/examples/
- **Access:** public
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA,VONA,SWX]; role=[conversion-fixtures, validation-fixtures]
- **Gap vs GIFTs:** CNL/NIL/collect/`translationFailedTAC` pairs; TC+VA SIGMET
- **Consumer:** golden encode/validate, e2e samples
- **Label:** normative-examples
- **Vendor:** `vendor/schemas/iwxxm/2025-2/IWXXM/examples/` (incl. `TAC-to-XML-Guidance.txt`)
- **Mined:** 2026-07-14 · verified pairs listed in [COVERAGE_MATRIX](./COVERAGE_MATRIX.md) + [reference-set dig](../mining/iwxxm-2025-2-reference-set-mining-notes.md)

### IWXXM 2025-2 ReleaseNotes

- **Publisher:** WMO TT-AvXML
- **URL:** https://schemas.wmo.int/iwxxm/2025-2/ReleaseNotes-IWXXM.txt
- **Access:** public
- **Applies to:** products=[all F6 + SWX/WAFS/QVACI/VONA]; profiles=[annex3]; role=[conversion, iwxxm-validation]
- **Gap vs GIFTs:** documents runwayState **removal** (RC1), dual nil registers (RC2), VAA elevation rename, etc.
- **Consumer:** `tac2iwxxm`, `iwxxm-validate`, F4 messaging
- **Label:** normative-schema (release / migration notes)
- **Caveats:** Prefer this + vendor pin over workshop decks for what changed in **2025-2**. Vendor file is **byte-identical** to publish (checked 2026-07-14).
- **Also:** GitHub release https://github.com/wmo-im/iwxxm/releases/tag/v2025-2 (Amd 82 summary; published 2025-11-25)
- **Mined:** 2026-07-14 · pin v2025-2

### IWXXM AHL / bulletin headings

- **URL:** https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/wmo-information-system-wis/about-manual-gts/ahls-aviation-data-over-icao-afs  
  (short redirects still seen: `/ahls-aviation-data-over-icao-afs`, `/en/activity-areas/wis/iwxxm/ahl-icao-data`)
- **Edition:** **v1.0.1** (2025-08-11) — confirmed live fetch **2026-08-01** (S036/EV-029 T0.2)
- **Access:** public
- **Applies to:** products=[all F6 + SWXA]; role=[bulletin-validation, conversion]
- **Gap vs GIFTs:** TAC T1T2 (`SA`/`SP`/…/`FN`) ↔ IWXXM T1T2 (`LA`/`LP`/…/`LN`) + BBB prefix families (`AAx`/`CCx`/`RRx`) + AMHS filename pattern
- **Consumer:** `tac-validate`, `tac2iwxxm` bulletin encode, dissemination, F8 worker
- **Label:** normative-exchange
- **Canonical prose:** [IWXXM_CONVERSION.md §AHL / bulletin](../IWXXM_CONVERSION.md#ahl--bulletin-canonical-ev-029) · matrix [COVERAGE_MATRIX §EV-029](./COVERAGE_MATRIX.md#eight-family-ahl--rules--s036--ev-029-823)
- **Mined:** 2026-07-14 (URL redirect refresh) · **re-confirmed 2026-08-01** (v1.0.1)

### Sibling repos (already vendored)

| Repo | URL | Role | Label |
|------|-----|------|-------|
| iwxxm-codelists | https://github.com/wmo-im/iwxxm-codelists | RDF → codes.wmo.int | normative-vocabulary |
| iwxxm-modelling | https://github.com/wmo-im/iwxxm-modelling/tree/v2025-2 | UML / EA→XSD+SCH generation (not runtime) | informative (tooling) — [mining notes](../mining/iwxxm-modelling-v2025-2-mining-notes.md) |
| iwxxm-translation | https://github.com/wmo-im/iwxxm-translation | Extra TAC/XML pairs + translator list | **informative** (README: no official WMO/ICAO status) — tip Amd79-80-2023 / IWXXM **2023-1**; parity policy [mining](../mining/iwxxm-translation-parity-mining-notes.md) · #797 |

### wmo-im/iwxxm-modelling (UML + EA→XSD/SCH tooling)

- **Publisher:** WMO TT-AvData / wmo-im
- **URL:** https://github.com/wmo-im/iwxxm-modelling/tree/v2025-2
- **Stable concept pattern:** UML `Pattern ID` → published `sch:pattern @id`; namespace `http://icao.int/iwxxm/2025-2`
- **Access:** public (Sparx EA needed to edit `.eap`)
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA,+SWX/WAFS]; profiles=[annex3]; role=[iwxxm-validation] (provenance only) · conversion (nilReason / WithNilReason lineage)
- **Gap vs GIFTs:** multi-product Schematron authoring outside GIFTs METAR encoder
- **Consumer:** design / UI-decode provenance — **not** runtime `iwxxm-validate` input
- **Label:** informative
- **Caveats:** Prefer published `iwxxm.sch` + XSD under vendor `iwxxm` pin; do not validate against `.eap`. Guidance names `SCHFromXMI-MultiVersion.xslt` but it is absent from the `v2025-2` tree. Vendor path: `vendor/schemas/iwxxm-modelling`.
- **Detail:** [mining/iwxxm-modelling-v2025-2-mining-notes.md](../mining/iwxxm-modelling-v2025-2-mining-notes.md)
- **Mined:** 2026-07-14 · pin `v2025-2` · #719

### Org survey — secondary / lineage (2026-07-14)

Full ranking: [mining/wmo-im-org-mining-notes.md](../mining/wmo-im-org-mining-notes.md). **~103** public repos under https://github.com/wmo-im ; only the IWXXM family above is primary for encode/validate. Annex 3 SARP PDFs are **not** hosted in this org.

| Repo | URL | Role | Label | Caveats |
|------|-----|------|-------|---------|
| collect | https://github.com/wmo-im/collect | bulletin lineage | historical (content = pin) | `1.2/collect.xsd` **byte-identical** to vendor `externalSchema/.../collect/1.2/`; prefer vendor for CI |
| wis2-cookbook (aviation) | https://github.com/wmo-im/wis2-cookbook (`publishing-aviation-data.adoc`) | WIS2 publish / Annex 3 use-rights | informative | Recommended policy + license; not TAC grammar |
| wis2-topic-hierarchy | https://github.com/wmo-im/wis2-topic-hierarchy | F8 topic routing | normative-exchange (WIS2) | Aviation leaves **only** `metar`, `taf`, `qvaci` |
| wis2-guide (§2.8.1.1) | https://github.com/wmo-im/wis2-guide | WIS2↔SWIM / IWXXM format | informative | IWXXM for SWIM; WIS2 **does not** group bulletins; COLLECT AHL as optional unique ID |
| GTStoWIS2 | https://github.com/wmo-im/GTStoWIS2 | historical AHL→topic | historical | Archived; richer T1T2 than current WTH — lineage only |
| CCT | https://github.com/wmo-im/CCT | 306 Vol I.2 common tables | normative-vocabulary | Not aviation TAC FM / 4678 |
| saf / metce / opm / met-basic | github.com/wmo-im/{saf,metce,opm,met-basic} | schema lineage | historical | Prefer **publish** https://schemas.wmo.int/{metce,opm,saf}/ + vendor `externalSchema`; saf **deprecated** (1.0–1.1 only; obsolete since IWXXM 2.0RC1); opm repo **archived**. METCE/OPM runtime = **1.2**; SAF = historical — [METCE](../mining/schemas-wmo-int-metce-mining-notes.md) · [OPM](../mining/schemas-wmo-int-opm-mining-notes.md) · [SAF](../mining/schemas-wmo-int-saf-mining-notes.md) |

**Not useful for Annex 3 TAC / IWXXM conversion:** BUFR4, GRIB2, WMDR/WCMP*, Hydro/WHOS, wis2box services, pymetdecoder (SYNOP-only), VolumeC1 (CCCC freeze).

### Tier A local clones (deep mine 2026-07-14)

- **Local (gitignored):** `.local/reference/wmo-im-tier-a/` — checkouts at **manifest SHAs** (not bare tag tips)
- **Notes:** [mining/wmo-im-tier-a-mining-notes.md](../mining/wmo-im-tier-a-mining-notes.md)
- **Caveats (defer to vendor pin):**
  - GitHub tag `v2025-2` tip (`2c4db03…`) **lags** vendor SHA `35180cbe…` (versioned `2025-2/IWXXM/` tree)
  - `iwxxm-codelists` label `49-2` is **not** a Git tag on the remote — pin by SHA
  - Dual nil/colour registers: classic F6 examples use `common/nil`; VONA/MetFeature/WAFS/QVACI prefer `iwxxm/nil` + `iwxxm/AviationColourCode` / `iwxxm/MeteorologicalFeature`
  - `TAC-to-XML-Guidance.txt` still mentions `runwayState` — **removed** in 2025-2 RC1; do not encode for this pin
  - `iwxxm-translation` Amd79-80-2023 fixtures: METAR/TAF/VAA/TCA only (no SIGMET/AIRMET trees); suite XML year **2023-1** — convert under pin **2025-2** without byte-match ([parity dig](../mining/iwxxm-translation-parity-mining-notes.md) · #797)
  - Dual colour members confirmed live 2026-07-30: `49-2` NIL/NOT_GIVEN/UNKNOWN vs `iwxxm` **UNASSIGNED**; MetFeature: `iwxxm/` **28** vs `49-2/` **27** (**+`VOLCANIC_ASH`**); pin SCH RDF matches ([codes dig](../mining/codes-wmo-int-aviation-mining-notes.md))
  - Live `306/4678` HTML browse ≈ **101** notations is **incomplete** — vendor CSV has **402** stable; CI uses CSV/RDF, not HTML count

### Tier B local clones (deep mine 2026-07-14)

- **Local (gitignored):** `.local/reference/wmo-im-tier-b/`
- **Notes:** [mining/wmo-im-tier-b-mining-notes.md](../mining/wmo-im-tier-b-mining-notes.md)
- **Durable findings:**
  - COLLECT runtime = vendor `externalSchema` (= stand-alone `collect` 1.2)
  - WIS2 aviation topic SoT: WTH CSV + `codes.wmo.int/wis/topic-hierarchy/.../aviation` — thin leaf set
  - Dual exchange models: IWXXM/AMHS **COLLECT** bulletins vs WIS2 **one resource per notification**
  - GTStoWIS2 TableA = historical AHL product map only (archived)
  - CCT stays Vol I.2 — do not cite for weather-group TAC validation

### WMO community IWXXM home

- **URL (intended live):** https://community.wmo.int/en/activity-areas/wis/iwxxm  
  (short form: https://community.wmo.int/iwxxm)
- **Access:** **broken as of 2026-07-14** — both paths return **HTTP 404**. Parent `/en/activity-areas/wis` still resolves to the WIS knowledge hub.
- **Best recovered snapshot (defer-to-latest while live is down):** https://web.archive.org/web/20260314162354/https://community.wmo.int/iwxxm  
  (page text “last updated **26 November 2025**”; “Latest release” → https://schemas.wmo.int/iwxxm/2025-2/; package table column **2025-2** final, Annex 3 Amd **82**)
- **Earlier snapshot (superseded):** https://web.archive.org/web/20251015180706/https://community.wmo.int/en/activity-areas/wis/iwxxm — still labelled **2025-2 RC2** / latest → 2023-1
- **Live related hubs:** https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/aviation · https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/wmo-information-system-wis
- **Applies to:** products=[all F6]; role=[iwxxm-validation, conversion] (index + **compatibility table** package×Annex 3)
- **Consumer:** F4 version policy, ops citations
- **Label:** informative index
- **Caveats:** Until WMO restores the page, cite the **2026-03-14 Wayback** table (or [VERSION_SUPPORT_POLICY Appendix A](../iwxxm/VERSION_SUPPORT_POLICY.md#appendix-a--package--iwxxm-line-matrix-informative), which matches it) plus **schemas.wmo.int** / [ReleaseNotes](https://schemas.wmo.int/iwxxm/2025-2/ReleaseNotes-IWXXM.txt) / GitHub `v2025-2`. Runtime validate against vendor pin **v2025-2**. Local HTML: `.local/reference/community-wmo-iwxxm-wayback/` (gitignored).
- **Detail:** [mining/community-wmo-iwxxm-wayback-mining-notes.md](../mining/community-wmo-iwxxm-wayback-mining-notes.md)
- **Mined:** 2026-07-14 (Wayback recovery) · [reference-set dig](../mining/iwxxm-2025-2-reference-set-mining-notes.md)

### PPT-02 IWXXM Framework (ESAF workshop, TT-AvData)

- **Publisher:** WMO TT-AvData (B.L. Choy); ICAO ESAF workshop materials
- **URL:** https://www.icao.int/filebrowser/download/26741?fid=26741
- **Access:** public filebrowser (**Cloudflare challenge** for automated fetch); do not commit PDF
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA,SWX,WAFS,QVACI,VONA]; profiles=[annex3]; role=[conversion, iwxxm-validation, bulletin] (overview)
- **Gap vs GIFTs:** METAR >4 RVR / 0.1 °C; SIGMET >7 polygon points; IWXXM-only WAFS/QVA/VONA; ROC translation attrs + `translationFailedTAC`; AMHS/FTBP + AHL `T1T2A1A2ii CCCC YYGGgg [BBB]`; package×Annex 3 matrix
- **Consumer:** `tac2iwxxm`, `iwxxm-validate`, bulletin, UI-decode
- **Label:** **informative**
- **Caveats:** Workshop briefing — **not** encode/validate SoT. Figures p.5/9/11/16 captured in mining notes + [VERSION_SUPPORT_POLICY Appendix A](../iwxxm/VERSION_SUPPORT_POLICY.md#appendix-a--package--iwxxm-line-matrix-informative); prefer vendor pin **v2025-2** + community table if numbers drift. Local: `.local/reference/ppt-02-iwxxm-framework-wmo/`
- **Detail:** [mining/PPT-02-IWXXM-Framework-WMO-mining-notes.md](../mining/PPT-02-IWXXM-Framework-WMO-mining-notes.md)
- **Mined:** 2026-07-14 · pin v2025-2 (figure refresh same day)

### ICAO Guidelines — OPMET Data Exchange using IWXXM (5th Edition)

- **Publisher:** ICAO (METP)
- **URL:** https://www.icao.int/sites/default/files/METP/Documents/Guidlines-for-the-Implementation-of-OPMET-Data-Exchange-using-IWXXM_5th-Edition.pdf
- **Edition note:** Fifth Edition — October 2023 (filename retains ICAO spelling “Guidlines”)
- **Access:** **public** PDF
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA,SWXA]; profiles=[annex3]; role=[conversion, iwxxm-validation, bulletin]
- **Gap vs GIFTs:** Translation Centre bulletin flow; COLLECT; AMHS/FTBP + gzip filename; `permissibleUsage`; partial-translation minimum fields; ROC/RODB Schematron & partial-translation stats; METNO — all outside GIFTs
- **Consumer:** `tac2iwxxm`, `iwxxm-validate`, bulletin, UI-decode, ops ([ICAO_OPMET_COMPLIANCE.md](../iwxxm/ICAO_OPMET_COMPLIANCE.md))
- **Label:** normative-exchange
- **Caveats:** Complementary to Doc **10003** (do not equate); §3.1.7 defers operational version matrix to [community IWXXM home](https://community.wmo.int/en/activity-areas/wis/iwxxm) — this edition does **not** contain PPT-02’s “deprecate ≤2021-2 after 2025-2” wording; translation-centre XSD attribute names are prose-only (use vendored `common.xsd`). Local: `.local/reference/opmet-iwxxm-exchange-guidelines-5th/`
- **Detail:** [mining/OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md](../mining/OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md)
- **Mined:** 2026-07-14 · pin v2025-2

### ICAO APAC — IWXXM Implementation FAQs (3rd Edition, March 2025)

- **Publisher:** ICAO Asia/Pacific (MET eDocs)
- **URL:** https://www.icao.int/sites/default/files/APAC/Documents/edocs/MET/2025-03_IWXXM-FAQs_3rd-Ed.pdf
- **Access:** **public** PDF (16 pp.)
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA,SWX]; profiles=[annex3]; role=[conversion, iwxxm-validation, bulletin]
- **Gap vs GIFTs:** Practical encode/ops FAQ — missing TAC → Guidance + iwxxm-translation; NSC vs cloud co-occurrence; `translationFailedTAC`; translationCentre attrs only for cross-State translation; COLLECT multi-version namespaces; SIGMET FIR→polygon; AFS COLLECT mandate
- **Consumer:** `tac2iwxxm`, `tac-validate`, `iwxxm-validate`, bulletin / F16–F19
- **Label:** **informative** (regional FAQ; cites Doc 10003, OPMET Guidelines, schemas.wmo.int, Package Compatibility wiki)
- **Caveats:** Complementary to OPMET Guidelines 5th — do not treat as encode SoT. Some examples still cite IWXXM **2023-1** / **2021-2** context diagrams; runtime pin remains **v2025-2**. Local: `.local/reference/icao-apac-iwxxm-faqs-3rd-2025/`
- **Detail:** [mining/icao-apac-iwxxm-faqs-3rd-2025-mining-notes.md](../mining/icao-apac-iwxxm-faqs-3rd-2025-mining-notes.md)
- **Mined:** 2026-07-30 · companions [codes-wmo-int-aviation](../mining/codes-wmo-int-aviation-mining-notes.md), [iwxxm-translation-parity](../mining/iwxxm-translation-parity-mining-notes.md)

---

## 5. National — US profile (FMH-1 / iwxxm-us)

### Federal Meteorological Handbook No. 1 (FMH-1)

- **Publisher:** OFCM / ICAMS
- **URL:** https://www.icams-portal.gov/resources/ofcm/fmh/FMH1/fmh1_2019.pdf  
  Index: https://www.icams-portal.gov/resources/ofcm/fmh/allfmh2.htm
- **Access:** public PDF (US federal handbook)
- **Applies to:** products=[METAR,SPECI]; profiles=[**iwxxm_us**]; role=[validation, conversion]
- **Gap vs GIFTs:** **entire REMARKS / US national content** (GIFTs stripped RMK) — §12.7 AO1/AO2, SLP, additive `T…`, `$`, …
- **Consumer:** `tac-validate` (US), `tac2iwxxm` extension map, UI-decode
- **Label:** normative (national)
- **Caveats:** Not Annex 3 SoT. US SPECI criteria (§2.5.2 miles/feet) **≠** Annex 3 App 3. Missing body groups are **omitted** (§12.5), not coded as `/`. Local dig: [mining/fmh1-2019-mining-notes.md](../mining/fmh1-2019-mining-notes.md) · `.local/reference/fmh1-2019/`
- **Mined:** 2026-07-14

### NWS Codes Registry — FMH-1 tables

- **URL:** https://codes.nws.noaa.gov/FMH-1
- **Access:** public Linked Data (HTTP **timeout** when probed 2026-07-14 — retry later)
- **Applies to:** profiles=[iwxxm_us]; role=[validation, conversion]
- **Label:** normative-vocabulary (national)
- **Caveats:** Prefer offline/handbook until registry responds; cross-check with FMH-1 PDF

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
- **Mined:** 2026-07-14; enriched 2026-07-30 (#773 / EV-024)

### IWXXM-US METAR and SPECI.pdf (MDL model documentation v3.0)

- **Publisher:** NOAA / NWS MDL
- **URL:** https://vlab.noaa.gov/web/mdl/data-modeling  
  Document: `METAR and SPECI.pdf` (VLab documents/6609493/…; Data Modeling Report 23 Dec 2022)
- **Access:** public PDF via VLab
- **Applies to:** products=[METAR,SPECI]; profiles=[**iwxxm_us**]; role=[conversion, iwxxm-validation]
- **Gap vs GIFTs:** Maps FMH-1 REMARKS → `iwxxm-us` types (Addendum, PeakWind, VariableRVR, Lightning, …)
- **Consumer:** `tac2iwxxm`, `tac-validate`, `iwxxm-validate`
- **Label:** normative-conversion-notes (national)
- **Caveats:** Supplement to WMO IWXXM — does not replace Annex 3. Local extract: `.local/reference/iwxxm-us-metar-speci-pdf/` · dig: [mining/iwxxm-us-metar-speci-pdf-mining-notes.md](../mining/iwxxm-us-metar-speci-pdf-mining-notes.md)
- **Mined:** 2026-07-30 (#773)

### NOAA-MDL/iwxxm-us-modelling

- **Publisher:** NOAA / NWS MDL
- **URL:** https://github.com/NOAA-MDL/iwxxm-us-modelling
- **Access:** public
- **Applies to:** profiles=[**iwxxm_us**]; role=[conversion, iwxxm-validation] (UML→XSD provenance)
- **Consumer:** maintainers (compare generated schemas to vendor pin)
- **Label:** informative (tooling)
- **Caveats:** EA project binary; prefer published XSD/PDF/HTML as auditable trail; do not hand-edit `vendor/schemas/iwxxm-us`
- **Mined:** 2026-07-30 (#773)

### Aviation Weather Center Data API (live fixtures)

- **Publisher:** NOAA / NWS Aviation Weather Center
- **URL:** https://aviationweather.gov/data/api/  
  OpenAPI: https://aviationweather.gov/data/schema/openapi.yaml  
  REST base: https://aviationweather.gov/api/data/
- **Stable concept pattern:** `/api/data/{metar|taf|…}?ids=…&format={raw|json|geojson|xml|iwxxm}&hours=…`
- **Access:** public HTTPS; rate-limited (~100 req/min); set a custom User-Agent; **no CORS**
- **Applies to:** products=[METAR,TAF,(AIRMET Alaska)]; profiles=[iwxxm_us useful]; role=[conversion, iwxxm-validation] (**fixtures / live smoke only**)
- **Gap vs GIFTs:** live worldwide METAR/TAF including **IWXXM** format; US REMARKS in TAC comments
- **Consumer:** live smoke, F8 ingest experiments — **not** CI golden SoT
- **Label:** **informative**
- **Caveats:** Sample METAR IWXXM (2026-07-14) used ns `http://icao.int/iwxxm/2025-2` but `schemaLocation` cited **`…/iwxxm/2025-2RC1/iwxxm.xsd`**; `permissibleUsage=NON-OPERATIONAL`; translation centre KKCI/AWC. METAR `format=iwxxm` may return **COLLECT** bulletin. Observed TAF IWXXM **missing `xmlns:xlink`** (not well-formed). Prefer official `schemas.wmo.int/…/examples/` for regression goldens. Validate against **vendored** `2025-2`, not RC1 path. Detail: [mining/awc-data-api-mining-notes.md](../mining/awc-data-api-mining-notes.md)
- **Mined:** 2026-07-14 · smoke refresh same day · pin v2025-2 · #719

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
| Active machine validation for pin | `vendor/schemas/iwxxm` + [IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) |
| Package API design | #698 / #699 |
| Converter implementation | #693 / `packages/tac2iwxxm` |

## Related tickets

| Ticket | Boundary |
|--------|----------|
| [#698](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/698) | TAC validation package — consumes this catalog |
| [#699](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/699) | IWXXM validation package — schema release pointers |
| [#693](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/693) | Converter — conversion citations |
| [#702](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/702) / [#714](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/714) | Decode / F7 UX provenance |
