# Documentation

This folder holds the tracked engineering spine for TAC-to-IWXXM. Agent skills
read the corpus index in [AGENTS.md](../AGENTS.md) first.

## Install and run

Local install and run steps live in the local (gitignored) ops tree when present:
`docs/ops/DEVELOPMENT.md`. Deploy manifests live under
[deploy/doks/](../deploy/doks/). Runtime non-secret profiles live under
[deploy/profiles/](../deploy/profiles/).

## Public user guide

Operator and integrator documentation lives in [`user-docs/`](../user-docs/)
(MkDocs, Read the Docs theme). Build locally:

```bash
pip install mkdocs
cd user-docs && mkdocs serve
```

Cross-page links point at the
[GitHub Wiki](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki). This site is not
the engineering HTTP contract. Use [api-contract.md](api-contract.md) and
[api/openapi.json](../api/openapi.json) for field-level API truth.

## Tracked spine

| Doc | Role |
|-----|------|
| [spec.md](spec.md) | System architecture (`system-spec`) |
| [tech-spec.md](tech-spec.md) | Runtime / deploy / deps hub |
| [env-variable.md](env-variable.md) | Environment variable names |
| [api-contract.md](api-contract.md) | HTTP narrative contract |
| [test-plan.md](test-plan.md) | Test matrix and gates |
| [user-journeys.md](user-journeys.md) | End-user journeys |
| [ui-style-guide.md](ui-style-guide.md) | Operator UI norms |

## Release notes

Release notes: [CHANGELOG.md](../CHANGELOG.md).

## Local-only trees

Architecture decisions, ops runbooks, domain mining notes, and STE dictionary
files stay on the developer machine. They are not part of the public git tree.
See [AGENTS.md](../AGENTS.md) §Local opt-in. Exception: `docs/domain/profiles/`
stays tracked for the ConversionProfile catalog and the API Docker image.
