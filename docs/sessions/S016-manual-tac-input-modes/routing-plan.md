# Routing plan — S016-manual-tac-input-modes

| Stage | Required | Mode | Skip rationale |
|-------|----------|------|----------------|
| 00-context | yes | scoped | Session open + `docs/context/manual-tac-input-modes.md` |
| 16-evolve | yes | orchestrator | EV-012 |
| 01-requirements | yes | delta | test-plan / UJ for input modes; checklist acceptance |
| 02-verify-plan | yes | delta | Consistency vs ADR-024 / F7 / api-contract |
| 10-e2e | yes | delta | Author + run Playwright T1–T4; Vitest gap check |
| 13-deploy-smoke | yes | full | H4–H5 + authenticated AHL + COLLECT 501 |
| 03-plan-tooling | no | — | No new guardrails |
| 04-tech-plan | no | — | No new API/arch; Playwright under 10 |
| 05-verify-tech | no | — | Skipped with 04 |
| 06-tech-tooling | no | — | No stack change |
| 07-build | no | — | Lean: author tests in 10 |
| 08-verify-build | no | — | Skipped with 07 |
| 09-qa | no | — | Covered by 10 + Vitest |
| 11-verify-impl | no | — | F7 stays Planned; no Fn flip |
| 12-verify-deploy | no | — | Smoke-only via 13 |

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Scope / cycle type | A — F7 validation; no new Fn; COLLECT 501 | 2026-07-20 (E12-1) |
| Automation | Vitest + Playwright T1–T4 + live staging | 2026-07-20 (E12-2) |
| Auto-switch | Required | 2026-07-20 (E12-3) |
| Deploy | 13-deploy-smoke included | 2026-07-20 (E12-4) |
| Routing | **Lean + 13** (00, 16, 01, 02, 10, 13) | 2026-07-20 (D-S016-EV012-route-1) |
