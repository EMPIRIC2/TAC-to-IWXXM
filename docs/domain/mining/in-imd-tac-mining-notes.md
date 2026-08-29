# IN IMD TAC mining notes (transitory)

> **Profile**: `IN_IMD` · **Cycle**: EV-089 · **Issue**: [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920)

## Sources triaged

| URL | Access | Proves |
|-----|--------|--------|
| https://mausam.imd.gov.in/ | public | IMD portal |
| India AIP GEN 3.5 | paywall/gap | TAF omissions; no AIRMET/GAMET — harden URL in Build |

## Rule stubs

| rule_id | Product | Summary | confidence |
|---------|---------|---------|------------|
| IN.BASE.ICAO | METAR/SPECI/TAF/SIGMET | Compat | med |
| IN.TAF.OMIT_VIS_TEMP | TAF | May omit forecast vis/temp — note/override candidate | med |

## Notes

- Do not invent IMDIMET XSD.
- No AIRMET/GAMET in v1.

## Next promote

NOAA/OGIMET India fixtures; decide override vs diagnostics for TAF omissions.
