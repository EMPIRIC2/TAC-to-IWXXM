# Evolve report — EV-025

| Field | Value |
|-------|-------|
| Cycle | EV-025 |
| Session | S032-iwxxm-us-remarks-va |
| Status | **completed** |
| Started | 2026-07-31 |
| Completed | 2026-07-31 |
| Issues | #810, #811, #812 closed; #809 left open (soft done; equality deferred) |
| PR | [#816](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/816) → `2412312` |
| Deploy smoke | **waived** — T7.3 deferred (`D-S032-EV025-closeout=1`); run when convert/validate ships |

## Scope

Dual-lane: (A) encode all dig ❌ iwxxm-us METAR/SPECI REMARKS types (#810/#811/#812 + adjacent);
(B) #809 WMO `sigmet-multi-location-VA` annex3 golden soft→strict (soft path only this cycle).

## Routing

Lean+build: `00→16→01→02→04→07→08→10` (+13 when ships). Skipped 03/05/06/09/11/12.
13-deploy-smoke waived at close (deferred).

## Results

| Gate | Result |
|------|--------|
| A→B | passed |
| B→C | passed |
| C→D | passed |
| Deploy | waived (T7.3 deferred) |

## Feature deltas

Deepened F6 / F6.b / F12 / F2 / F13 / F23. US REMARKS encode packs shipped. #809 soft-compare
golden + multi-location encode shipped; catalog remains `wmoReference` until ADR-032 equality
(`D-S032-EV025-s02m1-1`). Residual tracked in [Context: va-multi-location-809](context/va-multi-location-809.md).

## Follow-ups

- New cycle: #809 ADR-032 `canonicalize_xml` equality → catalog `wmoPass` (TC-EV025-009 promote)
- T7.3 / 13-deploy-smoke when API convert/validate behavior ships on Render
