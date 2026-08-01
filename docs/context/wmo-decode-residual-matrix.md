# Context — Official WMO decode residual matrix (#815)

**Session:** S034-wmo-decode-residual-matrix · **Cycle:** EV-027  
**Mode:** scoped · **Date:** 2026-07-31

## Problem

Sample menu + catalog work (EV-024 / UJ-039 / #804) made official stems **loadable**, but CI
does not yet assert **decode residual emptiness** across the full official TAC corpus.
Unexpected `"Not decoded: …"` on textbook WMO examples erodes operator trust.

## Issue SoT

[#815](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/815) — Quality: official WMO IWXXM TAC
examples load cleanly with no unexpected decode residuals.

## Feature / journey map

| Item | Ref |
|------|-----|
| Features | **F25 deepen**, **F9 deepen**, **F7.g deepen** (no new Fn proposed) |
| Journeys | UJ-039, UJ-036; deepen UJ-020 / decode residual clauses |
| ADR | ADR-032 (catalog tiers); ADR-025 (decode-tac / summary) |
| Prior | #780, #702, #804, S029 (parked), `FIXTURE_GAPS.md`, `test_tc_f9_sigmet_a6_decode_residuals.py`, BUG-2026-07-30 |

## Products in scope

METAR, SPECI, TAF, SIGMET, AIRMET, VAA, TCA (F6 seven). Deferred products stay out unless
already catalogued.

## Catalog snapshot (current `FIXTURE_GAPS`)

| Product | Catalog TAC count | Noted gaps |
|---------|-------------------|------------|
| METAR | 1 | Second WMO METAR — none in pin |
| SPECI | 1 | Second WMO SPECI — none in pin |
| TAF | 2 | none |
| SIGMET | 4 | TC A6-2 deferred (#738); multi-location-VA now passer |
| AIRMET | 1 | CNL peer — none in pin |
| VAA | 1 | Second — none in pin |
| TCA | 1 | Second — none in pin |

## Suggested first steps (from #815)

1. Diff vendor pin TAC peers vs `examplesCatalog.ts` + package annex3 fixtures
2. Run decode over the union; dump residual text per stem
3. Triage: fix coverage vs expected-allowlist vs child issue
4. Lock the matrix in CI before closing

## Non-goals

Encode equality promotion; IWXXM-US in WMO menu; inventing TAC; new products beyond F6 seven.

## UI surfaces

Workbench sample menu + F9 decode panel residual chrome — optional H4–H5 / local preview.
