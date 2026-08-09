# Build Plan Card

> Session: S061-ci-polish-quality-pr-stats | Updated: 2026-08-09 | Active: Phase 1 / M5 / T5.1

## Goal (one sentence)

Restore ≥95% coverage gates (#950), add quality/golden sticky PR comment #2, and ship free-tier Sentry + Upstash Redis slowapi + openapi-typescript FE types (#900).

## Constraints

- [Corpus: product §F29/F6/F21/F30/M5] [Corpus: tests] [Corpus: adr/ADR-007/006/031]
- Branch: `evolve/EV-052-ci-polish-quality-pr-stats` → PR **`stage`** [#969](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/969)
- Locked: Upstash; AC1–AC12; openapi-typescript; `D-S061-cov-branches=3` → [#968](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/968)
- Skip 12/13 unless live Redis multi-replica proof required

## In scope (this batch — M5)

- [ ] T5.1 — Docs — env/deps/ADR/feature-list/test-plan parity — Spec: TC-EV052-010
- [ ] T5.2 — Tip CI green (coverage + quality comment + OpenAPI check + units) — Spec: TC-EV052-012

## Out of scope (explicit)

- Vitest branches ≥95 (tracked #968); paid tiers; #874/#727/#836; AMS #958; stage→main
- M1–M4 — **completed**

## Dependencies / blockers

- Data: none
- Prior: M1–M4 **completed**
- Tooling: 06 skipped

## Acceptance for this batch

- [ ] Standing docs match implementation
- [ ] Tip PR CI green including `openapi:check`

## Next Plan prompt

Approve M5 T5.1–T5.2; Agent runs Task Loop. Then 08 → 09 → 11.
