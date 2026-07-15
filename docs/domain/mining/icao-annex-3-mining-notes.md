# ICAO Annex 3 — focused mining notes

**Status:** working notes (not normative). Cite section numbers / paraphrases only — no full SARP text in git ([ACCESS_AND_CITATION.md](../rules/ACCESS_AND_CITATION.md)).  
**Focus of this pass:** **Pass 2 (deeper)** — SPECI §2.3 shall vs Recommendation thresholds · CAVOK · METAR AUTO/missing → IWXXM · TREND landing forecasts · TAF change/PROB/FM · SIGMET/AIRMET phenomenon lists + validity windows · SPECI↔TAF parallel criteria  
**Prior pass:** F6 product map · IWXXM dual-dissemination **shall** · edition identity  
**Local PDF + extracts (gitignored):** `.local/reference/icao-annex-3/`  
**Date mined:** 2026-07-14 (pass 1 + pass 2)

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
| Title | Annex 3 — Meteorological Service for International Air Navigation |
| Publisher | ICAO |
| Official landing | <https://store.icao.int/en/annex-3-meteorological-service-for-international-air-navigation-1> |
| Listing | <https://store.icao.int/en/annexes/annex-3> |
| Pin / edition (this PDF) | **Twentieth Edition, July 2018** + amendments recorded through **No. 81** (applicable **28 Nov 2024**) |
| Pages | 220 (extract) |
| Local text | `.local/reference/icao-annex-3/fulltext.txt` |
| Access | **paywall** (user-supplied PDF local-only; do not redistribute) |
| Label | **normative** (SARPs) |
| Vendor pin (runtime XML) | `vendor/manifest.json` → `iwxxm` **v2025-2** (encode/validate SoT — not this PDF) |

---

## What this source is / is not

| Is | Is not |
|----|--------|
| ICAO **Standards and Recommended Practices** for aeronautical MET content, issue criteria, TAC templates (Part II appendices), and **shall** IWXXM GML dissemination for F6 products | IWXXM XSD / Schematron SoT (use `schemas.wmo.int/iwxxm/<pin>/`) |
| Pointer notes that IWXXM technical specs live in **WMO-No. 306 Vol I.3 Part D** and implementation guidance in **Doc 10003** | Alphanumeric code-form detail beyond Annex 3 tables (still use WMO-No. **306 Vol I.1** + `codes.wmo.int`) |
| Consolidated 20th edition body with Amd **79–81** reflected in Table A / amendment record / page slips | Confirmed identity with ICAO Store **21st Edition (Aug 2025)** marketing — **verify separately** |
| Relation statement (foreword) that Annex 3 aligned with WMO-No. 49 Vol II Parts I–II | Current WMO policy after **31 Dec 2023** discontinuation of those Parts — **defer** to WMO discontinuation notice + Annex 3 as SARP SoT |

---

## Document map (F6-relevant)

| Section | Approx. PDF pages | Relevance |
|---------|-------------------|-----------|
| Cover / ISBN / edition | 1–4 | 20th Ed. July 2018; Order AN 3 |
| Record of amendments | 5 | Amd 1–78 in edition; **79** (5/11/20 + 4/11/21), **80**, **81** (28/11/24) |
| TOC | 7–11 | Ch.4 reports · Ch.6 forecasts · Ch.7 SIGMET/AIRMET · Apps 2–6 |
| Foreword + Table A | 13–27 | Amd history: **77-A** digital Recommended Practice; **78** IWXXM mods; **79** IWXXM among subjects |
| Ch.1 Definitions | ~28–35 | **IWXXM**; **cloud of operational significance** |
| Ch.4 Observations & reports | 45–56 | METAR / SPECI issue; element order; SPECI when half-hourly METAR not used |
| Ch.6 Forecasts | 57–59 | TAF validity/issue cadence; **landing TREND** (2 h); take-off forecasts |
| Ch.7 SIGMET & AIRMET | 61–62 | Validity ≤4 h (VA/TC ≤6 h); cancel; lead times |
| App 2 (centres) | ~95–99 | VAA · TCA · SWX **shall** IWXXM GML; Tables A2-1 / A2-2 / A2-3 |
| App 3 (observations) | 111–~148 | CAVOK; SPECI §2.3; Table A3-2; TREND in METAR; AUTO/missing |
| App 5 (forecasts) | 149–160 | TAF elements; change/PROB; Tables A5-1 / A5-2; TREND forecast rules §2 |
| App 6 (SIGMET/AIRMET) | 167–185 | Phenomena lists; ISOL/OCNL/FRQ/SQL; Tables A6-1A…; CNL |
| Attachment C | 213 | Guidance table relating Ch.4 / App 3 report criteria (not stand-alone SoT) |

---

## Product × artifact matrix

| Product | TAC input (Annex 3) | IWXXM output (Annex 3 obligation) | Official example / encoding SoT | Gap vs GIFTs | Consumer |
|---------|---------------------|-----------------------------------|-----------------------------------|--------------|----------|
| METAR (+ optional TREND) | Ch.4 · App 3 · Table **A3-2**; TREND App 5 §2 / Ch.6 §6.3 | **shall** IWXXM GML (App 3 §2.1.3); missing → IWXXM missing note in template footnote | WMO 306 I.3 + Doc 10003; `metarSpeci.xsd` @ v2025-2 | GIFTs METAR-centric; REMARKS national; TREND depth TBD in GIFTs | `tac-validate`, `tac2iwxxm` |
| SPECI | Ch.4 §4.4 · App 3 §**2.3** · Table A3-2 | same | same | SPECI thresholds outside GIFTs | `tac-validate` |
| TAF | Ch.6 · App 5 · Table **A5-1** / **A5-2** | **shall** IWXXM (App 5 §1.1.2) | `taf.xsd` | Outside GIFTs depth | both |
| SIGMET | Ch.7 · App 6 · Table **A6-1A** | **shall** IWXXM (App 6 §1.1.6) | `sigmet.xsd` | Entire product outside GIFTs | both |
| AIRMET | Ch.7 · App 6 · Table A6-1A | **shall** IWXXM (App 6 §2.1.6) | `airmet.xsd` | Entire product outside GIFTs | both |
| VAA | App 2 §3 · Table **A2-1** | **shall** IWXXM (App 2 §3.1.2) | `volcanicAshAdvisory.xsd` (+ METCE) | Entire product outside GIFTs | both |
| TCA | App 2 §5 · Table **A2-2** | **shall** IWXXM (App 2 §5.1.3) | `tropicalCycloneAdvisory.xsd` (+ METCE) | Entire product outside GIFTs | both |
| SWX (extra) | App 2 §6 · Table A2-3 · Att E | **shall** IWXXM | space-weather package if in pin | Out of F6 core unless ticket expands | optional |

---

## Key findings

### 1. Edition identity vs store marketing

- Cover: **Twentieth Edition, July 2018**; supersedes previous on **8 November 2018** (PDF p.1).
- Amendment record lists **79–81** with applicability through **28 November 2024** (PDF p.5; Table A through ~p.27).
- Visible amendment slips in body: e.g. App 3 SPECI **No. 79** (PDF p.112); App 5 TAF visibility **No. 81** (PDF p.149); Att E **No. 79** (PDF p.217).
- Store **21st Edition (Aug 2025)** listing remains **unverified** against this binary.

### 2. IWXXM dissemination is Standard (“shall”), dual with TAC

METAR/SPECI, TAF, SIGMET, AIRMET, VAA, TCA (and SWX): **shall** be disseminated in IWXXM GML **in addition to** TAC/plain language. Notes → **WMO-No. 306 Vol I.3 Part D** + **Doc 10003**.

Amd **77-A**: digital exchange largely Recommended Practice; Amd **79** subjects include IWXXM upgrades matching current **shall** language.

### 3. Definitions that gate CAVOK / cloud lint

**Cloud of operational significance** (Ch.1): base below **1 500 m (5 000 ft)** or below highest **minimum sector altitude**, whichever greater; **or** CB / TCU **at any height**.

### 4. CAVOK (App 3 §2.2) — shall replace groups

When **simultaneously**: (a) vis **≥ 10 km** and lowest vis not reported; (b) no cloud of operational significance; (c) no significant aviation weather per App 3 §§4.4.2.3 / 4.4.2.5 / 4.4.2.6 → replace vis, RVR, present weather, and cloud groups by **CAVOK** in all aerodrome reports.

### 5. SPECI issuance — shall vs Recommendation (App 3 §2.3)

**Gate:** SPECI for dissemination beyond origin **unless** METAR half-hourly (Ch.4 §4.4.2 b). Local-special list (§2.3.1) includes operator minima, ATS needs, **ΔT ≥ 2°C**, Table A3-1 approach/climb-out, noise-abatement gust rule, **and** SPECI criteria.

| Class | § | Rule sketch (paraphrase — verify against licensed PDF) |
|-------|---|--------------------------------------------------------|
| **Shall** | 2.3.2 a | Wind dir Δ ≥ **60°**, mean speed before/after ≥ **5 m/s (10 kt)** |
| **Shall** | 2.3.2 b | Mean wind speed Δ ≥ **5 m/s (10 kt)** |
| **Shall** | 2.3.2 c | Gust Δ ≥ **5 m/s (10 kt)** with mean ≥ **7.5 m/s (15 kt)** before/after |
| **Shall** | 2.3.2 d | Onset/cessation/**intensity change**: freezing precip; mod/heavy precip (+ showers); TS **with** precip |
| **Shall** | 2.3.2 e | Onset/cessation: freezing fog; TS **without** precip |
| **Shall** | 2.3.2 f | Cloud below **450 m (1 500 ft)**: SCT-or-less ↔ BKN/OVC |
| **Recommendation** | 2.3.3 a | Wind through **operationally significant** thresholds (local) |
| **Recommendation** | 2.3.3 b | Vis through **800 / 1 500 / 3 000 m** (+ **5 000 m** if significant VFR) |
| **Recommendation** | 2.3.3 c | RVR through **50 / 175 / 300 / 550 / 800 m** |
| **Recommendation** | 2.3.3 d | Intensity/onset: duststorm, sandstorm, funnel cloud |
| **Recommendation** | 2.3.3 e | Onset/cessation: low drifting / blowing dust·sand·snow; squall |
| **Recommendation** | 2.3.3 f | BKN/OVC base through **30 / 60 / 150 / 300 m** (+ **450 m** if significant VFR) |
| **Recommendation** | 2.3.3 g | Obscured sky VV through **30 / 60 / 150 / 300 m** |
| **Recommendation** | 2.3.3 h | Other local operating-minima criteria (parallel to TAF §1.3.2 j) |

**Mixed improvement+deterioration:** single SPECI, treated as **deterioration** (§2.3.4).  
**Dissemination:** deterioration **immediate** (§3.1.3); improvement Recommendation after **10 min** maintained (§3.1.4).

### 6. METAR/SPECI template notes — AUTO / missing / IWXXM

Table **A3-2** (PDF ~p.133–135): `AUTO` or missing-report `NIL`; when an element is temporarily missing/incorrect, replace with **`/`** per digit/group; footnote: missing for TAC **and indicated as missing for its IWXXM version** (PDF p.135) — aligns with encode nil/missing practice without defining `nilReason` URIs (those stay in TAC-to-XML-Guidance / schemas).

### 7. TAF (Ch.6 + App 5) — deeper

- **Issue/cancel:** New TAF cancels previous same place/overlapping validity (Ch.6 §6.1). Keep under continuous review; else cancel (§6.2.5). **≤1** TAF valid per aerodrome (§6.2.7).
- **Validity cadence (Recommendation §6.2.6):** routine TAF validity **6–30 h**; &lt;12 h issued every **3 h**; 12–30 h every **6 h** (regional agreement).
- **Elements:** wind VRB/calm/gust/≥100 kt caps (App 5 §1.2.1); vis steps (Amd **81** slip on §1.2.2 page); weather ≤**3** groups from listed set + **NSW** to end; cloud layering FEW/SCT/BKN/OVC + CB/TCU; **NSC** when no op-sig cloud and not CAVOK (§1.2.4).
- **Change groups — shall weather triggers (§1.3.1):** freezing fog/precip; mod/heavy precip; thunderstorm; duststorm; sandstorm (begin/end/intensity).
- **Change groups — Recommendation thresholds (§1.3.2):** wind dir/speed/gust (same figures as SPECI family); vis through **150 / 350 / 600 / 800 / 1 500 / 3 000 m** (+ **5 000 m** VFR); weather onset lists; cloud base / amount / VV; local minima (**j**, parallel SPECI §2.3.3 h).
- **Indicators (Table A5-2):** **FM** supersedes all prior elements; **BECMG** period normally &lt;2 h, never &gt;4 h; **TEMPO** each instance &lt;1 h and aggregate &lt;½ of indicated period; **PROB** only **30** or **40**; ≥50% → not PROB (use BECMG/TEMPO/FM); PROB must not qualify BECMG or FM (§1.4).
- Template identifiers: **TAF / TAF AMD / TAF COR**, **NIL**, **CNL** (Table A5-1).

### 8. Landing TREND (Ch.6 §6.3 + App 5 §2)

- Landing forecasts = **trend** appended to local routine/special, METAR, or SPECI; validity **2 hours** from report time.
- Significant changes for wind / vis / weather / cloud; cloud changes require **all** cloud groups; vis change requires causal weather; no change → **NOSIG**.
- Change indicators **BECMG** / **TEMPO** with **FM / TL / AT** time groups (App 5 §2.3); guidance also Table **A3-3**.
- Vis trend shall-through values include **150 / 350 / 600 / 800 / 1 500 / 3 000 m** (+ **5 000 m** if significant VFR) — see App 5 §2.2.3.

### 9. SIGMET / AIRMET (Ch.7 + App 6)

| Rule | Cite |
|------|------|
| Concise abbreviated plain language; cancel when no longer occurring/expected | Ch.7 §7.1.2 / §7.2.2 |
| Validity ≤ **4 h**; VA & TC SIGMET ≤ **6 h** | §7.1.3 / §7.2.3 |
| Issue ≤ **4 h** before validity start; VA/TC as soon as practicable ≤ **12 h** before; VA/TC update ≥ every **6 h** | §7.1.6 |
| **One** phenomenon per message; no extra descriptive material; TS/TC SIGMET must **not** also cite associated TURB/ICE | App 6 §1.1.4–1.1.5 |
| AIRMET: below FL100 (or FL150 mountainous / higher if needed); must not duplicate Section I of low-level area forecast | Ch.7 §7.2.1 · App 6 §2.1.4 |
| SIGMET phenomena (abbrev. family): OBSC/EMBD/FRQ/SQL **TS[GR]**; **TC**; **SEV TURB**; **SEV ICE** [(FZRA)]; **SEV MTW**; **HVY DS/SS**; **VA**; **RDOACT CLD** | App 6 §1.1.4 (PDF p.167–168) |
| AIRMET phenomena: surface wind/vis; ISOL/OCNL **TS[GR]**; **MT OBSC**; CB/TCU ISOL/OCNL/FRQ; **MOD ICE/TURB/MTW** (with exclusions for convective association) | App 6 §2.1.4 (PDF p.169–170) |
| ISOL / OCNL / FRQ / SQL spatial definitions | App 6 §4.2 Recommendations (PDF p.171) |
| CNL forms in Table A6-1A | PDF ~p.180 |
| VA SIGMET also to VAACs; consistent VA with NOTAM coordination | Ch.7 §7.1.5 · App 6 dissemination |

**Wind shear alert threshold (related):** headwind/tailwind change ≥ **7.5 m/s (15 kt)** (Ch.7 §7.4.3) — aerodrome warning product, not F6 IWXXM core.

### 10. SPECI ↔ TAF parallelism (design hint)

Annex 3 explicitly links local operating-minima criteria for SPECI (**App 3 §2.3.3 h**) and TAF change/AMD (**App 5 §1.3.2 j**). Wind/vis/cloud threshold **families** are intentionally similar but **not identical** (e.g. TAF Recommended vis steps include **150 / 350 / 600** m that SPECI §2.3.3 b does not). `tac-validate` should not collapse SPECI and TAF into one threshold table without edition-checked diffs.

### 11. Separation from code forms & registries

Foreword: code forms in **WMO-No. 306 Vol I**; weather token inventory → `codes.wmo.int/306/4678`. Annex 3 templates bind **structure and SARP phenomena**, not the full coded vocabulary.

### 12. Foreword vs discontinued WMO-No. 49 Vol II

Foreword “identical to 49 Vol II” is **historical** after Parts I–II discontinuation (2023). Defer to Annex 3 + discontinuation notice; keep `49-2` as vocabulary namespace.

### 13. National REMARKS

Annex 3 international METAR/SPECI path does **not** define US **RMK** grammar. `RMK` strings in this PDF appear in advisory/example contexts (e.g. App 2), not as Annex 3 international METAR REMARKS SoT — US profile stays FMH-1 / iwxxm-us.

---

## Catalog paste rows

```text
### ICAO Annex 3 — Meteorological Service for International Air Navigation
- **Publisher:** ICAO
- **URL:** https://store.icao.int/en/annex-3-meteorological-service-for-international-air-navigation-1
- **Edition note (local dig):** Twentieth Edition, July 2018 + Amd through No. 81 (applicable 28 Nov 2024); store may list 21st Ed. 2025 — verify before citing newer text
- **Access:** paywall; local extracts `.local/reference/icao-annex-3/` (gitignored)
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA]; profiles=[annex3]; role=[validation] (+ IWXXM dual-dissemination obligation cites Doc 10003 / 306 I.3)
- **Gap vs GIFTs:** SPECI shall/Rec thresholds; CAVOK; TREND 2h; TAF FM/BECMG/TEMPO/PROB; SIGMET/AIRMET phenomena+validity; national REMARKS still out
- **Consumer:** tac-validate (primary); UI-decode citations; conversion only for “shall IWXXM” + missing-element footnote framing
- **Label:** normative
- **Mined:** 2026-07-14 (pass 2 deeper) · docs/domain/mining/icao-annex-3-mining-notes.md
```

---

## Domain-knowledge cross-check (defer to latest)

| Older claim (doc + date/edition) | This source finding | Action |
|----------------------------------|---------------------|--------|
| Catalog “21st Edition, August 2025” without local verify | Binary is **20th Ed. 2018** + Amd through **81** | **Caveat** catalog (already); keep |
| PPT-02 / historical: IWXXM as Recommended Practice (Amd 77) | App 2/3/5/6 **shall** IWXXM GML | **Supersede** Recommended-only framing |
| Doc 10003 Advance 2014: AIRMET/VAA/TCA out of v1 | Annex 3 requires full F6 (+ SWX) with IWXXM shall | Keep draft **historical** |
| Foreword “identical to WMO-No. 49 Vol II” | Parts I–II discontinued 2023 | **Caveat** foreword |
| Assumption SPECI and TAF share identical vis thresholds | SPECI Rec vis **800/1500/3000/(5000)** vs TAF Rec **150/350/600/800/1500/3000/(5000)** | **Do not merge** tables; document parallelism only |
| OPMET Guidelines 5th: validate TAC vs Annex 3 / 306 I.1 | Reinforced by App 3/5/6 template notes | Keep |
| VAA/TCA “template depth TBD” | App 2 Tables **A2-1** / **A2-2** + §3.1.2 / §5.1.3 **shall** IWXXM mined (pp. APP 2-5…); TCA issue gate ≥34 kt (§5.1.1); colour values in A2-1 include UNKNOWN/NOT GIVEN/NIL | **Promoted** M/C/O TAC checklists → [TAC_VALIDATION.md](../TAC_VALIDATION.md); colour→registry encode → [IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) |
| METAR/TAF/SIGMET template cites only | Tables **A3-2** / **A5-1** / App 6 phenomena | **Promoted** paraphrase TAC lint checklists → [TAC_VALIDATION.md](../TAC_VALIDATION.md) (continue 2026-07-14) |
| FMH-1 / US REMARKS URL-only | Separate dig [fmh1-2019-mining-notes.md](./fmh1-2019-mining-notes.md) | US profile Lint/encode strategy + §2.5.2.a SPECI table promoted |

---

## Implications for this repo

- **tac-validate / TAC_VALIDATION.md:** Promote a **citation map** (shall SPECI first; TAF change/PROB; TREND; SIGMET validity/phenomena; **App 2 VAA/TCA shall + tables**). Gate numeric-threshold engines on licensed Annex 3. Keep SPECI vs TAF tables separate. US SPECI → FMH-1 not App 3.
- **tac2iwxxm / IWXXM_CONVERSION.md:** Dual-exchange **shall** + Table A3-2 missing→IWXXM-missing footnote; nilReason URIs still from Guidance / schemas. VAA colour → registry hrefs even when TAC says UNKNOWN/NOT GIVEN.
- **iwxxm-validate:** Unchanged pin; phenomenon enums for SIGMET/AIRMET should stay aligned with registries + Schematron, using Annex 3 lists as SARP cross-check only.
- **UI-decode (#702) / F7:** Prefer short “per Annex 3 App 3 §2.3 / App 5 §1.3 / App 2 A2-* …” citations over long quotes.

---

## Local extract index

| Extract | Contents |
|---------|----------|
| `extracts/foreword-amd-77-to-81.txt` | Table A Amd 77–81 |
| `extracts/ch4-metar-speci-core.txt` | Ch.4 METAR/SPECI |
| `extracts/ch6-taf-core.txt` | Ch.6 TAF / TREND / take-off |
| `extracts/ch7-sigmet-airmet-core.txt` | Ch.7 validity / cancel / lead times |
| `extracts/app3-speci-criteria-and-dissemination.txt` | App 3 SPECI + dissemination (pass 1) |
| `extracts/app3-speci-criteria-full.txt` | App 3 §2.2–2.3 + §3.1 (pass 2) |
| `extracts/app3-template-a3-2-and-trend.txt` | Table A3-2 · AUTO/missing · TREND examples |
| `extracts/app5-taf-start.txt` | App 5 start (pass 1) |
| `extracts/app5-taf-change-groups-full.txt` | App 5 TAF + TREND change/PROB (pass 2) |
| `extracts/app6-sigmet-airmet-start.txt` | App 6 start (pass 1) |
| `extracts/app6-phenomena-and-templates.txt` | Phenomena · ISOL/OCNL/FRQ · templates/CNL |
| `extracts/app2-vaa-tca-swx-iwxxm.txt` | Advisory IWXXM shalls (pass 1) |
| `extracts/app2-vaa-tca-templates-full.txt` | App 2 full carve Tables A2-1…A2-3 (pass 2026-07-14) |
| `extracts/iwxxm-dissemination-shall.txt` | All “IWXXM GML form” pages |
| `extracts/attachment-c.txt` | Attachment C criteria table (guidance) |

---

## Suggested next mining passes

1. Store **21st Edition** re-diff (post-Amd 81 / any PANS-MET split).  
2. ICAO **Doc 8896** for SIGMET/TCA practice lint wording.  
3. Published **Doc 10003** translation-centre §§.  
4. Optional: Attachment B forecast accuracy + present-weather combination tables in App 3 §§4.4.2.x for encode-side weather lint (still prefer `306/4678` + Schematron for tokens).
