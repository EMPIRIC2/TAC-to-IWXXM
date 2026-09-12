# Scoped context — #809 VA multi-location (soft→strict residual)

**Mode:** scoped · **Date:** 2026-07-31  
**Status:** closed (S033 / EV-026 — equality + `wmoPass` shipped; #809 closed)  
**Session:** S033-va-multi-location-equality · **Cycle:** EV-026  
**Issue:** [#809](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/809)  
**Parent cycles:** S031/EV-024 (wired `wmoReference`) · S032/EV-025 (soft-compare shipped in [#816](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/816), merged)  
**Features:** F23 deepen · F6 convert · F7.g catalog tiers (ADR-032 amend)

## Verdict

**Complete (S033 / EV-026).** Soft path (EV-025) + ADR-032 `canonicalize_xml` equality under
defaults + catalog `wmoPass` (TC-EV025-009 / UJ-041) shipped in [#817](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/817);
live smoke PASS; #809 closed.

| Gate | Status |
|------|--------|
| Package soft-compare golden (TC-EV025-008) | ✅ (superseded by strict) |
| Multi-location OBS/FCST encode (`analysisCollection` ×2) | ✅ |
| M-xsd / M-sch smoke on convert output | ✅ |
| Catalog `wmoPass` + FIXTURE_GAPS cleared | ✅ EV-026 |
| ADR-032 equality → `wmoPass` (TC-EV025-009 promote) | ✅ EV-026 |

## Runtime SoT

| Asset | Path |
|-------|------|
| Vendor TAC/XML | `vendor/schemas/iwxxm/2025-2/IWXXM/examples/sigmet-multi-location-VA.{tac,xml}` |
| Package golden | `packages/tac2iwxxm/tests/fixtures/annex3_golden/sigmet_multi_location_va.tac` (strict ADR-032 equality) |
| Encode | `packages/tac2iwxxm/src/tac2iwxxm/profiles/annex3_products.py` (`_sigmet_location_analysis_xml`) |
| Parse | `packages/tac2iwxxm/src/tac2iwxxm/products/sigmet_airmet.py` (AND multi-location VA) |
| Catalog | `apps/frontend/src/fixtures/examples/examplesCatalog.ts` id `sigmet_multi_location_va` (`wmoPass`) |
| Gaps | `apps/frontend/src/fixtures/examples/FIXTURE_GAPS.md` (#809 equality passer recorded)
| Policy | [ADR-032](../adr/ADR-032-wmo-default-golden-glossary.md) §Decision (1)+(2) |

## Prior art (do not restart)

| Artifact | Use |
|----------|-----|
| [Context: iwxxm-us-remarks-va](iwxxm-us-remarks-va.md) | Dual-lane EV-025 scope (Lane B = #809) |
| S032 `t7-1-gate-c-dig-close.md` | Soft green; equality does not block Gate C |
| S032 `evolve-summary.md` | Closeout note: #809 left open |
| Issue comment on #809 (post-#816) | Acceptance checklist for residual |
| F23 VA-EGGX (TC-F23-003) | Adjacent VA passer; still `wmoReference` if equality fails |
| #738 TC SIGMET A6-2 | Explicitly out of scope for #809 |

## Soft path already green (do not re-litigate)

- Root `iwxxm:VolcanicAshSIGMET` (not plain `SIGMET` / VAA)
- ≥2 AND locations → dual `analysisCollection` with OBS + `forecastPositionAnalysis`
- Volcano `MT ASHVAL` + FL bands 150/300 and 250/370
- Soft gate **asserts inequality** today (`canonicalize_xml(ours) != vendor`) so promote cannot silently pass

## Equality blockers (confirmed T0.1 — S033 dig)

Live `canonicalize_xml` themes vs vendor (see
[t0-1-canonicalize-diff-themes.md](../sessions/S033-va-multi-location-equality/reports/t0-1-canonicalize-diff-themes.md)):

1. **Calendar year-month** — ours `2012-08-10`; vendor `2018-07-10` (TAC has day/hour only). → T1.2
2. **ATS / MWO display metadata** — ours `YUDD FIC` / `YUSO MWO` (+ type `FIC`); vendor `SHANWICK OCEANIC…` / `UK METEOROLOGICAL OFFICE - EXETER` (+ type `ATCC`). → T1.2
3. **Ring vertex order** — same closed rings; ours TAC WI order; vendor opposite winding / reorder. → T1.3
4. **Coordinate formatting** — ours `:.4f` (`42.2833`); vendor two-decimal (`42.28`). → T1.3
5. **phenomenonTime density** — ours 4 filled `TimeInstant`s; vendor 2 filled + 2 `xlink:href` reuse. → T1.4

Promote flip checklist when equality holds:

1. Flip TC-EV025-008 soft assert → equality (or add strict case; drop `soft_compare` / inequality assert).
2. Update TC-EV025-009 to expect equality + `wmoPass: true` (remove “not yet” asserts).
3. Catalog: `wmoReference` → `wmoPass`; label copy “passer” not “reference”.
4. FIXTURE_GAPS: remove equality-pending / #809 open note (or mark closed).
5. Close GitHub #809.

## Out of scope

- Removing sample-menu load while still reference
- TC SIGMET A6-2 (#738)
- Re-opening dig ❌ US REMARKS (#810–#812) — closed by #816

## Session / routing note

`active_session` S032/EV-025 still recorded as awaiting #816 merge; **#816 is merged**
(`2412312` on `main`). Residual equality is a **new** deepen (new SNNN / EV or hotfix-style
encode cycle) — do not silently reopen Lane A US work. Suggested type: `feature` deepen F23
with Lean+build; UI catalog toggle is light (Vitest/catalog only).

## Success

1. `canonicalize_xml(convert(vendor_tac)) == canonicalize_xml(vendor_xml)` under annex3 + default pin.
2. Catalog tier `wmoPass` for `sigmet_multi_location_va`.
3. TC-EV025-008/009 green under strict semantics; #809 closed.
