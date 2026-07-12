# Documentation

**Canonical design / parity set:** [`CORPUS.md`](CORPUS.md) — skills cite this, not ad-hoc doc lists.

**Session work:** [`sessions/`](sessions/) — see [skill-routing.md](skill-routing.md).

## Minimal corpus (root + adr + decisions)

| Corpus ID | Doc | Role |
|-----------|-----|------|
| product | [feature-list.md](feature-list.md) | Approved features (F1–F4, M1–M6) |
| journeys | [user-journeys.md](user-journeys.md) | User journeys |
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
| [skill-routing.md](skill-routing.md) | Which pipeline skill to run |
| [typing-policy.md](typing-policy.md) | Python/TS typing policy |
| [hotfix-log.md](hotfix-log.md) | Hotfix index |

## Folders

| Folder | Contents |
|--------|----------|
| [decisions/](decisions/) | Product/tech/requirements/evolve decision logs & audits |
| [ops/](ops/) | Development, env sync, secrets matrix, migration plan |
| [guides/](guides/) | Architecture, API overview, implementation, Supabase, OpenAIP |
| [domain/iwxxm/](domain/iwxxm/) | IWXXM versions, formatting, ICAO/OPMET, elevation |
| [domain/validation/](domain/validation/) | XSD/Schematron validation notes |
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
- IWXXM version switching: [domain/iwxxm/IWXXM_VERSION_SWITCHING.md](domain/iwxxm/IWXXM_VERSION_SWITCHING.md)
