# Build Plan Card

> Cycle: EV-060 | Session: S070-converter-operator-bugs | Updated: 2026-08-18
> Active: Build / M2 T2.1–T2.4 complete — next 08-verify-build then PR #1003

## Goal

Ship epic #1000 children to `stage` in four PRs. This batch: M2 IWXXM product pass-through (#1003 / F7.t).

## Constraints

- [Corpus: product §F7] [Corpus: product §F2] [Corpus: api] [Corpus: tests]
- Branch `evolve/EV-060-converter-operator-bugs` → PRs to `stage`; promote held
- No new deps / ADR / CORS origins
- Keep F7.s Validate-only (`validate_iwxxm` mode)

## In scope (this batch)

- [x] T2.1 — Test — Red product=iwxxm XML vs TAC text — Spec: [Corpus: tests §TC-EV060-1003]
- [x] T2.2 — Code — Additive enum `iwxxm`; convert no-op; lint XML; OpenAPI — Spec: [Corpus: api]
- [x] T2.3 — Code — FE product select + Convert disabled/no-op copy — Spec: [Corpus: product §F7]
- [x] T2.4 — Code — FileConverter / accumulate / QM honor — Spec: [Corpus: product §F7]

## Out of scope (explicit)

#933/#924; #912; F16–F19; F8 auto-push; promote; M3–M4 this batch; merge #1007 without user OK

## Parallelism

T2.1 then T2.2 (TDD). T2.3 after T2.2. T2.4 with T2.3 (shared FE).

## Verify / PR

08-verify-build M2 after T2.1–T2.4 (this batch); PR → `stage` for #1003 (may stack on #1007 tip).

## Gate

Spec→Build **open** (`D-S070-spec-build=1a`).
