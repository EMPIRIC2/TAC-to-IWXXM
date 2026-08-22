# APAC_ROBEX — APAC regional exchange overlay

> **Profile id**: `APAC_ROBEX` · **Kind**: exchange · **Priority**: P2 · **Status**: **stub** (EV-065 P0 / [#921](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/921))  
> **Catalog row**: [`catalog.yaml`](../catalog.yaml) · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

Regional **exchange** overlay for APAC ROBEX / IWXXM OPMET practice. P0 stub
delegates to the `GLOBAL_AFS` COLLECT baseline — same bulletin shell, registry id,
and packaging hook. ROBEX-specific filename or routing rules deepen on backlog.

## Owns (target)

| Area | Scope |
|------|-------|
| Regional packaging | APAC ROBEX bulletin conventions atop COLLECT |
| Registry id | `APAC_ROBEX` wire + `apac_robex` canonical |

## Does not own

- TAC grammar (semantic profiles)
- Dissemination credentials (F16–F19)
- Full ROBEX handbook rule matrix (deferred)

## Authoritative sources

| Source | Access | Proves |
|--------|--------|--------|
| [APAC IWXXM FAQs (3rd Ed.)](https://www.icao.int/sites/default/files/APAC/Documents/edocs/MET/2025-03_IWXXM-FAQs_3rd-Ed.pdf) | public | COLLECT mandate; translation centre policy |
| [ICAO APAC electronic documents](https://www.icao.int/APAC/apac-electronic-documents) | public | ROBEX handbook pointer |

## Mining notes

- [`icao-apac-iwxxm-faqs-3rd-2025-mining-notes.md`](../../mining/icao-apac-iwxxm-faqs-3rd-2025-mining-notes.md)

## Implementation (EV-065 P0)

| Target | Location |
|--------|----------|
| Registry | `exchange_registry.py` — `CANONICAL_APAC_ROBEX` |
| Packaging | `packaging.py` — COLLECT wrap via `GLOBAL_AFS` baseline |
| Tests | TC-EV065-002, TC-EV065-003 |

## Gaps

- ROBEX handbook durable URL pin
- Regional rules beyond GLOBAL_AFS COLLECT baseline
