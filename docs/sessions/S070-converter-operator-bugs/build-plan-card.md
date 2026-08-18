# Build Plan Card

> Cycle: EV-060 | Session: S070-converter-operator-bugs | Updated: 2026-08-18
> Active: Build / M4 T4.1–T4.3 — Auth UAT (#1006)

## Goal

Ship epic #1000 children to `stage`. This batch: M4 Auth register/login/logout/persist UAT (#1006). Guest convert (F21) must keep working.

## Constraints

- [Corpus: product §F31] [Corpus: product §F21] [Corpus: journeys] [Corpus: tests §TC-EV060-1006]
- Branch `evolve/EV-060-converter-operator-bugs` → PRs to `stage`; promote held
- No new deps / ADR / CORS origins / auth providers
- Keep F7.s Validate-only; not #933 profile editor

## In scope (this batch)

- [x] T4.1 — Test — Playwright register/login/logout/persist — Spec: [Corpus: tests §TC-EV060-1006-001..003]
- [x] T4.2 — UAT — Facilitated uat Build checklist — Spec: [Corpus: tests §TC-EV060-1006-004]
- [x] T4.3 — Verify — Guest convert still works (F21) — Spec: UJ-001

## Out of scope (explicit)

#933/#924; #912; F16–F19; F8 auto-push; promote; merge #1007 without user OK

## Parallelism

T4.1 → T4.2 → T4.3. T4.3 can share Playwright with T4.1 guest session.

## Verify / PR

08-verify-build M4 after T4.1–T4.3; stack on PR #1007 (M1–M3 already on this branch) unless split.

## Gate

Spec→Build **open** (`D-S070-spec-build=1a`).
