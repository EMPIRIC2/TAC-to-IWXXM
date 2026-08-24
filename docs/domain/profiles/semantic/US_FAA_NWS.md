# US_FAA_NWS — United States semantic overlay

> **Profile id**: `US_FAA_NWS` · **Legacy alias**: `iwxxm_us` (deprecation window → [#1025](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1025))  
> **Kind**: semantic · **Priority**: P0 · **Status**: implemented (F35); deepen [#919](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/919)  
> **Catalog row**: [`catalog.yaml`](../catalog.yaml) · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

United States national semantic overlay on the ICAO baseline: FMH-1 METAR/SPECI body and RMK
grammar, encoded with **IWXXM-US** extension XSDs alongside core IWXXM.

## Owns

| Area | Scope |
|------|-------|
| TAC parse / normalize | FMH-1 Ch.12 body order + RMK §12.7 |
| SPECI criteria | FMH-1 §2.5.2 (US statute miles / feet thresholds) |
| IWXXM extensions | `iwxxm-us` 3.0 — RMK → `extension` blocks, US-specific elements |
| Products | **METAR, SPECI** (primary); SIGMET national layer out of FMH-1 scope |

## Authoritative sources

| Source | Access | Proves |
|--------|--------|--------|
| [FMH-1 (2019)](https://www.icams-portal.gov/resources/ofcm/fmh/FMH1/fmh1_2019.pdf) | public | US METAR/SPECI + RMK coding |
| [IWXXM-US 3.0](https://nws.weather.gov/schemas/iwxxm-us/3.0/) | public | National extension XSD + UML |
| [FAA GEN 1.7](https://www.faa.gov/air_traffic/publications/atpubs/aip_html/part1_gen_section_1.7.html) | public | US differences from ICAO |

## Mining notes (transitory)

- [`fmh1-2019-mining-notes.md`](../../mining/fmh1-2019-mining-notes.md)
- [`iwxxm-us-metar-speci-pdf-mining-notes.md`](../../mining/iwxxm-us-metar-speci-pdf-mining-notes.md)

## Implementation

| Component | Location |
|-----------|----------|
| Registry | `packages/tac2iwxxm/src/tac2iwxxm/profile_registry.py` |
| Emitter | `packages/tac2iwxxm/src/tac2iwxxm/profiles/iwxxm_us.py` |
| Vendor pin | `vendor/manifest.json` → `iwxxm-us` **3.0** |
| Golden fixtures | `packages/tac2iwxxm/tests/fixtures/iwxxm_us_golden/` |

## Gaps (#919 deepen)

- Full FMH-1 RMK matrix beyond AO/SLP/PK/T/P free-text — **M7 done** (15 rows)
- **SIGMET/AIRMET national layer** — **M8 in progress** (EV-079): fixture pack + US AIRMET phenomenon tokens; iwxxm-us weather-hazard extensions deferred
- `ReferencePointGeometryParser` for VOR/airport reference geometry — deferred
- `codes.nws.noaa.gov/FMH-1` machine registry — probe timed out 2026-07-14
- US examples must **not** mix into WMO-only sample catalog (UJ-039 policy)
