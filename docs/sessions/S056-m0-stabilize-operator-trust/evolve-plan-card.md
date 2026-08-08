# Evolve Plan Card

> Cycle: EV-047 | Session: S056-m0-stabilize-operator-trust | Updated: 2026-08-08

## Goal

M0 slice: slim local husky to lint + fast units, hard-fail converter perf
regressions on PR/CI, and ship operator one-pager + minimal handbook.

## Features

- M5 — Workspace tooling (husky / pre-commit / Makefile) — deepen — [Corpus: product §M5]
- F6 — General TAC→IWXXM converter — deepen perf gate — [Corpus: product §F6]
- F7 — Multi-product operator UI — deepen help/docs link only — [Corpus: product §F7]

## In / out of scope

- In:
  - #833 husky = lint + fast unit subset; heavier gates CI / opt-in `make`
    (`D-S056-husky=1`, supersedes EV-036 day-to-day local-heavy path)
  - #834 converter regression harness + committed baselines + required CI check
  - #956 one-pager + #957 minimal handbook (no internal citations in user text)
  - Docs: `docs/ops/DEVELOPMENT.md` hook contract; test-plan / feature AC deltas
- Out:
  - #958 AMS abstract; converter micro-opts; weakening remote merge gates;
    staging/prod deploy unless help-link requires it

## Preset + routing

- Preset: Standard (skips 03/06/10/12/13)
- Stages (ordered): `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 11`

## Next child stage

**Finish Phase 0 intake** (AskQuestion: #834 thresholds + docs paths/help-link) →
then **01-requirements**.

## Locked decisions

| ID | Choice |
|----|--------|
| D-S056-open | 1 — S056 / EV-047 |
| D-S056-bundle | 1 — all four issues one cycle |
| D-S056-husky | 1 — lint + fast units; reverse EV-036 developer path |
| D-S056-preset | 1 — Standard; waive 12/13 |

## Risks / open decisions

- **#834 evaluation** — metric, baseline store, allowed delta, product scope,
  runner noise, pure-Python vs native (issue checklist)
- **#833 hook shape** — A (pre-commit lint / pre-push units) vs B (single
  pre-commit lint+units) — recommend in 01 after inventory
- **#956/#957 paths** — `docs/guides/` vs `docs/ops/` vs published site; help
  entry vs README Quick start only
- **Corpus:** operator handbook is under opt-in `docs/ops|guides` — cite
  product/journeys for help-link; no new CORPUS root member without AskQuestion
