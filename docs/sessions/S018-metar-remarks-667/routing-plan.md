# Routing plan — S018-metar-remarks-667

| Stage | Required | Mode | Skip rationale |
|-------|----------|------|----------------|
| 00-context | yes | scoped | Session open + context brief |
| 16-evolve | yes | orchestrator | EV-013 |
| 01-requirements | yes | delta | UJ / feature-list / test-plan for #667 |
| 02-verify-plan | yes | delta | Consistency vs F6 / IWXXM_CONVERSION never-drop |
| 04-tech-plan | yes | delta | Short execution tasks in session reports |
| 07-build | yes | delta | tac2iwxxm parse/emit/convert |
| 08-verify-build | yes | delta | lint + scoped pytest |
| 09-qa | yes | delta | package suite + format-check |
| 11-verify-impl | yes | delta | Per-acceptance #667 |
| 12-verify-deploy | yes | delta | Preflight readiness |
| 13-deploy-smoke | yes | delta | H1–H3; H4–H5 if convert issues surface in UI |
| 03-plan-tooling | no | — | No new guardrails |
| 05-verify-tech | no | — | Thin 04; fold into 02 |
| 06-tech-tooling | no | — | No stack change |
| 10-e2e | yes | delta | Amended 2026-07-20 (user request); UJ-026/UJ-010 T0 library |

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Scope | E13-1 Assumed (AskQuestion waived) | 2026-07-20 |
| Routing | Standard subset above | 2026-07-20 |
| Fn | F6 deepen; no new Fn | 2026-07-20 |
