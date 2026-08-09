# Build Plan Card

> Session: S061-ci-polish-quality-pr-stats | Updated: 2026-08-09 | Active: Phase 1 / M4 / T4.1

## Goal (one sentence)

Restore ≥95% coverage gates (#950), add quality/golden sticky PR comment #2, and ship free-tier Sentry + Upstash Redis slowapi + openapi-typescript FE types (#900).

## Constraints

- [Corpus: product §F29/F6/F21/F30/M5] [Corpus: tests] [Corpus: adr/ADR-007/006/031]
- Branch: `evolve/EV-052-ci-polish-quality-pr-stats` → PR **`stage`** [#969](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/969)
- Locked: Upstash; AC1–AC12; openapi-typescript; `D-S061-cov-branches=3` → [#968](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/968)
- Skip 12/13 unless live Redis multi-replica proof required

## In scope (this batch — M4)

- [ ] T4.1 — Test — generated types exist; openapi:check fails on drift — Spec: TC-EV052-009
- [ ] T4.2 — Config — openapi-typescript + generate/check scripts; commit artifact — Spec: D-S061-orval=1
- [ ] T4.3 — Code — wire FE convert/validate to generated types — Spec: AC9

## Out of scope (explicit)

- Vitest branches ≥95 (tracked #968); paid tiers; #874/#727/#836; AMS #958; stage→main
- M1–M3 — **completed**

## Dependencies / blockers

- Data: none
- Prior: M1–M3 **completed**
- Tooling: 06 skipped

## Acceptance for this batch

- [ ] Committed OpenAPI types; CI drift check
- [ ] High-churn convert/validate use generated types
- [ ] TC-EV052-009

## Next Plan prompt

Approve M4 T4.1–T4.3; Agent runs Task Loop. Then M5 docs/CI closeout.
