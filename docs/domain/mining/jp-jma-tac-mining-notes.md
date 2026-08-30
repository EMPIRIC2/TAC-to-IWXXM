# JP JMA TAC mining notes (transitory)

> **Profile**: `JP_JMA` · **Cycle**: EV-089 · **Issue**: [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920)

## Sources triaged

| URL | Access | Proves |
|-----|--------|--------|
| https://www.jma.go.jp/jma/indexe.html | public | JMA MET context |
| https://www.data.jma.go.jp/svd/vaac/data/index.html | public | Tokyo VAAC VAA |

## Rule stubs

| rule_id | Product | Summary | confidence |
|---------|---------|---------|------------|
| JP.BASE.ICAO | METAR/TAF/SIGMET | Compat | med |
| JP.VAA.TOKYO | VAA | Tokyo VAAC corpus; core IWXXM VAA path | med |

## Notes

- AIRMET out of v1 (D-EV089-jp-va).
- No national VA schema fork.

## Next promote

METAR/TAF/SIGMET/VAA fixtures + registry.
