# US REMARKS + VA theme → fixture map — S032 / EV-025

**Date**: 2026-07-31  
**Pins**: IWXXM **v2025-2** (`35180cbe3bec…`) · iwxxm-us **3.0**  
**Local PDF**: `.local/reference/iwxxm-us-metar-speci-pdf/` (gitignored; present)  
**Dig SoT**: `docs/domain/mining/iwxxm-us-metar-speci-pdf-mining-notes.md`

## TC → deliverable

| TC | Theme | Primary deliverable | Milestone |
|----|-------|---------------------|-----------|
| TC-EV025-001 | #810 Variable RVR / meanRVR withheld | `packages/tac2iwxxm` encode + `tests/fixtures/iwxxm_us_golden/` (+ lint if needed) | M1 |
| TC-EV025-002 | #811 Lightning / VOP | encode + goldens (+ `tac-validate` US REMARKS) | M2 |
| TC-EV025-003 | #812 SnowIncrease + sensor outage | encode + goldens (+ lint) | M3 |
| TC-EV025-004 | Adjacent dig ❌ packs | Parametrized goldens / matrix per dig row | M4 |
| TC-EV025-005 | US out of WMO sample menu | Vitest / `examplesCatalog.ts` regression | M6 |
| TC-EV025-006 | Malformed US REMARKS diagnostics | convert/lint negative fixtures | M6 |
| TC-EV025-007 | Unparsed REMARKS → `humanReadableText` | deepen existing Addendum path | M6 |
| TC-EV025-008 | #809 soft-compare golden | package annex3 golden + vendor stem | M5 |
| TC-EV025-009 | #809 `wmoPass` promote | catalog tier + ADR-032 equality | M5 |
| TC-EV025-010 | Combined-catalog validate smoke | `iwxxm-validate` WMO+US catalogs | M6 |

## UJ / policy

| Item | Binding |
|------|---------|
| UJ-040 | Structured iwxxm-us REMARKS under `profile=iwxxm_us` |
| UJ-041 | `sigmet-multi-location-VA` soft→strict / promote |
| S02.M1 | Soft-compare first; `wmoPass` only under ADR-032 equality |
| E25-T5=3 | Dig ❌ **encode** residual **blocks Gate C** |
| S02.L1 | TC-EV025-010 may document SCH deferrals (≠ encode residual) |
| E25-T4 | Finish Lane A (M1–M4) before Lane B (M5) |
| Exclude | USWX; US in WMO menu; vendor hand-edits; #808; #738 |

## Code / fixture anchors

| Surface | Path |
|---------|------|
| US profile writer | `packages/tac2iwxxm/src/tac2iwxxm/profiles/iwxxm_us.py` |
| Existing US goldens | `packages/tac2iwxxm/tests/fixtures/iwxxm_us_golden/` |
| US golden tests | `packages/tac2iwxxm/tests/test_tc_f6_003_metar_speci_iwxxm_us.py` (+ F15/F20 packs) |
| Vendor #809 stem | `vendor/schemas/iwxxm/2025-2/IWXXM/examples/sigmet-multi-location-VA.{tac,xml}` |
| Catalog (reference today) | `apps/frontend/src/fixtures/examples/examplesCatalog.ts` (`wmoSeed: sigmet-multi-location-VA`) |
| FIXTURE_GAPS | `apps/frontend/src/fixtures/examples/FIXTURE_GAPS.md` |
| Validate wire note | `apps/backend/tests/iwxxm/test_wmo_canonical_examples.py` (stem listed; encode child #809) |
| Dig checklist | `docs/domain/mining/iwxxm-us-metar-speci-pdf-mining-notes.md` |
| US XSD | `vendor/schemas/iwxxm-us/3.0/metarSpeci.xsd` (+ `common.xsd`) |

## Proposed new fixture layout (M1+)

Under `packages/tac2iwxxm/tests/fixtures/iwxxm_us_golden/` (or sibling `iwxxm_us_remarks/`):

| Stem pattern | TC / dig |
|--------------|----------|
| `metar_us_var_rvr*` | TC-EV025-001 / VariableRVR |
| `metar_us_lightning*` / `metar_us_vop*` | TC-EV025-002 |
| `metar_us_snow_inc*` / `metar_us_sensor*` | TC-EV025-003 |
| `metar_us_wshft*` · `metar_us_sky*` · … | TC-EV025-004 packs (per T4.x) |
| Soft/strict VA | prefer package golden path used by F23; vendor examples remain SoT for soft-compare |

## Milestone order (locked E25-T1)

`M0 → M1 #810 → M2 #811 → M3 #812 → M4 adjacent → M5 #809 → M6 deepen/validate → M7 Gate C audit/smoke`
