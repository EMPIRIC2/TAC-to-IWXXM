# ADR-019: Mark F6 and F8 Implemented after S008 11-verify-impl

> **Status**: Accepted  
> **Date**: 2026-07-12  
> **Deciders**: User (S008 11-verify-impl scope AskQuestion option 1)  
> **Stage**: 11-verify-impl  
> **Related**: ADR-013, ADR-014, ADR-017, ADR-018; feature-list.md  
> **Session**: S008-general-tac-iwxxm-converter / EV-006  
> **Decision id**: D-S008-11-scope-f6-f8-status

## Context

S008 build completed F6 (`tac2iwxxm` cutover + UI/API product/profile) and F8 (`apps/worker`
ingest). User journey and feature sign-off in 11-verify-impl approved F6, F2, and F8 with
documented live-connectivity waivers (routing skips 12-verify-deploy / 13-deploy-smoke).
`docs/feature-list.md` still listed F6 and F8 as **Planned**.

## Decision

1. Set **F6** and **F8** summary status to **Implemented**.
2. Leave **F7** as **Planned** (not built this cycle).
3. Do **not** bulk-refresh M1–M6 summary rows in this decision (option 2 declined).
4. Record live H4–H7 / T7.4 as deferred caveats under F6/F8 detail sections — not blocking
   Implemented for this build+verify cycle.

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | Leave Planned until live H4–H7 pass | User chose corpus status update now |
| 2 | Also refresh all M1–M6 statuses | User selected F6/F8-only update |
| 3 | Use Experimental until staging smoke | User approved Implemented with live deferred notes |

## Consequences

- Corpus parity: product feature list matches S008 verification outcome.
- Deploy/live gates remain open work (EV-006 `gates.deploy` pending; 12/13 skipped).
- Future session may promote live caveats to closed after H4–H7 / T7.4 green.
