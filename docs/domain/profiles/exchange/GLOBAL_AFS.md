# GLOBAL_AFS — default exchange overlay

> **Profile id**: `GLOBAL_AFS` · **Kind**: exchange · **Priority**: P0 · **Status**: default (packaging hook → [#921](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/921) / M6)  
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

## Implementation (M6)

| Target | Location |
|--------|----------|
| Exchange registry | TBD — `exchange_registry` per execution plan M6 |
| Default wire | `exchange.profile=GLOBAL_AFS` when packaging invoked (TC-EV063-004) |
| Tests | TC-EV063-004, TC-EV063-005 |

## Gaps

- `exchange_registry` + packaging hook not implemented until M6
- Regional overlays (`APAC_ROBEX`, `EUR_RODEX`, …) deferred to P2
