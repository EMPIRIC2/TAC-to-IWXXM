# Repository tests

[Corpus: tests]

Cross-cutting suites that are not owned by a single package under `apps/` or
`packages/`. Package-local tests stay next to their code
(`packages/*/tests`, `apps/*/tests`).

## Top-level tree

| Path | Role |
|------|------|
| `bugs/` | Hotfix and qa-gap regressions (thematic subdirs; see `bugs/README.md`) |
| `unit/` | Shared unit checks |
| `integration/` | Cross-service integration |
| `contracts/` | Pact / OpenAPI interaction fixtures |
| `smoke/` | Fast smoke |
| `bats/` | Shell bats (CI, deploy, env, …) |
| `quality_matrices/` | Product lint/convert/validate matrices |
| `regression/` | Named regression packs (e.g. Caribbean tester) |
| `live/` | Live / staging probes (often marked `live`) |
| `perf/` | Perf baselines |
| `migration/` `cutover/` `vendor/` `codegen/` `provenance/` `docs/` `scripts/` `ci/` `cmo_week1/` | Specialized suites |
| `fixtures/` | Shared fixtures |
| Root `test_*.py` | Legacy CI/config helpers — prefer a category dir for new files |

## Naming

| Kind | Pattern |
|------|---------|
| Bug repro | `bugs/<theme>/test_bug_YYYY_MM_DD_<slug>.py` |
| QA gap | `bugs/qa_gap/test_qa_gap_YYYY_MM_DD_<slug>.py` |
| Behavior unit | `test_<subject>_<scenario>.py` |
| Package TC archives | Existing `test_tc_*` / `test_ev*` stay; new files prefer behavior names; put TC/EV ids in docstrings or markers |

## CI

- Bug regressions: `pytest tests/bugs` (job matrix entry `bugs`)
- Format scope includes `tests/` (`make format-check`)

Detail and pass criteria: `docs/test-plan.md`.
