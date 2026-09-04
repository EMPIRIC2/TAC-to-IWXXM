# US_FAA_NWS — United States semantic overlay

> **Profile id**: `US_FAA_NWS` · **Legacy alias**: `iwxxm_us` (deprecation window → [#1025](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1025))  
> **Kind**: semantic · **Priority**: P0 · **Status**: implemented — #919 closed (EV-085)  
> **Catalog row**: [`catalog.yaml`](../catalog.yaml) · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

United States national semantic overlay on the ICAO baseline: FMH-1 METAR/SPECI body and RMK
grammar, encoded with **IWXXM-US** extension XSDs alongside core IWXXM.

## Owns

| Area | Scope |
|------|-------|
| TAC parse / normalize | FMH-1 Ch.12 body order + RMK §12.7 |
| SPECI criteria | FMH-1 §2.5.2 (US statute miles / feet thresholds) |
| IWXXM extensions | `iwxxm-us` 3.0 — RMK → `extension` blocks, US-specific elements |
| Products | **METAR, SPECI** (primary); **SIGMET/AIRMET** national layer (M8–M19); **TAF** lint overlay (M13); **SWXA/TCA** thin US validation policy (M22) |

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
| Profile fixtures | `packages/tac2iwxxm/tests/fixtures/profiles/US_FAA_NWS/` |
| Legacy goldens | `packages/tac2iwxxm/tests/fixtures/iwxxm_us_golden/` |

## Delivered (#919 EV-079..085)

- **M7** — 15 FMH-1 §12.7 structured RMK rows + goldens (EV-063)
- **M8–M11** — SIGMET/AIRMET phenomenon tokens, VOR geometry, weather-hazard emit, WST (EV-079..081)
- **M12–M13** — structured VIS verify; US TAF lint (`US_TAF_BECMG_FORBIDDEN`, `US_TAF_TEMPO_MAX_4H`)
- **M15–M19** — AIRMET outlook, multi-area, CONUS UPDT, FRZLVL, WAUS multi-section (EV-082..084)
- **M20–M22** — acceptance audit manifest + negative cases; SWXA/TCA thin policy (EV-085)

## Residual gaps (explicit)

| Gap | Disposition |
|-----|-------------|
| FMH-1 §12.7.2 additive RMK (T/P/6/7/$, ice accretion, `$` maintenance) | Post-#919 — no mined profile-pack fixtures (EV-085 M21) |
| M14 alias cutover `iwxxm_us` → `US_FAA_NWS` | Deferred [#1025](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1025) → 2026-10-31 |
| `codes.nws.noaa.gov/FMH-1` machine registry | Probe timed out 2026-07-14 — retry when reachable |
| US examples in WMO-only sample catalog | UJ-039 policy — US samples stay in profile pack only |
