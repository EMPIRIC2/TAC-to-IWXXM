# Fixture quality baseline — S059 / EV-050 (pre-07)

**Date:** 2026-08-09  
**Method:** Coarse token ∩ vendor notations (EV-046 style), refined for cloud groups
`FEW###` / `…TCU` suffixes and CSV `notation` column.  
**Corpus:** [Corpus: tests] [Corpus: product §F12/F15/F20/F23/F24/F28]  
**Note:** Pre-07 baseline only. **Post-M2 delta (T2.4):**
[fixture-coverage-delta-t2.4.md](./fixture-coverage-delta-t2.4.md)
(Validated membership CI landed in T2.1–T2.3; AC4 gap rows closed or defer+cite).

**Scan:** 263 `*.tac` under `packages/tac-validate/tests/fixtures` + `packages/tac2iwxxm`
(pre-07; post-M2 scan = 270 — see T2.4 delta).

## Register ∩ fixtures (current tip)

| Register / SoT | Hit / total | % | vs EV-046 Lean | Notes |
|----------------|-------------|---|----------------|-------|
| 306/4678 (CSV notations) | 18 / 402 | **4.5%** | ~4.0% | Present wx tokens; no membership CI yet |
| 49-2 PresentOrForecastWeather | 18 / 402 | **4.5%** | 4.0% | Same concept set |
| 49-2 AerodromeRecentWeather | 0 / 26 | **0%** | 0% | **Gap — no true `RExx` tokens** |
| 49-2 CloudAmountReportedAtAerodrome | 4 / 10* | **40–60%*** | 60% | FEW/SCT/BKN/OVC present as `FEW###` groups; *coarse ∩ also picks SIGMET EMBD/ISOL |
| 49-2 SigConvectiveCloudType | 2 / 2 | **100%*** | 50% (CB only) | `CB` bare + **`BKN020TCU`** suffix in `speci_r4_bkn_tcu.tac` |
| 49-2 SigWxPhenomena | 2 / 17 | **11.8%** | 11.8% | `VA`, `TC` |
| 49-2 AirWxPhenomena | 0 / 18 | **0%** | 0% | **Gap — TAC uses spaced forms (`ISOL TS`); register is `ISOL_TS` etc.** |
| 49-2 WeatherCausingVisibilityReduction | 6 / 19 | **31.6%** | 26.3% | BR/DZ/FG/RA/SN/VA |
| 49-2 SpaceWxPhenomena | 0 / 8 | **0%** | 0% | **Gap — effects are `HF COM` / `GNSS` / `RADIATION`, not `HF_COM_SEV`** |
| 49-2 SpaceWxLocation | 6 / 7 | **85.7%** | 85.7% | EQN/EQS/HNH/… |

\*Cloud / TCU % sensitive to tokenizer (bare vs cloud-group).

## Aggressive targets (`D-S059-fixtures=2c`) — readiness

| Target | Baseline | Evidence | 07 work implied |
|--------|----------|----------|-----------------|
| **`RE*` recent weather** | **0 / 26** | No register `RERA`/`RESN`/… in any `.tac`; false positives `REP`/`REPORTED` only | Add accept + negative recent-wx fixtures; membership vs RecentWeather |
| **AIRMET `_` phenomena** | **0 / 18** exact | `airmet_a2_phenomenon.tac` has `ISOL TS` (space), not `ISOL_TS` | Tokenize/normalize underscore↔space **or** add fixtures that exercise register notations; membership for AirWxPhenomena |
| **SpaceWxPhenomena** | **0 / 8** exact | `SWX EFFECT: HF COM` / `GNSS` / `RADIATION` + severity tokens `SEV`/`MOD` elsewhere | Map EFFECT+severity → `HF_COM_SEV` etc., or fixture notations; membership asserts |
| **TCU** | **Present (suffix)** | `accept/speci_r4_bkn_tcu.tac` → `BKN020TCU` | Keep; add sad/unknown cloud suffix if missing; ensure membership sees TCU |

## Sad / unknown packs (membership AC2)

Existing negatives useful as seeds: `negative/metar/wx_unknown_token.tac`, wx intensity cases,
`negative/airmet/multi_phenomenon.tac`, `negative/sigmet/multi_phenomenon.tac`.  
**Missing today:** dedicated unknown `RE*`, unknown AIRMET underscore notation, unknown
SpaceWxPhenomena notation packs.

## Bottom line for Standard build

Fixture **quality bar before harvest wiring** is unchanged from EV-046 on the hard gaps:
recent weather, AIRMET underscore, SpaceWxPhenomena remain **0% exact ∩**. Weather ~4.5%
and locations ~86% are already representative. Option **2c** means 07 must add those packs
(and likely a small tokenizer/normalize layer) before AC2/AC4 can go green.

## Profile note (AC7 — `D-S059-profiles=1b`)

This baseline is **profile-agnostic token ∩ WMO register** (L3). It does **not** yet
split `annex3` vs `iwxxm_us` lint outcomes. AC7 adds a dual-profile disposition for **all
F6 products** (`iwxxm_us` **N/A** where unsupported). US L5 REMARKS / FMH-1 diffs are
expected under `iwxxm_us` only and must not be scored as WMO membership failures.
