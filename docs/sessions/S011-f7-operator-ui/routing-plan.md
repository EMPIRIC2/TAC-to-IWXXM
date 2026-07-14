# Routing plan — S011-f7-operator-ui

| Stage | Required | Mode | Status | Skip rationale |
|-------|----------|------|--------|----------------|
| 00-context | yes | scoped | in_progress | — |
| 01-requirements | yes | delta | pending | — |
| 02-verify-plan | yes | delta | pending | — |
| 03-plan-tooling | no | — | skipped | Hooks/rules already exist from prior cycles |
| 04-tech-plan | yes | delta | pending | — |
| 05-verify-tech | yes | delta | pending | — |
| 06-tech-tooling | no | — | skipped | Lint/typecheck/CI already wired |
| 07-build | yes | full | pending | — |
| 08-verify-build | yes | full | pending | — |
| 09-qa | yes | full | pending | — |
| 10-e2e | yes | full | pending | — |
| 11-verify-impl | yes | full | pending | — |
| 12-verify-deploy | yes | full | pending | — |
| 13-deploy-smoke | yes | full | pending | — |

## Orchestrator

After 00 completes → **16-evolve** allocates `EV-00N`, then drives delta 01→…→13 per this plan.

## Approved

User approval recorded: **2026-07-13** (approve all defaults — packaging A, routing A, #5 A).
