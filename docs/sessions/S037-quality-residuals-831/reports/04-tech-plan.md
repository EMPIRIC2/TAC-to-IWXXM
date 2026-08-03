# 04-tech-plan — S037 / EV-030

**Started**: 2026-08-03  
**Mode**: evolve delta  
**Features**: **F29** + deepen F23 / F12 / F2 / F13 / F9 / F26 / F27  
**Branch**: `evolve/EV-030-quality-residuals-831`  
**Status**: **in_progress** — Batches 1–2 locked; execution plan drafted; awaiting Gate B

## Toolchain baseline (detected)

| Area | Choice |
|------|--------|
| Template | `static+api+worker` |
| Packages | `tac-validate`, `tac2iwxxm`, `iwxxm-validate`; FE Vite (catalog unlock) |
| Case storage | YAML/JSON under `tests/quality_matrices/testdata/` |
| Inventory | Unified index → matrix slots |
| Runners | `tests/quality_matrices/` (no new package) |
| Registry | ADR-028 reuse (TC SIGMET codes for #829) |
| Golden / catalog | ADR-032 unlock `sigmet-A6-2-TC` when quality path green |
| Runtime SoT | Vendor IWXXM **2025-2** |
| API | No new product enum; lint catalog additive; decode deepen (#820) |
| New deps | **None** — reuse `pyyaml` from `tac2iwxxm` (E30-T5=2 resolved) |
| Deploy | API redeploy if needed; H1–H3; **H4–H5 required** for FE unlock |
| CI | PR smoke subset + optional full-matrix marker/job |

## Pre-locked from 02

| ID | Lock |
|----|------|
| S02.M1 | #831 pilot = **METAR/SPECI** lint+encode+validate first |
| S02.M2 | #829 STNR/geometry may be **OOS with cite** |
| S02.M3 | #820 may leave **child residual** |
| S02.L1 | #831 harness = **session design note** unless 04 needs ADR |

## Interview locks — Batch 1 (`D-S037-04-batch-1` = 1,1,1,1)

| ID | Decision |
|----|----------|
| E30-T1 | Milestone structure **1** — **M0–M4** as proposed |
| E30-T2 | #831 case storage **1** — **YAML/JSON under testdata** + pytest load |
| E30-T3 | Rule inventory SoT **1** — **unified index** |
| E30-T4 | #829 catalog unlock **1** — unlock when quality path green |

## Interview locks — Batch 2 (`D-S037-04-batch-2` = 2,1,1,1)

| ID | Decision |
|----|----------|
| E30-T5 | Deps **2** — PyYAML allowed if needed → **already in stack** (`tac2iwxxm`); no new dep |
| E30-T6 | Deploy **1** — API redeploy; H1–H3; **H4–H5 required** for FE catalog unlock |
| E30-T7 | CI **1** — PR smoke subset + optional full-matrix job/marker |
| E30-T8 | Harness home **1** — session design note + `tests/quality_matrices/` |

## Approved milestone order (pending Gate B)

| M | Focus | Tasks |
|---|--------|------:|
| **M0** | #831 design note + inventory sketch + RuleCase spike | 4 |
| **M1** | F29 runners + METAR/SPECI pilot + inventory gate + CI + authoring docs | 8 |
| **M2** | #829 TC lint pack + STNR/OOS + A6-2-TC catalog unlock | 6 |
| **M3** | #820 VAA/TCA decode deepen + matrix/allowlist | 4 |
| **M4** | Smoke / 08–13 (H4–H5 for unlock) | 5 |
| | **Total** | **27** |

## Artifacts

- `reports/execution-plan.md` — **draft** (awaiting `D-S037-04-plan`)
- This report — Batches 1–2 locked

## Next

Gate B AskQuestion → on approve: complete 04 → **07-build** @ T0.1.
