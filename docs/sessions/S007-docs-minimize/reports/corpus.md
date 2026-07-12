# Corpus addition — S007

**Date:** 2026-07-12

## What

Defined a **common minimal corpus** for design and parity checks, referenced consistently by skills/rules:

| Artifact | Purpose |
|----------|---------|
| [`docs/CORPUS.md`](../../CORPUS.md) | Manifest + parity protocol + skill obligations |
| [`docs/tech-spec.md`](../../tech-spec.md) | Tech hub (config / env / deploy / deps) |
| [`.cursor/rules/core/docs-corpus.mdc`](../../../.cursor/rules/core/docs-corpus.mdc) | Always-on rule: cite `[Corpus: <id>]` |

## Corpus IDs

`product` · `journeys` · `system-spec` · `tech-spec` · `api` · `tests` · `adr` · `decisions`

## Wired

- `pipeline-preamble.md`, `sessions-reference.md`, `doc-planner/doc-types.md`
- `14-hotfix` Spec registry
- `spec-adherence.mdc`, `plan-adherence.mdc`, `iwxxm-domain-vocabulary.mdc`
- `docs/README.md` leads with corpus table

## Not done

- Commit / PR (awaiting user)
- Closing S007 / optional 18-pr-review
