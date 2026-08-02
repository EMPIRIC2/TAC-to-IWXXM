# Eight-family re-mine pass — S036 / EV-029 (T0.2)

**Date**: 2026-08-01  
**Mode**: full re-mine before Phase B (E29-T3=2)  
**Pin**: IWXXM **v2025-2** (`vendor/manifest.json`)  
**Issue**: [#823](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/823)  
**Live fetch**: [AHLs for aviation data over ICAO AFS](https://community.wmo.int/en/activity-areas/wis/iwxxm/ahl-icao-data) v1.0.1 (2025-08-11) — **fetched 2026-08-01**

## Method

1. Re-read #823 Phase A / B1–B5 + COM themes.  
2. Cross-check vendor `IWXXM/examples/` stems + `TAC-to-XML-Guidance.txt` presence.  
3. Refresh AHL `T1T2` tables from live WMO AHL page (overrides stale copies).  
4. Map each family × (lint · convert · iwxxm-validate · bulletin) against prior
   `docs/domain/mining/*` + COVERAGE_MATRIX Fn themes.  
5. Record **promote** / **implement (M*)** / **child-issue** / **OOS**.

Paywall sources (Annex 3 21st, PANS-MET 10157, Doc 10003): **cite-only**; prefer
vendor pin + Guidance + AHL page where they diverge (ADR-014).

---

## A. Shared AHL / bulletin (all families)

### A.1 Live AHL page (v1.0.1) — confirmed

| Item | Spec text (summary) | Engine impact |
|------|---------------------|---------------|
| AHL form | `T1T2A1A2ii CCCC YYGGgg [BBB]` | Parse all products |
| BBB RR/CC/AA | Prefix families `RRx` / `CCx` / `AAx`, x=A…X; Y/Z special | #823 B3 — **not** full-token `A`/`C` |
| IWXXM filename | `A_T1T2A1A2iiCCCCYYGGgg[BBB]_C_CCCC_yyyyMMddhhmmss[_ffffff].xml[.gz]` | Dissemination; use **IWXXM** T1T2 |
| TAC T1 | S/F/U/W/N tables | Product map below |
| IWXXM T1 | **L** = aviation XML | Product map below |

### A.2 TAC ↔ IWXXM T1T2 (AHL page + #823 B1)

| Product | TAC | IWXXM | Root | Vendor example |
|---------|-----|-------|------|----------------|
| METAR | SA | LA | `iwxxm:METAR` | `metar-A3-1` |
| SPECI | SP | LP | `iwxxm:SPECI` | `speci-A3-2` |
| TAF &lt;12h | FC | LC | `iwxxm:TAF` | `taf-A5-1` |
| TAF ≥12h | FT | LT | `iwxxm:TAF` | `taf-A5-2` (cancel) |
| TCA | FK | LK | `iwxxm:TropicalCycloneAdvisory` | `tc-advisory-A2-2` |
| SWXA | FN | LN | `iwxxm:SpaceWeatherAdvisory` | `spacewx-A7-3/4/5` |
| VAA | FV | LU | `iwxxm:VolcanicAshAdvisory` | `va-advisory-A7-2` |
| AIRMET | WA | LW | `iwxxm:AIRMET` | `airmet-A6-1a-TS` |
| SIGMET gen | WS | LS | `iwxxm:SIGMET` | `sigmet-A6-1a-TS`, `…-1b-CNL` |
| TC SIGMET | WC | LY | `iwxxm:TropicalCycloneSIGMET` | `sigmet-A6-2-TC` |
| VA SIGMET | WV | LV | `iwxxm:VolcanicAshSIGMET` | `sigmet-VA-EGGX`, multi-loc |
| VONA | WM | LM | VONA root | **OOS** converter |
| QVACI / WAFS | — | — | — | **OOS** |

### A.3 Current code gap (bulletin)

`packages/tac2iwxxm/.../bulletin.py` — **METAR/SPECI AHL only**.  
**Promote/implement M1**: generalize AHL parse + T1T2 map + BBB prefix rules +
filename helper; dissemination imports same API (E29-T2).

### A.4 Prior mining to reuse

| Note | Use |
|------|-----|
| `OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md` | COLLECT / AMHS / partial translation |
| `icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md` | SIGMET/AIRMET TAC shapes + AHL |
| `wmo-im-iwxxm-IWXXM-tree-mining-notes.md` | examples tree |
| `iwxxm-2025-2-reference-set-mining-notes.md` | reference inventory |

---

## B. Family digs (lint · convert · validate)

Status: `ok` = prior Fn bar sufficient pending deepen · `gap` = known open ·
`mine→promote` = durable rule to promote in T0.4 · `impl` = Phase B Ms

### B.1 METAR (M2) — F15 deepen

| Role | Status | Sources | Action |
|------|--------|---------|--------|
| Lint | ok/deepen | F15 themes; FMH1 dig | Gap-scan vs M0 matrix only |
| Convert | ok/deepen | Guidance; `metar-A3-1` | Extend goldens if matrix gap |
| Validate | ok | metarSpeci.xsd + SCH | Smoke in pack |
| Bulletin | gap | AHL SA→LA | **M1** then M2 AHL fixtures |

### B.2 SPECI (M3) — F20 deepen

| Role | Status | Sources | Action |
|------|--------|---------|--------|
| Lint/Convert/Validate | ok/deepen | F20; `speci-A3-2` | Same as METAR |
| Bulletin | gap | SP→LP | **M1**/M3 |

### B.3 TAF (M4) — F20 deepen

| Role | Status | Sources | Action |
|------|--------|---------|--------|
| Lint/Convert/Validate | ok/deepen | F20; `taf-A5-1/2` | FC vs FT AHL; cancel path |
| Bulletin | gap | FC/FT→LC/LT | **M1**/M4 |

### B.4 General SIGMET (M5) — F23 deepen

| Role | Status | Sources | Action |
|------|--------|---------|--------|
| Lint/Convert/Validate | ok/deepen | F23 G1–G3; EUR Doc 014; `sigmet-A6-1a/1b` | Residual matrix cells |
| Bulletin | gap | WS→LS | **M1**/M5 |
| CNL | ok/deepen | `sigmet-A6-1b-CNL` | Report-state TC-EV029-006 |

### B.5 VA SIGMET (M6) — F23 deepen

| Role | Status | Sources | Action |
|------|--------|---------|--------|
| Lint/Convert/Validate | ok/deepen | F23 V1–V3; `sigmet-VA-EGGX`; multi-loc soft | Residual + adjacency |
| Bulletin | gap | WV→LV | **M1**/M6 |

### B.6 TC SIGMET (M7) — F23 / #738 **GAP**

| Role | Status | Sources | Action |
|------|--------|---------|--------|
| Lint | gap | #738; EUR Doc 014 WC | Registry + fixtures **M7** |
| Convert | gap | `sigmet-A6-2-TC` → must be `TropicalCycloneSIGMET` not `SIGMET`/`TCA` | **M7** / TC-EV029-004 |
| Validate | gap | tropicalCycloneSigmet schema path | **M7** |
| Bulletin | gap | WC→LY | **M1**/M7 |
| Menu | deferred | S031 S02.M2 | Optional unlock later |

### B.7 AIRMET (M8) — F24 deepen

| Role | Status | Sources | Action |
|------|--------|---------|--------|
| Lint/Convert/Validate | ok/deepen | F24; `airmet-A6-1a-TS`; EUR Doc 014 | Residual cells |
| Bulletin | gap | WA→LW | **M1**/M8 |

### B.8 VAA (M9) — F26 / #820 / #823 B4 **GAP residual**

| Role | Status | Sources | Action |
|------|--------|---------|--------|
| Lint | ok/deepen | F26 V1–V3 | Residual |
| Convert | gap residual | B4: `=` splitter; nilReasons; forecast cardinality; multi-report | **M9** + #820 |
| Validate | ok/deepen | VAA 3.2.0 under 2025-2 | Goldens |
| Bulletin | gap | FV→LU; B2 framing | **M1**/M9 |

### B.9 TCA (M10) — F27 / #820 / #823 B4 **GAP residual**

| Role | Status | Sources | Action |
|------|--------|---------|--------|
| Lint | ok/deepen | F27 T1–T3 | Residual |
| Convert | gap residual | Same B4 themes; adjacency vs TC SIGMET | **M10** + #820 |
| Validate | ok/deepen | TCA 3.1.1 | Goldens |
| Bulletin | gap | FK→LK | **M1**/M10 |

### B.10 SWXA (M11) — F28 / #740 **GAP**

| Role | Status | Sources | Action |
|------|--------|---------|--------|
| Lint | gap | No F28 registry bar yet | **M11** TC-F28-001/004 |
| Convert | gap | `spacewx-A7-3/4/5` (+ alt); root `SpaceWeatherAdvisory` | **M11**; golden may be `wmoReference` (S02.L1) |
| Validate | gap | spaceWxAdvisory schema + SCH | **M11** |
| Bulletin | gap | FN→LN | **M1**/M11 / TC-F28-006 |
| API | gap | `product=swxa` runtime | **M11** (docs done) |
| Menu | deferred | Was roadmap in S031 | Unlock only if FE ships |

---

## C. Report-state / COM themes (#823 B3)

| Theme | Rule | Promote |
|-------|------|---------|
| BBB→reportStatus | AA*→AMENDMENT, CC*→CORRECTION, RR*→subsequent NORMAL | T0.4 + M1 |
| Invalid BBB | Reject over-broad gate like GIFTs `[ACR]{2}[A-Z]` | M1 lint |
| CNL / NIL | Not reportStatus; product/nilReason paths | Per-family Ms + TC-EV029-006 |
| Y/Z BBB | Special purposes per AHL page | Document; fixture if needed |

---

## D. Official examples inventory seed → **T0.3 complete**

Expanded matrix (shapes × families, catalog tiers, AHL `T1T2` gaps):
[`example-inventory.md`](./example-inventory.md).

| Stem | Family | Happy-path encode? | Notes |
|------|--------|--------------------|-------|
| metar-A3-1 | METAR | yes | wmoPass prior |
| speci-A3-2 | SPECI | yes | |
| taf-A5-1 / A5-2 | TAF | yes / cancel | |
| sigmet-A6-1a-TS / 1b-CNL | SIGMET gen | yes | |
| sigmet-A6-2-TC | TC SIGMET | **#738** | Quality bar M7 |
| sigmet-VA-EGGX | VA SIGMET | soft/pass | |
| sigmet-multi-location-VA | VA SIGMET | soft / wmoPass | |
| airmet-A6-1a-TS | AIRMET | yes | |
| va-advisory-A7-2 | VAA | yes | B4 residuals; vendor AHL FV |
| tc-advisory-A2-2 | TCA | yes | B4 residuals |
| spacewx-A7-3/4/5 (+ alt) | SWXA | **F28** | May wmoReference |
| *-translation-failed* | quarantine | no | Not happy path |
| *-NIL-collect* | COLLECT | validate only | AHL SA/FT present |
| vona / WAFS / qvaci | OOS | — | |

---

## E. Promote queue (T0.4)

1. COVERAGE_MATRIX — add **S036/EV-029** section; mark TC SIGMET / SWXA / AHL gaps; amend SIGMET row (#738 no longer OOS for this cycle).  
2. Canonicals — AHL T1T2 + BBB prefix + filename pattern (cite live AHL page).  
3. RULE_SOURCE_URLS — AHL page v1.0.1 row if missing/stale.  
4. Child issues — residual cells after promote (S02.M3); keep #823 open.

## F. HARD blockers for Phase B? (E29-T8)

| Item | Block? |
|------|--------|
| Paywall Annex 3 / PANS-MET full text | **No** — cite-only; vendor+AHL+Guidance sufficient for M0 exit |
| AHL page fetch | **Resolved** this pass |
| TC SIGMET / SWXA encode incomplete | **No** — Phase B Ms (not M0 blockers) |

**M0 exit (T0.6):** after T0.3–T0.5, AskQuestion only if new HARD gap appears.

---

## G. Next tasks

| Task | Deliverable |
|------|-------------|
| **T0.3** | ~~Example inventory~~ → [`example-inventory.md`](./example-inventory.md) |
| **T0.4** | Promote §E into `docs/domain/` |
| **T0.5** | AHL design note (tac2iwxxm API surface) |
| **T0.6** | M0 exit checklist |
