# Routing plan — S027-vaa-quality

**Preset:** Lean+build+11 (**approved** E21-4)  
**Orchestrator:** 16-evolve · **Cycle:** EV-021  
**Path:** `00→16→01→02→04→07→08→10→11→13`  
**Skip:** `03, 05, 06, 09, 12` (re-add if 04 introduces new deps/ADR tooling)

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 01-requirements | yes | delta | **completed** | E21-D1..D4; E21-E1=1 |
| 02-verify-plan | yes | delta | **completed** | PASS Batch F 1,1,1; Gate A Lean |
| 03-plan-tooling | no | — | skipped | Re-add if new ADR/rule tooling needed |
| 04-tech-plan | yes | delta | **completed** | E21-T1..T6 all 1; execution-plan approved |
| 05-verify-tech | no | — | skipped | — |
| 06-tech-tooling | no | — | skipped | — |
| 07-build | yes | full | **in_progress** | M0 done; next T1.1 |
| 08-verify-build | yes | full | pending | — |
| 09-qa | no | — | skipped | 08+10+11 cover |
| 10-e2e | yes | full | pending | VAA + TCA product-path journeys |
| 11-verify-impl | **yes** | full | pending | F26/F27 AC sign-off |
| 12-verify-deploy | no | — | skipped | — |
| 13-deploy-smoke | yes | full | pending | H1–H5 when API/FE change |

## Skip rationale

Same as S025/S026 quality bars: product encode/lint deepen on existing stack; no new deployable,
no greenfield tooling. **11-verify-impl** kept for AC sign-off before smoke. Dual product
(VAA+TCA) stays on Lean+build+11 (E21-1=2).

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Session open | S027 / `evolve/EV-021-vaa-quality` | 2026-07-29 |
| Intake | E21-1=2, E21-2=1, E21-3=1(+mine), E21-4=1 | 2026-07-29 |
| Routing | Lean+build+11 approved | 2026-07-29 |
| 02 PASS / Gate A | Batch F all 1; Lean skip AskQuestion → 04 | 2026-07-29 |
| 04 PASS / Gate B | Batch T all 1; execution-plan → 07 @ T0.1 | 2026-07-29 |
| M0 complete | T0.1–T0.3; theme map + wmo-quality extend | 2026-07-29 |
