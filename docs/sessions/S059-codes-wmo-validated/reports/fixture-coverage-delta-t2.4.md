# T2.4 — Fixture coverage delta + deferrals (S059 / EV-050)

**Date:** 2026-08-09  
**Task:** T2.4 (closes M2)  
**Tip at scan:** `48323861` (+ this docs commit)  
**Corpus:** [Corpus: tests] [Corpus: product §F12/F15/F20/F23/F24/F28]
[Corpus: decisions §EV-050] · domain `COVERAGE_MATRIX` / `RULE_SOURCE_URLS`

**Method:** Coarse uppercase TAC token ∩ vendor/`wmo_membership.json` notations
(EV-046 / pre-07 baseline style), plus:

- Cloud groups `FEW###` / `…TCU|CB` suffixes  
- AIRMET underscore tokens + space↔underscore normalize  
- SWXA **composed** `EFFECT` + OBS severity → `HF_COM_SEV` (lint membership path)

**Scan:** 270 `*.tac` under `packages/tac-validate/tests/fixtures` + `packages/tac2iwxxm`.

## Aggressive targets (`D-S059-fixtures=2c`) — closed

| Target | Pre-07 baseline | Post-T2.3 | Evidence |
|--------|-----------------|-----------|----------|
| **`RE*` recent weather** | 0 / 26 (0%) | **2 / 26 (7.7%)** | Accept `RERA`/`RESN`; negative `REZZZZ` → `UNKNOWN_WMO_MEMBERSHIP` |
| **AIRMET `_` phenomena** | 0 / 18 exact (0%) | **2 / 18 (11.1%)** | Accept `ISOL_TS`/`MOD_ICE`; spaced `ISOL TS` still normalizes; negative `ISOL_ZZ` |
| **SpaceWxPhenomena** | 0 / 8 exact (0%) | **0% exact · 3 / 8 (37.5%) composed** | Accept SX1 packs → `HF_COM_SEV` / `GNSS_MOD` / `RADIATION_MOD`; negative `FAKEWX` |
| **TCU** | Present suffix / CB-only in Lean | **2 / 2 (100%)** | `speci_r4_bkn_tcu.tac` + CB; membership sees `TCU` |

TC-EV050-004 green (`test_tc_ev050_004_aggressive_fixtures.py`).

### New / wired fixtures (EV050 theme)

| Path | Role |
|------|------|
| `accept/metar_ev050_recent_rera.tac` | Recent weather accept |
| `accept/metar_ev050_recent_resn.tac` | Recent weather accept |
| `accept/airmet_ev050_phenomenon_underscore.tac` | AirWx `ISOL_TS` |
| `accept/airmet_ev050_mod_ice_underscore.tac` | AirWx `MOD_ICE` |
| `negative/metar/unknown_recent_weather.tac` | Unknown `RE*` |
| `negative/airmet/unknown_phenomenon_underscore.tac` | Unknown AirWx `_` |
| `negative/swxa/unknown_effect.tac` | Unknown SpaceWx EFFECT |
| `accept/speci_r4_bkn_tcu.tac` | TCU (pre-existing; membership asserted) |
| `accept/swxa_sx1_{hf_com,gnss,radiation}.tac` | Composed SpaceWx (pre-existing; membership asserted) |

## Full register ∩ fixtures (post-M2)

| Register / SoT | Hit / total | % | vs pre-07 | Notes |
|----------------|-------------|---|-----------|-------|
| 306/4678 (CSV notations) | 18 / 402 | **4.5%** | same | Representative weather; not exhaustive |
| 49-2 PresentOrForecastWeather | 18 / 402 | **4.5%** | same | Same concept set |
| 49-2 AerodromeRecentWeather | 2 / 26 | **7.7%** | **↑ from 0%** | Gap row closed for AC4 |
| 49-2 CloudAmountReportedAtAerodrome | 4 / 10* | **40%*** | ~same | FEW/SCT/BKN/OVC; *tokenizer vs SIGMET EMBD/ISOL |
| 49-2 SigConvectiveCloudType | 2 / 2 | **100%** | **↑ from ~50–100%*** | CB + TCU |
| 49-2 SigWxPhenomena | 2 / 17 | **11.8%** | same | `VA`, `TC` |
| 49-2 AirWxPhenomena | 2 / 18 | **11.1%** | **↑ from 0%** | Underscore fixtures + normalize |
| 49-2 WeatherCausingVisibilityReduction | 6 / 19 | **31.6%** | same | BR/DZ/FG/RA/SN/VA |
| 49-2 SpaceWxPhenomena (exact token) | 0 / 8 | **0%** | same exact | TAC uses spaced EFFECT — see composed |
| 49-2 SpaceWxPhenomena (composed) | 3 / 8 | **37.5%** | **↑ from 0%** | Lint membership path |
| 49-2 SpaceWxLocation | 6 / 7 | **85.7%** | same | EQN/EQS/… |

\*Cloud % sensitive to tokenizer (bare vs cloud-group).

## Residual gaps — defer + cite (AC4)

No new GitHub children opened this task. Residuals stay under parent
[#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959) /
[#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889) with explicit deferral,
consistent with EV-050 OOS (exhaustive 402 weather combinations) and Gate A advisory
(AC8 defer+cite OK).

| Residual | Disposition | Cite |
|----------|-------------|------|
| Exhaustive present-weather beyond ~4.5% of 402 | **Defer** — combinatorial; representative + sad packs sufficient for Validated | evolve-decisions §EV-050 Out of scope; EV-046 AC3 exclusions |
| Remaining RecentWeather notations (24 / 26) | **Defer** — AC4 closed by accept+negative membership path, not full register | #959 |
| Remaining AirWxPhenomena (16 / 18) | **Defer** — underscore↔space path proven; expand opportunistically | #959 |
| Remaining SpaceWxPhenomena (5 / 8 composed) | **Defer** — three composed accept + unknown EFFECT prove membership; more effects optional F28 deepen | #959 / F28 |
| Exact SpaceWx register tokens in TAC | **Defer / N/A method** — TAC emits spaced EFFECT + severity; composed mapping is the Validated path | TC-EV050-004; lint wire T2.2 |
| NilReason as TAC tokens (0%) | **Defer / expected** — encoded as IWXXM `xlink:href`, not TAC lexicon | EV-046 exclusions; AC2 nil where lint already checks URIs |
| Colour / MetFeature / VONA duals beyond v1 families | **Defer** — EV-050 OOS unless needed for sad packs | evolve-decisions §EV-050 |
| URI drift vs live registry | **Keep** compose [#859](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/859) | AC3 / RULE_SOURCE_URLS |
| Scheduled live refresh / notify | **Keep** [#882](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/882) design-only (T4.1) | `D-S059-882=3a` |
| annex3 vs `iwxxm_us` disposition | **M3** (T3.1–T3.4) — not a fixture∩ gap | AC7–AC8 |

## EV-046 gap rows (S055 AC4) — status after EV-050 M2

| EV-046 gap | Status |
|------------|--------|
| Automated TAC∈register membership tests | **Closed in-cycle** (M1–M2 / TC-EV050-001..002) |
| Recent-weather (`RE*`) fixture tokens | **Closed** (representative + sad) |
| AIRMET AirWxPhenomena underscore matching | **Closed** (fixtures + normalize) |
| SpaceWxPhenomena fixture / membership path | **Closed** (composed + sad) |
| TCU convective type | **Closed** (100% register) |
| Raise weather fixture coverage beyond ~4% | **Still deferred** (cite above) |
| URI drift / #882 notify | **Unchanged** compose issues |

## Profile note

This delta remains **profile-agnostic** L3 token∩ / composed membership.
Dual-profile `annex3` vs `iwxxm_us` disposition is **M3** (AC7–AC8).

## AC4 / TC-EV050-004

| Criterion | Status |
|-----------|--------|
| Aggressive fixtures for RE*, AIRMET `_`, SpaceWx, TCU | **MET** |
| Coverage / COVERAGE_MATRIX delta | **MET** (this report + matrix pointer) |
| Residual gaps → child or defer+cite | **MET** — defer+cite table (no new children) |
