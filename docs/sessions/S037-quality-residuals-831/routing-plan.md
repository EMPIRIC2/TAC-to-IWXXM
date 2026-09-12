# Routing plan — S037-quality-residuals-831

**Preset:** Standard — intake `D-S037-open` Q2=1  
**Orchestrator:** 16-evolve · **Cycle:** EV-030  
**Path:** `00→16→01→02→04→07→08→09→10→11→12→13`  
**Skip:** `03, 05, 06` (re-add if 04 introduces new deps/ADR tooling/guardrails)  
**Work order:** #831 → #829 → #820

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | scoped | **completed** | Intake + routing approved `D-S037-route` = 1 |
| 16-evolve | yes | orchestrator | **in_progress** | Phase A → 01 after Fn lock |
| 01-requirements | yes | delta | **completed** | Manifest=2 (API/#829 catalog); close → 02 (`D-S037-E30-M`) |
| 02-verify-plan | yes | delta | **completed** | Gate A PASS (`D-S037-02-phase-a`); Batch F `1,1,1,1` |
| 03-plan-tooling | no | — | skipped | Re-add if new rules/hooks needed |
| 04-tech-plan | yes | delta | **completed** | Gate B PASS (`D-S037-04-plan`=1); 27-task plan approved |
| 05-verify-tech | no | — | skipped | No new deps (PyYAML reuse) |
| 06-tech-tooling | no | — | skipped | — |
| 07-build | yes | full | **in_progress** | @ T0.1 — #831 design note |
| 08-verify-build | yes | delta | pending | — |
| 09-qa | yes | delta | pending | — |
| 10-e2e | yes | smoke | pending | H4–H5 only if FE/menu unlock ships |
| 11-verify-impl | yes | delta | pending | Per-Fn acceptance |
| 12-verify-deploy | yes | delta | pending | — |
| 13-deploy-smoke | yes | full | pending | — |

## Skip rationale

Standard on an existing app: specs → tech plan → build → verify/deploy. No new deployable.
UI preview declined for this session; sample-menu unlock (#829) is a catalog/tier decision —
route H4–H5 only if frontend changes land.

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Session open / Phase 0 | `D-S037-open` = **1,1,2,1** — all three residuals; Standard; UI docs-only; type=feature | 2026-08-02 |
| Routing | `D-S037-route` = **1** — approve Standard → 16-evolve Phase 1 | 2026-08-02 |
| Fn allocation | `D-S037-fn` = **1,1,1** — F29 + deepen; start 01; commit open | 2026-08-02 |
| Manifest + 01 close | `D-S037-E30-M` = **2,1** — lean + API/catalog #829; → 02-verify-plan | 2026-08-02 |
| Batch F (02) | `D-S037-02-batch-f` = **1,1,1,1** — M1/M2/M3/L1 | 2026-08-03 |
| Gate A | `D-S037-02-phase-a` = **1** — PASS → **04-tech-plan** | 2026-08-03 |
| Batch 1 (04) | `D-S037-04-batch-1` = **1,1,1,1** — M0–M4; YAML; unified inventory; catalog unlock | 2026-08-03 |
| Batch 2 (04) | `D-S037-04-batch-2` = **2,1,1,1** — pyyaml reuse; H4–H5; PR smoke; `tests/quality_matrices/` | 2026-08-03 |
| Gate B | `D-S037-04-plan` = **1** — approve 27 tasks → **07 @ T0.1** | 2026-08-03 |
