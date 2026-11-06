# APAC_ROBEX — APAC regional exchange overlay

> **Profile id**: `APAC_ROBEX` · **Kind**: exchange · **Priority**: P2 · **Status**: **in_progress** (EV-1222 / [#1222](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1222))  
> **Catalog row**: [`catalog.yaml`](../catalog.yaml) · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

Regional **exchange** overlay for APAC ROBEX / IWXXM OPMET practice. COLLECT XML
shell follows OPMET IWXXM Exchange Guidelines (ROBEX HB §6.6.1). EV-1222 adds a
cited default `bulletinIdentifier` when the caller omits one.

## Owns (current)

| Area | Scope |
|------|-------|
| COLLECT wrap | Same `collect:MeteorologicalBulletin` shell as `GLOBAL_AFS` |
| Default bulletin id | `A_SACI31ZBBB.xml` when unset — ROBEX HB §6.4.2 / App A `SACI31 ZBBB` example + OPMET FTBP `A_TTAAiiCCCC…` stem |
| Registry id | `APAC_ROBEX` wire + `apac_robex` canonical |

## Does not own

- TAC grammar (semantic profiles)
- Dissemination credentials (F16–F19)
- Full ROBEX App A/B matrices / dynamic TTAAii from aerodrome

## Authoritative sources

| Source | Access | Proves |
|--------|--------|--------|
| [OPMET IWXXM Exchange Guidelines (5th Ed.)](https://www.icao.int/sites/default/files/METP/Documents/Guidlines-for-the-Implementation-of-OPMET-Data-Exchange-using-IWXXM_5th-Edition.pdf) | public | Shared COLLECT / FTBP / AFS baseline |
| [APAC ROBEX Handbook (19th Ed., Feb 2026)](https://www.icao.int/sites/default/files/APAC/Documents/edocs/MET/2026-02-APAC-ROBEX-HB-19TH-ED.pdf) | public | APAC ROBEX bulletin scheme; §6.6.1 defers IWXXM XML to Guidelines |
| [APAC IWXXM FAQs (3rd Ed.)](https://www.icao.int/sites/default/files/APAC/Documents/edocs/MET/2025-03_IWXXM-FAQs_3rd-Ed.pdf) | public | COLLECT mandate; translation centre policy |

## Mining notes

- [`OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md`](../../mining/OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md)
- [`icao-apac-iwxxm-faqs-3rd-2025-mining-notes.md`](../../mining/icao-apac-iwxxm-faqs-3rd-2025-mining-notes.md)
- [`icao-apac-robex-hb-19th-2026-mining-notes.md`](../../mining/icao-apac-robex-hb-19th-2026-mining-notes.md)

## Implementation

| Target | Location |
|--------|----------|
| Registry | `exchange_registry.py` — `CANONICAL_APAC_ROBEX` |
| Packaging | `packaging.py` — COLLECT + `APAC_ROBEX_DEFAULT_BULLETIN_IDENTIFIER` |
| Tests | TC-EV1222-001..004 |

## Gaps

- Full ROBEX App A/B bulletin matrices / ROC distribution lists
- Dynamic TTAAii selection from aerodrome (example default only)
