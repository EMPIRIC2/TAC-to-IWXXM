# Build Plan Card

> Cycle: EV-061 | Session: S071-pre-promote-ux-catalog | Updated: 2026-08-19  
> Active: **07-build M5 #1014** — Spec→Build **open** (`D-S071-spec-build=1a`)  
> M1–M4 PR: https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1016 (open → `stage`)

## Goal

Top-level **Lint & validation catalog** nav tab/page listing code, description, level,
and working source hrefs for TAC lint and IWXXM validation. Operator hrefs are verified
landings. Promote held until #1015.

## Constraints

- [Corpus: product §F7] [Corpus: product §F15] [Corpus: journeys §UJ-068]
  [Corpus: tests §TC-EV061-1014] [Corpus: api]
- Additive fields + IWXXM rows on existing `GET /lint-issue-catalog` — **no** new route
- No new deps / ADR / CORS origins
- No planning ids in OpenAPI or operator copy (EV-048)
- Source policy `D-S071-links-resolve`: operator hrefs = verified landings

## In scope (this batch — M5)

- [ ] T5.1 — Test — Red: tab/page lists code, description, level, working source hrefs — Spec: UJ-068 F7.v/F15
- [ ] T5.2 — Code — Additive catalog fields + IWXXM validation rows on `GET /lint-issue-catalog` — Spec: [Corpus: api] D-S071-api
- [ ] T5.3 — Code — Top-level nav tab/page; operator hrefs = verified landings — Spec: mining note
- [ ] T5.4 — Docs — OpenAPI aliases for additive catalog fields; no planning ids in attribution — Spec: EV-048

## Out of scope (explicit)

#1010–#1013 (M1–M4 done); #1015 promote gate; #996 click-for-detail

## Parallelism

T5.1 → T5.2 → T5.3 → T5.4 (TDD)

## Verify / PR

08-verify-build M5 after T5.4; stack on PR #1016 to `stage`.

## Gate

Spec→Build **open** (`D-S071-spec-build=1a`).
