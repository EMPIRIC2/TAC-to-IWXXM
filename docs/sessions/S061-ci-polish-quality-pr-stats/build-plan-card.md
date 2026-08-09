# Build Plan Card

> Session: S061-ci-polish-quality-pr-stats | Updated: 2026-08-09 | Active: Phase 1 / M3 / T3.1

## Goal (one sentence)

Restore ≥95% coverage gates (#950), add quality/golden sticky PR comment #2, and ship free-tier Sentry + Upstash Redis slowapi + openapi-typescript FE types (#900).

## Constraints

- [Corpus: product §F29/F6/F21/F30/M5] [Corpus: tests] [Corpus: adr/ADR-007/006/031]
- Branch: `evolve/EV-052-ci-polish-quality-pr-stats` → PR **`stage`** (not main)
- Locked: Upstash; AC1–AC12; openapi-typescript; `D-S061-cov-branches=3` → [#968](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/968)
- Skip 12/13 unless live Redis multi-replica proof required

## In scope (this batch — M3)

- [ ] T3.1 — Test — Sentry no-op when DSN unset; init when set — Spec: TC-EV052-006
- [ ] T3.2 — Code — wire sentry-sdk / @sentry/react behind env — Spec: AC6
- [ ] T3.3 — Test — slowapi Redis when REDIS_URL; fakeredis — Spec: TC-EV052-007..008
- [ ] T3.4 — Code — create_limiter() Redis storage URI — Spec: AC7; ADR-031
- [ ] T3.5 — Docs — env-contract / infra-free-tier secret stubs — Spec: AC11

## Out of scope (explicit)

- Vitest branches ≥95 (tracked #968); paid tiers; #874/#727/#836; AMS #958; stage→main
- M2 quality sticky (T2.1–T2.4) — **completed**

## Dependencies / blockers

- Data: none
- Prior: M1 + M2 **completed**
- Tooling: 06 skipped

## Acceptance for this batch

- [ ] Optional Sentry init; no-op without DSN
- [ ] Upstash/REDIS_URL shared slowapi; memory fallback when unset
- [ ] TC-EV052-006..008, TC-EV052-011

## Next Plan prompt

Approve M3 T3.1–T3.5; Agent runs Task Loop. Then M4 openapi-typescript.
