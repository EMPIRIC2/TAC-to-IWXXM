# UK Met Office / CAA TAC mining notes (transitory)

> **Profile**: `UK_METOFFICE` · **Cycle**: EV-089 · **Issue**: [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920)  
> **Not SoT** — promote durable rows into [Corpus: domain-profiles] / RULE_SOURCE_URLS.

## Sources triaged

| URL | Access | Proves |
|-----|--------|--------|
| https://www.caa.co.uk/our-work/publications/documents/content/cap746/ | public | CAP 746 aerodrome MET observations |
| https://www.metoffice.gov.uk/services/transport/aviation | public | UK aviation MET context |
| Session research | — | `EV-089…/evidence/deep-research-report-920.md` |

## Rule stubs

| rule_id | Product | Summary | confidence |
|---------|---------|---------|------------|
| UK.BASE.ICAO | METAR/SPECI/TAF | Treat as ICAO_2025 unless CAP 746 delta attested | med |

## Emit notes

- Thin path: core IWXXM only; no UK XSD.
- Overrides expected empty at kickoff.

## Next promote

1. Fixtures under `profiles/UK_METOFFICE/{METAR,SPECI,TAF}/`
2. Registry `uk_metoffice` allowlist
