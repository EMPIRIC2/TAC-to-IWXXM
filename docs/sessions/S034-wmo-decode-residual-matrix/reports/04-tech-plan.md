# 04-tech-plan — S034 / EV-027

**Date**: 2026-07-31  
**Mode**: delta  
**Issue**: #815  
**Status**: **completed** — Gate B approved (`D-S034-04-plan-approve`)

## Inputs

- Gate A PASS (`D-S034-02-phase-a`) — Batch F **1, 2, 1**
- Context: `docs/context/wmo-decode-residual-matrix.md`
- Policies: S02.M1/M2/L1; E27-4 triage; F9 G4 / ADR-025 intentional residuals

## Architecture (delta)

No new packages, routes, or deps expected.

| Area | Change |
|------|--------|
| `packages/tac2iwxxm` | Inventory discovery helper; residual matrix tests; allowlist artifact; decode coverage fixes |
| FE catalog | Register missing stems or FIXTURE_GAPS + children; Vitest completeness |
| Docs | Child issues for doc-intentional / deferred residuals |

ADR-025 / ADR-032 unchanged (apply residual naming + catalog tiers).

## Connectivity

No new CORS / origin map. Same decode-tac + static catalog as UJ-039/UJ-020.
H4–H5 via TC-EV027-005 only when FE ships (13).

## Approved plan

See `execution-plan.md` — M0 dig → **M1 catalog first** → M2 residual matrix → M3 verify/close.
14 tasks (T0.1–T3.4). **E27-T1=2** catalog-before-matrix.

## Batch T + Gate B

| ID | Lock |
|----|------|
| E27-T1..T5 | **2,1,2,1,1** |
| Gate B | **1** — approve plan → **07-build** @ T0.1 |
