# Routing plan — S008-general-tac-iwxxm-converter

| Stage | Required | Mode | Skip rationale |
|-------|----------|------|----------------|
| 00-context | yes | scoped | Architecture discovery + design partner brief |
| 01-requirements | yes | delta | New product Fn / F1 evolution for US extensions + multi-product |
| 02-verify-plan | no | — | Skipped: tooling/corpus already mature; delta docs verified in 05 |
| 03-plan-tooling | no | — | Skipped: hooks/rules exist; Cython build tooling deferred to 04/06 if chosen |
| 04-tech-plan | yes | delta | Package layout, C/Cython strategy, schema pins, metrics harness |
| 05-verify-tech | yes | delta | Audit tech plan against vendor + gifts constraints |
| 16-evolve | yes | full | Evolve cycle EV-00N — feature ids, ADR, execution plan |
| 07-build | yes | full | After evolve plan approved |
| 08-verify-build | yes | full | Milestone gates |
| 09-qa | yes | full | Quality suite |
| 10-e2e | yes | delta | Only if API/UI surface changes |
| 11-verify-impl | yes | full | Corpus parity |
| 12-verify-deploy | no | — | Skipped until package is wired into deployables |
| 13-deploy-smoke | no | — | Skipped until deploy wiring exists |

## Approved

User approval recorded: 2026-07-12 (chose close S007 + open S008 with this routing).
