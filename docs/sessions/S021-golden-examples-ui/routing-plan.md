# Routing plan — S021-golden-examples-ui

**Preset:** Lean+build (`E16-3`, 2026-07-22)  
**Orchestrator:** 16-evolve · **Cycle:** EV-016

| Stage | Required | Mode | Skip rationale |
|-------|----------|------|----------------|
| 00-context | yes | scoped | Session open + `docs/context/golden-examples-ui.md` |
| 16-evolve | yes | orchestrator | EV-016 |
| 01-requirements | yes | delta | F7 deepen — examples AC, UJ, test-plan H4–H5 |
| 02-verify-plan | yes | delta | Consistency across product / journeys / tests |
| 03-plan-tooling | **no** | — | No new Cursor rules/hooks expected |
| 04-tech-plan | yes | delta | FE catalog shape + FileConverter wiring tasks |
| 05-verify-tech | **no** | — | Lean+build; re-run if 04 introduces deps/ADR conflict |
| 06-tech-tooling | **no** | — | No new tooling |
| 07-build | yes | full | Frontend fixtures + Examples UX |
| 08-verify-build | yes | full | — |
| 09-qa | yes | full | — |
| 10-e2e | yes | full | Vitest + H4–H5 workbench smoke when FE deploys |
| 11-verify-impl | yes | full | Per–acceptance-criterion (F7 deepen / #780) |
| 12-verify-deploy | **no** | — | Lean+build; run only if deploy checklist forced |
| 13-deploy-smoke | yes | full | H4–H5 when frontend ships; no API/env changes expected |

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Session open | S021-golden-examples-ui / EV-016 | 2026-07-22 (E16-1) |
| Fn allocation | Deepen **F7** only | 2026-07-22 (E16-2) |
| Routing | **Lean+build** | 2026-07-22 (E16-3) |
| Scope | #780 AC locked | 2026-07-22 (E16-4) |
| AskQuestion | Written interview waive | 2026-07-22 |
