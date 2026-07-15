# ICAO OPMET IWXXM Exchange Guidelines (5th Ed.) — focused mining notes

**Status:** working notes (not normative). Verify against the official PDF.  
**Focus of this pass:** full document (Ch.1–8 + Apps A–C) · products · exchange / translation / statistics · domain-knowledge cross-check  
**Local PDF + extracts (gitignored):** `.local/reference/opmet-iwxxm-exchange-guidelines-5th/`

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
| Doc 10003 Advance 2014 (historical) | [mining/ICAO-Doc-10003-draft-2014-mining-notes.md](./ICAO-Doc-10003-draft-2014-mining-notes.md) |
| Workshop (informative) | [mining/PPT-02-IWXXM-Framework-WMO-mining-notes.md](./PPT-02-IWXXM-Framework-WMO-mining-notes.md) |

| Item | Value |
|------|-------|
| Title | Guidelines for the Implementation of OPMET Data Exchange using IWXXM |
| Publisher | ICAO (METP materials) |
| Edition | **Fifth Edition — October 2023** |
| Official landing | <https://www.icao.int/sites/default/files/METP/Documents/Guidlines-for-the-Implementation-of-OPMET-Data-Exchange-using-IWXXM_5th-Edition.pdf> |
| Pages | 46 |
| Local text | `.local/reference/opmet-iwxxm-exchange-guidelines-5th/fulltext.txt` |
| Date mined | 2026-07-14 |
| Access | **public** PDF (filename retains ICAO spelling “Guidlines”) |
| Label | **normative-exchange** (implementation guidelines for AFS/AMHS OPMET IWXXM) |
| Vendor pin (runtime) | `vendor/manifest.json` → `iwxxm` **v2025-2** |

---

## What this source is / is not

| Is | Is not |
|----|--------|
| ICAO METP **implementation** guidance for preparing, collecting, routing, and translating OPMET in IWXXM over **AMHS/FTBP** | ICAO Doc **10003** (store / paywall) — complementary; do not equate titles |
| Functional roles: Producer, Aggregator, **Translation Centre**, Switch, Databank (NOC/ROC/IROG/RODB) | TAC token → nilReason encode cookbook (use TAC-to-XML-Guidance + examples) |
| `permissibleUsage` / test-exercise rules; COLLECT aggregation; FTBP **filename** + gzip; partial-translation minimum fields; ROC/RODB **validation statistics** | Binding package×Annex 3 **compatibility table** numbers (defers to community.wmo.int) |
| Product coverage for ops: METAR/SPECI/TAF/SIGMET/AIRMET/VAA/TCA/**SWXA** (+ WAFS acronym) | Schema XSD/SCH machine SoT; named `translationCentre*` XSD attributes (prose only: centre id + time) |

---

## Document map

| Section | Approx. PDF pages | Relevance |
|---------|-------------------|-----------|
| Cover / TOC / figures | 1–5 | Edition; structure |
| Ch.1 Introduction | 6 | Purpose vs Annex 3; audience |
| Ch.2 Current ops & roles | 7–8 | NOC / ROC / IROG / International Databank |
| Ch.3 Operating principles | 9–11 | Transition; schema extensions; translation; COLLECT metadata; AMHS/FTBP; version/compatibility pointers; AIXM metadata |
| Ch.4 Functional framework | 12–17 | Producer/Aggregator/**Translation Centre**/Switch/Databank requirements; `A_TTAAii…xml.gz`; T1T2 **LA…LY** |
| Ch.5 Generation & use | 18–22 | `permissibleUsage*`; UUIDv4 `gml:id`; TAC→IWXXM translation centre ops; partial translation; agreement |
| Ch.6 Transition requirements | 23–26 | AMHS readiness; METNO / AIRAC timeline |
| Ch.7 Validation statistics | 27–28 | ROC/IROG/RODB + SADIS/WIFS stats (availability, Schematron success, partial translations, …) |
| Ch.8 Acronyms | 29–30 | Including SWXA/SWXC, Collect, FTBP, RQX |
| App A AMHS profile | 31–37 | Exactly one FTBP body part; compression in MET domain; Doc 9880-derived tables |
| App B Conformance tests | 38–43 | NOC submission/delivery tests (AMHS) |
| App C METNO format | 44–46 | `NEWBUL` / `DELBUL` / `ADDRPT` / `RMVRPT` |

---

## Product × artifact matrix

| Product | TAC / ops input | IWXXM / exchange output | Official example or guide in this PDF | Gap vs GIFTs | Consumer |
|---------|-----------------|-------------------------|---------------------------------------|--------------|----------|
| METAR | SA… bulletins; COR noted | `LA` FTBP; COLLECT bulletin; partial min: type+(COR)+CCCC+time | Filename ex. `A_LAFR31LFPW…xml.gz` (p.14) | Outside GIFTs for bulletin/AMHS | `tac2iwxxm`, bulletin, F8 |
| SPECI | SP… | `LP` | T1T2 list (p.15) | same | same |
| TAF | FC/FT…; AMD/COR | `LC` / `LT` by VT; partial min: type+(COR/AMD)+CCCC+time | p.15, p.21 | Outside GIFTs depth | same |
| SIGMET (WS/WV/WC) | WS/WV/WC… | `LS` / `LV` / `LY`; partial: CCCC + SIGMET\|AIRMET + VALID | p.15, p.21 | Entire product outside GIFTs | same |
| AIRMET | WA… | `LW`; same partial shape as SIGMET | p.15, p.21 | Entire product outside GIFTs | same |
| VAA | FV… | `LU`; partial: DTG, VAAC | p.15, p.21 | Entire product outside GIFTs | same |
| TCA | FK… | `LK`; partial: DTG, TCAC | p.15, p.21 | Entire product outside GIFTs | same |
| SWXA | Space-weather TAC/advisory | `LN`; partial: DTG, SWXC; stats by centre | p.15, p.21, §7 | Optional beyond F6 core | design / future |
| Bulletin / COLLECT | Aggregated same-type reports | `collect:MeteorologicalBulletin`; uuid `gml:id` | §3.1.4, §5.2 | Outside GIFTs | bulletin |
| Exchange | AFS routing | AMHS + **FTBP** + gzip; not AFTN payload | App A | Outside GIFTs | bulletin / F8 |

Failed convert path (this PDF): §5.3.3 “Incomplete (Partial) Translation” → IWXXM type shell + original TAC (maps to schema `@translationFailedTAC` / failed examples — attribute name from **schemas**, not spelled here).

---

## Key findings

### Roles & translation centre (Ch.2–4, §5.3)

- Prefer native IWXXM at source; where TAC→IWXXM is necessary, identify **where and when** translation occurred via IWXXM metadata (“centre identifier and time stamp”) (p.9, p.20).
- Translator works on a **bulletin** basis and is associated with an Aggregator / COLLECT function (p.13).
- Correction is originator/NOC/ROC — not typically the Translation Centre (p.20).
- Prerequisites include 24/7 ops, AMHS+FTBP access, COLLECT capability, archive **≥28 days** data and **≥2 months** translation logs (header, reception time, reject flag) (p.20).

### `permissibleUsage` ( §5.1 )

- Operational → `permissibleUsage="OPERATIONAL"` only (no reason fields) (p.18–19).
- Non-operational → `NON-OPERATIONAL` + `permissibleUsageReason` TEST|EXERCISE + recommended `permissibleUsageSupplementary` free text (p.19).
- When translation fails or test/exercise mapping is uncertain, presume **operational** so humans can still recover the TAC (p.20).

### Partial / incomplete translation ( §5.3.3 )

- On failure: emit product-typed IWXXM **without MET parameters**, carrying the original TAC; optional notify originator (p.20–21).
- Minimum recoverable fields listed for METAR, TAF, SIGMET/AIRMET, VAA, TCA, **SWXA** (p.21).

### COLLECT + `gml:id` ( §3.1.4, §5.2 )

- Aggregated same-type reports use Collect / Feature Collection; aggregating centre + collection time in metadata (p.9–10).
- Recommend **UUIDv4** as `gml:id` (prefix `uuid.…`) to avoid collisions when aggregating (p.19); notes a Schematron mandate was expected from “IWXXM v3” onward — confirm against **v2025-2** SCH before treating as hard rule.

### Exchange / filename ( §3.1.5, §4.1.4, App A )

- IWXXM over **AMHS with FTBP**; compressed in the **MET** domain (`.gz`); not carried as AFTN text (p.10, p.14, App A).
- Filename (WMO naming convention A):  
  `A_TTAAiiCCCCYYGGggBBB_C_CCCC_YYYYMMddhhmmss.xml.gz` (p.14).
- Aviation IWXXM T1T2: LA, LC, LK, LN, LP, LS, LT, LU, LV, LW, LY (p.14–15) — aligns with community AHL page.
- App A: IPM body = **exactly one** FTBP; compression field of FTBP unused because MET compresses first (p.31+).

### Versions ( §3.1.7 )

- Release cadence tied to WMO Fast Track; naming like **2021-2** explained (p.10–11).
- Machine artifacts at `https://schemas.wmo.int/iwxxm`; **which** version is operational = compatibility table on  
  `https://community.wmo.int/en/activity-areas/wis/iwxxm` (p.11).
- Outdated schemas remain published for archive decode; “no change once published” (p.11).
- **This 5th Edition (Oct 2023) does not** spell a “deprecate ≤2021-2 after 2025-2” sentence — that forward message is from [PPT-02](./PPT-02-IWXXM-Framework-WMO-mining-notes.md) (2025-10) saying guidelines *will be* updated.

### Validation & statistics ( §5.3.2, §5.3.5, Ch.7 )

- Validate TAC against Annex 3 / WMO 306 I.1; IWXXM against **most recent** official schema/Schematron unless bilaterally agreed otherwise; also FM 201 (collect) + FM 205 (p.20).
- Translator compliance: XSD, Schematron, test TAC set, translation metadata, monitoring metadata (p.21).
- §7 ROC/RODB stats: availability/timeliness (like TAC; exclude NIL/COR/AMD; SIGMET CNL out), Schematron success **per IWXXM version**, version-by-station, % non-operational, **% incomplete/partial translations**, volume, optional extensions / failure diagnostics; hierarchy Region → State → CCCC (or advisory centre) (p.27–28).

### METNO ( §6.1.6, App C )

- Global use of EUR/APAC-style METNO for bulletin catalogue changes on **AIRAC** dates; timeline table (p.25–26).
- App C verbs: `NEWBUL`, `DELBUL`, `ADDRPT`, `RMVRPT` (p.44–46).

---

## Domain-knowledge cross-check (in-repo)

| Repo claim / artifact | This guidelines find | Action |
|-----------------------|----------------------|--------|
| [ICAO_OPMET_COMPLIANCE.md](../iwxxm/ICAO_OPMET_COMPLIANCE.md) cites **Doc 10003 §7** for translation-centre stats | This PDF’s **§7** is ROC/RODB (and SADIS/WIFS) **exchange** validation statistics; translation-centre monitoring points at §7.1 (§5.3.4). Centre metadata attrs still from **schema**/published Doc 10003 | Keep Doc 10003 citation for store § ops; **also cite** these Guidelines for AMHS/partial-translation/ROC stats. Do not treat Advance 2014 Doc 10003 as §7 SoT |
| Project **indefinite** translation retention | Guidelines pre-req: ≥28 days data, ≥2 months translation logs (p.20) | **Delta** — guidelines are a *minimum* archive; project retention can exceed |
| [VERSION_SUPPORT_POLICY.md](../iwxxm/VERSION_SUPPORT_POLICY.md) “latest + 1 prior” attributed partly to Doc 10003 / OPMET | §3.1.7 defers operational versions to **community compatibility table**; no explicit “N and N−1” window in this edition | Cite community table + vendor pin; do not cite 5th Ed. alone for that window |
| PPT-02: Guidelines will deprecate ≤2021-2 once 2025-2 official | **Not present** in Oct 2023 5th Ed. text | Treat PPT-02 as future Guidelines update messaging; keep runtime pin **v2025-2** |
| PPT-02: omit translation attrs when producer self-translates | Guide focuses on fields **when** translation is conducted; omit rule clearer in PPT-02 / schema practice | Keep omit rule; label guide as ops packaging |
| `ICAO_OPMET_COMPLIANCE` always `permissibleUsage="OPERATIONAL"` | Matches **operational** production; Guidelines require TEST/EXERCISE flags for non-ops and OPERATIONAL on failed translation when uncertain | Align failed-path default with §5.3; don’t hardcode OPERATIONAL for intentional tests |
| Partial / `translationFailedTAC` examples | §5.3.3 minimum field lists + “original TAC” shell | Primary **ops** cite for quarantine encode; machine attr names from XSD/examples |
| AHL community T1T2 + F8 filename | Same LA…LY set + `A_…xml.gz` pattern | Guidelines **confirm** community AHL / ingest doc |
| Doc 10003 Advance 2014: “no bulletin schema” | Collect / `MeteorologicalBulletin` + FM 201 firmly in use here | Reinforces obsolete draft FAQ |
| [docs/context/realtime-tac-ingest.md](../../context/realtime-tac-ingest.md) already links this PDF | URL verified HTTP 200 (2026-07-14) | Promote into RULE_SOURCE_URLS (done with this pass) |

---

## Catalog paste rows

```text
### ICAO Guidelines — OPMET Data Exchange using IWXXM (5th Edition)
- Publisher: ICAO (METP)
- URL: https://www.icao.int/sites/default/files/METP/Documents/Guidlines-for-the-Implementation-of-OPMET-Data-Exchange-using-IWXXM_5th-Edition.pdf
- Stable concept pattern: n/a (ops guidelines); points to schemas.wmo.int/iwxxm + community.wmo.int/…/iwxxm compatibility table; AHL T1T2 LA…LY
- Access: public
- Applies to: products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA,SWXA]; profiles=[annex3]; role=[conversion, iwxxm-validation, bulletin]
- Gap vs GIFTs: Translation Centre bulletin flow; COLLECT; AMHS/FTBP+gzip filename; permissibleUsage; partial-translation mins; ROC stats; METNO — all outside GIFTs
- Consumer: tac2iwxxm | iwxxm-validate | bulletin | UI-decode | ops (ICAO_OPMET_COMPLIANCE)
- Label: normative-exchange
- Caveats: Not Doc 10003; Oct 2023 edition — no 2025-2 deprecation table; translation XSD attr names not listed (use common.xsd); filename keeps typo "Guidlines"
- Mined: 2026-07-14 · notes mining/OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md
```

---

## Implications for this repo

- **F6 / tac2iwxxm:** Set translation metadata when acting as third-party translator; implement failed path with product shell + original TAC and §5.3.3 minimum identity fields; default `permissibleUsage` to OPERATIONAL on uncertain/failed translation.
- **iwxxm-validate:** Schematron success + version in ops metrics; COLLECT uniqueness / UUID practice — confirm against vendored SCH for v2025-2.
- **bulletin / F8:** AMHS FTBP + gzip filename + T1T2 list are first-class; METNO App C is catalogue ops (not runtime convert).
- **ICAO_OPMET_COMPLIANCE / stats APIs:** Map metrics to Guidelines §7 dimensions (availability, Schematron-by-version, partial %, non-ops %, volume) where useful; do not claim identity with Doc 10003 §7 without the paywalled edition.
- **F4 / VERSION_SUPPORT_POLICY:** Prefer community compatibility table + vendor pin; cite this PDF only for “schemas stay published; ops versions from table.”
- **Caveats / TBD:** Watch for a **6th+ Edition** that may add PPT-02’s ≤2021-2 deprecation language after 2025-2.

---

## Local extract index

| Extract | Contents |
|---------|----------|
| `extracts/00-front-toc.txt` | Cover, TOC (p.1–5) |
| `extracts/01-purpose-roles.txt` | Ch.1–2 roles (p.6–8) |
| `extracts/02-operating-principles.txt` | Ch.3 incl. versions (p.9–11) |
| `extracts/03-functional-framework.txt` | Ch.4 filename + T1T2 (p.12–17) |
| `extracts/04-generation-translation.txt` | Ch.5 permissibleUsage / translation (p.18–22) |
| `extracts/04b-partial-translation-minfields.txt` | §5.3.3 mins (p.20–21) |
| `extracts/05-transition-stats.txt` | Ch.6–8 METNO + §7 stats (p.23–30) |
| `extracts/06-appendix-amhs.txt` | App A AMHS profile (p.31–37) |
| `extracts/07-appendix-tests.txt` | App B tests (p.38–43) |
| `extracts/08-appendix-metno.txt` | App C METNO (p.44–46) |

---

## Suggested next mining passes

1. When ICAO publishes a **post-2025-2** Guidelines edition, re-mine §3.1.7 for version deprecation language vs PPT-02.
2. Purchase / mine **published** Doc 10003 and reconcile its translation-centre chapter with Guidelines §5.3 / §7.
3. Diff vendored v2025-2 Schematron for `gml:id` UUID rules vs §5.2 recommendation.
