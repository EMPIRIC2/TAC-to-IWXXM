# WMO-306 Vol. I.3 (2019 ed., upd. 2021) — focused mining notes

**Status:** working notes (not normative). **Historical** vs the 2023 dig and runtime vendor pin.  
**Focus:** PDF pages **1–272** (**complete**).  
**Ticket:** parent dig [#719](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/719) (closed); this dig [#798](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/798).  
**Local extracts (gitignored):** `.local/reference/wmo-306-vI-3-2019-upd-2021/`

**Prefer for standing SoT:** [WMO-306-vI-3-2023-mining-notes.md](./WMO-306-vI-3-2023-mining-notes.md) + `vendor/manifest.json` → IWXXM **v2025-2** + `FM205.adoc`. Related foundation digs: [schemas-wmo-int-metce](./schemas-wmo-int-metce-mining-notes.md), [opm](./schemas-wmo-int-opm-mining-notes.md), [saf](./schemas-wmo-int-saf-mining-notes.md) (SAF = **historical** for 2025-2 encode); vocab refresh [codes-wmo-int-aviation](./codes-wmo-int-aviation-mining-notes.md).

**Promote durable findings into:**

| Doc | Path |
|-----|------|
| Domain hub | [../README.md](../README.md) |
| TAC validation | [../TAC_VALIDATION.md](../TAC_VALIDATION.md) |
| IWXXM conversion | [../IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) |
| IWXXM validation | [../IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) |
| Master URL catalog | [../rules/RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) |
| Coverage matrix | [../rules/COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) |

| Item | Value |
|------|-------|
| Title | Manual on Codes, Volume I.3 – International Codes (Part D) |
| Publisher | WMO |
| Official landing | e-Library (captcha); ISBN 978-92-63-10306-2; later edition record often cited as https://library.wmo.int/idurl/4/35769 |
| Pin / edition | **2019 edition, Updated in 2021** (PDF cover) |
| Date mined | 2026-07-30 |
| Access | local PDF / e-Library captcha — **do not commit** binary or fulltext |
| Label | normative (historical edition) |
| Pages (PDF) | 272 total; dig **1–272** (**complete**) |

---

## What this source is / is not

| Is | Is not |
|----|--------|
| Full Part D PDF: COLLECT→METCE→OPM→SAF→FM **205-15 Ext / 16 / 2018** + Appendix **D-1…D-10** + schema URL pins through **IWXXM 3.0** | Alphanumeric TAC FM templates (Vol **I.1**) |
| Historical NIL / cancel / NOSIG / field nilReasons / `@translationFailedTAC` / D-* landings for IWXXM **1.1–3.0** | Runtime XSD/SCH truth (`schemas.wmo.int/iwxxm/2025-2/` + vendor) |
| Bridge SAF→**AIXM**; AIRMET/TCA/VAA/SWX scopes; printed D-1 incl. `noSignificantChange` | FM **205-2021-2 / 2023-1** (absent here — use [2023 dig](./WMO-306-vI-3-2023-mining-notes.md)) |

---

## Document map

### Pass A — pp. 1–50

| PDF pp. | Content | Project relevance |
|---------|---------|-------------------|
| 1–6 | Cover, copyright, revision track | Provenance |
| 7–13 | Contents | Locates FM 205 |
| 15–32 | Part D front matter | Cite-only |
| 33–36 | FM numbering + namespace/edition rules | F4 version story |
| 37–39 | Code-table URI policy | Vocab / `codes.wmo.int` |
| 40–43 | **FM 201** COLLECT | Bulletin / #797 P2 |
| 44–50 | **FM 202-15 Ext** METCE → **xsd-volcano** | VAA/VONA |

### Pass B — pp. 51–120

| PDF pp. | Content | Project relevance |
|---------|---------|-------------------|
| 51–53 | METCE **erupting volcano** + **tropical cyclone** (15-Ext) | VA SIGMET / TCA / VAA |
| 54–67 | **FM 202-16** METCE (repeat volcano/TC + observation types) | Same METCE policy; dual historical trees |
| 68–75 | **FM 203** OPM | Foundation only — [opm dig](./schemas-wmo-int-opm-mining-notes.md) |
| 76–83 | **FM 204** SAF (aerodrome/runway/airspace) | **IWXXM 1.1 only**; note: 2.1+ drops SAF |
| 84–85 | **FM 205-15 Ext** scope + req-class index (METAR/SPECI/TAF/SIGMET/VA/TC SIGMET) | Product map for 1.1 |
| 86–87 | Namespaces (`icao.int/iwxxm/1.1`) + virtual typing / Code table **D-4** | Obs-type URIs under `49-2/…/IWXXM/1.0/` |
| 87–109 | Cloud…METAR/SPECI observation + trend | Early field nilReason (cloud base); CAVOK/NOSIG notes |
| 110–118 | TAF record + **`@status`** NORMAL/AMD/CNL/COR/MISSING | NIL–CNL recipes (1.1) |
| 118–120 | SIGMET evolving condition + analysis start (`saf:AirspaceVolume`) | Geometry lineage — not 2025-2 SoT |

### Pass C — pp. 121–180

| PDF pp. | Content | Project relevance |
|---------|---------|-------------------|
| 121–126 | Finish FM **205-15 Ext** SIGMET (NORMAL/CANCELLATION) + position analysis | F23 CNL lineage |
| 126–127 | VA SIGMET + **TC SIGMET** (`metce:TropicalCyclone`; phenomenon `49-2/SigWxPhenomena/TC`) | #738 / #739 |
| 127–130 | **FM 205-16** IWXXM **2.1** scope + namespaces | Adds AIRMET/TCA/VAA; **AIXM 5.1.1** replaces SAF; external `iwxxm.sch`; METCE **1.2** |
| 130–145 | 2.1 METAR/SPECI/fields (AirportHeliport); NIL + NOSIG→`inapplicable` | Defer NOSIG to pin (`noSignificantChange` in later eras) |
| 145–151 | 2.1 TAF `@status` + forecast records | Same CNL/NIL family as 1.1 with AIXM |
| 152–157 | 2.1 SIGMET / evolving collection / VA SIGMET | AIXM airspace; CNL |
| 157–160 | **AIRMET** (first appearance in this Manual line) | F24 / #731 |
| 161–165 | **TCA** + **VAA** (+ ash cloud `aixm:AirspaceVolume`) | F27 / F26 |
| 166 | **`@translationFailedTAC`** on Report — no partial operational translate | #797 P0 |
| 167–171 | Cloud forecast + typed nil helpers (angle/length/…) | Encode hygiene |
| 172–180 | **FM 205-2018** IWXXM **3.0** start — adds **Space Weather** Advisories; METAR NIL + trend/NOSIG | #740; NOSIG→`noSignificantChange` |

### Pass D — pp. 181–230

| PDF pp. | Content | Project relevance |
|---------|---------|-------------------|
| 181–183 | Obs field nilReasons (T/Td/QNH/vis/RVR/WX/cloud/CLR·SKC) + **CAVOK** omit | Matches conversion METAR table |
| 183–188 | Runway state / RVR / sea / wind shear | **Runway state:** printed in 3.0; **do not encode** on 2025-2 pin |
| 188–191 | Cloud (VV XOR layers) + **NSC** / **NCD** | `nothingOfOperationalSignificance` / `notDetectedByAutoSystem` |
| 192–196 | **TAF** `@isCancelReport` + NIL `baseForecast`/`missing`; NSW/NSC; **VV absent (no nil)** | F20; lineage vs 1.1 `@status` CNL |
| 197–206 | TC/VA SIGMET collections + **SIGMET core** CNL | `@isCancelReport`; omit phenomenon+analysis; D-10 `SigWxPhenomena` |
| 207–210 | **AIRMET** CNL (same cancel pattern) | F24; D-10 cite may say AirWx — prefer SigWx / 2023 dig caveat |
| 211–219 | **TCA** / **VAA** (UNNAMED/UNKNOWN; colour unknown/withheld/missing; remarks `inapplicable`) | F27 / F26 |
| 220–222 | **SWX** advisory + Report attrs incl. **`@translationFailedTAC`** (p.222) | #740; #797 (also p.166 in 2.1) |
| 223–229 | Cloud/wind forecast helpers + typed nil measures | Encode hygiene |
| 230 | **CRS** (`srsName` / `srsDimension=2` / `axisLabels`) + UUID + Extension start | Convert-only C1 |

### Pass E — pp. 231–272 (**final**)

| PDF pp. | Content | Project relevance |
|---------|---------|-------------------|
| 231 | Finish **Extension** (`iwxxm:extension`, `processContents=strict`, last child) | `iwxxm_us` / national extension lineage |
| 232–236 | FM **221** TSML / **231** WMLTS / **232** WaterML / **241** WMDR | **Out of F6 encode path** (see [tsml dig](./schemas-wmo-int-tsml-mining-notes.md)) |
| 237 | **Code table D-1** nil reasons → `codes.wmo.int/common/nil` | Includes `noSignificantChange`, NSC/NCD/NSW notations |
| 238–240 | D-2 physical quantity kinds | Cite-only |
| 241–245 | D-3 METCE obs types; OPM/SAF stubs | METCE lineage |
| 246–251 | **D-4** IWXXM obs types split **1.0** (205-15 Ext) vs **2.1** (205-16) | Historical `om:type` code-spaces |
| 252 | D-5 observable properties | Cite-only |
| 253 | **D-6** recent weather → landing `49-2/AerodromeRecentWeather`; concept URIs **`306/4678/{TAC}`** | Encode href family |
| 254–266 | **D-7** present/forecast weather → `49-2/AerodromePresentOrForecastWeather`; URIs **`306/4678/`** | Same 4678 Manual-wins (#797) |
| 267 | **D-8** cloud amount → `49-2/CloudAmountReportedAtAerodrome` | Prefer live/RDF over printed bufr4 path quirks |
| 268 | **D-9** CB / TCU → `49-2/SigConvectiveCloudType` | Cloud type hrefs |
| 269 | **D-10** → **`49-2/SigWxPhenomena`** only (TC, VA, SEV_*, …) | Reinforces AirWx mis-cite caveat |
| 270–271 | Appendix B schema URL pins (COLLECT…IWXXM **2.1** + **3.0**) | **Stops at 3.0** — no 2021-2/2023-1/2025-2 |
| 272 | Back matter | — |

**Dig complete.** No further PDF windows for this edition.

---

## Key findings (paraphrase; cite PDF page)

### Namespace / edition policy (p.33)

- XML editions get unique namespaces (year-of-work **or** version number).
- Printed examples: METCE `http://def.wmo.int/metce/2013`; IWXXM **2.1** `http://icao.int/iwxxm/2.1`.
- Table-version snapshots independent of XML edition.
- **Defer:** encode/validate → vendor **2025-2**.

### Code-table identifiers (pp.37–38)

- Vol I.1/I.2 regulations apply inside Part D GML schemas.
- Weather tokens → **`306/4678`** + Manual-wins (#797), not this front matter alone.

### FM 201 COLLECT (pp.40–43)

- Packages same-type GML features for GTS/**AFS** bulletin practice; may include **NIL** station reports when routine reports unavailable.
- Dual trees: **201-15-Ext** and **201-16**.

### FM 202 METCE — volcano / erupting / TC (pp.50–52, 56–58)

| Class | Shall / should | Notes |
|-------|----------------|-------|
| Volcano | `metce:name` literal; `metce:position` → `gml:Point` | Block-caps **recommendation**; GVP catalogue note (`wis.wmo.int/volcano`) |
| Erupting volcano | Depends on volcano; `metce:eruptionDate` ISO 8601 date-time | Source of ash / significant phenomena |
| Tropical cyclone | `metce:name` only in this METCE release | Block-caps recommendation; “more detailed representations may be used” |

**Implication:** Aligns with standing conversion cites for METCE `Volcano` / `TropicalCyclone` / `EruptingVolcano` — verify against pinned METCE XSD, not 1.1 printed trees alone.

### FM 203 OPM / FM 204 SAF (pp.68–83)

- OPM = observable-property scaffolding (transitive via METCE Process).
- **SAF note (p.76):** SAF-XML used in FM **205-15 Ext** (IWXXM **1.1**); FM **205-16** (IWXXM **2.1**) **does not require** SAF-XML.
- **Defer:** 2025-2 encode uses AIXM — do not emit `saf:` ([saf dig](./schemas-wmo-int-saf-mining-notes.md); coverage matrix).

### FM 205-15 Ext — IWXXM 1.1 scope (pp.84–86)

- Products in scope: **METAR, SPECI, TAF, SIGMET** (incl. VA / TC SIGMET classes in TOC).
- Namespace package: `http://icao.int/iwxxm/1.1` → `schemas.wmo.int/iwxxm/1.1/iwxxm.xsd`.
- Depends on METCE 1.1, OPM 1.1, **SAF 1.1**.
- Virtual typing via `om:type` + Code table **D-4** URIs under `http://codes.wmo.int/49-2/observation-type/IWXXM/1.0/…`.

### Cloud base nilReason (p.87)

- Cloud base may be omitted with `@nilReason`; when nil: `@xsi:nil="true"` and `@uom="N/A"`.
- Cloud amount `@xlink:href` → Code table **D-8** (aerodrome cloud amount).
- **Same pattern family** as later Guidance / 2023 dig; prefer pin Guidance + SCH for current encode.

### METAR/SPECI / trend / NOSIG (pp.103–108, keyword hits)

- Report `@status` enumerations include **NORMAL / MISSING / CORRECTION** (METAR/SPECI report class).
- Notes equate **MISSING** to a “NIL” routine report (not provided on anticipated timescale).
- **NOSIG** appears in trend-forecast context (empty trend + nilReason lineage — 2023 dig prefers `noSignificantChange` for 3.0-era; older 1.1/2.1 sometimes used `inapplicable`).
- **CAVOK** notes on observation/trend/forecast records (visibility/cloud omission patterns).
- Code table **D-1** nil reasons published at `http://codes.wmo.int/common/nil` (explicit TAF note p.118).

### TAF `@status` recipes (pp.116–118) — IWXXM 1.1

| `@status` | Paraphrase of shalls |
|-----------|----------------------|
| **NORMAL** | `baseForecast` present; `validTime`; no previous-report aerodrome/period |
| **AMENDMENT** / **CORRECTION** | `baseForecast` + `validTime` + `previousReportValidPeriod`; previous aerodrome recommended |
| **CANCELLATION** | No `baseForecast` / `changeForecast`; `validTime` = cancelled period; `previousReportAerodrome` |
| **MISSING** (NIL) | `baseForecast` present but **empty `om:result`** + `@nilReason`; no `changeForecast` / `validTime` / previous-report fields |

Change-forecast `@changeIndicator` enum includes BECOMING, TEMPORARY_FLUCTUATIONS, FROM, PROBABILITY_30/40 (+ TEMPORARY variants). Recommendation: ≤ **5** change forecasts.

**Defer:** current TAF CNL/NIL encode → vendor examples + Guidance + 2023 dig / F20 goldens — not 1.1 SAF-flavoured paths.

### SIGMET start (pp.118–120) — IWXXM 1.1

- Evolving meteorological condition: `intensityChange` NO_CHANGE / …; geometry via **`saf:AirspaceVolume`**; speed/direction of motion; zero speed ⇒ direction constraints.
- Analysis is METCE `SamplingObservation` subclass; `om:type` → `…/IWXXM/1.0/SIGMETEvolvingConditionAnalysis`; feature-of-interest sampling surface + `saf:Airspace`.
- **Defer:** 2025-2 SIGMET geometry / AIXM — F23 goldens + vendor examples; SAF path is lineage only.

### SIGMET finish + VA/TC SIGMET (pp.121–127) — IWXXM 1.1

- SIGMET `@status`: **NORMAL** or **CANCELLATION** only (no AMD/COR on SIGMET in this line).
- CANCELLATION: cancelled airspace details via a single `analysis` instance (phenomenon details constrained).
- TC SIGMET: `iwxxm:tropicalCyclone` → `metce:TropicalCyclone`; phenomenon href **`http://codes.wmo.int/49-2/SigWxPhenomena/TC`**.
- VA SIGMET class depends on SIGMET + erupting-volcano METCE (same family as later pins).

### FM 205-16 — IWXXM 2.1 (pp.127–171)

**Scope expansion (p.127):** METAR/SPECI/TAF/SIGMET **+ AIRMET + TCA + VAA** (still no SWX).

**Package (p.129):**
- Namespace `http://icao.int/iwxxm/2.1` → `schemas.wmo.int/iwxxm/2.1/`
- External Schematron: `…/2.1/rule/iwxxm.sch`
- **AIXM 5.1.1** replaces SAF for aerodrome/airspace (`aixm:AirportHeliport`, `aixm:Unit`, `aixm:AirspaceVolume`)
- METCE **1.2** (was 1.1 under 205-15 Ext)
- Obs-type URIs under `49-2/observation-type/IWXXM/2.1/…`

**METAR/SPECI NIL / NOSIG (p.131):**
- `@status` MISSING ⇒ empty `om:result` + nilReason; no `@automatedStation`; no `trendForecast`
- NOSIG **recommendation**: empty `trendForecast` with `@nilReason` indicating **`inapplicable`** (2.1-era)
- **Defer:** 2023 dig / pin prefer **`noSignificantChange`** for later IWXXM lines — do not promote 2.1 `inapplicable` as current SoT

**TAF (pp.145–147):** Same NORMAL/AMD/CNL/COR/MISSING family as 1.1; aerodrome via **AIXM** `AirportHeliport`.

**SIGMET 2.1 (pp.152–157):** Still NORMAL/CANCELLATION; airspace/units via AIXM; evolving-condition collection pattern.

**AIRMET (pp.157–160):** First printed AIRMET requirements class in this Manual — MWO `aixm:Unit`, sequenceNumber, validPeriod, phenomenon `@xlink:href`.

**TCA / VAA (pp.161–165):**
- TCA: advisoryNumber, issueTime, observation/forecast OM types `TropicalCycloneObservedConditions` / `…ForecastConditions` under IWXXM/2.1
- VAA: ash cloud geometry via **`aixm:AirspaceVolume`**; D-1 nil cite

**`@translationFailedTAC` (p.166)** — durable; already in conversion SoT / #797:
- On incomplete TAC→IWXXM translate: put original TAC on `Report/@translationFailedTAC`
- Provide only report type + translation metadata — **no** partially translated operational content
- Permissible usage may remain normal; failed TAC may still be operationally useful; **never** distribute partial translate as operational

**Typed nil helpers (pp.170–171):** angle/length-with-nil-reason requirements classes (encode hygiene lineage).

### FM 205-2018 — IWXXM 3.0 start (pp.172–180)

- Scope adds **Space Weather Advisories** (SWXC) alongside METAR…VAA
- Requirements URIs under `http://def.wmo.int/iwxxm/3.0/req/…`
- **METAR NIL (p.176):** empty `observation` + `@nilReason=…/missing`; **`trendForecast` absent**
- **NOSIG (p.179):** empty `trendForecast` + `@nilReason=…/noSignificantChange` — **prefer over** 2.1 `inapplicable`
- **NSW / trend NSC (p.179):** `nothingOfOperationalSignificance`
- BECMG/TEMPO without specified time → `phenomenonTime` + `missing` (or `unknown` if uncertain)

### FM 205-2018 — richest nilReason tables (pp.181–230)

**Observation fields (pp.181–183)** — sensor fail → `@xsi:nil="true"`, `@uom="N/A"`, `…/notObservable` for air temp, dewpoint, QNH, visibility, RVR; present weather empty + `notObservable`.

**Cloud / AUTO / CLR·SKC (p.182):**
- Layer amount/base unobserved: empty layer/base + `notObservable` **or** `notDetectedByAutoSystem`
- Cloud type (AUTO limits): empty `cloudType` + `notObservable`
- Clear sky, not CAVOK: empty `cloud` or `base` + `inapplicable`

**CAVOK (p.183 / forecast p.195):** `@cloudAndVisibilityOK=true`; **omit** visibility, rvr, presentWeather/weather, cloud.

**NSC / NCD (p.189):** empty cloud + `nothingOfOperationalSignificance` (NSC) or `notDetectedByAutoSystem` (NCD). VV XOR cloud layers.

**TAF (pp.192–194)** — 3.0 cancel model (not 1.1 `@status` CANCELLATION):

| Case | Encoding |
|------|----------|
| CNL | `@isCancelReport=true` + `cancelledReportValidPeriod`; empty `validPeriod` / `baseForecast` / `changeForecast` |
| NIL | empty `baseForecast` + `…/missing` |
| NSW / NSC | same `nothingOfOperationalSignificance` family |
| VV N/A | `verticalVisibility` **missing with no nilReason** |

**SIGMET / AIRMET CNL (pp.204, 210):** `@isCancelReport=true` + cancelled seq/period; **`phenomenon` and `analysis` empty**. SIGMET D-10 → `SigWxPhenomena` (p.204 note).

**TCA / VAA (pp.211–215):**
- TCA: `UNNAMED`; remarks / no-next → `inapplicable`
- VAA: volcano UNKNOWN/UNNAMED; location/eruptionDetails → `unknown`; colourCode → `unknown` / `withheld` / `missing`; remarks / no further advisories → `inapplicable`

**SWX (pp.220–221):** remarks + nextAdvisoryTime nils → `inapplicable` (same advisory family).

**Report / translate (p.222):** `@reportStatus` ∈ {NORMAL, AMENDMENT, CORRECTION}; translation attrs + **`@translationFailedTAC`** — no partial operational translate (same rule as FM 205-16 p.166; requirement URI print quirk `translatedFailedTAC` — body uses `@translationFailedTAC`).

**CRS (p.230):** geometry shall carry `srsName`, `srsDimension="2"`, `axisLabels` (2-D only).

**Runway state (pp.183–185):** fully specified in this 3.0 print — **historical for pin**; IWXXM **2025-2** removed runway-state from METAR (already caveated in conversion SoT).

### Extension + non-aviation FM + Appendix D/B (pp.231–272)

**Extension (p.231):** `iwxxm:extension` last child; `<any processContents='strict'>` — national XSD must be resolvable for validation (`iwxxm_us` lineage).

**FM 221/231/232/241 (pp.232–236):** TSML / WaterML / WMDR — **not** F6 TAC→IWXXM encode path.

**D-1 nil reasons (p.237)** — published at `http://codes.wmo.int/common/nil`. Printed notations include:
`AboveDetectionRange`, `BelowDetectionRange`, `inapplicable`, `missing`, `noSignificantChange` (NOSIG), `notDetectedByAutoSystem` (NCD), `notObservable`, `nothingOfOperationalSignificance` (NSC/NSW), `template`, `unknown`, `withheld`.
→ Corroborates conversion SoT; prefer live RDF / pin SCH over reprinting full table in git.

**D-4 (pp.246–251):** Version-split observation-type code-spaces `49-2/observation-type/IWXXM/1.0/` vs `/2.1/` — historical; encode/`om:type` → pin-era URIs.

**D-6 / D-7 (pp.253–266):** Landings `49-2/AerodromeRecentWeather` and `49-2/AerodromePresentOrForecastWeather`; **concept URIs** use **`http://codes.wmo.int/306/4678/{TAC}`** (RE* recent weather maps to base TAC token in URI). Aligns with #797 Manual-wins / vendor CSV SoT.

**D-8 / D-9 (pp.267–268):** Landings `CloudAmountReportedAtAerodrome` / `SigConvectiveCloudType` (CB, TCU). Printed rows may show `bufr4/codeflag/…` paths — **prefer** live `49-2/` / vendor RDF concept URIs used by examples/SCH.

**D-10 (p.269):** Landing **`http://codes.wmo.int/49-2/SigWxPhenomena`** — entries include TC, VA, SEV_ICE, SEV_TURB, FRQ_TS, … **No AirWxPhenomena** in this table (supports 2023 dig AIRMET D-10 mis-cite caveat).

**Appendix B (pp.270–271):** Schema URL inventory through COLLECT 1.1/1.2, METCE 1.1/1.2, OPM, SAF 1.1, IWXXM **2.1** and **3.0** (incl. `spaceWxAdvisory.xsd`). **Does not** list 2021-2 / 2023-1 / 2025-2 — defer package selection to 2023 dig + vendor pin.

---

## Product × artifact matrix (pp.1–272)

| Product | Input | Output hook (this PDF) | Official cue | Gap vs GIFTs | Consumer |
|---------|-------|------------------------|--------------|--------------|----------|
| Bulletin | multi-report | COLLECT | FM 201 + App B | packaging | dissemination |
| VAA / VONA / VA SIGMET | volcano TAC | METCE + VAA colour nils; D-10 `VA` | FM 202 / 205-* / D-10 | name/pos/colour | `tac2iwxxm` |
| TCA / TC SIGMET | TC name | METCE TC; D-10 `TC` | FM 202 / 205-* / D-10 | name; advisory OM | `tac2iwxxm` |
| METAR / SPECI | TAC | 1.1→3.0 field nils; D-1/D-6/D-7/D-8/D-9 | FM 205-* + App A | pin Guidance | convert + validate |
| TAF | TAC | `@isCancelReport` / NIL / VV omit; D-7 | FM 205-2018 | F20 goldens | convert |
| SIGMET / AIRMET | TAC | `@isCancelReport`; D-10 SigWx | FM 205-2018 / D-10 | F23/F24 | convert |
| SWX | — | Scope + remarks nils from **3.0** | FM 205-2018 | #740 | later |
| Translate fail | bad TAC | `@translationFailedTAC` | p.166 + p.222 | #797 | convert quarantine |
| Geometry | coords | CRS 2-D attrs | p.230 | C1 convert-only | convert |
| National ext | — | `iwxxm:extension` strict | p.231 | `iwxxm_us` | validate |

---

## Catalog paste rows

```text
### WMO-No. 306 Vol. I.3 (2019 ed., upd. 2021) — historical Part D PDF

- **Publisher:** WMO
- **URL:** WMO e-Library (ISBN 978-92-63-10306-2); prefer later 2023 catalog entry https://library.wmo.int/idurl/4/35769
- **Access:** e-Library captcha / local PDF — do not commit
- **Applies to:** products=[all F6 + bulletin + SWX scope]; profiles=[annex3]; role=[conversion] (historical)
- **Gap vs GIFTs:** Full dig 1–272: COLLECT; METCE; IWXXM 1.1–3.0 NIL–CNL/NOSIG/field nils; SAF→AIXM; AIRMET/TCA/VAA/SWX; translationFailedTAC; CRS; Extension; D-1…D-10 landings (4678 / SigWx / CloudAmount)
- **Consumer:** `tac2iwxxm`, `iwxxm-validate` (vocab landings), dissemination (COLLECT)
- **Label:** normative (historical)
- **Working notes:** mining/WMO-306-vI-3-2019-upd-2021-mining-notes.md
- **Caveats:** Dig **complete**; package maps stop at IWXXM 3.0 — superseded by 2023 dig + vendor v2025-2; 2.1 NOSIG→inapplicable deferred; runway-state historical vs 2025-2 removal; prefer live codes.wmo.int / vendor RDF over printed bufr4 path quirks in D-8
```

---

## Domain-knowledge cross-check (defer to latest)

| Older / this claim | Later source | Action |
|--------------------|--------------|--------|
| This PDF = 2019/upd-2021 Part D (complete) | [2023 dig](./WMO-306-vI-3-2023-mining-notes.md) (+ FM 205-2021-2 / 2023-1) | Historical only; 2023 for later FM lines |
| App B pins through IWXXM 3.0 (pp.270–271) | vendor **2025-2** + `FM205.adoc` | Do not use App B as runtime package map |
| IWXXM 1.1 + SAF geometry | vendor 2025-2 + AIXM | Do not encode SAF |
| NOSIG → `inapplicable` (2.1) | D-1 + 3.0 p.179 `noSignificantChange` | Prefer pin |
| TAF `@status` CANCELLATION | 3.0 `@isCancelReport` | Prefer pin / Guidance |
| Field nilReason tables | Guidance + examples + 2023 dig | Corroborate — already SoT |
| Runway-state (3.0 print) | 2025-2 removed | Reject for pin encode |
| D-10 = SigWxPhenomena (p.269) | 2023 AIRMET AirWx mis-cite | Prefer SigWx / pin vocab |
| D-6/D-7 → `306/4678/{TAC}` | vendor CSV + #797 | Prefer vendor CSV (402) over live HTML count |
| D-8 printed bufr4 URIs | live `49-2/CloudAmount…` / RDF | Prefer registry/examples |
| `@translationFailedTAC` | vendor + FAQ · #797 | Already SoT |
| Extension strict (p.231) | `iwxxm_us` / pin extension | Lineage only unless profile requires |

---

## Implications for this repo

- **F6 / tac2iwxxm:** Dig complete — **no new conflicting SoT**. D-1/D-6/D-7/D-10 landings corroborate conversion + codes catalog. Engine gap (stubbing aviation nils as `missing`) unchanged (#719).
- **tac-validate:** Vol I.1 / Annex 3 for TAC; 4678 inventory → vendor CSV.
- **iwxxm-validate:** Pin SCH + RDF; App B package list is historical through 3.0 only.
- **#798 acceptance:** All dig windows done; durable items already in canonicals/catalog or closed as corroboration.

---

## Promotion status

| Item | Status |
|------|--------|
| Catalog historical row | Done — dig **complete** |
| Mining index | Done |
| IWXXM_CONVERSION | Dig cross-link; field/D-* corroboration |
| IWXXM_VALIDATION | Vocab landings already catalogued; no package-map promote from App B |
| COVERAGE_MATRIX | Dig pointer complete |
| Re-promote printed package/D-tables as SoT | **Deferred** (vendor + live registry win) |
| Close #798 dig windows | **Done** (pp.1–272) |

---

## Suggested next mining passes

1. None for this PDF — dig **complete**. Optional: close #798 after review.
2. Prefer ongoing encode work against vendor Guidance / 2025-2 examples (engine backlog), not further OCR of this edition.
3. For later Manual lines (WAFS / 2023-1 deferral prose) stay on [2023 dig](./WMO-306-vI-3-2023-mining-notes.md).
