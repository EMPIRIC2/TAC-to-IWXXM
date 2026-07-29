# Context — SIGMET quality (general + VA) (S025 / EV-019)

Scoped brief for F15/F20 sequel on the SIGMET family. Full discovery lives in
01-requirements + domain matrix.

## Tickets

| Issue | Product | IWXXM root | Stance this cycle |
|-------|---------|------------|-------------------|
| [#733](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/733) | General SIGMET | `iwxxm:SIGMET` | Full quality bar |
| [#739](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/739) | Volcanic-ash SIGMET | `iwxxm:VolcanicAshSIGMET` | Full quality bar (parallel) |

## Stack (mirror EV-011 / EV-015)

- `packages/tac-validate` — registry codes (ADR-028), accept/negative
- `packages/tac2iwxxm` — goldens / product_matrix / `products/sigmet_airmet.py`
- `packages/iwxxm-validate` — XSD + Schematron round-trip
- `docs/domain/rules/COVERAGE_MATRIX.md` — SIGMET + VA SIGMET rows
- WMO encode: `vendor/schemas/iwxxm/2025-2/IWXXM/examples/TAC-to-XML-Guidance.txt`
  + 2025-2 corrections (no `runwayState`)

## Code anchors (pre-discovery)

| Area | Path |
|------|------|
| Convert | `packages/tac2iwxxm/src/tac2iwxxm/products/sigmet_airmet.py` |
| Product matrix tests | `packages/tac2iwxxm/tests/test_tc_f6_001_002_product_matrix.py` |
| US profile SIGMET/AIRMET | `packages/tac2iwxxm/tests/test_tc_f6_003_taf_sigmet_airmet_iwxxm_us.py` |
| Lint products | `packages/tac-validate/src/tac_validate/products.py` |
| Example goldens (matrix) | `sigmet-A6-1a-TS`, CNL `…-1b-CNL`, VA `sigmet-VA-EGGX` |

## AIRMET / SIGMET family exceptional rules (from #733/#739)

| TAC condition | IWXXM rule |
|---------------|------------|
| CNL | `isCancelReport=true`; cancelled sequence + validity; omit phenomenon/analysis |
| Single coordinate point | `gml:CircleByCenterPoint` radius zero |
| Single altitude | Same lower and upper limits |
| STNR | Nil direction inapplicable; speed zero |
| Polygon or line | GML with declared CRS |
| NO VA EXP | `nothingOfOperationalSignificance` (VA absence) |

## Out of scope (siblings)

| Issue | Product |
|-------|---------|
| [#738](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/738) | Tropical-cyclone SIGMET (`iwxxm:TropicalCycloneSIGMET`) |
| [#731](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/731) | AIRMET |
| [#736](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/736) | VAA (distinct from VA SIGMET) |
| [#737](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/737) | TCA |
| #740 / #741 | SWX / VONA |

Confirm Batch 2: siblings remain cite-only unless shared common-rule touch.

## Resolutions (local)

| ID | Resolution |
|----|------------|
| R1 | Cycle = #733 + #739 full bars; #738 OOS (E19-2) |
| R2 | F23 + deepen F6.d/F12; ADR-028 reuse (E19-3) |
| R3 | Lean+build routing (E19-4) |
| R4 | Full AC depth — guidance + fixtures + goldens + matrix (E19-5) |
| R5 | Siblings OOS; F7 smoke only (E19-6) |
| R6 | Deploy smoke H1–H5 when API/FE change (E19-7) |
| R7 | Phase 0 locked; pause before 01 (E19-8=B) |
| R8 | No local UI preview — docs/repo only (E19-ui assumed B) |
