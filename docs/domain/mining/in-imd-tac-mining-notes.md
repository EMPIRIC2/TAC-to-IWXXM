# IN IMD TAC mining notes (transitory)

> **Profile**: `IN_IMD` · **Cycle**: EV-094 / [#1098](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1098) (kickoff EV-089 / #920)

## Sources triaged

| URL | Access | Proves |
|-----|--------|--------|
| https://mausam.imd.gov.in/ | public | IMD portal |
| India AIP GEN 3.5 | paywall/gap | No AIRMET/GAMET; harden durable URL in Build |
| AllMetsat / public TAC portals | public | Sample METAR/TAF (VABB, VIDP) — attribute URL+UTC in fixtures |
| Session research | — | EV-094 `evidence/deep-research-report-deepen.md` |

## Rule stubs

| rule_id | Product | Summary | confidence |
|---------|---------|---------|------------|
| IN.BASE.ICAO | METAR/SPECI/TAF/SIGMET | Compat core | med |
| IN.TAF.OMIT_TX_TN | TAF | TX/TN often omitted — **lint overlay** `in_imd` info awareness (D-EV094-in-taf); not hard error | high |

## Emit / lint notes

- Convert: core IWXXM only; no IMDIMET XSD invent.
- Lint: first thin-pack national overlay beyond CA/US — when `profile=in_imd|IN_IMD` and TAF lacks TX/TN tokens, emit registered info code (Build names code; keep operator copy free of planning ids).

## Next promote

1. Fixtures without TX/TN + with TX/TN (if found)
2. Registry + `profiles.py` SUPPORTED_PROFILES wire
3. TC-EV094-004
