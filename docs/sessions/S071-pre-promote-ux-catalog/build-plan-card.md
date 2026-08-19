# Build Plan Card

> Cycle: EV-061 | Session: S071-pre-promote-ux-catalog | Updated: 2026-08-19  
> Active: **07-build M4 #1013** — Spec→Build **open** (`D-S071-spec-build=1a`)  
> M1–M3 PR: https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1016 (open → `stage`)

## Goal

Product Type + Profile stay on one polished bar without wrap at ≥1024px; mode selects
and conversion parameters each share one aligned bar/row; stacking OK below 1024px.
Keyboard labels preserved. Promote held until #1015.

## Constraints

- [Corpus: product §F7] [Corpus: journeys §UJ-066] [Corpus: journeys §UJ-067]
  [Corpus: tests §TC-EV061-1013]
- Layout only — no HTTP change (`docs/api-contract.md` FE Product/Profile bars)
- No new deps / ADR / CORS origins
- Preserve accessible names: Product, Profile, Input mode, Expand/Collapse parameters

## In scope (this batch — M4)

- [ ] T4.1 — Test — Red: no-wrap ≥1024px; stack below; a11y labels — Spec: UJ-066/067 F7.u
- [ ] T4.2 — Code — Product Type + Profile one bar; mode selects one row; params one row — Spec: feature-list F7.u

## Out of scope (explicit)

#1010/#1011/#1012 (M1–M3 done); #1014 catalog; #1015 promote gate

## Parallelism

T4.1 → T4.2 (TDD)

## Verify / PR

08-verify-build M4 after T4.2; stack on PR #1016 to `stage`.

## Gate

Spec→Build **open** (`D-S071-spec-build=1a`).
