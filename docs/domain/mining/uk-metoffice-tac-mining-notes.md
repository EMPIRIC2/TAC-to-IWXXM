# UK Met Office / CAA TAC mining notes (transitory)

> **Profile**: `UK_METOFFICE` · **Cycle**: EV-094 / [#1098](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1098) (prior EV-089 / #920 closed)  
> **Not SoT** — promote durable rows into [Corpus: domain-profiles] / RULE_SOURCE_URLS.

## Sources triaged

| URL | Access | Proves |
|-----|--------|--------|
| https://www.caa.co.uk/our-work/publications/documents/content/cap746/ | public | CAP 746 aerodrome MET observations |
| https://www.metoffice.gov.uk/services/transport/aviation | public | UK aviation MET context |
| https://aviationweather.gov/api/data/metar?ids=EGLL&format=raw | public | Attributed EGLL METAR corpus (M1) |
| https://aviationweather.gov/api/data/taf?ids=EGLL&format=raw | public | Attributed EGLL TAF corpus (M1) |
| Session research | — | `EV-094…/evidence/deep-research-report-deepen.md` |

## Fixture harvest (EV-094 M1)

| Product | Station | observed_at_utc | source_kind | Notes |
|---------|---------|-----------------|-------------|-------|
| METAR | EGLL | 2026-08-31T13:50:00Z | official (AWC API) | Replaces EV-089 synthetic |
| TAF | EGLL | 2026-08-31T10:55:00Z | official (AWC API) | Complete body (research snippet was truncated) |
| SPECI | EGLL | — | `synthetic_ev089` | **Gap** — no attributed real SPECI in harvest |

## Rule stubs

| rule_id | Product | Summary | confidence |
|---------|---------|---------|------------|
| UK.BASE.ICAO | METAR/SPECI/TAF | Treat as ICAO_2025 unless CAP 746 delta attested | med |

## Overrides

Empty — civil ICAO path; military colour-state OOS (D-EV094-uk-mil). Wind-shear reporting absent on UK civil METAR is not an override (feature unused).

## Emit notes

- Thin path: core IWXXM only; no UK XSD.
- Convert allowlist unchanged: METAR, SPECI, TAF.

## Next promote

1. Harvest attributed real SPECI (close catalog gap)
2. Flip catalog `status` → `implemented` when pack AC met (#1098)
3. Promote any CAP 746 deltas into RULE_SOURCE_URLS when attested
