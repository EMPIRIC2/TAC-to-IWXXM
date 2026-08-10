# Evolve Plan Card

> Cycle: EV-053 | Session: S062-vitest-branches-95 | Updated: 2026-08-10T15:40:40Z

## Goal

Raise Vitest `branches` to ≥95% (FileConverter-heavy) and close the explicit
`D-S061-cov-branches` waiver tracked by [#968](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/968).

## Features

- F29 — deepen (quality / coverage honesty) — [Corpus: product §F29]
- M5 — deepen (workspace Vitest gates) — [Corpus: product §M5]
- No new Fn

## In / out of scope

- In: `vitest.config.ts` branches ≥95; FileConverter branch tests and/or justified
  excludes; coverage inventory `branch_waiver` → resolved; decisions + test-plan cites
- Out: lowering other thresholds; #874/#727/#836; Sentry/Redis/openapi; stage→main;
  operator UI redesign

## Preset + routing

- Preset: **Standard** (`D-S062-route=1`)
- Stages (ordered): `00 → 16 → 01 → 02 → 04 → 07 → 08 → 09 → 11`
- Skipped: `03`, `05`, `06`, `10`, `12`, `13`

## Next child stage

**01-requirements** (delta) — lock AC + FileConverter include/exclude strategy after
Phase 0–1 proceed gate.

## Risks / open decisions

- Re-including `FileConverter.tsx` in coverage may need a large test campaign (~144
  branch misses historically)
- Alternative: keep exclude + raise aggregate branches another way — must stay honest
  (no silent soft gate) per [Corpus: adr/ADR-007] / #968

## Locked decisions

| ID | Choice |
|----|--------|
| D-S062-route | 1 — Standard |
| D-S062-ui-preview | 2 — no local UI preview |
| D-S062-dirty | 2 — #972 already on stage |
