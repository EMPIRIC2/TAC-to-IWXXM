# Example inventory — TAC shapes × families (T0.3)

**Date**: 2026-08-01  
**Task**: T0.3 · **TC**: TC-EV029-002 · **UJ**: UJ-043  
**Cycle**: EV-029 / S036 · **Issue**: [#823](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/823)  
**Pin**: `vendor/schemas/iwxxm/2025-2/IWXXM/examples/` (manifest **v2025-2**)

Expands remine §D. Does **not** invent TAC — vendor + package fixtures only.
Promote durable cells into `COVERAGE_MATRIX` / FIXTURE_GAPS in **T0.4** (docs) and
wire missing shapes in Phase B milestones.

## Shape legend

| Shape | Meaning |
|-------|---------|
| **Standalone** | Single report body, no WMO AHL line |
| **AHL** | `T1T2A1A2ii CCCC YYGGgg [BBB]` + report(s) |
| **Multi-report** | AHL + N reports / `=` terminators (bulletin) |

Status: `covered` · `gap` · `N/A` · `OOS` · `defer+Ms` (gap documented; implement later)

Peer tiers (ADR-032): `wmoPass` · `wmoReference` · `vendor-only` (not in FE catalog) ·
`package` (non-WMO demo / lint fixture).

---

## A. Family × shape coverage matrix (TC-EV029-002)

| Family | Standalone | AHL | Multi-report | Primary IWXXM peer | Milestone |
|--------|------------|-----|--------------|--------------------|-----------|
| AHL/COM (shared) | N/A | covered (METAR pack) | covered (METAR multi) | N/A (framing) | **M1** |
| METAR | covered | covered | covered | `metar-A3-1.xml` | **M2** |
| SPECI | covered | covered (T3.1) | covered (T3.1) | `speci-A3-2.xml` | **M3** |
| TAF | covered | covered (NIL-collect) | **gap** | `taf-A5-1/2.xml` | **M4** |
| SIGMET gen | covered | covered (quarantine collect) | **gap** | `sigmet-A6-1a-TS.xml` | **M5** |
| VA SIGMET | covered | **gap** | **gap** | `sigmet-VA-EGGX.xml` / multi-loc | **M6** |
| TC SIGMET | covered (vendor) | **gap** | **gap** | `sigmet-A6-2-TC.xml` | **M7** (#738) |
| AIRMET | covered | **gap** | **gap** | `airmet-A6-1a-TS.xml` | **M8** |
| VAA | covered | covered (vendor FVFE01) | **gap** (#820) | `va-advisory-A7-2.xml` | **M9** |
| TCA | covered | **gap** | **gap** (#820) | `tc-advisory-A2-2.xml` | **M10** |
| SWXA | covered (vendor) | **gap** (FN) | N/A (advisory form) | `spacewx-A7-3/4/5.xml` (+ alt) | **M11** (F28) |

**Verdict:** No silent blanks — every family has ≥1 standalone peer **or** an explicit
`gap`/`defer+Ms` cell. Multi-report and non-METAR AHL are the main deepen queue for M1+.

---

## B. Official vendor stems (expand remine §D)

Paths under `vendor/schemas/iwxxm/2025-2/IWXXM/examples/` unless noted.

| Stem | Family | Shape (vendor) | FE catalog | Peer XML | Encode / note |
|------|--------|----------------|------------|----------|---------------|
| `metar-A3-1` | METAR | Standalone | `metar_a3_1` **wmoPass** | yes | Happy path |
| `speci-A3-2` | SPECI | Standalone | `speci_a3_2` **wmoPass** | yes | Happy path |
| `taf-A5-1` | TAF | Standalone | `taf_a5_1` **wmoPass** | yes | Happy path |
| `taf-A5-2` | TAF | Standalone (AMD/CNL) | `taf_a5_2` **wmoPass** | yes | Cancel / CNL |
| `sigmet-A6-1a-TS` | SIGMET gen | Standalone | `sigmet_a6_1a_ts` **wmoPass** | yes | Happy path |
| `sigmet-A6-1b-CNL` | SIGMET gen | Standalone (CNL) | `sigmet_a6_1b_cnl` **wmoPass** | yes | CNL product path |
| `sigmet-A6-2-TC` | TC SIGMET | Standalone | **gap** FIXTURE_GAPS | yes | **#738** · M7 · not catalog |
| `sigmet-VA-EGGX` | VA SIGMET | Standalone (`=` end) | `sigmet_va_eggx` **wmoReference** | yes | Soft / deepen M6 |
| `sigmet-multi-location-VA` | VA SIGMET | Standalone (AND locs) | `sigmet_multi_location_va` **wmoPass** | yes | Multi-location ≠ multi-report |
| `airmet-A6-1a-TS` | AIRMET | Standalone | `airmet_a6_1a_ts` **wmoPass** | yes | Happy path |
| `va-advisory-A7-2` | VAA | **AHL** `FVFE01` + body | `vaa_a7_2` **wmoPass** | yes | B4 residuals · M9 |
| `tc-advisory-A2-2` | TCA | Standalone (TC ADVISORY) | `tca_a2_2` **wmoPass** | yes | B4 residuals · M10 |
| `spacewx-A7-3` | SWXA | Standalone (SWX ADVISORY) | **gap** (deferred product) | yes + `_alternate` | **F28** · may `wmoReference` (S02.L1) |
| `spacewx-A7-4` | SWXA | Standalone | gap | yes + alt | F28 |
| `spacewx-A7-5` | SWXA | Standalone | gap | yes | F28 |
| `metar-NIL-collect` | METAR | **AHL** `SAYU31` + NIL | deferred (COLLECT) | yes | Validate/COLLECT · not menu |
| `taf-NIL-collect` | TAF | **AHL** `FTYU31` + NIL | deferred (COLLECT) | yes | Validate/COLLECT · not menu |
| `*-translation-failed*` | quarantine | various | OOS happy-path | yes | Quarantine only |
| `vona-A7-1` | VONA | Standalone | **OOS** | yes | Converter OOS |
| `qvaci-Example` / WAFS | — | XML-only | **OOS** | yes | Converter OOS |

Inventory SoT (F6 seven happy-path):  
`packages/tac2iwxxm/tests/fixtures/wmo_official_tac_inventory.py` — **extend in M11** for
`spacewx-*` when F28 catalog unlocks (do not silently add to happy-path before M11).

---

## C. Package / FE shape fixtures (non-vendor or bulletin demos)

| Fixture | Family | Shape | Role | Path |
|---------|--------|-------|------|------|
| `metar_single_ahl.txt` | METAR | AHL `SAUS31` + 1 METAR | Bulletin parse | `packages/tac2iwxxm/tests/fixtures/` |
| `metar_ahl_with_bbb.txt` | METAR | AHL + `CCA` BBB | BBB→COR | same |
| `metar_multi_ahl.txt` | METAR | AHL + 2 METARs (`=`) | Multi-report | same (+ FE `ahl_metar_multi`) |
| `metar_basic.golden.xml` | METAR | IWXXM collect | FE `collect_iwxxm` | `annex3_golden/` |
| `metar_c1_multi_report.tac` | METAR | Multi-report (lint) | Accept pack | `tac-validate/.../accept/` |
| `product_matrix/*` | mixed | Standalone (trimmed) | Convert matrix | `tac2iwxxm/.../product_matrix/` |

**AHL `T1T2` fixture coverage (B1 / TC-EV029-003):** **M1 closed** — heading-only
accept fixtures for every TAC `T1T2` under `packages/tac2iwxxm/tests/fixtures/ahl/`
(+ BBB accept/reject). Vendor still supplies **FV** / NIL-collect peers. Remaining gaps
are **body split + multi-report** per family (M2–M11).

| TAC `T1T2` | Family | AHL heading fixture | Remaining |
|-----------:|--------|---------------------|-----------|
| SA | METAR | package + `ahl/sa_*` + `fixtures/metar/*` + NIL-collect | **M2 closed** (BBB→`reportStatus` + product-order pack) |
| SP | SPECI | package + `ahl/sp_speci.txt` + `fixtures/speci/*` | **T3.1** fixtures (BBB→`reportStatus` + multi + product-order); T3.2/T3.3 close |
| FC / FT | TAF | `ahl/fc_*` / `ahl/ft_*` | M4 body split |
| WS | SIGMET gen | `ahl/ws_sigmet.txt` | M5 body split |
| WV | VA SIGMET | `ahl/wv_va_sigmet.txt` | M6 body split |
| WC | TC SIGMET | `ahl/wc_tc_sigmet.txt` | M7 body split |
| WA | AIRMET | `ahl/wa_airmet.txt` | M8 body split |
| FV | VAA | `ahl/fv_vaa.txt` + vendor A7-2 | M9 multi-report |
| FK | TCA | `ahl/fk_tca.txt` | M10 body split |
| FN | SWXA | `ahl/fn_swxa.txt` | M11 body + encode |

---

## D. Report-state seed (feeds TC-EV029-006)

| State | Example stem / fixture | Families covered today | Gaps |
|-------|------------------------|------------------------|------|
| Normal | Most A3/A5/A6/A7 peers | All except SWXA catalog | SWXA M11 |
| Amendment | `taf-A5-2` (AMD…CNL); METAR BBB `CCA` is COR not AMD | TAF; METAR COR fixture | Per-family `AAx` AHL · M1+ |
| Correction | `metar_ahl_with_bbb.txt` (`CCA`); lint `*_cor*` | METAR/SPECI lint | Other families COR AHL |
| Cancellation | `sigmet-A6-1b-CNL`; `taf-A5-2` CNL | SIGMET gen, TAF | AIRMET CNL peer absent (FIXTURE_GAPS); others |
| NIL / missing | `metar-NIL-collect`; `taf-NIL-collect`; lint `*_nil*` | METAR, TAF | Per-family NIL · not reportStatus |

CNL/NIL are **not** `reportStatus` — product paths (theme map + remine §C).

---

## E. FIXTURE_GAPS / catalog delta notes (document only — T0.4 may amend)

Current FE `FIXTURE_GAPS.md` / catalog (unchanged this task):

| Item | Status | EV-029 action |
|------|--------|---------------|
| Second METAR/SPECI/AIRMET/VAA/TCA peer | Documented (pin has one) | Keep; no invent |
| `sigmet-A6-2-TC` menu defer | #738 | Unlock **M7** when quality path green |
| `spacewx-*` deferred product | F28 | Register **M11** (`wmoPass` or `wmoReference`) |
| Non-METAR AHL / multi-report | Not in FIXTURE_GAPS table | Add stem-level rows in T0.4 or child issues (S02.M3) |
| SIGWX / VONA / QVACI | OOS | Keep OOS — do not catalog |

---

## F. OOS converter inputs

| Stem / class | Reason |
|--------------|--------|
| `vona-*` | VONA product OOS for tac2iwxxm convert |
| `qvaci-Example.xml` / WAFS | Not TAC→IWXXM operator path |
| SIGWX charts | Not in eight-family convert scope |

---

## G. HARD blockers for Phase B? (E29-T8)

| Item | Block M0 exit? |
|------|----------------|
| Missing SPECI AHL fixtures | **Closed T3.1** — `fixtures/speci/speci_ahl_*` + multi; other families remain M4+ |
| TC SIGMET / SWXA not in catalog | **No** — #738 / F28 Ms |
| Multi-report only for METAR | **No** — #820 / M9–M10 |
| Paywall Annex 3 full text | **No** — cite-only |

No new HARD gap from this inventory.

---

## H. Next

| Task | Deliverable |
|------|-------------|
| **T0.4** | Promote durable rows → `COVERAGE_MATRIX` + canonicals; child-issue residuals |
| **T0.5** | AHL/`T1T2`/BBB design note (tac2iwxxm surface) |
| **T0.6** | M0 exit checklist |
