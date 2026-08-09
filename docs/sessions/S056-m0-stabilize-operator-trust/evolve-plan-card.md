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

**07-build / M3 T3.1** — operator docs + Help (`D-S056-next-m3=1`, `D-S056-m3-order=2`).  
M2.5 T2.5.1–T2.5.4 COMPLETE @ `da31bf1f`. T1.5 ruleset apply deferred (`D-S056-t15-admin` — no repo admin).

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
| D-S056-next-m3 | 1 — M3 operator docs + Help (skip T1.5 for now; no admin) |
| D-S056-t15-admin | blocked — no repo admin; ruleset apply deferred; script/docs remain |
| D-S056-cov95 | 2 — package + per-file ≥95% this cycle (all Python packages in CI) |
| D-S056-m3-order | 2 — resolve coverage first, then M3 docs/Help |

## Risks / open decisions

- Help UI placement in existing shell (07 T3.3)
- CORPUS: guides remain opt-in; cite product/journeys for Help — no new root member
- M2.5 coverage COMPLETE (package + per-file ≥95 incl. auth/worker) @ `da31bf1f` (pushed)
- T1.5 admin ruleset apply still pending when admin available
