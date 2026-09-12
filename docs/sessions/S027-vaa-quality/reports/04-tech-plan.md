# 04-tech-plan — S027 / EV-021

**Started**: 2026-07-29  
**Mode**: evolve delta  
**Features**: F26, F27 + deepen F6.f / F12 / F7.g  
**Branch**: `evolve/EV-021-vaa-quality`  
**Status**: **completed** — Batch T all 1; plan approved E21-T6=1; handoff 07 @ T0.1

## Toolchain baseline (detected)

| Area | Choice |
|------|--------|
| Template | `static+api+worker` |
| Packages | `tac2iwxxm`, `tac-validate`, `iwxxm-validate`; FE Vite |
| Registry | ADR-028 reuse (VAA + TCA codes) |
| Golden compare | `canonicalize_xml` under defaults (ADR-032) |
| Themes | **F26 themes** V1–V3/C1; **F27 themes** T1–T3/C1 (`D-S027-EV021-s02m1-1`) |
| Catalog unlock | Incremental per product (`D-S027-EV021-s02m2-1`) |
| CI | Extend combined `wmo-quality.yml` (`D-S027-EV021-s02l1-1`) |
| Deploy | Existing Render API+FE; H4–H5 when FE |
| New deps | **None** (E21-T3=1) |

## Pre-locked from 02

| ID | Lock |
|----|------|
| S02.M1 | Keep F26 V1–V3 / F27 T1–T3 + Fn-theme prefix |
| S02.M2 | Incremental unlock VAA then TCA independently |
| S02.L1 | Extend `wmo-quality.yml` (finalize task shape here) |

## Milestone order (approved)

| M | Focus |
|---|--------|
| M0 | Research close + extend `wmo-quality.yml` |
| M1 | F26 VAA lint (V1–V2) |
| M2 | F26 VAA golden (V3) + C1 |
| M3 | F27 TCA lint (T1–T2) |
| M4 | F27 TCA golden (T3) + C1 |
| M5 | F7.g catalog unlock (incremental) |
| M6 | Smoke / 08 / 10 / 11 / 13 |

## Interview locks

| ID | Decision |
|----|----------|
| E21-T1 | Milestone order **1** |
| E21-T2 | Research **1** — close inventory |
| E21-T3 | Deps **1** — none |
| E21-T4 | Deploy **1** — H4–H5 when FE |
| E21-T5 | Kill-switch **1** |
| E21-T6 | Plan **1** — approve → 07 @ T0.1 |

## Artifacts

- `reports/execution-plan.md` — **approved**
- `reports/vaa-tca-theme-fixture-map.md` — T0.1 (started in 07)
- 04-exit consistency — **PASS** (05 skipped)

## Next

**07-build** — T0.1 theme→fixture map (inventory close).
