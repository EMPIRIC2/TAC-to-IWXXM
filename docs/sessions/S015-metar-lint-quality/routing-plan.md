# Routing plan — S015-metar-lint-quality

| Stage | Required | Mode | Skip rationale |
|-------|----------|------|----------------|
| 00-context | yes | scoped | Session open + `docs/context/metar-lint-quality.md` (research seed) |
| 16-evolve | yes | orchestrator | EV-011 |
| 01-requirements | yes | delta | F15 + F6/F12 deepen; #732 acceptance → corpus |
| 02-verify-plan | yes | delta | Consistency across product / domain / test-plan |
| 03-plan-tooling | yes | delta | Guardrails for issue-registry codes/severities (no ad-hoc literals) |
| 04-tech-plan | yes | delta | Execution plan: registry → METAR rules → goldens → CI metrics |
| 05-verify-tech | yes | delta | — |
| 06-tech-tooling | yes | delta | Registry packaging, fixture layout, CI hooks if needed |
| 07-build | yes | full | — |
| 08-verify-build | yes | full | — |
| 09-qa | yes | full | — |
| 10-e2e | yes | full | Library + API `product=metar` + workbench smoke |
| 11-verify-impl | yes | full | Per-Fn (F15 + F6/F12 deepen) sign-off |
| 12-verify-deploy | yes | full | Render checklist if API/FE contract changes |
| 13-deploy-smoke | yes | full | H1–H5 when deployables change; waive only if build-only |

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Fn allocation | F15 + deepen F6/F12 | 2026-07-19 (E11-4) |
| Scope | Full #732 + registry + goldens + **max** research/validation/conversion expansion (R1–R6 + catalog + opportunistic) | 2026-07-19 (E11-3, E11-6) |
| Routing | **00–13 incl. 03/06**; Render 12–13 included | 2026-07-19 (E11-5 = A) |
| Research depth | Aggressive encode **and** research catalog in 01 **and** registry+goldens; plus any other METAR quality wins in-cycle | 2026-07-19 (E11-6 = 1+2+3+) |
