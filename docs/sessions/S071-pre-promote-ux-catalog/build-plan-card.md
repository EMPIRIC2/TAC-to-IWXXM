# Build Plan Card

> Cycle: EV-061 | Session: S071-pre-promote-ux-catalog | Updated: 2026-08-19  
> Active: **08-verify-build M3 #1010** — Spec→Build **open** (`D-S071-spec-build=1a`)  
> M1+M2+M3 PR: https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1016 (open → `stage`)

## Goal

Validate IWXXM shows item-by-item F9 decode rows (not a raw dump) when decode exists;
keep F7.s / F7.t. Promote held until #1015.

## Constraints

- [Corpus: product §F2] [Corpus: product §F7] [Corpus: product §F9] [Corpus: api]
  [Corpus: tests §TC-EV061-1010] [Corpus: journeys §UJ-064]
- Additive optional `segments`/`summary` on `/validate` **or** FE maps existing decode
- No new deps / ADR / CORS origins
- Keep F7.s Validate-only and F7.t IWXXM product pass-through

## In scope (this batch — M3)

- [x] T3.1 — Test — Red: validate IWXXM shows item-by-item rows not raw dump — Spec: UJ-064 F9/F2
- [x] T3.2 — Code — Additive optional `segments`/`summary` on `/validate` (F9 shape) or FE maps existing decode — Spec: [Corpus: api] D-S071-api
- [x] T3.3 — Code — FE decode panel parity; keep F7.s / F7.t — Spec: [Corpus: product §F7]

## Out of scope (explicit)

#1011/#1012 (M1–M2 done); #1013 bars; #1014 catalog; #1015 promote gate

## Parallelism

T3.1 → T3.2 → T3.3 (TDD) — complete.

## Verify / PR

08-verify-build M3 next; stack on PR #1016 to `stage`.

## Gate

Spec→Build **open** (`D-S071-spec-build=1a`).
