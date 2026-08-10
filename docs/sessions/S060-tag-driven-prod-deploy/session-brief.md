# Session brief — S060-tag-driven-prod-deploy

> **Cycle**: EV-051 · **Type**: feature · **Opened**: 2026-08-09  
> **Branch**: `evolve/EV-051-tag-driven-prod-deploy` (base `stage@c146baec`)  
> **Orchestrator**: 16-evolve  
> **Corpus**: [Corpus: product §F30] [Corpus: deploy] [Corpus: adr/ADR-034] [Corpus: tests]

## Goal

Solo-dev prod cutover: full CI must pass before Deploy; **staging** still auto-deploys
after full CI on `stage` push; **prod** deploys only when a `vYYYY.MM.DD-deploy` tag is
pushed (optional `workflow_dispatch` escape hatch) — not on bare `main` push.

## Intent (locked draft — await D-S060-scope)

Design **2 + 3 + 4** (user):

1. **Widen Deploy `needs`** to include at least `e2e-smoke` (frontend already inside
   `test` matrix) so Deploy waits on “full” CI in `ci-cd.yml`.
2. **Split**: push to `main` runs full CI **without** prod Deploy.
3. **Tag-driven prod**: Deploy prod on `vYYYY.MM.DD-deploy` (and optional
   `workflow_dispatch` for a SHA).
4. Amend ADR-034 / `docs/deploy.md` / `doks-promote-from-stage.mdc` / TC-F30-010 wording.

## Out of scope

- GitHub Environment required reviewers (solo cannot rely on them)
- Chat/Slack approve bots
- Changing PyPI package-tag publish path
- Resuming parked EV-043 / EV-044 sessions (remain parked; this cycle deepens F30)
- Quality-pack workflows as Deploy `needs` unless user expands scope
- UI / product feature work (`ui_preview: n/a`)

## Features

- Deepen **F30** only (no new Fn) — platform CD / promote path

## UI preview

N/A — no browser UI in this session.

## Related

- Parked: S052/EV-043, S053/EV-044 (F30 DOKS) — not resumed
- Prior auto-deploy-on-main: ADR-034 / feature-list TC-F30-010 — to amend
