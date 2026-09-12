# Context — local pre-commit long jobs (S044 / EV-036)

**Mode:** scoped · **Date:** 2026-08-05  
**Session:** [S044-local-precommit-long-jobs](../sessions/S044-local-precommit-long-jobs/session-brief.md)

## Goal

Run local-capable long quality jobs on **developer machines via pre-commit** so GitHub
Actions spend fewer minutes. `[Corpus: product]` **M5** deepen; `[Corpus: tech-spec]` /
`[Corpus: tests]` gate placement; ops `docs/ops/DEVELOPMENT.md`.

## Baseline

- **pre-commit:** fast gates (`.pre-commit-config.yaml`)
- **pre-push:** `make validate-ci` + `make ci-prepush` (`.husky/pre-push`)
- **CI:** `validate` + matrix `test` (+ alembic / native / e2e-smoke / deploy) in `ci-cd.yml`

## Non-goals

- Product UI / React workbench changes
- Jobs requiring remote-only secrets, GHCR publish, or live prod E2E
