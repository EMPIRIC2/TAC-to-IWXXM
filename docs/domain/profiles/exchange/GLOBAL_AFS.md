# GLOBAL_AFS — default exchange overlay

> **Profile id**: `GLOBAL_AFS` · **Kind**: exchange · **Priority**: P0 · **Status**: **implemented** (EV-065 / #921)  
> **Catalog row**: [`catalog.yaml`](../catalog.yaml) · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

Default **exchange** profile when packaging or disseminate-prep paths are invoked without an
explicit exchange id. Selects bulletin headers, COLLECT aggregation, FTBP filename conventions,
and AFS routing defaults — **not** TAC grammar (semantic profiles own that).

## Owns (target)

| Area | Scope |
|------|-------|
| Bulletin packaging | COLLECT `MeteorologicalBulletin` aggregation |
| Filename / routing | FTBP `A_TTAAii…xml.gz` patterns per OPMET Guidelines |
| Product designators | AHL T1T2 mapping (LA/LP/LC/… per product) |
| Translation metadata | `translationCentre*` attrs when on behalf of another State |

## Does not own

- Dissemination destination credentials (F16–F19 BYOC — memory-only)
- TAC parse rules or national RMK policy (semantic profiles)
- Live sink egress (`DISSEMINATION_EGRESS_ALLOWLIST`)

## Authoritative sources

| Source | Access | Proves |
|--------|--------|--------|
| [OPMET IWXXM Exchange Guidelines 5th Ed.](https://www.icao.int/sites/default/files/METP/Documents/Guidlines-for-the-Implementation-of-OPMET-Data-Exchange-using-IWXXM_5th-Edition.pdf) | public | COLLECT, AMHS/FTBP, translation centre rules |
| [WMO AHL / AFS](https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/wmo-information-system-wis/about-manual-gts/ahls-aviation-data-over-icao-afs) | public | AHL product type designators |
| [wmo-im/iwxxm](https://github.com/wmo-im/iwxxm) | public | `collect.xsd` |

## Mining notes (transitory)

- [`OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md`](../../mining/OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md)

## Implementation (EV-065)

| Target | Location |
|--------|----------|
| Exchange registry | `packages/dissemination/src/dissemination/exchange_registry.py` |
| COLLECT packaging | `packages/dissemination/src/dissemination/packaging.py` |
| API wire | `POST /api/v1/convert-bulletin` — default `exchange_profile=GLOBAL_AFS` |
| Fixtures | `packages/dissemination/tests/fixtures/profiles/GLOBAL_AFS/` |
| Tests | TC-EV063-004, TC-EV063-005, TC-EV065-001 |

## Gaps

- FTBP `A_TTAAii…xml.gz` filename synthesis from AHL (partial — `bulletinIdentifier` when AHL parseable)
- Regional overlays (`APAC_ROBEX` P0 stub landed EV-065; `EUR_RODEX`, …) deepen separately
