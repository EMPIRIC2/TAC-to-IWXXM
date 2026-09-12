# METAR research catalog — S015 / EV-011

> Seeded in 01-requirements (E11-6). Cite external sources; do not copy paywalled Annex 3 prose
> into wheels. Implementation maps themes → registry codes in 07-build.

## Sources

| Source | Role |
|--------|------|
| [MetarCentral — How to Read METAR](https://metarcentral.com/learn/how-to-read-metar) | Field checklist + RMK examples |
| [AviationRef METAR decoder](https://www.aviationref.com/metar-decoder) | Sample TAC set; decode UX patterns |
| [moryakovdv/iwxxmConverter](https://github.com/moryakovdv/iwxxmConverter) | Convert IR → JAXB → Schematron; RMK still TODO upstream |
| [FlightPlanDatabase FMS](https://flightplandatabase.com/dev/specification) | **Excluded** — not METAR |

## Themes → work items

| ID | Theme | Lint (F12/F15) | Convert (F6) | Validate |
|----|-------|----------------|--------------|----------|
| R1 | Station / time / field order | ERROR missing CCCC/DDHHMMZ; WARNING odd order | Emit correctly | — |
| R2 | Visibility SM vs meters / fractions / 9999 | Dialect checks | Correct units in IWXXM | XSD units |
| R3 | Weather phenomena grammar | Invalid intensity/descriptor combos | wx codes → IWXXM | SCH where applicable |
| R4 | Clouds / CAVOK / VV / CB/TCU | Coverage + height rules; INFO for CB/TCU | Cloud layers | SCH |
| R5 | Remarks (AO1/AO2, SLP, P, T, PK WND) | INFO/WARNING for known RMK; ERROR malformed | `iwxxm_us` extensions | US schema |
| R6 | Golden convert + SCH round-trip | — | Expand product_matrix goldens | M-xsd / M-sch CI |
| R7 | METAR↔SPECI adjacency | Product hint / Auto-detect; shared rule pack; no silent cross-product pass | Same `metarSpeci` path; SPECI goldens | M-xsd/M-sch for SPECI |
| R8 | AUTO / COR / NIL / NOSIG / TEMPO / RVR / wind VRB·gust | Registry code + accept/negative each (**HARD** — E11-28) | Match Annex-3 / US where fixtures allow | As fixtures allow |

## Sample TAC seeds (from public decoder pages — for fixtures, not copyright claims)

International-style and US-style examples from AviationRef / MetarCentral guides should be
adapted into `packages/*/tests/fixtures/` with expected registry codes and golden XML where
conversion is in scope. Prefer short synthetic cases over long copied pages.
