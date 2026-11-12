# APAC encode theme → fixture map — S030 / EV-023 (T0.1)

**Date**: 2026-07-30  
**Task**: T0.1  
**Issue**: [#800](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/800)  
**Authority**: Runtime SoT `vendor/manifest.json` → IWXXM **v2025-2**. FAQ / 2019 Manual /
translation suite XML = **informative** only.

**Seeds**:  
- [icao-apac-iwxxm-faqs-3rd-2025-mining-notes.md](../../../domain/mining/icao-apac-iwxxm-faqs-3rd-2025-mining-notes.md)  
- [codes-wmo-int-aviation-mining-notes.md](../../../domain/mining/codes-wmo-int-aviation-mining-notes.md)  
- [iwxxm-translation-parity-mining-notes.md](../../../domain/mining/iwxxm-translation-parity-mining-notes.md)  
- [WMO-306-vI-3-2019-upd-2021-mining-notes.md](../../../domain/mining/WMO-306-vI-3-2019-upd-2021-mining-notes.md)  
- Standing: `IWXXM_CONVERSION.md`, `IWXXM_VALIDATION.md`, `COVERAGE_MATRIX.md`

## Keep-green (regression)

| Pack | Owner |
|------|-------|
| F15–F27 quality goldens / lint packs | Prior sessions |
| F23–F25 WMO packs | S025/S026 |
| F26/F27 VAA/TCA | S027 |

Do **not** treat `*-translation-failed.*` as happy-path goldens (ADR-032 / prior quality bars).

---

## TC-EV023-001 — NSC without layered cloud (P0 / M1)

| Role | Path / cue |
|------|------------|
| Primary TAC seed | `vendor/schemas/iwxxm-translation/Amd79-80-2023/metar/EFHK-290020Z.tac` (SPECI … **NSC** … NOSIG) |
| TAF NSC seeds | `…/taf/OIZC-131130Z.tac`; `SARP-131100Z.tac`; `SARP-131251Z.tac` |
| Local annex3 | `packages/tac2iwxxm/tests/fixtures/annex3_golden/speci_nsc.tac`; `speci_a3_2.tac` (trend NSC) |
| Encode target | Empty/nil `<iwxxm:cloud nilReason="…/common/nil/nothingOfOperationalSignificance"/>` — **no** layered CloudLayer children |
| Negative | Synth TAC or XML with NSC **and** FEW/SCT/… layers → SCH/XSD or convert assert fail |
| Lint today | Research `NSC_PRESENT` (`info`) in `tac-validate` — tighten in T1.3 if exclusivity needs stronger severity/code |
| Convert today | `profiles/annex3.py` `NIL_NSC`; `metar_speci.py` `_NSC` — verify no dual emit |
| TC / tasks | TC-EV023-001 → T1.1–T1.3 |
| Cite | FAQ §14.3; Guidance cloud/NSC; mining translation parity §NSC |

---

## TC-EV023-002 — Missing WX / Guidance nils (P0 / M2)

| Role | Path / cue |
|------|------------|
| No WX group | `Amd79-80-2023/metar/LTCN-282350Z.tac`; `EDDH-290020Z.tac` (NSW / empty weather) |
| AUTO `//` WX | `…/metar/CWFD-290000Z.tac` → `notObservable` / related AUTO nils |
| AUTO vis | `…/metar/ENFB-282350Z.tac` |
| URI families | Prefer official 2025-2 example vocabulary: usually `codes.wmo.int/common/nil/…`; use `iwxxm/nil` only where XSD `vocabulary=` requires |
| Guidance | `vendor/schemas/iwxxm/2025-2/IWXXM/examples/TAC-to-XML-Guidance.txt` |
| Corroborate only | WMO-306 2019/upd-2021 D-1 tables — **not** alternate SoT |
| TC / tasks | TC-EV023-002 → T2.1–T2.2 |

---

## TC-EV023-003 — translationFailedTAC quarantine (P0 / M3)

| Role | Path |
|------|------|
| Official 2025-2 failed examples | `vendor/schemas/iwxxm/2025-2/IWXXM/examples/*-translation-failed.{tac,xml}` |
| Products | METAR, TAF, AIRMET, VA/TCA advisory, SWX (OOS encode), SIGMET-in-COLLECT |
| Attr matrix (shared) | `reportStatus`, `permissibleUsage`, `@translationFailedTAC`, `translationCentreDesignator/Name`, `translationTime`, `translatedBulletinID`, `translatedBulletinReceptionTime` |
| Policy | Quarantine shell + original TAC string; **no** operational TAC-in-XML-comments; **no** partial operational translate |
| Default in-State convert | Still **omit** centre attrs on *success* path (FAQ §14.5); failed official examples model a Translation Centre (always show centre attrs) |
| Deepen | UJ-016 soft-preview consistency |
| TC / tasks | TC-EV023-003 → T3.1–T3.2 |
| Cite | FAQ §4.1 / §8.6; OPMET Guidelines §5.3.3; mining translation parity |

---

## TC-EV023-004 — Dual-register colour + nil (P1 / M4)

| Role | Path |
|------|------|
| `49-2/AviationColourCode` | `vendor/schemas/iwxxm-codelists/TTL/49-2/AviationColourCode.ttl` + CSV entity |
| `iwxxm/AviationColourCode` | Prefer pin 2025-2 VAA colour set (GREEN/YELLOW/ORANGE/RED/**UNASSIGNED**) — see codes mining notes |
| Dual nil | SCH RDF: `common/nil` + `iwxxm/nil` offline vendor copies |
| Suite lag note | Amd79 VAA `FVAU03ADRM-0424` may use `49-2/…/RED`; our 2025-2 encode prefers `iwxxm/` where XSD says so |
| CI | **No** live codes.wmo.int HTML (vendor CSV 402 ≠ live HTML ≈101 for 306/4678) |
| TC / tasks | TC-EV023-004 → T4.1–T4.2 |

---

## TC-EV023-005 — iwxxm-translation informative suite (P1 / M5)

| Role | Path |
|------|------|
| Suite tip | `vendor/schemas/iwxxm-translation/Amd79-80-2023/` |
| Products | **metar/** (METAR+SPECI), **taf/**, **volcanic-ash-advisory/**, **tropical-cyclone-advisory/** |
| Absent | SIGMET / AIRMET trees — keep `schemas.wmo.int` / vendor 2025-2 examples as P0 for those |
| Assert | TAC → our **2025-2** convert → XSD+SCH; **informative** marker |
| Do not | Byte-match suite 2023-1 XML; ignore `gml:id`, translation* attrs, clock fields |
| CI | Soft/xfail in main CI (**E23-T4=2**) |
| TC / tasks | TC-EV023-005 → T5.1–T5.2 (+ T0.3 marker) |

---

## TC-EV023-006 — translationCentre* gate (P1 / M4)

| Role | Detail |
|------|--------|
| Default | **Omit** `translationCentreDesignator` / `translationCentreName` on successful in-State convert |
| Emit | Form `emit_translation_centre=true` + optional `translation_centre_designator` / `translation_centre_name` (**E23-T2**) |
| Contrast | Official `*-translation-failed.xml` always include centre attrs (Translation Centre model) |
| Canonicalize | `metar_shared.xml_canonical` already strips translation* for golden compare |
| TC / tasks | TC-EV023-006 → T4.3–T4.4 |
| Cite | FAQ §14.5 |

---

## TC-EV023-007 — SIGMET FIR / “S OF” polygon helpers (P2 / M6)

| Role | Detail |
|------|--------|
| Scope | Helper unit tests + impl; **not** full TC SIGMET quality bar |
| Coord | [#738](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/738) / F23 geometry backlog |
| Cite | [Geospatial objects wiki](https://github.com/wmo-im/iwxxm/wiki/Geospatial-objects-in-IWXXM); FAQ §3.3 |
| Prefer | Polygon TAC over FIR-boundary-only when both possible |
| TC / tasks | TC-EV023-007 → T6.1–T6.2 |

---

## TC-EV023-008 — COLLECT / multi-version namespaces (P2 / M6)

| Role | Detail |
|------|--------|
| Scope | Hooks/docs/tests on **F16–F19 / bulletin** path (**S02.M2**) — not single-report convert SoT |
| Mandate | AFS COLLECT + per-group `http://icao.int/iwxxm/{version}` |
| Fixture cue | `sigmet-translation-failed-collect` (failed member inside COLLECT) |
| TC / tasks | TC-EV023-008 → T6.3 |

---

## TC-EV023-009 — Optional #798 QA + coverage matrix (P2 / M6)

| Role | Detail |
|------|--------|
| Optional QA | aviation nilReasons stubbed as `missing`; VAA/VONA METCE; TCA METCE name-only — **only if** gaps survive defer-to-latest |
| Matrix | Confirm `COVERAGE_MATRIX.md` APAC/codes/#800 citations after P0/P1 |
| Git | No `.local/` binaries |
| TC / tasks | TC-EV023-009 → T6.4 |

---

## HTTP / config locks (for M4 / M7)

| Item | Lock |
|------|------|
| Form | `emit_translation_centre` (bool, default false) |
| Optional Form | `translation_centre_designator`, `translation_centre_name` |
| New deps | AskQuestion per dep (**E23-T3=2**) |
| Kill-switch | AskQuestion if HARD P0 blocked (**E23-T5**) |

## Milestone crosswalk

| TC | Milestone | Tasks |
|----|-----------|-------|
| 001 | M1 | T1.1–T1.3 |
| 002 | M2 | T2.1–T2.2 |
| 003 | M3 | T3.1–T3.2 |
| 004 | M4 | T4.1–T4.2 |
| 006 | M4 | T4.3–T4.4 |
| 005 | M5 (+T0.3) | T5.1–T5.2 |
| 007–009 | M6 | T6.1–T6.4 |
| smoke | M7 | T7.1–T7.4 |
