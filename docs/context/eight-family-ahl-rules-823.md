# Scoped context — eight-family-ahl-rules-823 (S036 / EV-029)

**Mode:** scoped · **Date:** 2026-08-01  
**Session:** S036-eight-family-ahl-rules-823 · **Cycle:** EV-029  
**Issue:** [#823](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/823) (umbrella)

## Problem

External review + #823 confirm the eight-family TAC→IWXXM product set, with **three distinct
SIGMET IWXXM roots** (general / VA / TC), plus concrete gaps in:

1. **AHL / bulletin framing** — splitter, `T1T2` TAC↔IWXXM map, BBB→`reportStatus`, COLLECT
2. **Encode correctness** — VAA/TCA multi-report, nil reasons, forecast cardinality (vs GIFTs gaps)
3. **Three-SIGMET family** — especially TC SIGMET (#738 still open)
4. **SWXA** — mining notes exist; no dedicated quality Fn row yet (#740)
5. **Coverage matrix / examples** — not yet proven 1-by-1 across lint · convert · IWXXM validate
   for all TAC input shapes (standalone / AHL / multi-report)

## Runtime SoT

`vendor/manifest.json` → IWXXM **2025-2**. Prefer `schemas.wmo.int` + vendor pin over Doc 10003
(2019) / GIFTs where they diverge (ADR-014).

## Product × AHL map (from #823 B1)

| Product | TAC `T1T2` | IWXXM `T1T2` | IWXXM root |
|---------|-----------:|-------------:|------------|
| METAR | SA | LA | `iwxxm:METAR` |
| SPECI | SP | LP | `iwxxm:SPECI` |
| TAF &lt;12h | FC | LC | `iwxxm:TAF` |
| TAF ≥12h | FT | LT | `iwxxm:TAF` |
| General SIGMET | WS | LS | `iwxxm:SIGMET` |
| TC SIGMET | WC | LY | `iwxxm:TropicalCycloneSIGMET` |
| VA SIGMET | WV | LV | `iwxxm:VolcanicAshSIGMET` |
| AIRMET | WA | LW | `iwxxm:AIRMET` |
| VAA | FV | LU | `iwxxm:VolcanicAshAdvisory` |
| TCA | FK | LK | `iwxxm:TropicalCycloneAdvisory` |
| SWXA | FN | LN | `iwxxm:SpaceWeatherAdvisory` |

## Prior art (do not restart)

| Artifact | Use |
|----------|-----|
| `docs/domain/TAC_VALIDATION.md` | Lint rules SoT |
| `docs/domain/IWXXM_CONVERSION.md` | Encode rules SoT |
| `docs/domain/IWXXM_VALIDATION.md` | XSD/SCH rules SoT |
| `docs/domain/rules/COVERAGE_MATRIX.md` | Gap cells |
| `docs/domain/mining/*` | S031/EV-024 + product mining notes |
| #823 body + addendum COM-### rule inventory | Machine-oriented rule IDs to promote |
| F15/F20/F23/F24/F25/F26/F27 | Prior quality bars — deepen, don't re-litigate |

## Out of converter scope

WAFS SIGWX · VONA · QVACI (structured/digital origins; not legacy TAC converter inputs).

## Success

1. Phase A: coverage matrix + canonicals + example inventory have no silent gaps for the eight
   families × three roles × report states × TAC input shapes (cells filled or child-issued).
2. Phase B: engines implement promoted rules in product order; CI green; child issues for residuals.
3. Shared AHL/`T1T2`/filename model usable by `tac2iwxxm` and dissemination (no sink UI).
)
