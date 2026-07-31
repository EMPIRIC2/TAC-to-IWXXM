# T0.1 — Canonicalize diff themes vs vendor (#809)

**Date**: 2026-07-31  
**Task**: T0.1 · EV-026 / S033  
**Inputs**: vendor `sigmet-multi-location-VA.{tac,xml}` (IWXXM 2025-2); `convert(..., product=SIGMET, profile=annex3)`  
**Verdict**: `canonicalize_xml(ours) != canonicalize_xml(vendor)` — blockers confirmed; maps cleanly to M1 tasks

## Method

1. Convert vendor TAC under annex3 + `2025-2`.
2. Compare `canonicalize_xml` (ADR-032) — not equal.
3. Diff raw XPath fields that survive soft-compare (soft path already green in EV-025).

## Theme → M1 task map

| # | Theme | Observed (ours → vendor) | Task | Locked by |
|---|-------|--------------------------|------|-----------|
| 1 | Calendar / issueTime year-month | `2012-08-10T12:00:00Z` → `2018-07-10T12:00:00Z` (TAC day/hour only) | **T1.2** | S02.M1 |
| 2 | ATS / MWO display stamps | `YUDD FIC` + type `FIC` / `YUSO MWO` → `SHANWICK OCEANIC AREA CONTROL CENTRE` + type `ATCC` / `UK METEOROLOGICAL OFFICE - EXETER` | **T1.2** | S02.M1 |
| 3 | Ring vertex order | Same closed rings; ours follows TAC WI order; vendor uses opposite winding (rings 0/1/3 reverse; ring 2 reordered) | **T1.3** | S02.M2 |
| 4 | Coordinate formatting | Ours `:.4f` (`43.2500`, `42.2833`); vendor two-decimal (`43.25`, `42.28` for N4217) | **T1.3** | S02.M2 |
| 5 | phenomenonTime density | Ours: 4 filled `TimeInstant`s (OBS/FCST × 2 collections). Vendor: 2 filled + 2 `xlink:href` reuse of those instants (`#uuid.…`) | **T1.4** | Context blocker 5 |

## Geometry detail (posList)

| Ring | Ours (token count) | Vendor | Relation |
|------|--------------------|--------|----------|
| 0 OBS loc1 | 6 pts `43.2500…` TAC order | 6 pts `43.25…` | same points, reverse winding + 2dp |
| 1 FCST loc1 | 5 pts | 5 pts | reverse + 2dp |
| 2 OBS loc2 | 5 pts incl. `42.2833` | 5 pts incl. `42.28` | reorder + round |
| 3 FCST loc2 | 5 pts | 5 pts | reverse + 2dp |

Soft gate already asserts equal **count** of `gml:posList` (≥4) — equality needs order + format.

## phenomenonTime detail

| Slot | Ours | Vendor |
|------|------|--------|
| Collection 0 OBS | filled `2012-08-10T12:00:00Z` | filled `2018-07-10T12:00:00Z` |
| Collection 0 FCST | filled `…T18:00:00Z` | filled `…T18:00:00Z` |
| Collection 1 OBS | filled (duplicate instant) | `xlink:href` → OBS uuid |
| Collection 1 FCST | filled (duplicate instant) | `xlink:href` → FCST uuid |

`gml:timePosition` count: ours **5** (includes issueTime) vs vendor **3** (issueTime + 2 phenomenon instants).

## Non-themes (already green — do not re-litigate)

- Root `iwxxm:VolcanicAshSIGMET`
- Dual `analysisCollection` with OBS + `forecastPositionAnalysis`
- Volcano `MT ASHVAL` + FL bands 150/300 and 250/370
- M-xsd / M-sch smoke on convert output

## Encoder touchpoints (for M1)

| Area | Likely code |
|------|-------------|
| Stamps | annex3 SIGMET helper (hardcoded `2012-08` / synthetic ATS–MWO) — stem-scoped override |
| Geometry | `_sigmet_location_analysis_xml` / posList emit in `annex3_products.py` |
| Time refs | phenomenonTime emit — prefer xlink reuse when second collection shares OBS/FCST instants |

## Out of scope (unchanged)

- #810–#812 US REMARKS reopen
- #738 TC SIGMET A6-2
- Default convert API stamp policy beyond this stem (S02.M1)

## Next

**T1.1** — flip TC-EV025-008 to strict `canonicalize_xml` equality (expect red).
