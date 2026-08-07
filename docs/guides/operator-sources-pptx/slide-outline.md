# Slide outline — National compliance briefing (TAC → IWXXM)

**Audience:** Heads of MET services / aviation authorities / State representatives
responsible for meeting **ICAO/WMO OPMET–IWXXM** exchange expectations.
**Tone:** Why compliance matters → which sources bind → how this tool helps prove
lint → convert → validate. Not a click tutorial.

**Citation pack:** [citation-search-guide.md](./citation-search-guide.md)
**Policy:** cite landings + section numbers; never paste Annex 3 / MoC body text.

---

## Slide 1 — Title

**Title:** Meeting OPMET IWXXM Exchange Expectations
**Subtitle:** TAC → validated IWXXM for international air navigation · Schema pin **IWXXM v2025-2**

**Bullets:**
- For: State MET / ANSP / aviation authority leadership
- Scope: convert Traditional Alphanumeric Code (TAC) to IWXXM XML and prove quality

**Speaker notes:** Frame as **compliance enablement**. Obligations come from ICAO/WMO —
this system implements lint/convert/validate against published schemas.
[citation-search-guide.md] [Corpus: product §F6/F7]

**Sources footer:** Annex 3 (Store) · OPMET Guidelines 5th (public) · schemas.wmo.int/2025-2

---

## Slide 2 — Why leadership cares

**Title:** From TAC operations to IWXXM exchange

**Bullets:**
- TAC remains widely used for **presentation** and local ops
- International OPMET **exchange** increasingly requires **IWXXM** (XML/GML)
- Annex 3 sets MET service / product SARPs (State-adopted edition) — *Access: paywall*
- Public **OPMET IWXXM Exchange Guidelines (5th Ed., 2023)** describe prep, translation, exchange over AFS/AMHS
- Authorities need: **valid TAC → correct IWXXM → XSD + Schematron pass**

**Speaker notes:** Do **not** invent a global TAC sunset date unless your licensed Annex 3 /
regional agreement states it. Workshop ~2030 talk is **informative** only (PPT-02).

**Cite:** Annex 3 Store · Guidelines PDF · Doc 10003 Store

---

## Slide 3 — Binding sources map

**Title:** Sources States cite for IWXXM programmes

**Bullets:**
| Layer | Instrument | Access |
|-------|------------|--------|
| SARPs / TAC templates | **ICAO Annex 3** | Paywall (Store) |
| Exchange model | **ICAO Doc 10003** | Paywall (Store) |
| Implementation of exchange | **OPMET IWXXM Guidelines 5th** | Public PDF |
| Code forms / FM 205 | **WMO-No. 306 Vol I.3** | Library |
| Machine schemas | **schemas.wmo.int/iwxxm/2025-2** | Public |
| Vocabularies | **codes.wmo.int** | Public |
| Overview only | TT-AvData workshop PPT-02 | Public **informative** |

**Speaker notes:** Walk leaders through citation-search-guide §2–§3. Regional guides
(e.g. EUR Doc 014) **complement** Annex 3 — they do not replace it.

---

## Slide 4 — What “compliance-ready IWXXM” means

**Title:** Proof points Regulators and ROCs expect

**Bullets:**
1. TAC matches Annex 3 / WMO templates (lint)
2. Encode follows IWXXM structure + nilReason practice (convert)
3. Well-formed XML
4. Passes **XSD** for the agreed IWXXM year line
5. Passes **Schematron** (+ codelist checks)
6. Prefer official TAC↔XML example pairs for acceptance tests
7. Translation metadata when translating for another centre; retain TAC on failure

**Speaker notes:** Guidelines 5th §5.3.2 — schema **and** Schematron. Default pin **2025-2**.
Hub: docs/domain/README.md pipeline table.

**Cite:** Guidelines 5th · schemas.wmo.int/2025-2 · IWXXM_VALIDATION.md

---

## Slide 5 — How this system maps

**Title:** Software pipeline aligned to ICAO/WMO sources

**Bullets:**
- **Operator workbench** — multi-product TAC, decode, live lint/preview (F7/F9/F10)
- **`tac-validate`** — Annex 3 / vocab lint with source-traced issue codes
- **`tac2iwxxm`** — TAC → IWXXM encode (vendor pin)
- **`iwxxm-validate`** — XSD + Schematron against **v2025-2**
- **Provenance** — RULE_SOURCE_URLS / PROVENANCE_MAP / lint catalog attribution
- **Not a substitute** for State licensing of Annex 3 / Doc 10003

**Cite:** feature-list F6/F7 · vendor/manifest.json · operator-ui-runbook.md

---

## Slide 6 — Products in scope

**Title:** Products covered for State programmes

**Bullets:**
- Core: METAR, SPECI, TAF, SIGMET, AIRMET, VAA, TCA
- Extensions where pinned: SWXA, VONA
- Profiles: **annex3** (default) · **iwxxm_us** (national REMARKS)
- Bulletin modes: TAC / AHL / COLLECT

**Cite:** Annex 3 product apps · COVERAGE_MATRIX · EUR Doc 014 (regional)

---

## Slide 7 — Schema pin & version governance

**Title:** Validate against a published IWXXM line

**Bullets:**
- Runtime pin: **IWXXM v2025-2** (+ codelists **49-2**; US **3.0** when needed)
- Public SoT: https://schemas.wmo.int/iwxxm/2025-2/
- github.com/wmo-im/iwxxm tag `v2025-2`
- Conflict rule: machine pin wins over older printed tables / workshop slides

**Cite:** schemas.wmo.int · vendor/manifest.json · VERSION_SUPPORT_POLICY.md

---

## Slide 8 — Governance & access (procurement / legal)

**Title:** What your State must hold vs what is free

**Bullets:**
- **Purchase / license:** Annex 3, Doc 10003, Doc 8896 (ICAO Store)
- **Library access:** WMO-No. 306 Vol I.3
- **Free for implementation & CI:** schemas.wmo.int, codes.wmo.int, OPMET Guidelines PDF, EUR Doc 014, wmo-im GitHub
- This repository **does not** redistribute Annex 3 / Manual on Codes full text

**Cite:** ACCESS_AND_CITATION.md · citation-search-guide.md §2

---

## Slide 9 — Recommended leadership actions

**Title:** Next steps for a State programme

**Bullets:**
1. Confirm Annex 3 / Doc 10003 editions on file
2. Agree IWXXM year line with ROC/Region (align to **2025-2** or documented bilateral)
3. Require **XSD + Schematron** in translator acceptance criteria
4. Stand up lint → convert → validate with official example packs
5. Monitor partial-translation / failure rates (Guidelines §7 themes)
6. Keep regional guides as supplements only

**Cite:** Guidelines 5th · Doc 10003 · ICAO_OPMET_COMPLIANCE.md

---

## Slide 10 — Informative workshop context (optional)

**Title:** Industry briefing context (not SARPs)

**Bullets:**
- TT-AvData “IWXXM Framework” (ESAF, Oct 2025) — public download
- Useful for landings map / messaging — label **INFORMATIVE**
- Forward messages (e.g. TAC sunset discussions) → verify against **your** Annex 3 edition / Region

**Cite:** https://www.icao.int/filebrowser/download/26741?fid=26741

---

## Slide 11 — References (handout)

**Title:** Cite these landings

**Bullets:**
- Annex 3 — store.icao.int/en/annexes/annex-3
- Doc 10003 — ICAO Store
- OPMET IWXXM Guidelines 5th — icao.int METP PDF (public)
- schemas.wmo.int/iwxxm/2025-2/
- codes.wmo.int
- library.wmo.int — Manual on Codes I.3
- Full search steps: `docs/guides/operator-sources-pptx/citation-search-guide.md`

---

## Slide 12 — Closing

**Title:** Compliance is standards-led; software makes it operable

**Bullets:**
- SARPs and manuals define the obligation
- Public schemas and Guidelines define the machine test
- This system: **lint → convert → XSD + Schematron** with source-traced rules
- Staff path: operator UI runbook · Leadership path: this deck + citation guide

**Cite:** [Corpus: product §F6/F7] [docs/domain/README.md]
