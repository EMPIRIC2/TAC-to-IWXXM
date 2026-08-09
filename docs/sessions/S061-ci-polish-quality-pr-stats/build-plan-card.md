# Build Plan Card

> Session: S061-ci-polish-quality-pr-stats | Updated: 2026-08-09 | Active: handoff → 08-verify-build

## Goal (one sentence)

Restore ≥95% coverage gates (#950), add quality/golden sticky PR comment #2, and ship free-tier Sentry + Upstash Redis slowapi + openapi-typescript FE types (#900).

## Constraints

- [Corpus: product §F29/F6/F21/F30/M5] [Corpus: tests] [Corpus: adr/ADR-007/006/031]
- Branch: `evolve/EV-052-ci-polish-quality-pr-stats` → PR **`stage`** [#969](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/969)
- Tip CI: https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31330124240 (**success**)
- Locked: Upstash; AC1–AC12; openapi-typescript; `D-S061-cov-branches=3` → [#968](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/968)
- Skip 12/13 unless live Redis multi-replica proof required

## In scope (this batch)

- [x] M1–M5 implementation tasks
- [ ] 08-verify-build → 09-qa → 11-verify-impl (routed)

## Out of scope (explicit)

- Vitest branches ≥95 (tracked #968); paid tiers; #874/#727/#836; AMS #958; stage→main

## Dependencies / blockers

- None for verify path

## Acceptance for this batch

- [x] Tip PR CI green (openapi:check + coverage + quality sticky)
- [ ] 08/09/11 gate digests

## Next Plan prompt

Run **08-verify-build** Phase C gate, then **09-qa** + **11-verify-impl**.
