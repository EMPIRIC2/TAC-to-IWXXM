# EUR_RODEX — European regional exchange overlay

> **Profile id**: `EUR_RODEX` · **Kind**: exchange · **Priority**: P2 · **Status**: **stub** (EV-086 P0 / EV-090 mining promote / [#921](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/921))  
> **Catalog row**: [`catalog.yaml`](../catalog.yaml) · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

Regional **exchange** overlay for EUR RODEX / IWXXM OPMET practice. P0 stub
delegates to the `GLOBAL_AFS` COLLECT baseline — same bulletin shell, registry id,
and packaging hook. RODEX-specific filename or routing rules deepen on backlog.

## Owns (target)

| Area | Scope |
|------|-------|
| Regional packaging | EUR RODEX bulletin conventions atop COLLECT |
| Registry id | `EUR_RODEX` wire + `eur_rodex` canonical |

## Does not own

- TAC grammar (semantic profiles)
- Dissemination credentials (F16–F19)
- Full RODEX handbook rule matrix (deferred)

## Authoritative sources

| Source | Access | Proves |
|--------|--------|--------|
| [OPMET IWXXM Exchange Guidelines (5th Ed.)](https://www.icao.int/sites/default/files/METP/Documents/Guidlines-for-the-Implementation-of-OPMET-Data-Exchange-using-IWXXM_5th-Edition.pdf) | public | Shared COLLECT / FTBP / AFS baseline |
| [EUR OPMET Data Management Handbook (EUR Doc 018, Ed. 15)](https://www.icao.int/sites/default/files/EURNAT/Documents/EUR%20and%20Nat%20Docs/EUR%20Documents/EUR%20Documents/018%20-%20OPMET%20Handbook/EUR-Doc-18-EN-Edition-15-Amd-0.pdf) | public | Main guidance material for the EUR RODEX schema, including IWXXM exchange and RODB procedures |

## Mining notes

- [`OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md`](../../mining/OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md)
- [`icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md`](../../mining/icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md) — EUR Docs 018/020 pointers for IWXXM/exchange detail

## Implementation (EV-086 P0)

| Target | Location |
|--------|----------|
| Registry | `exchange_registry.py` — `CANONICAL_EUR_RODEX` |
| Packaging | `packaging.py` — COLLECT wrap via `GLOBAL_AFS` baseline |
| Tests | TC-EV086-001..002 |

## Gaps

- Regional rules beyond GLOBAL_AFS COLLECT baseline
