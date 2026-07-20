---
session_id: S018-metar-remarks-667
type: feature
status: completed
branch: cursor/metar-remarks-live-e2e-2e2e
started_at: 2026-07-20
completed_at: 2026-07-20
intent: "Handle Remark Portion of METARs (#667)"
orchestrator: 16-evolve
evolve_cycle_id: EV-013
close_note: "User Q0=A waived leftover verify bookkeeping to start upload/dissemination evolve (#729/#2/#6); EV-013 closed; #750 remarks live"
context_briefs:
  - docs/context/metar-remarks-667.md
standing_docs_touched:
  - docs/user-journeys.md
  - docs/feature-list.md
  - docs/test-plan.md
---

# Session S018 — metar-remarks-667

## Intent

Close [GitHub #667](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/667): METAR/SPECI
`RMK` must not be silently ignored — retain/process where possible, or clearly state exclusion.

## Intake decisions (Phase 0 — Assumed; AskQuestion UI waived)

| ID | Decision |
|----|----------|
| E13-1 | Dual bar: `annex3` → `REMARKS_EXCLUDED` ConvertIssue; `iwxxm_us` → keep AO2/SLP/PK WND + never-drop remainder via `humanReadableText`; parse T/P into IR (free-text emit; no invented NWS URIs for processedQuantity) |
| E13-2 | Routing **Standard** (needs 07-build): 00→16→01→02→04→07→08→09→11→12→13; skip 03/05/06/10 |
| E13-3 | No new Fn — deepen **F6** |

## Scope

### In

- `packages/tac2iwxxm` METAR/SPECI parse + convert issues + `iwxxm_us` Addendum emit
- Unit tests / bug-style regression for #667
- Corpus deltas: UJ + feature-list note + test-plan row

### Out

- Full FMH-1 remark catalog (WSHFT, PRESRR, snow, `$` structured, etc.)
- Invented `codes.nws.noaa.gov` concept URIs for processedQuantity
- Non-METAR/SPECI products; FE redesign

## Feature mapping

| Fn | Role |
|----|------|
| **F6** (deepen) | Remark retain / exclusion messaging |

## Links

- Issue: [#667](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/667)
- Prior: S008 F6 US REMARKS; S015 R5 lint (closed)
- Schema: `vendor/schemas/iwxxm-us/3.0/metarSpeci.xsd` Addendum.humanReadableText
