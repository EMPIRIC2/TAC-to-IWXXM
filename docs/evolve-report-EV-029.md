# Evolve report — EV-029

| Field | Value |
|-------|-------|
| Cycle | EV-029 |
| Session | S036-eight-family-ahl-rules-823 |
| Status | **completed** |
| Started | 2026-08-01 |
| Completed | 2026-08-02 |
| Features | **F28** (new) + deepen F6 / F6.bulletin / F12 / F2 / F13 / F15 / F20 / F23 / F24 / F26 / F27 |
| Issues | [#823](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/823) **closed**; [#740](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/740) **closed**; [#738](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/738) closed (M7) |
| PRs | [#827](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/827) M1; [#828](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/828) → `4e6577a` |
| Deploy smoke (13) | **PASS** — API `dep-d9ntlclbedkc73fvcuvg` + FE `dep-d9ntlde1egvs738ph9h0`; H0c/H1/H3/H4/H5 + SWXA live |
| Close decision | `D-S036-13` = **1** (approve T12.6 → T12.7) |

## Scope

Umbrella #823 — mine then implement IWXXM 2025-2 AHL/bulletin, per-family quality packs,
and F28 SWXA (`product=swxa`). Product order: AHL/COM → METAR → SPECI → TAF → SIGMET
(gen/VA/TC) → AIRMET → VAA → TCA → SWXA. Exclude SIGWX / VONA / QVACI.

## Routing

Standard: `00→16→01→02→04→07→08→09→10→11→12→13` (skip 03/05/06).

## Results

| Gate | Result |
|------|--------|
| A→B | passed (`D-S036-02-phase-a`) |
| B→C | passed (`D-S036-04-plan`) |
| C→D | passed (M0–M12; 08 PASS) |
| Deploy (13) | passed (`D-S036-13` = 1) |

## Package / runtime

| Item | Version / note |
|------|----------------|
| `tac2iwxxm` | **0.2.3** (in-tree; no PyPI tag this cycle) |
| API product | `product=swxa` live |
| FE Examples | `spacewx-A7-3` unlocked; A7-4/A7-5 deferred |

## Verification

- 08-verify-build: pass
- 09-qa + 10-e2e: pass (UJ-043; H4–H5 at 13)
- 11-verify-impl: approved (`D-S036-11`)
- 12-verify-deploy: READY (`D-S036-12`)
- 13-deploy-smoke: pass — see session `deploy-smoke.md`

## Follow-ups

- [#829](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/829) — TC SIGMET lint / STNR / menu
- [#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820) — VAA/TCA decode residual
- [#831](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/831) — parameterized rule matrices
- Optional: PyPI tag for `tac2iwxxm` 0.2.3 in a later ops cycle
