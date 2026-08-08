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

- Preset: Standard (skips 03/06/12/13; **10-e2e required** for Help)
- Stages (ordered): `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11`

## Next child stage

**01-requirements** — confirm AC1–AC9 (`D-S056-01-ac`) → **02-verify-plan**.

## Locked decisions

| ID | Choice |
|----|--------|
| D-S056-open | 1 — S056 / EV-047 |
| D-S056-bundle | 1 — all four issues one cycle |
| D-S056-husky | 1 — lint + fast units; reverse EV-036 developer path |
| D-S056-husky-shape | 1 (A) — pre-commit lint; pre-push fast units |
| D-S056-perf | 1 — convert p95 / 20% / CI-only / thin product smoke |
| D-S056-docs | 1 — guides one-pager + handbook; README + Help |
| D-S056-preset | 1 — Standard; waive 12/13; 10 re-enabled |
| D-S056-phase0 | 1 — Phase 0 locked |

## Risks / open decisions

- Absolute ms ceiling value (derive in 04 from baselines×1.20 + floor)
- Exact “fast unit subset” Makefile target name (04 inventory)
- Help UI placement in existing shell (04/07)
- CORPUS: guides remain opt-in; cite product/journeys for Help — no new root member
