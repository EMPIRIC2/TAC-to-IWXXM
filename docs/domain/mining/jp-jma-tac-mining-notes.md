# JP JMA TAC mining notes (transitory)

> **Profile**: `JP_JMA` · **Cycle**: EV-094 / [#1098](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1098) (kickoff EV-089 / [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920))

## Sources triaged

| URL | Access | Proves |
|-----|--------|--------|
| https://www.jma.go.jp/jma/indexe.html | public | JMA MET context |
| https://www.data.jma.go.jp/svd/vaac/data/index.html | public | Tokyo VAAC VAA |
| https://aviationweather.gov/api/data/metar?ids=RJTT&format=raw | public | Attributed RJTT METAR (EV-094 M4) |
| https://aviationweather.gov/api/data/taf?ids=RJTT&format=raw | public | Attributed RJTT TAF (EV-094 M4) |

## Rule stubs

| rule_id | Product | Summary | confidence |
|---------|---------|---------|------------|
| JP.BASE.ICAO | METAR/SPECI/TAF/SIGMET | Compat; SPECI allowlisted M4 | med |
| JP.VAA.TOKYO | VAA | Tokyo VAAC corpus; core IWXXM VAA path | med |

## Notes

- AIRMET out of v1 (D-EV089-jp-va).
- No national VA schema fork.

## Next promote

FIR SIGMET + real SPECI + attributed Tokyo VAAC VAA corpora.
