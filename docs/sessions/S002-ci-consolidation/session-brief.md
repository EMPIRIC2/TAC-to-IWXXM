# Session S002 — CI consolidation (EV-002)

**Type**: feature (general evolve)  
**Orchestrator**: 16-evolve  
**Feature**: M5 (Workspace tooling)  
**Branch**: `evolve/EV-002-ci-consolidation` (to be created at 07-build)  
**Opened**: 2026-06-22

## Intent

Reduce GitHub Actions job count and workflow file sprawl for PR/push CI without lowering
quality gates. Offload fast static analysis to pre-commit; keep full test suite in CI.

## Approved scope

See [evolve-decisions.md §Cycle EV-002](../../decisions/evolve-decisions.md).

## Routing plan

| Stage | Status | Notes |
|-------|--------|-------|
| 01-requirements | completed | Delta to feature-list, test-plan, evolve-decisions |
| 02-verify-plan | pending | Consistency pass on CI spec delta |
| 03-plan-tooling | pending | Pre-commit hook definitions |
| 04-tech-plan | pending | Execution plan for ci-cd.yml rewrite |
| 05-verify-tech | pending | |
| 06-tech-tooling | pending | pre-commit repo hooks (actionlint, yamllint) |
| 07-build | pending | Implement consolidated CI + pre-commit |
| 08-verify-build | pending | |
| 11-verify-impl | pending | Acceptance criteria from EV-002 |
| 09-qa, 10-e2e, 12, 13 | skipped | No product or deploy surface changes |

## Success criteria

- ≤3 CI jobs on PR (validate, test)
- All pre-EV-002 checks still run in CI
- Pre-commit fast hooks mirror validate job
- `make ci` unchanged
