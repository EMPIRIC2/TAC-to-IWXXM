# Eight-family theme → deliverable map — S036 / EV-029

**Date**: 2026-08-01  
**Task**: T0.1  
**Issue**: [#823](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/823)  
**Pin**: `vendor/manifest.json` → IWXXM **v2025-2**  
**UJ**: UJ-043

## Roles × surfaces

| Role | Engine | Primary paths |
|------|--------|---------------|
| Lint | `packages/tac-validate` (ADR-028 registry) | fixtures `accept`/`negative`; ISSUE_CATALOG |
| Convert | `packages/tac2iwxxm` | bulletin/AHL; annex3 goldens; decode |
| IWXXM-validate | `packages/iwxxm-validate` | XSD + Schematron under defaults |
| API | `apps/backend` | `/convert`, `/lint`, `/validate`, `product=` enum |
| Examples (opt.) | FE catalog | TC-EV029-008 / TC-F28-005 when unlocked |

## Report states (all families)

| State | TAC / AHL cue | IWXXM expectation |
|-------|---------------|-------------------|
| Normal | no BBB / RR | `reportStatus` NORMAL or product default |
| Amendment | `AAx` | AMENDMENT |
| Correction | `CCx` | CORRECTION |
| Cancellation | product CNL form | **not** reportStatus — product CNL path |
| Missing / NIL | NIL / missing | nilReason / product NIL — **not** reportStatus |

Audit cells in COVERAGE_MATRIX for each family × role × applicable state (TC-EV029-006).

## TAC input shapes

| Shape | Meaning | Inventory (T0.3) |
|-------|---------|------------------|
| Standalone | single report, no AHL | ≥1 per family or gap |
| AHL | WMO AHL header + report(s) | ≥1 per `T1T2` in B1 |
| Multi-report | AHL + N reports / `=` terminators | where product permits |

OOS: SIGWX · VONA · QVACI (converter inputs).

## Product × AHL × root × milestone

| Family | TAC `T1T2` | IWXXM `T1T2` | Root | Milestone | CI workflow (E29-T4) |
|--------|-----------:|-------------:|------|-----------|----------------------|
| AHL/COM (shared) | — | — | bulletin model | **M1** | `ahl-com-quality.yml` |
| METAR | SA | LA | `iwxxm:METAR` | **M2** | `metar-quality.yml` |
| SPECI | SP | LP | `iwxxm:SPECI` | **M3** | `speci-quality.yml` |
| TAF | FC/FT | LC/LT | `iwxxm:TAF` | **M4** | `taf-quality.yml` |
| SIGMET gen | WS | LS | `iwxxm:SIGMET` | **M5** | `sigmet-quality.yml` |
| VA SIGMET | WV | LV | `iwxxm:VolcanicAshSIGMET` | **M6** | `va-sigmet-quality.yml` |
| TC SIGMET | WC | LY | `iwxxm:TropicalCycloneSIGMET` | **M7** | `tc-sigmet-quality.yml` or extend |
| AIRMET | WA | LW | `iwxxm:AIRMET` | **M8** | `airmet-quality.yml` |
| VAA | FV | LU | `iwxxm:VolcanicAshAdvisory` | **M9** | `vaa-quality.yml` |
| TCA | FK | LK | `iwxxm:TropicalCycloneAdvisory` | **M10** | `tca-quality.yml` |
| SWXA | FN | LN | `iwxxm:SpaceWeatherAdvisory` | **M11** | `swxa-quality.yml` |

## TC → deliverable → milestone

| TC | Theme | Primary deliverable | Milestone |
|----|-------|---------------------|-----------|
| TC-EV029-001 | Coverage matrix eight-family × roles | `docs/domain/rules/COVERAGE_MATRIX.md` + canonicals; no silent blanks | **M0** (T0.4) + close per Ms |
| TC-EV029-002 | TAC shape + IWXXM example inventory | `reports/mining/` inventory + FIXTURE_GAPS / fixtures | **M0** (T0.3) |
| TC-EV029-003 | Shared AHL / BBB / T1T2 | `tac2iwxxm` bulletin API + fixtures; design note T0.5 | **M0** / **M1** |
| TC-EV029-004 | TC SIGMET root (#738) | TC fixtures + convert/validate; not gen SIGMET / not TCA | **M7** |
| TC-EV029-005 | VAA/TCA bulletin residuals (#820) | `=`-split + encode/decode; child issues OK | **M9** / **M10** |
| TC-EV029-006 | Report-state matrix | fixtures + matrix cells Normal/AMD/COR/CNL/NIL | **M0** seed; **M1–M11** fill |
| TC-EV029-007 | Product-order smoke | one accept fixture / family in CI order | **M12** (T12.1); packs M2–M11 |
| TC-EV029-008 | Optional H4–H5 FE | Examples unlock only | **M12** waive unless FE |
| TC-F28-001 | SWXA registry completeness | ADR-028 rows + CI unknown-code fail | **M11** |
| TC-F28-002 | SWXA accept → XSD+SCH | convert root + validate | **M11** |
| TC-F28-003 | SWXA golden / peer | ADR-032 equality or `wmoReference` | **M11** (S02.L1) |
| TC-F28-004 | SWXA negatives | negative pack + registered codes | **M11** |
| TC-F28-005 | SWXA product-path smoke | API `product=swxa`; FE if unlocked | **M11** / **M12** |
| TC-F28-006 | SWXA adjacency + FN→LN | no mis-root; AHL map; reject `swx` | **M1** / **M11** |

## Family × role gap audit skeleton (fill in M0 T0.2–T0.4)

Status codes: `pass` · `gap` · `N/A` · `defer+child` · `mine` (needs T0.2 dig)

| Family | Lint | Convert | IWXXM-validate | Notes / prior Fn |
|--------|------|---------|----------------|------------------|
| AHL/COM | **pass** (BBB) | **pass** (parse/map/filename) | N/A (framing) | F6.bulletin; #823 B1–B3 — **M1 closed** |
| METAR | mine | mine | mine | F15 Done — deepen gaps only |
| SPECI | mine | mine | mine | F20 Done — deepen |
| TAF | mine | mine | mine | F20 Done — deepen |
| SIGMET gen | mine | mine | mine | F23 Done — deepen |
| VA SIGMET | mine | mine | mine | F23 Done — deepen |
| TC SIGMET | gap | gap | gap | #738 open; F23 deepen |
| AIRMET | mine | mine | mine | F24 Done — deepen |
| VAA | mine | mine | mine | F26 Done; #820 / #823 B4 |
| TCA | mine | mine | mine | F27 Done; #820 / #823 B4 |
| SWXA | gap | gap | gap | **F28** Planned; #740; spacewx examples exist |

## Related issues

| Issue | Absorbed into |
|-------|----------------|
| #823 | Umbrella — stays open until children linked/closed (S02.M3) |
| #738 | **M7** TC SIGMET |
| #820 | **M9** / **M10** VAA/TCA |
| #740 | **M11** F28 SWXA |

## Code / docs touchpoints

| Surface | Path |
|---------|------|
| Coverage matrix | `docs/domain/rules/COVERAGE_MATRIX.md` |
| Mining notes | `docs/domain/mining/*` + session `reports/mining/` |
| AHL / bulletin | `packages/tac2iwxxm/src/tac2iwxxm/bulletin.py` (+ models) |
| Registry | `packages/tac-validate` ADR-028 registry |
| API product enum | `apps/backend` + `docs/api-contract.md` (`swxa`) |
| WMO examples | `vendor/schemas/iwxxm/2025-2/IWXXM/examples/` |
| Prior theme map | `docs/sessions/S031-iwxxm-domain-mine/reports/domain-mine-theme-map.md` |

## M0 gate (E29-T3)

No M1+ implementation until T0.2–T0.6 complete (full re-mine + promote + exit checklist).
HARD gaps → AskQuestion (E29-T8); residuals may be child-issued (S02.M3).

## Next

**T0.2** — ~~Full re-mine~~ → `reports/mining/eight-family-remine-pass.md`  
**T0.3** — ~~Example inventory~~ → `reports/mining/example-inventory.md`  
**T0.4** — ~~Promote~~ → `COVERAGE_MATRIX` §EV-029 + `IWXXM_CONVERSION` AHL canonical  
**T0.5** — ~~AHL design note~~ → `reports/mining/ahl-design-note.md`  
**T0.6** — ~~M0 exit~~ → `reports/m0-exit-checklist.md` **PASS** → **M1 @ T1.1**
