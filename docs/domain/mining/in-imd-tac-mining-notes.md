# IN IMD TAC mining notes (transitory)

> **Profile**: `IN_IMD` · **Cycle**: EV-094 / [#1098](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1098) (kickoff EV-089 / #920)

## Sources triaged

| URL | Access | Proves |
|-----|--------|--------|
| https://mausam.imd.gov.in/ | public | IMD portal |
| India AIP GEN 3.5 | paywall/gap | No AIRMET/GAMET; harden durable URL in Build |
| https://aviationweather.gov/api/data/metar?ids=VIDP&format=raw | public | Attributed METAR (EV-094 M5) |
| https://aviationweather.gov/api/data/taf?ids=VIDP&format=raw | public | Attributed TAF without TX/TN (EV-094 M5) |
| Session research | — | EV-094 `evidence/deep-research-report-deepen.md` |

## Rule stubs

| rule_id | Product | Summary | confidence |
|---------|---------|---------|------------|
| IN.BASE.ICAO | METAR/SPECI/TAF/SIGMET | Compat core | med |
| IN.TAF.OMIT_TX_TN | TAF | TX/TN often omitted — lint overlay `in_imd` → `IN_TAF_TX_TN_OMITTED` info (D-EV094-in-taf) | high |

## Emit / lint notes

- Convert: core IWXXM only; no IMDIMET XSD invent.
- Lint: `profile=in_imd|IN_IMD` (TAF only); when TX/TN tokens absent, emit `IN_TAF_TX_TN_OMITTED` (info). Annex3 path unchanged.

## Next promote

1. ~~Fixtures without TX/TN + registry wire + TC-EV094-004~~ (M5)
2. Attributed SPECI / SIGMET when public corpus found
3. AIP GEN 3.5 durable URL
