# AFI — Africa–Indian Ocean regional exchange overlay

> **Profile id**: `AFI` · **Kind**: exchange · **Priority**: P2 · **Status**: **stub** (EV-086 P0 / [#921](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/921))  
> **Catalog row**: [`catalog.yaml`](../catalog.yaml) · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

Regional **exchange** overlay for the ICAO AFI region. P0 stub delegates to the
`GLOBAL_AFS` COLLECT baseline. Authoritative regional rule sources are TBD (#913).

## Owns (target)

| Area | Scope |
|------|-------|
| Regional packaging | AFI bulletin conventions atop COLLECT |
| Registry id | `AFI` wire + `afi` canonical |

## Does not own

- TAC grammar (semantic profiles)
- Dissemination credentials (F16–F19)
- Regional handbook rule matrix (deferred until sources mined)

## Authoritative sources

| Source | Access | Proves |
|--------|--------|--------|
| *(none listed — #913)* | gap | AFI exchange overlay rules |

## Implementation (EV-086 P0)

| Target | Location |
|--------|----------|
| Registry | `exchange_registry.py` — `CANONICAL_AFI` |
| Packaging | `packaging.py` — COLLECT wrap via `GLOBAL_AFS` baseline |
| Tests | TC-EV086-001..002 |

## Gaps

- Authoritative AFI exchange source row in catalog
- Regional rules beyond GLOBAL_AFS COLLECT baseline
