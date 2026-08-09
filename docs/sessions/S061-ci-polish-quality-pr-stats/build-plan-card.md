# Build Plan Card

> Session: S061-ci-polish-quality-pr-stats | Updated: 2026-08-09 | Active: Phase 1 / M2 / T2.1

## Goal (one sentence)

Restore ≥95% coverage gates (#950), add quality/golden sticky PR comment #2, and ship free-tier Sentry + Upstash Redis slowapi + openapi-typescript FE types (#900).

## Constraints

- [Corpus: product §F29/F6/F21/F30/M5] [Corpus: tests] [Corpus: adr/ADR-007/006/031]
- Branch: `evolve/EV-052-ci-polish-quality-pr-stats` → PR **`stage`** (not main)
- Locked: Upstash; AC1–AC12; openapi-typescript; `D-S061-cov-branches=3` → [#968](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/968)
- Skip 12/13 unless live Redis multi-replica proof required

## In scope (this batch — M2)

- [ ] T2.1 — Test — quality stats aggregator + markdown formatter — Spec: TC-EV052-005
- [ ] T2.2 — Code — `format_quality_pr_comment.py` + sticky marker — Spec: AC4
- [ ] T2.3 — Config — `quality-pr-comment` job in ci-cd.yml — Spec: TC-EV052-004
- [ ] T2.4 — Test/Docs — sticky idempotence parity — Spec: AC5

## Out of scope (explicit)

- Vitest branches ≥95 (tracked #968); paid tiers; #874/#727/#836; AMS #958; stage→main

## Dependencies / blockers

- Data: none
- Prior: M1 T1.1–T1.5 **completed**
- Tooling: 06 skipped

## Acceptance for this batch

- [ ] Second sticky PR comment with match/soft-diff/fail/skip × product × profile
- [ ] Formatter unit-tested; update-in-place sticky
- [ ] TC-EV052-004..005

## Next Plan prompt

Approve M2 T2.1–T2.4; Agent runs Task Loop. Then M3 Sentry+Redis.
