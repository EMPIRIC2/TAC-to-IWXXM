# BR DECEA TAC mining notes (transitory)

> **Profile**: `BR_DECEA` · **Cycle**: EV-089 · **Issue**: [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920)

## Sources triaged

| URL | Access | Proves |
|-----|--------|--------|
| https://aisweb.decea.mil.br/ | public | Brazilian AIS / AIP access |
| https://www2.anac.gov.br/ | public | ANAC institutional context |

## Rule stubs

| rule_id | Product | Summary | confidence |
|---------|---------|---------|------------|
| BR.BASE.ICAO | METAR/SPECI/TAF/SIGMET/AIRMET | ICAO_2025 emit | med |
| BR.GAMET.PARSE | GAMET | Fixture/parse-only — no IWXXM (D-EV089-gamet) | high |

## Emit notes

- SAM packaging → #921 / `CAR_SAM` note only.
- No BR national XSD.

## Next promote

Fixtures + registry for convert products; optional GAMET TAC under ops/.
