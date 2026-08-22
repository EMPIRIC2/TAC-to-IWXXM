# CA_ECCC — Canada semantic overlay (P1)

> **Profile id**: `CA_ECCC` · **Kind**: semantic · **Priority**: P1 · **Status**: planned  
> **Implementation**: [#916](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/916) (first P1 national after US deepen)  
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

## Mining notes

Not yet mined — URLs triaged from [#913](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/913)
initial list. Promote section-level findings into this stub when mining closes.

## Implementation (not started)

| Target | Location |
|--------|----------|
| Fixture layout | `profiles/CA_ECCC/<product>/{valid,invalid,expected-*}` |
| Vendor pin candidate | `https://dd.weather.gc.ca/today/aviation/iwxxm/schema/` — not in `vendor/manifest.json` yet |
| Child issue | #916 |

## Gaps

- MANOBS/MANAIR section-level rule stubs not yet extracted
- No golden convert path or registry row in `profile_registry.py`
- Vendor pin for `iwxxm-ca` not staged in manifest
