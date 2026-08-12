# Documentation

**Canonical design / parity set:** [`CORPUS.md`](CORPUS.md) — skills cite this, not ad-hoc doc lists.

**Session work:** [`sessions/`](sessions/) — see [skill-routing.md](skill-routing.md).

**Current deploy tips:** [`deploy-state.md`](deploy-state.md) (staging has Quality metrics;
prod last promote 2026-08-10).

## Minimal corpus (root + adr + decisions)

| Corpus ID | Doc | Role |
|-----------|-----|------|
| product | [feature-list.md](feature-list.md) | Approved features (Quality metrics deepen on stage) |
| journeys | [user-journeys.md](user-journeys.md) | User journeys (incl. Quality metrics) |
| system-spec | [spec.md](spec.md) | Architecture & constraints |
| tech-spec | [tech-spec.md](tech-spec.md) | Hub → config / env / deploy / deps |
| api | [api-contract.md](api-contract.md) | HTTP contract |
| tests | [test-plan.md](test-plan.md) | Test tiers & TC-IDs |
| — | [config-spec.md](config-spec.md), [env-contract.md](env-contract.md), [deploy.md](deploy.md), [dependency-inventory.md](dependency-inventory.md) | Tech-spec satellites |
| adr | [adr/](adr/) | Architecture decision records |
| decisions | [decisions/](decisions/) | Interview / evolve decision logs |

## Other root (not corpus)

| Doc | Role |
|-----|------|
| [CORPUS.md](CORPUS.md) | Corpus manifest + parity protocol |
| [CHANGELOG.md](CHANGELOG.md) | Release / unreleased stage notes |
| [deploy-state.md](deploy-state.md) | Staging + prod tip SHAs |
| [skill-routing.md](skill-routing.md) | Which pipeline skill to run |
| [typing-policy.md](typing-policy.md) | Python/TS typing policy |
| [hotfix-log.md](hotfix-log.md) | Hotfix index |
| [evolve-report-EV-*.md](evolve-report-EV-056.md) | Standing evolve closeout reports |

## Folders

| Folder | Contents |
|--------|----------|
| [decisions/](decisions/) | Product/tech/requirements/evolve decision logs & audits |
| [ops/](ops/) | Development, env sync, secrets matrix, migration plan |
| [guides/](guides/) | Operator one-pager / handbook; architecture narratives |
| [domain/](domain/) | Rule provenance hub — TAC / IWXXM validation + conversion strategies |
| [domain/rules/](domain/rules/) | URL catalog, coverage matrix, citation policy |
| [domain/iwxxm/](domain/iwxxm/) | IWXXM versions, formatting, ICAO/OPMET, elevation |
| [domain/validation/](domain/validation/) | Engine architecture / Schematron render notes |
| [reports/](reports/) | Historical project-level QA / E2E / verification reports |
| [testing/](testing/) | Testing strategy & coverage plans |
| [integration/](integration/) | Auth, airport data, OpenAIP integration notes |
| [adr/](adr/) | Architecture decision records |
| [bug-reports/](bug-reports/) | BUG-* investigation reports |
| [context/](context/) | Scoped context briefs |
| [sessions/](sessions/) | Session briefs, routing plans, stage reports |
| [sql-optimization/](sql-optimization/) | SQL notes |
| [ARCHIVE/](ARCHIVE/) | Superseded / pre-monorepo docs |

## Quick links

- Local setup: [ops/DEVELOPMENT.md](ops/DEVELOPMENT.md)
- Env sync: [ops/env-sync-runbook.md](ops/env-sync-runbook.md)
- Operator one-pager: [guides/operator-one-pager.md](guides/operator-one-pager.md)
- Operator handbook: [guides/operator-handbook.md](guides/operator-handbook.md)
- Domain E2E strategy (TAC → convert → XSD/SCH): [domain/README.md](domain/README.md)
- TAC / Annex 3 validation: [domain/TAC_VALIDATION.md](domain/TAC_VALIDATION.md)
- TAC→IWXXM conversion rules: [domain/IWXXM_CONVERSION.md](domain/IWXXM_CONVERSION.md)
- IWXXM XSD/Schematron validation: [domain/IWXXM_VALIDATION.md](domain/IWXXM_VALIDATION.md)
- IWXXM version switching: [domain/iwxxm/IWXXM_VERSION_SWITCHING.md](domain/iwxxm/IWXXM_VERSION_SWITCHING.md)
- Staging Quality metrics: https://app.staging.tac-to-iwxxm.com/quality
