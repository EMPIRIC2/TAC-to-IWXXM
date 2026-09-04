# NZ_CAA_MET — New Zealand CAA / MetService semantic overlay (P1)

> **Profile id**: `NZ_CAA_MET` · **Kind**: semantic · **Priority**: P1 · **Status**: in_progress (EV-087 / [#918](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/918))  
> **Catalog row**: [`catalog.yaml`](../catalog.yaml) · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

New Zealand national semantic overlay: **domestic vs international TAF** dialects and METAR
AUTO conventions (`NCD`, `UP`, solidi / `///`).

## Owns (target)

| Area | Scope |
|------|-------|
| TAC parse / normalize | Domestic extras (`30KM`, cloud &gt;1500 ft, `2000FT WIND`, `QNH MNM/MAX`); intl Annex 3-shaped TAF |
| IWXXM encode | **Core WMO only** — no published NZ extension XSD (EV-087 research) |
| Products | TAF, METAR, SPECI |
| SIGMET | ICAO base unless later mining shows deltas |

## Key policy (locked)

| Topic | Rule | Decision |
|-------|------|----------|
| Domestic extras | Parse to IR + fixtures; core IWXXM only if attested; else remarks + diagnostics | D-EV087-nz-domestic |
| National XSD | None — do not invent | D-EV087-xsd |

## Authoritative sources

| Source | Access | Proves |
|--------|--------|--------|
| [NZ CAA aviation weather products](https://www.aviation.govt.nz/airspace-and-aerodromes/meteorology/aviation-weather-products/) | public | Domestic vs international TAF; AUTO policy |

## Mining notes

- [`nz-caa-met-tac-mining-notes.md`](../../mining/nz-caa-met-tac-mining-notes.md)

## Implementation (Build)

| Component | Location |
|-----------|----------|
| Registry | `packages/tac2iwxxm/src/tac2iwxxm/profile_registry.py` (`nz_caa_met`) |
| Fixtures | `packages/tac2iwxxm/tests/fixtures/profiles/NZ_CAA_MET/` |

## Gaps

- Additional AIP/CAA PDF durable URLs after local harvest.
- Structured IWXXM mapping for `2000FT WIND` / QNH range only if a published SoT appears.
