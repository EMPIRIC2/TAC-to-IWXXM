# ICAO Doc 10003 (Advance 2014 draft) — focused mining notes

**Status:** working notes (not normative). Verify against the published / store edition — this PDF is **unedited Advance 2014**.  
**Focus of this pass:** full draft (Ch.1–5 + Apps A–C) · products · roles · domain-knowledge cross-check  
**Local PDF + extracts (gitignored):** `.local/reference/icao-doc-10003-draft-en/`

**Standing catalog:**

| Doc | Path |
|-----|------|
| Master URL catalog | [../rules/RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) |
| Coverage matrix | [../rules/COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) |
| Access / citation | [../rules/ACCESS_AND_CITATION.md](../rules/ACCESS_AND_CITATION.md) |
| IWXXM creation | [IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) |
| IWXXM validation | [IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) |
| OPMET / translation ops | [ICAO_OPMET_COMPLIANCE.md](../iwxxm/ICAO_OPMET_COMPLIANCE.md) |
| Version support policy | [VERSION_SUPPORT_POLICY.md](../iwxxm/VERSION_SUPPORT_POLICY.md) |
| FM 205 companion | [mining/WMO-306-vI-3-2023-mining-notes.md](./WMO-306-vI-3-2023-mining-notes.md) |
| Workshop (informative) | [mining/PPT-02-IWXXM-Framework-WMO-mining-notes.md](./PPT-02-IWXXM-Framework-WMO-mining-notes.md) |

| Item | Value |
|------|-------|
| Title | Manual on the Digital Exchange of Aeronautical Meteorological Information |
| Publisher | ICAO |
| Document | Doc 10003 · AN/xxx |
| Edition (this file) | **Advance 2014 Edition — unedited** |
| Official store (final / paywall) | <https://store.icao.int/en/manual-on-the-icao-meteorological-information-exchange-model-doc-10003> |
| Pages | 37 |
| Local text | `.local/reference/icao-doc-10003-draft-en/fulltext.txt` |
| Date mined | 2026-07-14 |
| Access | Draft PDF (user-supplied); published editions **paywall** |
| Label | Draft = **informative** / **historical**; published Doc 10003 = **normative** (cite store) |
| Vendor pin (runtime) | `vendor/manifest.json` → `iwxxm` **v2025-2** |

---

## What this source is / is not

| Is | Is not |
|----|--------|
| Early MARIE-PT guidance aligned with Annex 3 **Amendment 76** (digital METAR/SPECI/TAF/SIGMET, Nov 2013) | Binding / final ICAO Doc 10003 text |
| Architecture story: SWIM layers, IWXXM + SAF logical/physical models, ISO 191xx foundation | Encode cookbook for IWXXM **2025-2** (use examples + TAC-to-XML-Guidance + FM 205) |
| IWXXM **v1** product baseline + early XSD package list + present/recent weather combination checks | Coverage of AIRMET · VAA · TCA · VONA · SWX · COLLECT bulletins |
| FAQ on report-vs-bulletin, compression, convert-at-source vs ROC | Section **7** translation-centre ops / statistics (see domain check below); for public AMHS/partial-translation/ROC stats use [OPMET Guidelines 5th](./OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md) |

Front-matter notice (PDF p.1): content may change; **not authoritative** until officially approved.

---

## Document map

| Section | Approx. PDF pages | Relevance |
|---------|-------------------|-----------|
| Notice / foreword | 1–3 | Draft status; Amd 76 product set; dual TAC+digital exchange |
| TOC / abbreviations | 4–5 | SAF, METCE, OPM, IWXXM, TREND |
| Ch.1 Background | 6–9 | ATM / SWIM motivation (informative) |
| Ch.2 Digital exchange principles | 10–16 | Global/regional/user constructs; SWIM layers; ISO foundation; component stack |
| Ch.3 IWXXM + SAF logical models | 17–20 | Baseline products; UML context-diagram inventory; historical ICAO landings |
| Ch.4 IWXXM + SAF XML schema | 21–31 | XSD list; sample `common.xsd` (1.0RC2); weather combination tables |
| Ch.5 Metadata | 32 | Placeholder — “IWXXM version 1 has no specific metadata requirements” |
| App A UML | 33–34 | Class / association primer |
| App B XML/GML | 35–36 | GML application schema / `icao.int/iwxxm` namespace |
| App C FAQ | 37 | Bulletin not supported (then); convert-at-source vs regional OPMET centres |

---

## Product × artifact matrix

| Product | TAC input (draft era) | IWXXM (draft) | Official example / guidance (then) | Gap vs GIFTs / today | Consumer |
|---------|----------------------|---------------|------------------------------------|----------------------|----------|
| METAR (+ TREND) | Annex 3 / WMO 306 TAC | Logical + `metarSpeci.xsd` | Historical `icao.int/iwxxm/1.0` | GIFTs METAR-centric; runtime → **v2025-2** | `tac2iwxxm`, `iwxxm-validate` |
| SPECI (+ TREND) | same | same package | same | same | same |
| TAF | TAC + digital | `taf.xsd` | same | Outside GIFTs depth | same |
| SIGMET | Abbreviated plain language + digital | `sigmet.xsd` | same | Outside GIFTs | same |
| AIRMET / VAA / TCA | — | **out of scope** in v1 baseline | — | Entire products outside this draft | F6 still needs later Doc 10003 / Annex 3 / schemas |
| Bulletin / COLLECT | FAQ: grouping **not** supported | — | — | Today: `iwxxm-collect.xsd` + AHL | `bulletin` |

---

## Key findings

### Foreword — Amendment 76 product set (PDF p.3)

- Amd 76 enables digital exchange of **METAR, SPECI (incl. TREND), TAF, SIGMET** for States in a position to do so.
- METAR/SPECI/TAF digital is **in addition to** WMO TAC code forms; SIGMET digital is in addition to abbreviated plain language.
- Annex 3 expects: global exchange model + **XML/GML** + **appropriate metadata** (metadata fleshed out only in later IWXXM / Doc editions — Ch.5 is empty here).

### Ch.2 — components (PDF p.14–15)

Identified stack (v1):

1. **IWXXM logical model** (UML / ISO 19109) — METAR/SPECI/TREND, TAF, SIGMET only  
2. **SAF logical model** — aerodromes/runways etc. pending a shared ICAO aero model  
3. **IWXXM / SAF XML** (GML application schemas)  
4. **WMO foundation packages:** METCE (`schemas.wmo.int/metce/1.0`), OPM (`schemas.wmo.int/opm/1.0`) — manual says refer to WMO guidance for those

**Extensibility** called fundamental (PDF p.14) — aligns with later `iwxxm-us` / regional extensions under profile hooks.

ISO foundation list (PDF p.13): 19103, 19107, 19108, **19115**, 19123, **19136 (GML)**, 19139, **19156 (O&M)**, ISO 639-2, W3C XSD.

### Ch.3 — logical baseline (PDF p.17–19)

- Baseline TAC forms to replace digitally: METAR(+TREND), SPECI(+TREND), TAF, SIGMET.  
- Context diagrams listed include **METAR/SPECI Runway State**, weather, cloud, surface wind, SIGMET analyses, SAF measure/aerodrome/airspace/unit.  
- Historical publish pointers (do not use as runtime SoT): `www.icao.int/iwxxm/1.0/doc`, `www.icao.int/saf/1.0/doc`.  
- Positions IWXXM vs broader **WXXM** (footnote: IWXXM = selected Annex 3 products; WXXM = broader aviation met).

### Ch.4 — physical schema (PDF p.21–31)

**XSD inventory (v1):** `iwxxm.xsd`, `common.xsd`, `metarSpeci.xsd`, `sigmet.xsd`, `taf.xsd` + SAF `saf.xsd` / `features.xsd` / `measures.xsd` / `dataTypes.xsd`.

**Namespace in printed sample** (PDF p.22): `http://icao.int/iwxxm/1.0RC2` (and SAF `1.0RC2`) — **not** today’s `http://icao.int/iwxxm/2025-2`.

Sample embeds Schematron namespace declarations and `codes.wmo.int/common/c-15/...` quantity URIs on elements (verticalVisibility, cloud base, wind) — pattern still relevant; **pin-aligned** registries + vendor RDF for CI.

**Present / recent weather** (§4.2.5–4.2.10, PDF pp.25–30): enumerates permissible METAR/SPECI weather / recent-weather TAC token combinations for IWXXM GML encoding (incl. missing `//`).  
→ Do **not** treat this Advance list as current SoT; prefer Annex 3 + `http://codes.wmo.int/306/4678/{TAC}` + vendor Schematron. Local dump only: `.local/.../extracts/ch4-present-recent-weather.txt`.

### Ch.5 — metadata (PDF p.32)

Explicit placeholder: IWXXM v1 has **no** specific metadata requirements. Later schema attributes (`translationCentre*`, `translatedBulletin*`, `permissibleUsage`, …) live in current `common.xsd` and in ops docs — **not** derived from this chapter.

### App C FAQ (PDF p.37) — operational implications

1. **Smallest unit = report**, not bulletin — bulletin/COLLECT schema **not** supported in this draft.  
2.–3. Compression optional; binary XML noted as one option among several.  
4. Prefer XML/GML **at source** (AUTO systems / forecaster tools) in SWIM spirit.  
5. Alternative: convert at **national / regional OPMET centres** (ROCs) — early framing of translation-centre role later formalized in published Doc 10003 / OPMET guidelines.

---

## Domain-knowledge cross-check (in-repo claims vs this draft)

| In-repo claim | Evidence in Advance 2014 draft | Verdict |
|---------------|--------------------------------|---------|
| [ICAO_OPMET_COMPLIANCE.md](../iwxxm/ICAO_OPMET_COMPLIANCE.md) implements Doc 10003 **§7** translation-centre / statistics | TOC stops at Ch.5; **no Section 7** | **Cite paywalled published edition** for §7 — not this draft. Keep ops guide; add edition caveat. |
| Translation attrs (`translationCentreName`, `translatedBulletinID`, …) required by Doc 10003 | Ch.5 empty; attrs **are** in vendor `common.xsd` (2025-2) | Schema SoT = **pin**; Doc 10003 prose SoT = **store edition** |
| [VERSION_SUPPORT_POLICY.md](../iwxxm/VERSION_SUPPORT_POLICY.md): Doc 10003 recommends **latest + 1 prior** IWXXM version | No version-support window text in this draft | **Unverified here** — keep policy if aligned with later editions / OPMET guidelines; do not cite Advance 2014 for it |
| CREATION_SOURCES “align with Doc 10003” for translation metadata | Partially — FAQ ROC conversion only | Point to mining notes + published Doc; PPT-02 for operator reminder |
| Runway state in METAR encode path | Listed in Ch.3 logical inventory | Matches historical model; **IWXXM 2025-2** creation notes: runway-state types **removed** — do not encode for current pin |
| Bulletin encoding | FAQ: **not** supported | Superseded by COLLECT / `iwxxm-collect.xsd` + AHL guidance |
| Weather encode validation lists | Ch.4 tables | Historical; use **codes.wmo.int** + Schematron today |
| F6 product coverage via Doc 10003 alone | Only four products | AIRMET/VAA/TCA need Annex 3 + current schemas / later Doc editions |

---

## Catalog paste rows

```text
### ICAO Doc 10003 — Manual on the Digital Exchange of Aeronautical Meteorological Information (published)
- Publisher: ICAO
- URL: https://store.icao.int/en/manual-on-the-icao-meteorological-information-exchange-model-doc-10003
- Access: paywall
- Applies to: products=[all F6 + ops]; profiles=[annex3]; role=[conversion, iwxxm-validation, bulletin]
- Gap vs GIFTs: translation-centre / exchange prose beyond METAR GIFTs heritage
- Consumer: tac2iwxxm metadata; ops / ICAO_OPMET_COMPLIANCE; #699 prose pointer
- Label: normative
- Caveats: cite edition; do not mirror PDF text
- Mined: 2026-07-14 · companion draft notes

### ICAO Doc 10003 — Advance 2014 Edition (unedited draft)
- Publisher: ICAO (unedited advance)
- URL: store landing above (final); local `.local/reference/icao-doc-10003-draft-en/`
- Access: draft PDF local-only; not authoritative
- Applies to: products=[METAR,SPECI,TAF,SIGMET]; profiles=[annex3]; role=[conversion, iwxxm-validation] (historical)
- Gap vs GIFTs: architecture + early weather-combination encoding notes; no AIRMET/VAA/TCA; no §7
- Consumer: design / lineage docs; not runtime SoT
- Label: informative / historical
- Caveats: Amd 76 / IWXXM 1.0 era; namespaces 1.0RC2; bulletin FAQ obsolete vs COLLECT
- Mined: 2026-07-14 · notes mining/ICAO-Doc-10003-draft-2014-mining-notes.md
```

---

## Implications for this repo

- **F6 / tac2iwxxm:** Use **v2025-2** examples + TAC-to-XML-Guidance + FM 205 for encode; treat this draft as **lineage** only (product set, SAF/METCE stack story, ROC conversion FAQ).  
- **tac-validate:** Weather combination tables are historical IWXXM-encode lists — vocab still via Annex 3 / `306/4678`, not by re-implementing the draft tables.  
- **iwxxm-validate:** Validate against vendored **2025-2** XSD/SCH; draft’s `1.0RC2` sample is obsolete.  
- **Bulletin:** Ignore draft “no bulletin schema”; use COLLECT + AHL sources.  
- **Caveats / TBD:** Obtain / cite **published** Doc 10003 sections for §7 ops and any “N+1 version” support policy; mark in-repo claims accordingly.

---

## Local extract index

| Extract | Contents |
|---------|----------|
| `extracts/front-matter.txt` | Notice, foreword, TOC, abbreviations |
| `extracts/ch1-background.txt` | ATM / net-centric / MET consequences |
| `extracts/ch2-digital-exchange.txt` | SWIM, ISO foundation, IWXXM+SAF+METCE+OPM |
| `extracts/ch3-logical-models.txt` | Baseline products, UML inventory |
| `extracts/ch4-xml-schema.txt` | XSD list + printed schema sample |
| `extracts/ch4-present-recent-weather.txt` | Present/recent weather combination pages |
| `extracts/ch5-metadata.txt` | Metadata placeholder |
| `extracts/app-a-uml.txt` | UML primer |
| `extracts/app-b-xml-gml.txt` | GML / application schema |
| `extracts/app-c-faq.txt` | FAQ (bulletin, compression, conversion locus) |

---

## Suggested next mining passes

1. Licensed **published** Doc 10003 (current edition) — extract § translation centres / version guidance only (no full-text commit).  
2. ~~Reconcile OPMET Guidelines ↔ translation attrs~~ — Guidelines 5th mined 2026-07-14 ([notes](./OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md)); attrs still schema/PPT-02 SoT for names/omit-when-self-produced. Remaining: purchased Doc 10003 vs Guidelines §5.3.  
3. Diff Ch.4 weather combination list vs current Schematron / `306/4678` for drift tickets (do not paste lists into git).
