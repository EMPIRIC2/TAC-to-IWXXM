# 04-tech-plan — S021 / EV-016

**Status**: **completed**  
**Date**: 2026-07-26  
**Mode**: evolve delta (F7.g / #780)  
**Decision**: E16-16=A — execution plan approved  
**Routing**: Lean+build — 05/06 skipped unless forced

## Summary

| Item | Value |
|------|-------|
| Execution plan | `docs/sessions/S021-golden-examples-ui/reports/execution-plan.md` |
| Milestones | M1–M3 (**11** tasks) |
| New deps | **None** — reuse Radix `ui/select` (E16-15) |
| API / env / CORS | No deltas (E16-9) |
| ADR | Reuse ADR-024; no new ADR |
| Deploy | FE static only; H4–H5 on 13 |
| 05 / 06 | Skipped (Lean+build) |

## Interview batches

| Batch | Answers | IDs |
|-------|---------|-----|
| 1 Architecture / catalog / UX | A / A / A / A / B′ | E16-11..E16-15 |
| 2 Plan approve | **A** | E16-16 |

### Batch 1 detail

| ID | Topic | Decision |
|----|-------|----------|
| E16-11 | Catalog shape | Typed TS + copied `.tac`/`.xml` under `apps/frontend/src/fixtures/examples/` |
| E16-12 | Placement | Examples control next to product / Manual TAC Input |
| E16-13 | Fixtures | annex3 / product_matrix / iwxxm_us pairing; VAA/TCA 1+gap |
| E16-14 | IWXXM | Happy-path single-report XML → `inputMode=collect_iwxxm` |
| E16-15 | Select UI | **B′** — existing Radix `./ui/select` (no new npm package); not bare HTML `<select>` |

## Connectivity (04)

No new `configure_cors` / staging-secrets tasks — static FE assets only; browser still hits existing API origin. H4–H5 smoke required when frontend deploys (stage 13).

## Next

Phase B→C passed → **07-build** @ T1.1.
