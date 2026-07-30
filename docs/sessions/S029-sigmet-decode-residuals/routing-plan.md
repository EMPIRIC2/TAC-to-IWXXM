# Routing plan — S029-sigmet-decode-residuals

**Preset:** Lean (**proposed** — confirm in 00/16 Phase 0)  
**Orchestrator:** 16-evolve · **Cycle:** EV-022  
**Path:** `00→16→01 light→07→10 smoke→13 optional`  
**Skip:** `02, 03, 04, 05, 06, 08, 09, 11, 12` (re-add if scope grows)

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | scoped | **in_progress** | Session open |
| 16-evolve | yes | orchestrator | pending | Phase 0 intake |
| 01-requirements | yes | light | pending | F9 deepen delta only |
| 02-verify-plan | no | — | skipped | Lean |
| 03-plan-tooling | no | — | skipped | — |
| 04-tech-plan | no | — | skipped | Lean light |
| 05-verify-tech | no | — | skipped | — |
| 06-tech-tooling | no | — | skipped | — |
| 07-build | yes | full | pending | Decode residual tokens |
| 08-verify-build | no | — | skipped | Covered by 10 smoke |
| 09-qa | no | — | skipped | — |
| 10-e2e | yes | smoke | pending | Smoke only |
| 11-verify-impl | no | — | skipped | — |
| 12-verify-deploy | no | — | skipped | — |
| 13-deploy-smoke | **optional** | optional | pending | If API/FE change needs live verify |

## Skip rationale

F9 deepen on existing decode/summary path — no new deployable, no greenfield tooling.
Light 01 + direct 07; smoke 10; 13 only if live surface changes.

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Session open | S029 / `feat/EV-022-sigmet-decode-residuals` (D-S029-open) | 2026-07-30 |
| Routing | Lean proposed — confirm Phase 0 | pending |
