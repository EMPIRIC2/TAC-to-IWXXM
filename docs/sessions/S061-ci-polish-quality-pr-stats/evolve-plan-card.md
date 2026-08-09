# Evolve Plan Card

> Cycle: EV-052 | Session: S061-ci-polish-quality-pr-stats | Updated: 2026-08-09

## Goal

Restore 95% coverage gates, add a second sticky PR comment for golden/quality outcomes
by profile, and ship free-tier Sentry + shared rate-limit backend + OpenAPI typed FE client.

## Features

- F29 — Parameterized quality matrices — deepen (PR outcome comment) — [Corpus: product §F29]
- F6 — TAC→IWXXM / M-golden — deepen (stats aggregation) — [Corpus: product §F6]
- F21 — Public app abuse controls — deepen (Redis-backed slowapi) — [Corpus: product §F21]
- F30 — Platform / observability — deepen (Sentry) — [Corpus: product §F30] [Corpus: adr/ADR-006]
- M5 — Workspace tooling — deepen (Orval/openapi-typescript) — [Corpus: product §M5]
- Tests / ADR-007 — 95% gates — [Corpus: tests] [Corpus: adr/ADR-007]

## In / out of scope

- In:
  - #950 inventory + enforce ≥95% everywhere; fill tests (no silent waive)
  - Sticky PR comment #2: quality-matrix + annex3/`iwxxm_us` golden outcome tables
    (match / soft-diff / fail / skip × product × profile); marker ≠ EV-036 coverage
  - #900 implement: Sentry (API+FE+worker), Redis-compatible rate-limit store, Orval or
    openapi-typescript client gen
  - Free-tier verification + infra change report (see `reports/infra-free-tier.md`)
- Out:
  - Paid Sentry/Valkey unless free fails; #874/#727; #836 UI metrics tab; AMS #958;
    stage→main promote this cycle

## Preset + routing

- Preset: Standard
- Stages (ordered): `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 11`
- Skip: `03`, `06`, `10`, `12`, `13` (unless Redis live proof required)

## Next child stage

**07-build** — M5 docs/CI closeout (T5.1–T5.2); then **08-verify-build**.

## Locked decisions

| ID | Choice |
|----|--------|
| D-S061-redis | **1** — Upstash Redis free |
| D-S061-01-ac | **1** — AC1–AC12 |
| D-S061-route | **1** — Standard |
| D-S061-gateA | **1** — PASS Gate A → 04 |
| D-S061-04-plan | **1** — openapi-typescript; plan as drafted |
| D-S061-gateB | **1** — PASS Gate B → 07 |
| D-S061-cov-branches | **3** — lines/stmts/funcs ≥95; branches → #968 |

## Risks / open decisions

- M5 tip CI must stay green with `openapi:check` + coverage/quality stickies
- Sentry Developer: 1 user, 5k errors/mo — sample/filter under quota
- Vitest branches still waived at 84 (`#968`)
