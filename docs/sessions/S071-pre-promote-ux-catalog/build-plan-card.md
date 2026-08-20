# Build Plan Card

> Cycle: EV-061 | Session: S071-pre-promote-ux-catalog | Updated: 2026-08-20  
> Active: **07-build M6 #1015** — Spec→Build **open** (`D-S071-spec-build=1a`)  
> M1–M5 PR: https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1016 (open → `stage`)

## Goal

Stricter **stage→main** promote gate: required checks include full unit, lint, typecheck,
and full Playwright E2E (not smoke-only), plus Staging gate. Document in deploy.md.

## Constraints

- [Corpus: product §F34] [Corpus: journeys §UJ-DEV-009] [Corpus: deploy]
  [Corpus: tests §TC-EV061-1015] [Corpus: tech-spec]
- Restore lint/typecheck as CI jobs on promote PRs (`D-S071-ci`)
- No new product deps / ADR / CORS origins
- Branch protection may need maintainer admin

## In scope (this batch — M6)

- [ ] T6.1 — Test/Docs — Inventory current required checks vs target set — Spec: UJ-DEV-009 deploy.md
- [ ] T6.2 — Config — CI jobs: lint + typecheck + full Playwright E2E on promote PRs — Spec: D-S071-ci
- [ ] T6.3 — Docs — deploy.md + promote PR template; branch-protection runbook — Spec: [Corpus: deploy]

## Out of scope (explicit)

#1010–#1014 (M1–M5 done); live H4–H5 (12/13)

## Parallelism

T6.1 → T6.2 → T6.3

## Verify / PR

08-verify-build M6 after T6.3; stack on PR #1016 to `stage`. Promote held until #1015 lands.

## Gate

Spec→Build **open** (`D-S071-spec-build=1a`).
