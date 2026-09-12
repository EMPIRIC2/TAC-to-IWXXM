# 04-tech-plan — S033 / EV-026

**Date**: 2026-07-31  
**Mode**: delta  
**Issue**: #809  
**Status**: **completed** — Gate B approved (`D-S033-04-plan-approve`)

## Inputs

- Gate A PASS (`D-S033-02-phase-a`) — Batch F 1,1,1
- Context: `docs/context/va-multi-location-809.md`
- Soft path: EV-025 / #816

## Architecture (delta)

No new packages, routes, or deps expected. Encoder deltas in
`packages/tac2iwxxm` (annex3 SIGMET/VA path) + frontend catalog tier flip
(`examplesCatalog.ts` / FIXTURE_GAPS / Vitest). ADR-032 unchanged (apply equality).

## Connectivity

No new CORS / origin map. Catalog Vitest only; H4–H5 only if 13 ships FE.

## Approved plan

See `execution-plan.md` — M0 dig → M1 red/encoder/green → M2 catalog → M3 verify/close.
12 tasks (T0.1–T3.4).

## Batch T + Gate B

| ID | Lock |
|----|------|
| E26-T1..T5 | **1,1,2,1,1** |
| Gate B | **1** — approve plan → **07-build** @ T0.1 |
