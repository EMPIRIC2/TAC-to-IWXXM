# Quality matrices for every supported product

Session: EV-1265-product-matrices. Ticket: #1265. Scale: full. Gate: closed.

[Corpus: product §F29] [Corpus: tests]

UI reference: not applicable. This cycle does not change the operator screen. The note is from the issue and the matrix tree.

## Goal

Give TAF, SIGMET, AIRMET, VAA, TCA, SWXA, and VONA the same F29 fill METAR/SPECI already has. Each in-scope rule has lint, convert, and validate matrices: 20 slots (5 happy, 5 sad, 5 edge-pass, 5 edge-fail), or a cited out-of-scope. `needs-fixture` is 0, including the Canadian lint pack. Ready slots pass the quality-matrix smoke. The inventory gate covers the new packs the way the METAR/SPECI pilot covers that pack.

Fill order for the remaining work: TAF convert and validate, then SIGMET, AIRMET, then VAA, TCA, SWXA, VONA.

Lint packs for those products, and the Canadian lint pack, are already ready. This cycle keeps them. It does not re-audit them. Canada has no convert or validate pack in the issue's in-list; only its lint scaffolds were named, and those are already ready.

## What the tree already holds

Counted from `tests/quality_matrices/testdata` on 2026-09-28. The issue text that says these product directories are missing, and that Canadian lint is 240 `needs-fixture`, is stale.

| Pack | Files | Ready | needs-fixture | Cited out of scope |
|---|---:|---:|---:|---:|
| lint/taf | 29 | 580 | 0 | 0 |
| lint/sigmet | 29 | 580 | 0 | 0 |
| lint/airmet | 14 | 280 | 0 | 0 |
| lint/vaa | 8 | 160 | 0 | 0 |
| lint/tca | 8 | 160 | 0 | 0 |
| lint/swxa | 6 | 120 | 0 | 0 |
| lint/vona | 5 | 100 | 0 | 0 |
| lint/ca_eccc | 12 | 240 | 0 | 0 |
| convert/metar_speci | 16 | 273 | 0 | 47 |
| lint/metar_speci | 36 | 720 | 0 | 0 |
| validate/metar_speci | 43 | 860 | 0 | 0 |

TAF convert and TAF validate are filled. Convert is 8 files, 160 ready slots. Validate is 14 files. Happy and edge-pass are convert-then-accept. Some sad and edge-fail slots are ready native Schematron negatives; residual sad/edge-fail stay cited out-of-scope. `needs-fixture` is 0.

SIGMET convert and SIGMET validate are filled. Convert is 7 files, 140 ready slots. Validate is 22 files (`SIGMET.*`, `VolcanicAshSIGMET.*`, and `TropicalCycloneSIGMET.*`), with the same mix of ready negatives and cited residual out-of-scope. `needs-fixture` is 0.

AIRMET, VAA, TCA, SWXA, and VONA convert and validate are filled. Convert themes: AIRMET 1, VAA 1, TCA 1, SWXA 3, VONA 1 (140 ready). Validate patterns: AIRMET 20, VAA 14, TCA 10, SWXA 5, VONA 3.

Native Schematron XPath1 stand-ins now cover those product prefixes on IWXXM 2025-2 (not only `METAR_SPECI`). Seventeen validate patterns have ready sad and edge-fail slots with XML that reports the pattern id. The remaining seventy-one validate patterns keep cited out-of-scope sad/edge-fail slots where the stand-in still does not surface that pattern id. `needs-fixture` is 0.

The product inventory is `tests/quality_matrices/inventory/product_matrices.yml`: 22 convert rules and 88 validate rules. Canada still has no convert or validate pack. `lint/selectable/` stays outside this ticket.

F29 stays **Done**. This cycle deepens it. It does not add a feature id. METAR/SPECI, including the 47 cited convert out-of-scope slots from #970, stays closed.

## Out of scope

- Reopening the METAR/SPECI fill.
- Live network feeds.
- Claiming full Annex 3 coverage.
- Leaving empty `needs-fixture` scaffolds as the finished state.
- Operator UI, browser end-to-end, and a deploy.
- Promoting `stage` to `main`.

## Feasible shape

Counted 2026-09-28 from `vendor/schemas/iwxxm/2025-2/IWXXM/rule/iwxxm.sch` and `packages/tac2iwxxm/tests/fixtures/annex3_golden`. The runners in `tests/quality_matrices/runners.py` already call lint, convert, and validate for any product string. No new dependency and no new HTTP route.

Convert rules are encode themes, one file per Annex 3 golden stem, the same kind as `metar_a3_1` in `inventory/metar_speci_pilot.yml`. Stems on file: TAF 8, SIGMET 7, AIRMET 1, VAA 1, TCA 1, SWXA 3, VONA 1.

Validate rules are the product-prefixed Schematron pattern ids, the same kind as `METAR_SPECI.*`. Counts: TAF 14, SIGMET 15, volcanic-ash SIGMET 4, tropical-cyclone SIGMET 3, AIRMET 20, volcanic-ash advisory 14, tropical-cyclone advisory 10, space-weather advisory 5, volcano observatory notice 3. Shared `Common`, `IWXXM`, and `MeteorologicalFeature` patterns stay out, as they did for METAR/SPECI. WAFS stays out.

Happy convert slots start from those goldens. Happy validate slots convert TAC, then check the XML. Sad and edge-fail validate slots use XML that names the pattern, as the METAR/SPECI pilot does. A slot that cannot be filled from an in-repo fixture without a live feed is a cited out-of-scope, which keeps `needs-fixture` at 0.

The new inventory file lists `matrix_roots`. `metar_speci_pilot.yml` is the only inventory allowed to omit that key.

## Build intent

Offline pytest matrices and the inventory gate only. Smoke runs ready slots. The full matrix lane stays optional. No new public HTTP route.
