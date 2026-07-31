# Validate / CI wire — S031 / EV-024 (M6 / TC-EV024-007)

**Date**: 2026-07-30  
**Pin**: IWXXM **v2025-2** examples under vendor

## Wired

| Surface | Coverage |
|---------|----------|
| `WMOExamplesLoader` + `test_wmo_canonical_examples` | All mirrored XML: well-formed, XSD, GML (SCH soft-skip platform-wide) |
| `test_ev024_in_scope_stems_loaded_with_tac` | Explicit inventory of product-in-scope TAC↔XML stems |
| Frontend catalog (M5) | `wmoPass` + `wmoReference` (VA-EGGX, multi-location-VA) |

## In-scope stems (asserted)

`metar-A3-1` · `speci-A3-2` · `taf-A5-1` · `taf-A5-2` · `sigmet-A6-1a-TS` ·
`sigmet-A6-1b-CNL` · `sigmet-VA-EGGX` · `sigmet-multi-location-VA` · `airmet-A6-1a-TS` ·
`va-advisory-A7-2` · `tc-advisory-A2-2`

## Convert soft-compare deferred (child issues)

| Stem | Reason | Ticket |
|------|--------|--------|
| `sigmet-multi-location-VA` | No annex3 M-golden / equality pack this cycle | *filed in T7.1* |
| `sigmet-A6-2-TC` | Quality bar OOS sample menu | #738 |
| SWX / VONA / WAFS / QVACI | Roadmap (S02.M2) | #740 / #741 |

## Not wired as happy-path

- `*-translation-failed*` — quarantine (#800)
- NIL-collect — validate shape only
- US iwxxm-us examples — never in WMO catalog
