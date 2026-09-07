# HK HKO TAC mining notes (transitory)

> **Profile**: `HK_HKO` · **Cycle**: EV-094 / [#1098](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1098) (kickoff EV-089 / #920)

## Sources triaged

| URL | Access | Proves |
|-----|--------|--------|
| https://www.hko.gov.hk/en/index.html | public | HKO services |
| Hong Kong AIP GEN 3.5 | paywall/gap | Product policy — harden durable URL when public pin found |
| https://aviationweather.gov/api/data/metar?ids=VHHH&format=raw | public | Attributed METAR (EV-094 M6) |
| https://aviationweather.gov/api/data/taf?ids=VHHH&format=raw | public | Attributed TAF with TX/TN (EV-094 M6) |
| Session research | — | EV-094 `evidence/deep-research-report-deepen.md` |

## Rule stubs

| rule_id | Product | Summary | confidence |
|---------|---------|---------|------------|
| HK.BASE.ICAO | METAR/SPECI/TAF/SIGMET/VAA | APAC fixtures; empty overrides (Annex-conformant incl. TX/TN) | high |

## Notes

- SIGMET + VAA stay on convert allowlist (D-EV094-products); corpora may remain synthetic until harvest.
- Chinese-language bulletin variants not required for v1.
- No published HK IWXXM extension XSD — core-only emit.

## Next promote

1. ~~Attributed VHHH METAR/TAF + TX/TN confirmation~~ (M6)
2. Attributed SPECI / Hong Kong FIR SIGMET / VAA when public corpus found
3. AIP GEN 3.5 durable URL
