# NZ CAA / MetService TAC mining notes (transitory)

> **Profile**: `NZ_CAA_MET` · **Cycle**: EV-087 · **Issue**: [#918](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/918)  
> **Not SoT** — promote durable rows into [Corpus: domain-profiles] / RULE_SOURCE_URLS.

## Sources triaged

| URL | Access | Proves |
|-----|--------|--------|
| https://www.aviation.govt.nz/airspace-and-aerodromes/meteorology/aviation-weather-products/ | public | Domestic vs international TAF; AUTO guidance |
| Session report | — | `~/.cursor/workflow/.../EV-087.../reports/external-domain-research.md` |

## Rule stubs (promote → fixtures)

| rule_id | Product | Summary | confidence |
|---------|---------|---------|------------|
| NZ.TAF.DOMESTIC | TAF | &gt;10 km vis as km; cloud &gt;1500 ft; `2000FT WIND`; `QNH MNM/MAX` | med |
| NZ.TAF.INTERNATIONAL | TAF | Annex 3-shaped (e.g. NZAA/NZWN/NZCH) | med |
| NZ.TAF.RMK_2000FT_WIND | TAF | `2000FT WIND dddffKT` | med |
| NZ.TAF.RMK_QNH | TAF | `QNH MNM nnnn MAX mmmm` | high |
| NZ.METAR.NCD | METAR | AUTO no cloud detected (not SKC) | high |
| NZ.METAR.UP | METAR | Unidentified precipitation | high |
| NZ.METAR.// | METAR | Solidi / `///` sensor or base unknown | high |

## Emit notes

- Domestic extras → IR + remarks unless core IWXXM mapping attested (D-EV087-nz-domestic).
- No NZ national XSD found.

## Next promote

1. Fixture pack under `profiles/NZ_CAA_MET/TAF|METAR/`
2. Harden CAA/AIP PDF citations after local harvest
