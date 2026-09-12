# Routing plan — S026-airmet-quality-wmo-examples

**Preset:** Lean+build+11 (**approved** — D-S026-E20-routing-C1)  
**Orchestrator:** 16-evolve · **Cycle:** EV-020  
**Path:** `00→16→01→02→04→07→08→10→11→13`  
**Skip:** `03, 05, 06, 09, 12`

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | scoped | **completed** | Session open; intake locked |
| 16-evolve | yes | orchestrator | **in_progress** | EV-020 → 04 |
| 01-requirements | yes | delta | **completed** | E20-E1..E3 |
| 02-verify-plan | yes | delta | **completed** | PASS Batch F; ADR-032 Accepted |
| 03-plan-tooling | no | — | skipped | Re-add if glossary needs new ADR/rule |
| 04-tech-plan | yes | delta | **completed** | Plan approved E20-F8; execution-plan.md |
| 05-verify-tech | no | — | skipped | Re-add if 04 adds deps/ADR |
| 06-tech-tooling | no | — | skipped | — |
| 07-build | yes | full | **in_progress** | T0.1 research catalog |
| 08-verify-build | yes | full | pending | — |
| 09-qa | no | — | skipped | 08+10+11 cover |
| 10-e2e | yes | full | pending | UJ-035 / UJ-036 (+ UJ-020/032 deepen) |
| 11-verify-impl | **yes** | full | pending | F24/F25 AC sign-off (C=1) |
| 12-verify-deploy | no | — | skipped | — |
| 13-deploy-smoke | yes | full | pending | H1–H5 when API/FE change |

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Session open | S026 / `evolve/EV-020-airmet-quality` | 2026-07-29 |
| Intake E20-1..6 / A / B | Locked | 2026-07-29 |
| Fn allocation | F24 + F25 + deepen F9/F7.g/F6/F3 | 2026-07-29 |
| Routing | **C=1** Lean+build+11 | 2026-07-29 |
| Proceed to 01 | E20-8 | 2026-07-29 |
| 01 complete | E20-E3 → 02 | 2026-07-29 |
| 02 PASS / Gate A | Batch F all 1; ADR-032 Accepted → 04 | 2026-07-29 |
| 04 plan approved | E20-F1..F8; Gate B→C → 07 @ T0.1 | 2026-07-29 |
