# 04-tech-plan — S037 / EV-030

**Started**: 2026-08-03  
**Completed**: 2026-08-03  
**Mode**: evolve delta  
**Features**: **F29** + deepen F23 / F12 / F2 / F13 / F9 / F26 / F27  
**Branch**: `evolve/EV-030-quality-residuals-831`  
**Status**: **completed** — Gate B PASS (`D-S037-04-plan`=1) → 07 @ T0.1

## Toolchain baseline

| Area | Choice |
|------|--------|
| Template | `static+api+worker` |
| Case storage | YAML/JSON under `tests/quality_matrices/testdata/` |
| Inventory | Unified index → matrix slots |
| Runners | `tests/quality_matrices/` (no new package) |
| Registry | ADR-028 reuse |
| Catalog | Unlock `sigmet-A6-2-TC` when quality path green (ADR-032) |
| New deps | **None** — reuse `pyyaml` from `tac2iwxxm` |
| Deploy | H1–H3; **H4–H5 required** for FE unlock |
| CI | PR smoke + optional full-matrix marker/job |

## Interview locks

| Batch | Decision |
|-------|----------|
| Batch 1 `1,1,1,1` | M0–M4; YAML cases; unified inventory; catalog unlock on green |
| Batch 2 `2,1,1,1` | PyYAML reuse; H4–H5; PR smoke; design note + `tests/quality_matrices/` |
| Gate B `1` | Approve 27 tasks → 07 @ T0.1 |

## Artifacts

- `reports/execution-plan.md` — **approved** (27 tasks, M0–M4)
- This report — **completed**

## Next

**07-build** — T0.1 design note.
