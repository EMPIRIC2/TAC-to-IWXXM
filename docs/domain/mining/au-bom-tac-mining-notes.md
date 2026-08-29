# AU BoM TAC mining notes (transitory)

> **Profile**: `AU_BOM` · **Cycle**: EV-087 · **Issue**: [#917](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/917)  
> **Not SoT** — promote durable rows into [Corpus: domain-profiles] / RULE_SOURCE_URLS.

## Sources triaged

| URL | Access | Proves |
|-----|--------|--------|
| http://www.bom.gov.au/aviation/data/education/taf-metar-speci-reference-card.pdf | public PDF | INTER (&lt;30 min) vs TEMPO (30–60); RMK T/Q; TAF3 in RMK; AUTO NCD/UP/solidi; CAVOK not on AUTO |
| https://www.bom.gov.au/aviation/taf3/index.shtml | public | TAF3 service definition |
| https://www.bom.gov.au/aviation/forecasts/international-taf/ | public | Example TAC |
| Session report | — | `~/.cursor/workflow/.../EV-087.../reports/external-domain-research.md` |

## Rule stubs (promote → fixtures)

| rule_id | Product | Summary | confidence |
|---------|---------|---------|------------|
| AU.TAF.INTER | TAF | Intermittent &lt;30 min change group | high |
| AU.TAF.TEMPO | TAF | Temporary 30–60 min (BoM split from INTER) | high |
| AU.TAF.RMK_T | TAF | RMK `T` 3-hourly temps (°C, `M` negative) | high |
| AU.TAF.RMK_Q | TAF | RMK `Q` 3-hourly QNH (hPa) | high |
| AU.TAF.TAF3 | TAF | RMK `TAF3` / `TAF3 VALID TL` service marker | med |
| AU.METAR.NCD | METAR | AUTO nil cloud detected | high |
| AU.METAR.UP | METAR | Unidentified precipitation | high |
| AU.METAR.MISSING | METAR | Solidi missing groups | high |
| AU.METAR.CAVOK | METAR | CAVOK not used on AUTO | high |

## Emit notes

- `INTER` → IR distinct; IWXXM `TEMPORARY_FLUCTUATIONS` + provenance (D-EV087-inter-emit).
- No AU national XSD found.

## Next promote

1. Fixture pack under `profiles/AU_BOM/TAF|METAR/`
2. RULE_SOURCE_URLS rows for reference card + TAF3 page
