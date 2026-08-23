# CA_ECCC — Canada semantic overlay (P1)

> **Profile id**: `CA_ECCC` · **Kind**: semantic · **Priority**: P1 · **Status**: implemented (EV-064 M1–M6 / #916 P1 slice)  
> **Implementation**: [#916](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/916) · **Evolve**: EV-064-ca-eccc-profile  
> **Catalog row**: [`catalog.yaml`](../catalog.yaml) · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

Environment and Climate Change Canada (ECCC / MSC) national semantic overlay: MANOBS
surface observations, MANAIR aviation forecasts, and Canadian IWXXM extension schemas.

## Owns (target)

| Area | Scope |
|------|-------|
| TAC parse / normalize | MANOBS METAR/SPECI; MANAIR TAF/AIRMET |
| IWXXM extensions | `iwxxm-ca.xsd`, `common-ca.xsd`, `taf-ca.xsd`, `airmet-ca.xsd` |
| Products | METAR, SPECI, TAF, AIRMET (initial P1 slice per #916) |

## Authoritative sources

| Source | Access | Proves |
|--------|--------|--------|
| [MANOBS](https://www.canada.ca/en/environment-climate-change/services/weather-manuals-documentation/manobs-surface-observations.html) | public | Canadian surface observation standards |
| [MANAIR 8th Ed.](https://www.canada.ca/en/environment-climate-change/services/weather-manuals-documentation/manair-standards-procedures-aviation-weather-forecasts-8th-ed.html) | public | Canadian aviation forecast standards |
| [MSC IWXXM-CA XSD](https://dd.weather.gc.ca/today/aviation/iwxxm/schema/) | public | National extension schema tree |
| [MSC aviation IWXXM datamart](https://eccc-msc.github.io/open-data/msc-data/aviation/iwxxm/readme_aviation-iwxxm-datamart_fr/) | public | Operational IWXXM 3.0.0 + CA extensions |

## Mining notes (transitory)

- [`manobs-manair-ca-mining-notes.md`](../../mining/manobs-manair-ca-mining-notes.md) — MANOBS/MANAIR TAC rules
- [`eccc-iwxxm-ca-mining-notes.md`](../../mining/eccc-iwxxm-ca-mining-notes.md) — IWXXM 3.0.0 + `*-ca.xsd` + code-ca + datamart

## IWXXM version line

MSC operational practice pins **IWXXM 3.0.0** core (`http://icao.int/iwxxm/3.0`) plus CA
extensions — independent of the app default **2025-2** SoT line ([ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)).

## Implementation

| Component | Location |
|-----------|----------|
| Registry | `packages/tac2iwxxm/src/tac2iwxxm/profile_registry.py` |
| Emitter | `packages/tac2iwxxm/src/tac2iwxxm/profiles/ca_eccc.py` |
| Vendor pin (target) | `vendor/manifest.json` → `iwxxm-ca` 3.0 + IWXXM `3.0.0` core |
| Validate profile | `packages/iwxxm-validate` — `ca_eccc` path (EV-064 M2) |

## Gaps (post EV-064 M6 / EV-066 / EV-067)

- Extended Canadian-only remark flags (CONTRAILS/AURORA) in structured Addendum
- AerodromeVariableRVR / ObservedLightning (P2)
- SIGMET national overlay — out of #916 scope
