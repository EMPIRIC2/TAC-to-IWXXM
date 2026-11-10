# Documentation index

This folder holds the tracked engineering spine for TAC to IWXXM.
Agents start at [AGENTS.md](../AGENTS.md). Writers follow
[documentation-standards.md](documentation-standards.md).

## Root spine

| Doc | Role |
|-----|------|
| [product-requirements.md](product-requirements.md) | Project definition and behavioral requirements |
| [technical-requirements.md](technical-requirements.md) | Functional and technical requirements and pass criteria |
| [architecture.md](architecture.md) | System architecture and component boundaries |
| [domain-contract.md](domain-contract.md) | TAC/IWXXM domain pipeline and profiles |
| [api-contract.md](api-contract.md) | HTTP narrative contract |
| [ops-contract.md](ops-contract.md) | Local, staging, and production ops contract |
| [integration-contract.md](integration-contract.md) | External system integration rules |
| [data-flows.md](data-flows.md) | Primary data paths |
| [data-integrations.md](data-integrations.md) | Systems that supply or receive data |
| [ui-style-guide.md](ui-style-guide.md) | Operator UI norms |
| [documentation-standards.md](documentation-standards.md) | Writing and corpus rules |
| [env-variable.md](env-variable.md) | Environment variable names |
| [user-journeys.md](user-journeys.md) | Journey schema (matrix in CSV) |
| [test-plan.md](test-plan.md) | Test schema and test tiers (matrix in CSV) |

## CSV matrices

| File | Role |
|------|------|
| [user-journeys.csv](user-journeys.csv) | Journey rows tied to tests |
| [test-plan.csv](test-plan.csv) | Test-case and coverage rows |
| [risks.csv](risks.csv) | Risks log |
| [assumptions.csv](assumptions.csv) | Assumptions log |
| [issues.csv](issues.csv) | Issues log |
| [decisions.csv](decisions.csv) | Decisions log |

## Tracked config (not under docs)

| Path | Role |
|------|------|
| [config/profiles/](../config/profiles) | Conversion profile catalog for the API |
| [config/rules/](../config/rules) | Issue catalog and provenance map |
| [config/engineering/](../config/engineering) | Coverage surface inventories |

## Public user guide

Operator and integrator docs for end users live in [`user-docs/`](../user-docs).
That site is not the engineering HTTP contract.

## Local feeders (not tracked)

`docs/domain/`, `docs/engineering/`, `docs/ops/`, `docs/adr/`, decision notes, guides,
UX logs, STE dictionary files, and `docs/local-feeders/` stay on the developer machine.
See [AGENTS.md](../AGENTS.md) for the local opt-in list.

## Compatibility pointers

| Old path | Now |
|----------|-----|
| `docs/spec.md` | [architecture.md](architecture.md) |
| `docs/tech-spec.md` | [technical-requirements.md](technical-requirements.md) |
| `docs/domain/profiles/` | [config/profiles/](../config/profiles) + [domain-contract.md](domain-contract.md) |
| `docs/domain/rules/` | [config/rules/](../config/rules) + [domain-contract.md](domain-contract.md) |
| `docs/engineering/` coverage YAML | [config/engineering/](../config/engineering) |
| `docs/ops/` runbooks | [ops-contract.md](ops-contract.md) |
