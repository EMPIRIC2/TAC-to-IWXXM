# ICAO APAC IWXXM FAQs (3rd Ed., March 2025) — mining notes

Transitory dig — **not** standing SoT. Promote durable citations into domain canonicals / `rules/`.

**Source:** IWXXM Implementation in APAC Region — Frequently Asked Questions (FAQs), Third Edition  
**URL:** https://www.icao.int/sites/default/files/APAC/Documents/edocs/MET/2025-03_IWXXM-FAQs_3rd-Ed.pdf  
**Local:** `.local/reference/icao-apac-iwxxm-faqs-3rd-2025/`  
**Label:** **informative** (regional Q&A; points at normative docs)  
**Mined:** 2026-07-30  
**Ticket:** [#797](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/797)  
**Companion sources (same dig):** [codes.wmo.int](./codes-wmo-int-aviation-mining-notes.md), [iwxxm-translation parity](./iwxxm-translation-parity-mining-notes.md)

## Focus

Encoder / translator / validator product implications for F6–F23 and dissemination F16–F19 — not AMHS network ops prose unless it constrains XML shape.

## What this source is / is not

| Is | Is not |
|----|--------|
| APAC workshop FAQ (2017–2020 events + 2025 refresh) | Binding SARPs (use Annex 3) |
| Pointers to Doc 10003, OPMET IWXXM Exchange Guidelines, Package Compatibility wiki, iwxxm-translation | Substitute for OPMET Guidelines 5th (already mined) |
| Practical encode gotchas (NSC, `translationFailedTAC`, COLLECT multi-version) | Full Schematron rule set |

## Key excerpts (with page markers)

| Page | Claim / quote | Canonical / consumer target |
|------|---------------|-------------------------------|
| 2 | Topics: production, exchange, compression, versions, **translation**, validation, extensions, common issues | catalog |
| 3–5 | Product set includes METAR/SPECI, TAF, SIGMET, AIRMET, TCA, VAA, **SWX**; evolution toward phenomenon/object (WAFS SWX, VONA, QVA); TAC global exchange sunset **~2030** (Amd 84) | `IWXXM_CONVERSION` roadmap; #740/#741 |
| 6 **§3.2** | Missing TAC params → consult `TAC-to-XML-Guidance.txt` on schemas.wmo.int + real examples in **wmo-im/iwxxm-translation** | `tac2iwxxm` Guidance + informative goldens |
| 6 **§3.3** | SIGMET geometry: prefer polygon; “S OF” / “ENTIRE FIR” → FIR boundary intersection; wiki Geospatial-objects-in-IWXXM | SIGMET convert (F23 / #738) |
| 6 **§3.4** | Only METAR/TAF need aggregation; **all** AFS IWXXM must use **COLLECT** before send | bulletin / F16–F19 |
| 6–7 **§4.1** | Do **not** put TAC in IWXXM comments operationally; on unreliable translation, include original TAC with no further info (`translationFailedTAC` path) | convert quarantine |
| 10–11 **§8.6–8.9** | Use `translationFailedTAC` on failure; fixtures: schemas examples + iwxxm-translation; incomplete translation → notify originator | convert + operator UX |
| 11 **§8.3** | TAC→IWXXM allowed under agreement; **IWXXM→TAC not permitted** when original TAC exists | product policy |
| 12 **§9** | Extensions need web-accessible XSD (+ SCH); integrity first; business-rule QC later; cites NCAR CRUX | `iwxxm-validate` scope |
| 14–15 **§14.3** | **NSC** and layered `cloud` must **not** co-occur — NSC ⇒ cloud element not required (validation alarm) | `tac2iwxxm` + SCH |
| 15 **§14.5** | `translationCentre*` attrs only when translation is **on behalf of another State** | convert metadata defaults |
| 15–16 **§14.7** | Multi-version COLLECT: declare `http://icao.int/iwxxm/{version}` per group | bulletin aggregators |

## Gaps / conflicts vs this repo

| FAQ claim | Repo state | Action |
|-----------|------------|--------|
| Prefer iwxxm-translation for translator checks (§8.7) | Vendor pin `iwxxm-translation` @ Amd79-80-2023 / IWXXM **2023-1**; COVERAGE_MATRIX treats as **P2 informative**; historical live-test diffs vs **2025-2** encode | Ticket: structure-compare suite (not byte-match) on Amd79-80-2023 METAR/TAF/VAA/TCA |
| NSC ≠ cloud layers (§14.3) | Encoder emits NSC nilReason; lint has `NSC_PRESENT` research flags — need explicit **negative** convert+SCH fixture for NSC+layer | Ticket P0 encode/lint |
| Missing WX → Guidance (§3.2) | Guidance cited in canonicals; ensure missing-wx nils match Guidance + translation fixtures | Ticket P1 |
| SIGMET FIR geometry (§3.3) | F23 done for family quality; polygon-from-FIR still hard | Link #738 / geometry backlog |
| COLLECT always for AFS (§3.4) | Dissemination F16–F19; convert may emit single reports | Ops / bulletin — not engine SoT |
| Examples cite **2023-1** html (§14.3) | Runtime pin **v2025-2** | Prefer vendor/pin docs; FAQ pages are edition-lagged |

## Product × artifact matrix

| Product | TAC / ops input | IWXXM / register | Official example or FAQ § | Gap vs GIFTs | Consumer |
|---------|-----------------|------------------|---------------------------|--------------|----------|
| METAR / SPECI | Missing WX; NSC; CAVOK | Guidance nils; empty cloud | §3.2, §14.3 | NSC+layer co-occurrence | `tac2iwxxm`, `tac-validate`, SCH |
| TAF | Same nil/omit patterns | same | §3.2; COLLECT aggregation §3.4 | Multi-aerodrome bulletins | convert + bulletin |
| SIGMET | Relative geometry (“S OF”, ENTIRE FIR) | FIR→polygon | §3.3 + geospatial wiki | Outside GIFTs | convert (#738 / #797) |
| AIRMET | (same geometry family) | same | §3.3 | Outside GIFTs | convert |
| VAA / TCA | Translator fixture checks | iwxxm-translation pairs | §8.7 | Outside GIFTs | P2 informative goldens |
| SWX / VONA / QVA | Roadmap only | phenomenon-based packages | §2.3 / §2.5 | IWXXM-only path | #740 / #741 — not F6 gate |
| Bulletin / AFS | COLLECT wrap; multi-version ns | `iwxxm-collect` | §3.4, §14.7 | Outside GIFTs | F16–F19 / ops |

## Catalog paste rows

```text
### ICAO APAC IWXXM FAQs (3rd Ed., March 2025)
- Publisher: ICAO Asia/Pacific (MET eDocs)
- URL: https://www.icao.int/sites/default/files/APAC/Documents/edocs/MET/2025-03_IWXXM-FAQs_3rd-Ed.pdf
- Access: public PDF; local .local/reference/icao-apac-iwxxm-faqs-3rd-2025/
- Applies to: products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA,SWX]; profiles=[annex3]; role=[conversion,iwxxm-validation,bulletin]
- Gap vs GIFTs: NSC exclusivity; translationFailedTAC; translationCentre cross-State only; COLLECT multi-version
- Consumer: tac2iwxxm | tac-validate | iwxxm-validate | bulletin
- Label: informative
- Caveats: not encode SoT; some cites lag pin (2023-1 html); prefer OPMET Guidelines 5th for AMHS/FTBP
- Mined: 2026-07-30 · #797
```

## Domain-knowledge cross-check

| Older claim | This source (Mar 2025 FAQ) | Action |
|-------------|----------------------------|--------|
| Doc 10003 Advance 2014 “no bulletin schema” | COLLECT + multi-version namespaces §14.7 | Keep Advance dig **historical**; COLLECT SoT = pin + OPMET Guidelines |
| OPMET Guidelines 5th (Oct 2023) translationCentre prose | FAQ §14.5: attrs only for **another State** | **Complement** Guidelines — promote FAQ nuance into `IWXXM_CONVERSION` (done); Guidelines remain normative-exchange |
| PPT-02 “omit translation attrs when self-translating” | Same as FAQ §14.5 | Keep both informative; FAQ is clearer for State boundary |
| FAQ cites schemas **2023-1** context diagrams §14.3 | Vendor pin **v2025-2** | Defer runtime to pin; treat FAQ diagram link as edition-lagged |
| iwxxm-translation as translator validation (§8.7) | Suite tip still **2023-1** XML | Informative TAC inputs only; P0 = official 2025-2 examples ([parity dig](./iwxxm-translation-parity-mining-notes.md)) |

## Implications for this repo

- **F6 / tac2iwxxm:** NSC omit layers; missing WX via Guidance; quarantine `@translationFailedTAC`; gate `translationCentre*`; no operational TAC-in-comments.
- **tac-validate:** Optional NSC+layer warn before convert (A3-2 footnote promoted).
- **iwxxm-validate:** Negative NSC+layer SCH smoke under #797; dual nil RDF unchanged.
- **bulletin / F16–F19:** COLLECT for AFS; multi-version namespace groups — ops, not single-report SoT.
- **Caveats / TBD:** Engine fixtures remain #797; AMHS FTBP Authorization Time out of encode scope.

## Suggested next mining passes

1. ~~Diff official `examples/*-translation-failed*` vs FAQ §8.6 / Guidelines §5.3.3~~ — **done** in [parity dig](./iwxxm-translation-parity-mining-notes.md) (full translation* attr set on pin examples).
2. Geospatial wiki for SIGMET FIR phrases — **skimmed**: [Geospatial objects in IWXXM](https://github.com/wmo-im/iwxxm/wiki/Geospatial-objects-in-IWXXM) documents `issuingAirTrafficServicesRegion` as `aixm:Airspace` with optional `aixm:geometryComponent` / `gml:PolygonPatch` for FIR boundary — supports FAQ §3.3 polygon preference; deeper geometry engine work remains #738 / #797.
3. When Annex 3 Amd 84 TAC-sunset text is public, refresh roadmap cites (FAQ §2.12 is forward-looking informative only).

## Promotion checklist

- [x] Catalog row for FAQ PDF → `RULE_SOURCE_URLS.md` (this pass)
- [x] Canonical prose in `IWXXM_CONVERSION.md` (NSC, missing WX, translationFailedTAC, translationCentre, P2 suite policy, FAQ landing)
- [x] Coverage matrix “FAQ informative” row + consumer routing
- [x] `TAC_VALIDATION.md` A3-2 NSC exclusivity footnote
- [x] `IWXXM_VALIDATION.md` NSC + dual colour/nil register notes
- [x] Mining index updated
- [x] Product matrix + cross-check + implications (this continue)
- [x] PDF re-verified identical to Downloads upload (SHA-256 `ec29cd61…`) · 2026-07-30 continue
- [x] translation-failed / geospatial wiki follow-ups documented
- [ ] Engine fixtures / lint deepen — remains #797 (seed TAC list in [parity dig](./iwxxm-translation-parity-mining-notes.md))
