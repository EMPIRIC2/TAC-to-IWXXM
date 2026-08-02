# TAC validation

**Purpose:** Authoritative URLs for **validating TAC inputs** (templates, business rules, vocabularies) for F6 products under profile **`annex3`**, plus pointers for **`iwxxm_us`**.  
**Ticket:** [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719) · feeds [#698](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/698).  
**Not in scope:** implementing validators; IWXXM XML validation (see [IWXXM_VALIDATION.md](IWXXM_VALIDATION.md)).

Hub: [README.md](README.md) · URL catalog: [rules/RULE_SOURCE_URLS.md](rules/RULE_SOURCE_URLS.md) · Mining digs: [mining/](mining/)

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

## Validation strategy (TAC / Annex 3)

Pipeline placement: **stage 1** of the domain E2E flow ([README.md](README.md)
§End-to-end strategy). Run **before** convert; never treat XSD/Schematron as a TAC
substitute.

### Layered approach (recommended)

| Layer | What to check | Public / offline path | When paywall Annex 3 is required |
|-------|---------------|----------------------|----------------------------------|
| **L1 — Product / report type** | METAR vs SPECI vs TAF vs …; NIL/AMD/COR/CNL shape | Official `.tac` examples under `/iwxxm/2025-2/examples/` | SPECI issue criteria, TAF change thresholds, SIGMET validity windows |
| **L2 — Group order & presence** | Groups required by product template | Example pairs + Table cites (A3-2, A5-1, A6-1A, A2-*) | Full SARP must/shall presence rules |
| **L3 — Token membership** | Weather, cloud, phenomena spellings | **codes.wmo.int** + vendor RDF snapshots | Colour *meanings* (Doc 9766); national REMARKS |
| **L4 — Business thresholds** | SPECI shall vs Rec; TAF FM/BECMG/TEMPO/PROB; SIGMET one-phenomenon | Cite Annex 3 sections only (no full text in git) | Numeric engines need licensed PDF |
| **L5 — Profile overlay** | US REMARKS / national differences | FMH-1 + `codes.nws.noaa.gov` + iwxxm-us | — |

**CI / no-license fallback:** gate on **L1 + L3 + official `.tac` accept shapes**; label
L2/L4 engines that need Annex 3 prose as “requires licensed Annex 3 reference” in design
notes. Do **not** scrape Annex 3 into fixtures ([ACCESS_AND_CITATION.md](rules/ACCESS_AND_CITATION.md)).

### Profile strategies

| Profile | Primary SoT stack | Explicit non-goals |
|---------|-------------------|--------------------|
| **`annex3`** | Annex 3 (+ Doc 8896 practice) → WMO-306 Vol I.1 FM templates → codes.wmo.int | Do not invent IWXXM nilReasons here; do not use GIFTs as SoT |
| **`iwxxm_us`** | Annex 3 core + **FMH-1** REMARKS + NWS registries | Do not strip REMARKS at lint time (historical GIFTs gap) |

### Product rule routing (quick)

| Product | Strategy focus | See also |
|---------|----------------|----------|
| METAR | Template A3-2; CAVOK; AUTO/missing `/`; vocab 4678 / 49-2 | Rule citation map · **A3-2 checklist** below |
| SPECI | Same as METAR **plus** App 3 §2.3 shall/Rec thresholds (not TAF lists) | Dig §10 — do not merge SPECI↔TAF tables · **A3-2 checklist** |
| TAF | Validity / AMD / NIL / CNL; App 5 change weather; Table A5-2 | Official `taf-A5-*.tac` · **A5-1 checklist** |
| SIGMET / AIRMET | One-phenomenon; validity lead; SigWx / AirWx (+ VIS-cause) registries | Entire products outside GIFTs · **A6 checklist** |
| VAA / TCA | App 2 Tables A2-1 / A2-2 + shall IWXXM; colour via registry; Doc 9766 meanings paywall | Examples + dig §App 2 · checklists below |

### METAR / SPECI TAC lint checklist (Annex 3 Table A3-2 — paraphrase)

M/C/O = mandatory / conditional / optional. Encode nilReasons stay in
[IWXXM_CONVERSION.md](IWXXM_CONVERSION.md). Numeric SPECI **issue** thresholds are
App 3 §2.3 (not this table).

| # | Element (abbrev.) | Incl. | Lint focus |
|---|-------------------|-------|------------|
| 1 | `METAR` / `SPECI` (+ `COR`) | M | Product type |
| 2 | CCCC | M | ICAO location |
| 3 | `ddhhmmZ` | M | Observation time UTC |
| 4 | `AUTO` / `NIL` | C | AUTO; missing report → `NIL` **ends** message |
| 5 | Surface wind | M | dddff(+G) + MPS\|KT; VRB/CALM; `dddVddd`; missing digits → `/` |
| 6 | Visibility | M | Prevailing (+ dir min when required) **or** `CAVOK` |
| 7 | RVR `Rnn…` | C | When required; tendency U/D/N |
| 8 | Present weather | C | Intensity/−/+ / VC + type; AUTO unknown precip `UP` / `//` |
| 9 | Cloud / VV | M\* | FEW/SCT/BKN/OVC[+CB/TCU] / `VVnnn` / `NSC` / `NCD` — omitted under CAVOK |
| 10 | T / Td | M | `tt/td` (M for below 0) |
| 11 | QNH | M | `Qnnnn` (or national Axxxx under `iwxxm_us`) |
| 12 | Recent / wind shear / RWY state | C/O | RE…; WS; runway deposits — **2025-2 encode:** no `runwayState` |
| 13 | TREND | O | `NOSIG` / `BECMG` / `TEMPO` + FM/TL/AT (≤2 h; App 5 §2) |

\*Cloud mandatory when not CAVOK / NSC/NCD path. Footnote: TAC `/` missing → mark
**missing in IWXXM** (Guidance nilReasons — not defined in Annex 3).  
**NSC exclusivity (encode + optional lint):** do not combine `NSC` with FEW/SCT/BKN/OVC cloud layers in the same observation/forecast group — IWXXM expects NSC as empty-cloud + `nothingOfOperationalSignificance`, not layered cloud (APAC FAQ §14.3 · #797 · [IWXXM_CONVERSION](IWXXM_CONVERSION.md)). Lint may warn before convert.

**Shall IWXXM:** App 3 §**2.1.3** (dual TAC + IWXXM GML).

### TAF TAC lint checklist (Annex 3 Table A5-1 — paraphrase)

| # | Element (abbrev.) | Incl. | Lint focus |
|---|-------------------|-------|------------|
| 1 | `TAF` / `TAF AMD` / `TAF COR` | M | Type |
| 2–3 | CCCC · `ddhhmmZ` | M | Location; issue time |
| 4 | `NIL` | C | Missing forecast → ends message |
| 5 | Validity `ddhh/ddhh` | M | Period of validity |
| 6 | `CNL` | C | Cancel → ends message (`isCancelReport` on encode) |
| 7–10 | Wind · Vis/CAVOK · Weather · Cloud/VV/NSC | M/C | Base forecast; weather vocab via 4678 / 49-2 |
| 11 | TX/TN | O | Max/min T with day-hour |
| 12 | Change / PROB groups | C | `FM` / `BECMG` / `TEMPO` / `PROB30|40` [TEMPO]; NSW; App 5 §**1.3** shall vs Rec — **≠** SPECI lists |

**Shall IWXXM:** App 5 §**1.1.2**.

### SIGMET / AIRMET TAC lint checklist (Annex 3 App 6 / Table A6-1A — paraphrase)

| Concern | Lint focus |
|---------|------------|
| Identity | `SIGMET` / `AIRMET` + MWO/FIR + sequence + `VALID` period |
| One phenomenon | **Exactly one** phenomenon family per message (App 6 §1.1.4 / §2.1) |
| SIGMET tokens (examples) | OBSC/EMBD/FRQ/SQL TS[GR]; TC (+name); SEV TURB/ICE/MTW; HVY DS/SS; VA; RDOACT CLD |
| AIRMET tokens (examples) | SFC WIND/VIS(+cause); ISOL/OCNL TS; MT OBSC; BKN/OVC CLD; ISOL/OCNL/FRQ CB/TCU; MOD TURB/ICE/MTW |
| Geometry / levels | FIR/CTA + location (+ TC/VA extras); flight levels per template |
| Cancel | `CNL SIGMET|AIRMET …` (+ VA MOV TO FIR when applicable) |
| Corrections | Prefer **CNL + new** — do **not** use `COR` (not in Annex 3; unsupported in IWXXM) — [EUR Doc 014](mining/icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md) |
| Do not pair | TS (+TC) messages must **not** also describe associated TURB/ICE |

**Shall IWXXM:** App 6 §**1.1.6** (SIGMET) · §**2.1.6** (AIRMET). Href SoT: SigWx / AirWx registries.

### VAA TAC lint checklist (Annex 3 Table A2-1 — paraphrase)

M/C/O = mandatory / conditional / optional. Encode recipes stay in
[IWXXM_CONVERSION.md](IWXXM_CONVERSION.md); this table gates **TAC shape** only.

| # | Element (abbrev.) | Incl. | Lint focus |
|---|-------------------|-------|------------|
| 1 | `VA ADVISORY` | M | Product type |
| 2 | `STATUS: TEST\|EXER` | C | Ops vs test/exercise |
| 3–4 | `DTG:` · `VAAC:` | M | Issue time UTC; centre name |
| 5–8 | `VOLCANO:` · `PSN:` · `AREA:` · `SUMMIT ELEV:` | M | UNKNOWN / UNNAMED / SFC allowed |
| 9–10 | `ADVISORY NR:` · `INFO SOURCE:` | M | Year/seq; free text ≤32 |
| 11 | `AVIATION COLOUR CODE:` | O | RED/ORANGE/YELLOW/GREEN / UNKNOWN / NOT GIVEN / NIL — **machine IDs** → `iwxxm/AviationColourCode` (not Doc 9766 prose) |
| 12–14 | Eruption details · OBS/EST VA DTG · OBS/EST VA CLD | M | UNKNOWN; `VA NOT IDENTIFIABLE…` path |
| 15–17 | `FCST VA CLD +6/+12/+18 HR` | M | Or `NO VA EXP` / `NOT AVBL` / `NOT PROVIDED` |
| 18–19 | `RMK:` · next advisory | M | `NIL` remarks; next-msg time |

**Shall IWXXM:** App 2 §**3.1.2** (dual TAC/plain + IWXXM GML).

### TCA TAC lint checklist (Annex 3 Table A2-2 — paraphrase)

| # | Element (abbrev.) | Incl. | Lint focus |
|---|-------------------|-------|------------|
| 1–2 | `TC ADVISORY` · `STATUS:` | M / C | Same TEST/EXER rule as VAA |
| 3–6 | `DTG:` · `TCAC:` · `TC:` · `ADVISORY NR:` | M | `TC: NN` for unnamed |
| 7–12 | OBS PSN · CB (O) · MOV · INTST CHANGE · C · MAX WIND | M (CB O) | Issue **only if** max 10-min mean wind ≥ **34 kt** (17 m/s) expected (§**5.1.1**); CB may be `NIL` |
| 13–20 | FCST PSN / MAX WIND +6/+12/+18/+24 HR | M | Fixed valid times from DTG |
| 21–22 | `RMK:` · `NXT MSG:` | M | `NIL` / `NO MSG EXP` |

**Shall IWXXM:** App 2 §**5.1.3**.

### Fail-closed vs advisory

| Class | Examples | Lint stance |
|-------|----------|-------------|
| **Hard reject** | Unknown product; illegal weather token vs registry; malformed NIL/CNL vs official example | Block convert |
| **Advisory / needs Annex 3** | SPECI shall thresholds; TAF Recommended vis steps; SIGMET lead-time windows | Warn or gate behind licensed ruleset |
| **Out of scope for `tac-validate`** | XML well-formed; XSD; Schematron; encode mapping | Post-convert via [IWXXM_VALIDATION.md](IWXXM_VALIDATION.md) / [IWXXM_CONVERSION.md](IWXXM_CONVERSION.md) |

### OPMET translator pre-condition (public)

[OPMET IWXXM Exchange Guidelines 5th Ed.](mining/OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md)
§5.3.2: validate TAC against **Annex 3 / WMO-No. 306 Vol I.1** before / as part of translation
compliance; IWXXM against the **most recent** official schema + Schematron unless bilaterally
agreed otherwise. Domain CI without licensed Annex 3 still follows L1+L3+official `.tac`
above — do not scrape SARP prose into fixtures.

---

## Normative SARPs & practice (Annex III family)

### ICAO Annex 3

| Field | Value |
|-------|-------|
| Title | Annex 3 — Meteorological Service for International Air Navigation |
| Publisher | ICAO |
| URL | https://store.icao.int/en/annex-3-meteorological-service-for-international-air-navigation-1 |
| Listing | https://store.icao.int/en/annexes/annex-3 |
| Access | **Paywall** — cite only ([ACCESS_AND_CITATION.md](rules/ACCESS_AND_CITATION.md)) |
| Label | normative |
| Products | METAR · SPECI · TAF · SIGMET · AIRMET · VAA · TCA |
| Local dig | [mining/icao-annex-3-mining-notes.md](mining/icao-annex-3-mining-notes.md) — **20th Ed. (2018) + Amd through 81**; store **21st Ed.** claim unverified |

**Use for validation rules that are not “XML encoding”:**

- Report types and issue criteria (e.g. SPECI thresholds — App 3 §2.3; Ch.4 §4.4)
- Contents / element order of aerodrome observations (Ch.4 §4.5; Table **A3-2**)
- TAF change groups / AMD / NIL / CNL (App 5 · Table **A5-1**)
- SIGMET / AIRMET templates and one-phenomenon rule (App 6 · Table **A6-1A**)
- VAA / TCA advisory templates (App 2 · Tables **A2-1** / **A2-2**)
- Observing and reporting obligations that FM 205 / IWXXM XSD **do not** redefine

**IWXXM dual exchange (obligation only):** Annex 3 requires F6 products **shall** be disseminated in IWXXM GML **in addition to** TAC/plain language, with encoding deferred to WMO-No. **306 Vol I.3 Part D** and Doc **10003**. Runtime encode/validate still follows `vendor/manifest.json` pin — not Annex 3 tables.

**Rule citation map** (paraphrase only; numeric engines need licensed PDF — dig pass 2):

| Lint / rule family | Primary cite | Notes |
|--------------------|--------------|-------|
| SPECI issue gate | Ch.4 §4.4.2 · App 3 §2.3 | Not required if METAR half-hourly |
| SPECI **shall** thresholds | App 3 §**2.3.2** | Wind 60°/5 m·s⁻¹ family; selected weather onset; cloud SCT↔BKN below 450 m |
| SPECI **Recommendation** thresholds | App 3 §**2.3.3** | Vis 800/1500/3000/(5000); RVR 50/175/300/550/800; more weather; cloud base/VV |
| SPECI dissemination timing | App 3 §3.1.3–3.1.4 | Deterioration immediate; improvement ~10 min Rec |
| CAVOK | App 3 §2.2 · Ch.1 “cloud of operational significance” | Replaces vis/RVR/WX/cloud groups |
| METAR/SPECI template · AUTO/missing | Table **A3-2** | `/` for missing → also IWXXM missing (footnote) |
| TAF validity / single valid | Ch.6 §6.2.6–6.2.7 | 6–30 h Rec; ≤1 TAF per aerodrome |
| TAF change/AMD weather (**shall**) | App 5 §**1.3.1** | Freezing fog/precip; mod/heavy precip; TS; DS/SS |
| TAF change thresholds (**Rec**) | App 5 §**1.3.2** · Table **A5-2** | Vis steps **≠** SPECI list (includes 150/350/600); FM/BECMG/TEMPO/PROB |
| Landing TREND | Ch.6 §6.3 · App 5 §2 | 2 h; NOSIG; BECMG/TEMPO + FM/TL/AT |
| SIGMET/AIRMET validity & lead | Ch.7 §7.1–7.2 | ≤4 h (VA/TC SIGMET ≤6 h); issue windows |
| SIGMET/AIRMET phenomena · CNL | App 6 §1.1 / §2.1 · Table **A6-1A** | One phenomenon; no TS+TURB/ICE pairing |
| VAA template · IWXXM shall | App 2 §**3.1.2** · Table **A2-1** | Colour column: RED/ORANGE/YELLOW/GREEN/UNKNOWN/NOT GIVEN/NIL — machine IDs → `iwxxm/AviationColourCode` |
| TCA issue gate · template · IWXXM shall | App 2 §**5.1.1** (≥34 kt) · §**5.1.3** · Table **A2-2** | Dual TAC/plain + IWXXM |
| SWX advisory (optional) | App 2 §**6.1.2** · Table **A2-3** | shall IWXXM; beyond F6 core unless enabled |

Do **not** merge SPECI and TAF threshold tables — Annex 3 keeps parallel but distinct lists ([mining dig](mining/icao-annex-3-mining-notes.md) §10).

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

### ICAO EUR Doc 014 — EUR SIGMET and AIRMET Guide (5th Ed. 2023)

| Field | Value |
|-------|-------|
| Title | EUR SIGMET and AIRMET Guide |
| URL | https://www.icao.int/sites/default/files/EURNAT/Documents/EUR%20and%20Nat%20Docs/EUR%20Documents/EUR%20Documents/014%20-%20EUR%20SIGMET%20and%20AIRMET%20Guide/EUR-Doc-14-EN-5th-Ed-2023-rev-Dec23-clean.pdf |
| Access | **Public** |
| Label | normative-conversion-notes (regional); Annex 3 remains SARPs SoT |
| Use | Public companion for **A6 checklist**: WMO AHL (`WS`/`WV`/`WC`/`WA`), first-line `VALID`, sequence forms, CNL, **no `COR`**, validity caps, App A abbreviations, App C examples |
| Notes | [mining/icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md](mining/icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md) · local 90-page extract under `.local/reference/icao-eur-doc-14-sigmet-airmet-2023/` |

### ICAO Doc 10003 (encode / exchange — not primary TAC SARPs)

| Field | Value |
|-------|-------|
| Title | Manual on the Digital Exchange of Aeronautical Meteorological Information |
| URL | https://store.icao.int/en/manual-on-the-icao-meteorological-information-exchange-model-doc-10003 |
| Access | **Paywall** (published); Advance 2014 draft mined locally — notes only |
| Label | normative (published); informative/historical (Advance 2014 draft) |
| Use for `tac-validate` | Indirect — early draft lists IWXXM-permissible METAR present/recent weather **combinations** (encode-side); **do not** re-home Annex 3 TAC rules from Doc 10003. Prefer Annex 3 + `codes.wmo.int/306/4678` |
| Notes | [mining/ICAO-Doc-10003-draft-2014-mining-notes.md](mining/ICAO-Doc-10003-draft-2014-mining-notes.md) |

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

Offline RDF (pin-aligned): `vendor/schemas/iwxxm/2025-2/IWXXM/rule/codes.wmo.int-*.rdf` (also mirrored under repo-root `IWXXM/rule/` in some layouts).

---

## Official TAC fixtures (accept / reject shapes)

Use WMO official examples as golden TAC for gates — not proprietary corpora:

| Product | Example TAC prefix (`schemas.wmo.int/iwxxm/2025-2/examples/`) |
|---------|----------------------------------------------------------------|
| METAR | `metar-A3-1.tac`, NIL collect, `metar-translation-failed` |
| SPECI | `speci-A3-2.tac` |
| TAF | `taf-A5-1.tac`, cancel `taf-A5-2.tac` |
| SIGMET | `sigmet-A6-1a-TS.tac`, CNL, TC (`sigmet-A6-2-TC`), VA |
| AIRMET | `airmet-A6-1a-TS.tac` |
| VAA | `va-advisory-A7-2.tac` |
| TCA | `tc-advisory-A2-2.tac` |
| SWXA | `spacewx-A7-3/4/5.tac` (+ translation-failed) — **F28 / EV-029 M11** |

AHL data type designators (TAC vs IWXXM) — page **v1.0.1** (2025-08-11):  
https://community.wmo.int/en/activity-areas/wis/iwxxm/ahl-icao-data  
(**301 →** https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/wmo-information-system-wis/about-manual-gts/ahls-aviation-data-over-icao-afs — live 200 as of 2026-07-14; **re-confirmed 2026-08-01**).  
Canonical `T1T2` / BBB / filename: [IWXXM_CONVERSION.md §AHL / bulletin](IWXXM_CONVERSION.md#ahl--bulletin-canonical-ev-029).

Additional (informative) pairs: https://github.com/wmo-im/iwxxm-translation — Amd79-80-2023 trees cover **METAR / TAF / VAA / TCA** only (no SIGMET/AIRMET dirs). Prefer official `iwxxm` examples for F6 gates. Local Tier A mine: [mining/wmo-im-tier-a-mining-notes.md](mining/wmo-im-tier-a-mining-notes.md).

---

## US profile (`iwxxm_us`) — Annex 3 differences

| Resource | URL | Use |
|----------|-----|-----|
| FMH-1 (2019) | https://www.icams-portal.gov/resources/ofcm/fmh/FMH1/fmh1_2019.pdf | Surface obs / METAR REMARKS coding — [mining dig](mining/fmh1-2019-mining-notes.md) |
| FMH index | https://www.icams-portal.gov/resources/ofcm/fmh/allfmh2.htm | Related handbooks |
| NWS FMH-1 registry | https://codes.nws.noaa.gov/FMH-1 | Machine tables (probe **timed out** 2026-07-14) |
| iwxxm-us 3.0 | https://nws.weather.gov/schemas/iwxxm-us/3.0/ | National encode/validate surface |
| MDL data modeling | https://vlab.noaa.gov/web/mdl/data-modeling | Context for US extensions |

GIFTs historically stripped REMARKS — **US profile validation is a first-class gap** this catalog fills.

### US METAR/SPECI strategy (FMH-1)

| Layer | Rule (paraphrase) | Lint / encode stance |
|-------|-------------------|----------------------|
| Body order | type → CCCC → time → AUTO/COR → wind **KT** → vis **SM** → RVR **FT** → weather → sky → T/Td → altimeter **A** | Profile-aware token parse |
| Missing data | Omit missing group + preceding space (§12.5) | **≠** Annex 3 `/` → nilReason path |
| SPECI criteria | §**2.5.2.a** miles/feet list below | **Do not merge** with Annex 3 App 3 §2.3 |
| REMARKS | After `RMK`: §12.7.1 plain/auto (AO1/AO2, PK WND, SLP, …) + §12.7.2 additive (`T…`, precip, `$`) | **Hard keep** — never strip; map to iwxxm-us `extension` |
| Clear sky | SKC / CLR | Differ from NSC/NCD/CAVOK annex3 patterns |

#### US REMARKS keep-list → iwxxm-us (paraphrase)

Lint: retain the full `RMK` string and known structured tokens. Encode maps into
`iwxxm-us` **`extension` / Addendum** (not ICAO `iwxxm:`). Element names from vendored
`vendor/schemas/iwxxm-us/3.0/metarSpeci.xsd` (+ `common.xsd`).

| FMH token / family (§12.7) | iwxxm-us target (typical) |
|----------------------------|---------------------------|
| `AO1` / `AO2` | `observingSystemType` → `codes.nws.noaa.gov/FMH-1/ObservingSystemType` |
| `PK WND` | `AerodromePeakWind` |
| `WSHFT` | `AerodromeWindShift` |
| Variable / sector VIS · variable RVR | sector / `AerodromeVariableRVR` families |
| Lightning · tornadic · volcanic plain language | `ObservedLightning` / visually-observable / `humanReadableText` |
| `PRESRR` / `PRESFR` | `pressureChangeIndicator` → FMH-1 `PressureChangingRapidly` vocab |
| `SLPppp` / `SLPNO` | `seaLevelPressure` (nillable) |
| `SNINCR` / snow depth | `snowIncrease` / `snowDepth` |
| Additive `T…` / 1/2/4 max-min / `5appp` | `maxMinTemperatures` / `pressureTendency*` |
| Precip additive `P` / `6` / `7` | `processedQuantity` |
| `$` maintenance | `maintenanceIndicator` |
| Unparsed plain language | `Remarks/freeText` or `humanReadableText` — **never drop** |

NWS machine tables may be unreachable (`codes.nws.noaa.gov/FMH-1` timeout 2026-07-14) —
keep URL cites; do not invent concept URIs.

#### US SPECI issue criteria (FMH-1 §2.5.2.a — paraphrase)

Use for profile **`iwxxm_us` only**. Applicable only when the station can evaluate the event
(e.g. tornadic visual criteria do not apply to non-staffed AUTO). Make SPECI ASAP after criteria.

| # | Trigger | Threshold sketch |
|---|---------|------------------|
| 1 | Wind shift | Dir Δ ≥ **45°** in &lt; **15 min** and speed ≥ **10 kt** throughout |
| 2 | Visibility | Crosses **3 / 2 / 1** statute mi (or published approach min; else **½** mi) |
| 3 | RVR | Highest designated RVR crosses **2,400 ft** (preceding 10 min); military may skip |
| 4 | Tornado / funnel / waterspout | Observed or disappears/ends |
| 5 | Thunderstorm | Begins or ends (no new-TS SPECI if one already reported) |
| 6 | Precipitation | Hail begin/end; freezing precip / ice pellets / snow begin/end/intensity |
| 7 | Squalls | When squalls occur |
| 8 | Ceiling | Forms/dissipates/crosses **3000 / 1500 / 1000 / 500** ft (or approach min; else **200** ft) |
| 9 | Sky | Layer/obscuration aloft **below 1000 ft** newly present vs prior METAR/SPECI |
| 10–12 | Volcano / mishap / misc | First noted eruption; mishap unless intervening obs; agency/observer-critical |

Local PDF + Ch.12 carve: `.local/reference/fmh1-2019/` (gitignored).

---

## Product checklist for #698 design Q3

| Product | Minimum normative cite for TAC validation |
|---------|-------------------------------------------|
| METAR | Annex 3 (paywall) **or** registry weather/cloud + official `.tac` + **A3-2 checklist** |
| SPECI | Annex 3 SPECI criteria + same vocab as METAR + **A3-2 checklist** |
| TAF | Annex 3 / Doc 8896 + examples (AMD/CNL/NIL) + **A5-1 checklist** |
| SIGMET | Annex 3 + SigWxPhenomena + examples + **A6 one-phenomenon** |
| AIRMET | Annex 3 + AirWxPhenomena + VIS-cause + **A6** |
| VAA | Registry colour codes + official VAA examples; Annex 3 App 2 §3.1.2 **shall** IWXXM + Table **A2-1** (local dig); Doc 9766 for colour **meanings** (paywall) |
| TCA | Official TCA examples; Annex 3 App 2 §5.1.3 **shall** IWXXM + Table **A2-2** (issue gate ≥34 kt §5.1.1) |

If paywalled prose is unavailable in CI, gate on **public vocab + official TAC examples**, and label SARPs-derived lint as “requires Annex 3 licensed reference” in design notes.

---

## Related domain docs

- Implementation layers (post-convert IWXXM): [COMPREHENSIVE_VALIDATION.md](validation/COMPREHENSIVE_VALIDATION.md)
- Failure taxonomy: [FAILURE_TAXONOMY.md](validation/FAILURE_TAXONOMY.md)
- IWXXM creation (encode): [IWXXM_CONVERSION.md](IWXXM_CONVERSION.md)
- Informative workshop framing (TAC still used for **presentation**; plans for TAC sunset ~2030; AHL bulletin heading): [mining/PPT-02-IWXXM-Framework-WMO-mining-notes.md](mining/PPT-02-IWXXM-Framework-WMO-mining-notes.md) — **not** a TAC SARP substitute; classic TAC template limits (e.g. ≤4 RVR) do **not** cap IWXXM encode capacity
