# Evolve Plan Card

> Cycle: EV-051 | Session: S060-tag-driven-prod-deploy | Updated: 2026-08-09

## Goal

Full CI before Deploy; staging auto on `stage`; prod only via `vYYYY.MM.DD-deploy`
tag (+ optional `workflow_dispatch`); amend ADR-034 / deploy docs / promote rule.

## Features

- F30 — deepen platform CD / promote — [Corpus: product §F30] [Corpus: deploy]
  [Corpus: adr/ADR-034]

## In / out of scope

- In: widen Deploy `needs` (+ `e2e-smoke`); no auto Deploy on `main` push; tag-driven
  prod; optional dispatch; docs/ADR/rule/`ci-cd.yml`; amend TC-F30-010
- Out: Environment reviewers; Slack bots; PyPI path change; resume EV-043/044; quality
  packs as Deploy needs (unless expanded); `stage`→`main` promote this cycle

## Preset + routing

- Preset: **Lean+** (`D-S060-route=1`) — `00 → 16 → 01 → 02 → 03 → 07 → 08 → 09 → 11`
- Skip: `04`, `05`, `06`, `10`, `12`, `13`

## Next child stage

**CLOSED** — `D-S060-close=1`; PR #966 MERGED → `stage` @ `8882856b`.

## Risks / open decisions

- First prod cutover after `stage`→`main` promote needs deliberate
  `vYYYY.MM.DD-deploy` tag (or workflow_dispatch)
- Quality-pack workflows as Deploy `needs` remains OOS
