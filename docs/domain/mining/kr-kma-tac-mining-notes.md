# KR KMA TAC mining notes (transitory)

> **Profile**: `KR_KMA` · **Cycle**: EV-094 / [#1098](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1098) (kickoff EV-089 / [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920))

## Sources triaged

| URL | Access | Proves |
|-----|--------|--------|
| https://www.kma.go.kr/eng/ | public | KMA English portal |
| https://aviationweather.gov/api/data/metar?ids=RKSI&format=raw | public | Attributed RKSI METAR (EV-094 M3) |
| https://aviationweather.gov/api/data/taf?ids=RKSI&format=raw | public | Attributed RKSI TAF (EV-094 M3) |
| Korea AIP GEN 3.5 | paywall/gap | Product policy — harden URL later |

## Rule stubs

| rule_id | Product | Summary | confidence |
|---------|---------|---------|------------|
| KR.BASE.ICAO | METAR/SPECI/TAF/SIGMET/AIRMET | Compat / empty overrides; SPECI allowlisted M3 | med |

## Next promote

FIR SIGMET/AIRMET + real SPECI corpus attribution; AIP GEN 3.5 durable URL.
