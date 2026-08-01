# T0.1–T0.3 — Official WMO TAC inventory + residual dig

**Date**: 2026-07-31 · **Cycle**: EV-027 · **Issue**: #815

## Pin SoT

`vendor/schemas/iwxxm/2025-2/IWXXM/examples/*.tac` (manifest pin v2025-2).

## In-scope product TAC peers (F6 seven)

| Vendor stem | Disposition | Catalog id / gap |
|-------------|-------------|------------------|
| metar-A3-1 | registered | `metar_a3_1` wmoPass |
| speci-A3-2 | registered | `speci_a3_2` wmoPass |
| taf-A5-1 | registered | `taf_a5_1` wmoPass |
| taf-A5-2 | registered | `taf_a5_2` wmoPass |
| sigmet-A6-1a-TS | registered | `sigmet_a6_1a_ts` wmoPass |
| sigmet-A6-1b-CNL | registered | `sigmet_a6_1b_cnl` wmoPass |
| sigmet-VA-EGGX | registered | `sigmet_va_eggx` wmoReference |
| sigmet-multi-location-VA | registered | `sigmet_multi_location_va` wmoPass |
| sigmet-A6-2-TC | **gap** | deferred #738 (FIXTURE_GAPS.md / inventory) |
| airmet-A6-1a-TS | registered | `airmet_a6_1a_ts` wmoPass |
| va-advisory-A7-2 | registered | `vaa_a7_2` wmoPass |
| tc-advisory-A2-2 | registered | `tca_a2_2` wmoPass |

## Explicitly out of happy-path WMO list

| Stem class | Reason |
|------------|--------|
| `*-translation-failed*` | quarantine (UJ-039) |
| `spacewx-*` | deferred product |
| `vona-*` | deferred product |
| `metar-NIL-collect` / `taf-NIL-collect` | COLLECT / validate shape — not sample-menu happy-path (EV-024) |

## Product-level FIXTURE_GAPS (already)

METAR / SPECI / AIRMET / VAA / TCA — second peer absent from pin (document only).

## T0.3 — decode residuals (registered peers)

| Stem | n_res | Sample residuals |
|------|------:|------------------|
| metar_a3_1 | 1 | `R12/1000U` |
| speci_a3_2 | 0 | — |
| taf_a5_1 | 0 | — |
| taf_a5_2 | 1 | `CNL` |
| sigmet_a6_1a_ts | 0 | — |
| sigmet_a6_1b_cnl | 1 | `SIGMET 2` |
| sigmet_va_eggx | 7 | geometry / eruption tokens |
| sigmet_multi_location_va | 24 | multi-location geometry / FL |
| airmet_a6_1a_ts | 0 | — |
| vaa_a7_2 | 13 | advisory fields (F9 G4 candidate) |
| tca_a2_2 | 14 | advisory fields (F9 G4 candidate) |

## Catalog-first verdict (T0.2)

No silent omissions among in-scope single-report peers: every stem is registered **or**
documented deferred (A6-2-TC / NIL-collect / translation-failed / spacewx / vona).
M1 locks this in CI; M2 addresses residual matrix.
