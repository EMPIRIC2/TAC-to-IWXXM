# WMO-306 Vol. I.3 (2023) — focused mining notes

**Status:** working notes (not normative). Always verify against the PDF / [schemas.wmo.int](https://schemas.wmo.int/).  
**Scope of this pass:** Part D → FM 205 IWXXM → **all F6 TAC→IWXXM products** (METAR, SPECI, TAF, SIGMET, AIRMET, TCA, VAA) + nil/missing encodings. Ticket mirror: [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719).  
**Local PDF + extracts (gitignored):** `.local/reference/wmo-306-vI-3-2023/`

**Standing catalog (promoted from #719):**

| Doc | Path |
|-----|------|
| Master URL catalog | [../rules/RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) |
| Coverage matrix | [../rules/COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) |
| Annex 3 / TAC validation | [../TAC_VALIDATION.md](../TAC_VALIDATION.md) |
| IWXXM creation | [IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) |
| IWXXM validation | [IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) |
| Workshop overview (informative) | [mining/PPT-02-IWXXM-Framework-WMO-mining-notes.md](./PPT-02-IWXXM-Framework-WMO-mining-notes.md) |
| Doc 10003 Advance 2014 (historical) | [mining/ICAO-Doc-10003-draft-2014-mining-notes.md](./ICAO-Doc-10003-draft-2014-mining-notes.md) |

| Item | Value |
|---|---|
| Title | Manual on Codes, Volume I.3 – International Codes |
| Edition | 2023 |
| Official record | <https://library.wmo.int/idurl/4/35769> |
| Pages | 272 |
| Local text | `.local/reference/wmo-306-vI-3-2023/fulltext.txt` |
| Vendor pin (runtime) | `vendor/manifest.json` → `iwxxm` tag **v2025-2** (PDF index stops at FM 205-2023-1 online package) |

**Supersession note (2026-07-14):** Printed FM **205-2023-1** package tables in this edition are **historical** for runtime encode/validate. Prefer vendor pin + working **FM 205-2025-2** AsciiDoc in `vendor/schemas/iwxxm/documentation/manual/FM205.adoc` (or local clone `.local/reference/wmo-im-tier-a/iwxxm/`) and [mining/wmo-im-tier-a-mining-notes.md](./wmo-im-tier-a-mining-notes.md). Keep this PDF mine for I.3 prose / NIL–CNL requirements classes that still apply as policy text.

**Earlier edition (2026-07-30):** Local dig of **2019 edition, Updated in 2021** (PDF pp.**1–230**: through FM **205-2018** IWXXM 3.0 richest nilReason tables + CRS) lives at [WMO-306-vI-3-2019-upd-2021-mining-notes.md](./WMO-306-vI-3-2019-upd-2021-mining-notes.md) · #798. Treat as historical; this 2023 dig remains the preferred Manual I.3 cite path before vendor pin.

---

## Document map (FM 205)

Volume I.3 is entirely **Part D** (XML / data-model representations). FM 205 is the IWXXM family; the manual retains historical requirements classes for older IWXXM lines:

| FM subsection | Approx. PDF pages | Role for this project |
|---|---|---|
| General §3.2 Nil reasons | ~28 | Global nilReason vocabulary (Code table D-1) |
| FM 205-15 EXT (IWXXM ~1.1) | ~66–120 | Early METAR/SPECI + NIL report rules |
| FM 205-16 (IWXXM ~2.1) | ~120–155 | Same pattern; `@status` NORMAL / MISSING / CORRECTION |
| FM 205-2018 (IWXXM 3.0-era) | ~155–210 | **Richest nilReason field rules** for METAR/SPECI/TAF |
| FM 205-2021-2 | ~210–225 | Version/resources bridge |
| FM 205-2023-1 (IWXXM 2023-1) | ~225–230 | Scope + package versions; **defers detail to online schemas** |
| Appendix A code tables D-1… | ~237+ | Nil reasons, quantity kinds, IWXXM code tables D-4… |

**Important for F4 (version handling):** FM **205-2023-1** does **not** reprint the full requirements-class tables. It points to:

- Schemas: `https://schemas.wmo.int/iwxxm/2023-1/` (incl. `metarSpeci.xsd`)
- Schematron: `…/2023-1/rule/iwxxm.sch`
- Examples + TAC→XML guidance: `…/2023-1/examples/`
- UML: published alongside

Annex 3 amendment mapping in the manual (excerpt): Amendment 79 → IWXXM **2023-1** with METAR/SPECI package **3.1.0**.

---

## Code table D-1 — nil reasons (canonical)

Regulation **§3.2**: where permitted, use Code table D-1 to explain a missing/void GML value.  
Registry: `http://codes.wmo.int/common/nil`  
URI form = code-space + notation (e.g. `http://codes.wmo.int/common/nil/missing`).

| Label | Notation | Typical METAR/SPECI use (from FM 205 req classes) |
|---|---|---|
| Above detection range | `AboveDetectionRange` | Instrument over-range (less common in METAR body) |
| Below detection range | `BelowDetectionRange` | Instrument under-range |
| Inapplicable | `inapplicable` | Clear-sky / no applicable cloud base when CAVOK absent; older NOSIG trend pattern |
| Missing | `missing` | NIL report; trend BECMG/TEMPO without time; TAF NIL `baseForecast` |
| No significant change (NOSIG) | `noSignificantChange` | Empty `trendForecast` when NOSIG |
| Nothing detected by automated system | `notDetectedByAutoSystem` | Auto CB/TCU amount/base not detected (`NCD`-class) |
| Not observable | `notObservable` | Sensor failure / obstruction (temp, dewpoint, QNH, vis, RVR, weather, cloud, cloudType…) |
| Nothing of operational significance | `nothingOfOperationalSignificance` | NSW / NSC (`weather` or `cloud` empty); runway deposit depth insignificant |
| Template | `template` | Value to be filled later |
| Unknown | `unknown` | Value unknown but probably exists |
| Withheld | `withheld` | Value not divulged |

---

## METAR / SPECI encoding rules (FM 205)

### Product identity

- **METAR** = routine aerodrome report at fixed intervals (`iwxxm:METAR` extends meteorological aerodrome observation report).
- **SPECI** = special report when criteria met (`iwxxm:SPECI`); same parameter set as METAR (manual notes SPECI may include QFE when applicable).
- Both depend on requirements class **meteorological aerodrome observation report** (plus extension class in 3.0-era tables).

### Report `@status` / NIL reports

Pattern across 1.1 / 2.1 / 3.0-era tables:

1. Report status is one of **`NORMAL`**, **`MISSING`**, **`CORRECTION`** (wording varies slightly by revision; notes equate MISSING to a “NIL” routine report).
2. When status is **MISSING** (NIL report):
   - Observation **result empty** + **`nilReason`** on the result (1.1/2.1: “appropriate” nil reason).
   - **IWXXM 3.0-era** is explicit: `@nilReason = http://codes.wmo.int/common/nil/missing`, and **`trendForecast` absent / not used**.
   - `@automatedStation` absent (1.1/2.1 NIL rules).
3. Notes: MISSING = routine report not provided on anticipated timescale (“NIL” report). CORRECTION/CORRECTED = amended content for a prior error.

### Trend / NOSIG

- ≤ **3** trend forecasts when present.
- **NOSIG**: empty `trendForecast` with  
  `@nilReason = http://codes.wmo.int/common/nil/noSignificantChange` (3.0-era).  
  Older 1.1/2.1 recommendation used **`inapplicable`** for NOSIG — prefer the version’s schema/schematron in force.
- BECMG/TEMPO **without specified time** → empty `phenomenonTime` with `@nilReason = …/missing` (and related uncertain-time variants).

### Observation fields — nil / omission (3.0-era, highly relevant)

| Situation | Encoding |
|---|---|
| Air temp / dewpoint / QNH not observable | Element with `@xsi:nil="true"`, `@uom="N/A"`, `@nilReason=…/notObservable` |
| Visibility / RVR not observable | Same pattern on `visibility` / `rvr` |
| Present weather not observable | Empty `presentWeather` + `@nilReason=…/notObservable` |
| Present weather reported | `@xlink:href` into **Code table D-7**; ≤ 3 codes |
| Recent weather | D-6 URIs; ≤ 3 codes |
| Auto CB/TCU but amount/base not observed | Empty `cloud/layer` (or `layer/base`) + `notObservable` **or** `notDetectedByAutoSystem` |
| Cloud type not observable by auto | Empty `cloudType` + `notObservable` |
| Clear sky, not CAVOK | Empty `cloud` or `base` + `inapplicable` |
| **CAVOK** | `@cloudAndVisibilityOK="true"`; **omit** `visibility`, `rvr`, `presentWeather`, `cloud` |
| Forecast NSW | Empty `weather` + `nothingOfOperationalSignificance` |
| Forecast / trend NSC | Empty `cloud` + `nothingOfOperationalSignificance` |
| Forecast vertical visibility N/A | Element **missing with no nilReason** (explicit non-use of nil) |
| Visibility > 10 km | Numeric `10000` + operator `ABOVE` |

Reporting obligations for *when* to include RVR, weather, etc. remain in **WMO-No. 49 Vol. II / ICAO Annex 3** — FM 205 specifies the **XML encoding**, not the observing regulations themselves.

### Code tables called out for METAR/SPECI

| Table | Topic | Online registry (as cited) |
|---|---|---|
| D-1 | Nil reasons | `http://codes.wmo.int/common/nil` |
| D-4 | IWXXM observation types | (appendix; version-split tables) |
| D-5 | Observable properties | appendix |
| D-6 | Aerodrome recent weather | `http://codes.wmo.int/49-2/AerodromeRecentWeather` |
| D-7 | Present/forecast weather | `http://codes.wmo.int/49-2/AerodromePresentOrForecastWeather` |
| D-8 | Cloud amount at aerodrome | appendix |
| D-9 | Significant convective cloud type | appendix |
| D-10 | Significant weather phenomena | appendix |

---

## F6 product map (TAC input → IWXXM output)

Richest printed encoding tables are under **FM 205-2018**. FM **205-2023-1** (PDF pp. 225–230) lists products and defers machine detail to `https://schemas.wmo.int/iwxxm/2023-1/`. Full matrices are on [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719).

| F6 product | IWXXM root | 205-2018 PDF pages (approx.) | Key encoding hooks |
|---|---|---|---|
| METAR / SPECI | `iwxxm:METAR` / `SPECI` | ~165–178 | NIL → `…/nil/missing`; NSC/NCD/CAVOK; D-6/D-7 weather |
| TAF | `iwxxm:TAF` | ~181 | CNL → `@isCancelReport` + empty forecasts; NIL → empty `baseForecast` + missing |
| SIGMET (+ TC / VA) | `iwxxm:SIGMET` / `TropicalCycloneSIGMET` / `VolcanicAshSIGMET` | ~190–194 | Phenomenon → D-10 `SigWxPhenomena`; CNL omits phenomenon+analysis |
| AIRMET | `iwxxm:AIRMET` | ~196–199 | Same cancel pattern; cloud/SFC VIS/wind members |
| TCA | `iwxxm:TropicalCycloneAdvisory` | ~199–202 | Observation/forecast legs; remarks / nextAdvisoryTime nils |
| VAA | `iwxxm:VolcanicAshAdvisory` | ~202–205 | `colourCode` → AviationColourCode; unknown/withheld/missing nils |

**Edition ladder (PDF p. 24):** 205-15 Ext = METAR/SPECI/TAF/SIGMET → 205-16 adds AIRMET/TCA/VAA → 205-2018 adds Space Wx → 205-2021-2 / 2023-1 add WAFS SIGWX.

**Callout:** AIRMET notes (p. 199) incorrectly send “D-10” to `AirWxPhenomena`; prefer 205-2023-1.4 + SIGMET notes → `SigWxPhenomena`.

### Annex 3 → package versions (205-2023-1.2.4)

| IWXXM line | METAR/SPECI | TAF | SIGMET | AIRMET | TCA | VAA |
|---|---|---|---|---|---|---|
| 3.0.0 (Amd 78) | 3.0.0 | 3.0.0 | 3.0.0 | 3.0.0 | 3.0.0 | 3.0.0 |
| 2021-2 (Amd 79) | 3.1.0 | 3.0.1 | **4.0.0** | 3.1.0 | 3.1.0 | 3.1.0 |
| 2023-1 (Amd 79) | 3.1.0 | 3.0.1 | **4.0.0** | **3.1.1** | 3.1.0 | 3.1.0 |

---

## Implications for this repo

- **F1/F6 conversion:** NIL/CNL and field-level nilReasons for **all** F6 products must use D-1 URIs — not free text. Hazard products need D-10 phenomenon hrefs; VAA needs AviationColourCode.
- **F2 validation:** Prefer version-pinned XSD + Schematron under `vendor/schemas/` / `schemas.wmo.int` for the selected IWXXM line (`v2025-2` today); this manual’s requirements classes are historical/normative prose, not a substitute for live Schematron.
- **F4:** Treat **205-2023-1** as the index into package versions; keep detailed encoding checks against the schema line in use (many detailed nil/CNL rules still appear under the **205-2018 / IWXXM 3.0** requirements text).
- **#719 catalog:** Cite this volume for IWXXM modelling / conversion provenance; cite Annex 3 / WMO-No. 49 for TAC observing/template rules this PDF does not reprint.

---

## Local extract index

| Extract | Contents |
|---|---|
| `extracts/general_nil_and_ids.txt` | §3 identifiers + nil reasons intro |
| `extracts/fm205_*_*.txt` | Per FM subsection page dumps |
| `extracts/fm205_2018_taf_sig_airmet_vaa_tca.txt` | 205-2018 TAF→SWX product pages |
| `extracts/fm205_2023_1_full.txt` | Scope + package table + code-list URLs |
| `extracts/nilreason_mentions.txt` | All pages mentioning nilReason / D-1 |
| `extracts/metar_speci_mentions.txt` | Pages with METAR/SPECI |
| `extracts/nil_and_status_rules.txt` | Status / NIL / field nil clusters |
| `extracts/code_tables_d1_nil.txt` | Appendix D-1… |
| `extracts/code_tables_d4_d10.txt` | IWXXM weather/cloud tables |

---

## Suggested next mining passes

1. Diff **vendor `iwxxm` v2025-2 Schematron** against the 3.0-era nilReason/CNL tables above.
2. Mine **Code table D-10** (`SigWxPhenomena`) for SIGMET/AIRMET TAC phenomenon ↔ URI mapping in `tac2iwxxm`.
3. ~~Catalog paywalled ICAO Annex 3 / Doc 8896 URLs~~ — done in [TAC_VALIDATION.md](../TAC_VALIDATION.md) / [RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) (WMO-No. 49 Vol II SARPs discontinued → Annex 3).
4. Prefer live TAC→XML guidance under `https://schemas.wmo.int/iwxxm/2025-2/examples/` over OCR of this PDF for day-to-day convert recipes.
