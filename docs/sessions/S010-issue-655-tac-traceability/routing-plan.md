# Routing plan — S010 / EV-007

| Stage | Mode | Required | Status | Skip rationale |
|-------|------|----------|--------|----------------|
| 00-context | scoped | yes | in_progress | — |
| 01-requirements | delta | yes | pending | — |
| 02-verify-plan | — | no | skipped | Lean UI-only delta; spec delta + 04 plan sufficient |
| 03-plan-tooling | — | no | skipped | No new guardrails |
| 04-tech-plan | delta | yes | pending | — |
| 05-verify-tech | — | no | skipped | No stack/arch change |
| 06-tech-tooling | — | no | skipped | No new deps |
| 07-build | full | yes | pending | — |
| 08-verify-build | full | yes | pending | — |
| 09-qa | full | yes | pending | — |
| 10-e2e | delta | yes | pending | H4–H5 connectivity after frontend deploy |
| 11-verify-impl | full | yes | pending | — |
| 12-verify-deploy | full | yes | pending | Frontend redeploy required |
| 13-deploy-smoke | full | yes | pending | Prod Source TAC verification |

**Branch**: `evolve/EV-007-issue-655-tac-traceability`  
**Orchestrator**: 16-evolve
