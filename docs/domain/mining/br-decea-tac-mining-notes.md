# BR DECEA TAC mining notes (transitory)

> **Profile**: `BR_DECEA` · **Cycle**: EV-094 / [#1098](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1098) (prior EV-089 / #920 closed)

## Sources triaged

| URL | Access | Proves |
|-----|--------|--------|
| https://aisweb.decea.mil.br/ | public | Brazilian AIS / AIP access |
| https://www2.anac.gov.br/ | public | ANAC institutional context |
| https://aviationweather.gov/api/data/metar?ids=SBGR&format=raw | public | Attributed SBGR METAR (M2) |
| https://aviationweather.gov/api/data/taf?ids=SBGR&format=raw | public | Attributed SBGR TAF (M2) |
| Session research | — | `EV-094…/evidence/deep-research-report-deepen.md` (AISWEB SBGR samples) |

## Fixture harvest (EV-094 M2)

| Product | Station / FIR | observed_at_utc | source_kind | Notes |
|---------|---------------|-----------------|-------------|-------|
| METAR | SBGR | 2026-08-31T15:00:00Z | official (AWC API) | Replaces EV-089 synthetic |
| TAF | SBGR | 2026-08-31T09:00:00Z | official (AWC API) | Replaces EV-089 synthetic |
| SPECI | SBGR | — | `synthetic_ev089` | Gap |
| SIGMET | — | — | `synthetic_ev089` | Gap — Brazilian FIR corpus pending |
| AIRMET | — | — | `synthetic_ev089` | Gap |
| GAMET | SBBR / SBAO | — | `synthetic_ev089` | **parse-only** (D-EV094-gamet) |

## Rule stubs

| rule_id | Product | Summary | confidence |
|---------|---------|---------|------------|
| BR.BASE.ICAO | METAR/SPECI/TAF/SIGMET/AIRMET | ICAO_2025 emit | med |
| BR.GAMET.PARSE | GAMET | Fixture/parse-only — no IWXXM (D-EV094-gamet) | high |

## Overrides

Empty — Annex 3 path (D-EV094-fixtures).

## Emit notes

- SAM packaging → #921 / `CAR_SAM` note only.
- No BR national XSD.

## Next promote

1. Harvest attributed SPECI + Brazilian FIR SIGMET/AIRMET
2. Flip catalog `status` → `implemented` when pack AC met
