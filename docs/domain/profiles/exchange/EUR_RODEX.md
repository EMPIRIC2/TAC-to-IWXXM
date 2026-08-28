# EUR_RODEX — European regional exchange overlay

> **Profile id**: `EUR_RODEX` · **Kind**: exchange · **Priority**: P2 · **Status**: **stub** (EV-086 P0 / [#921](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/921))  
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
| EUR RODEX Handbook (candidate URL in catalog) | gap | European regional exchange overlay |

## Implementation (EV-086 P0)

| Target | Location |
|--------|----------|
| Registry | `exchange_registry.py` — `CANONICAL_EUR_RODEX` |
| Packaging | `packaging.py` — COLLECT wrap via `GLOBAL_AFS` baseline |
| Tests | TC-EV086-001..002 |

## Gaps

- RODEX handbook durable URL pin / edition
- Regional rules beyond GLOBAL_AFS COLLECT baseline
