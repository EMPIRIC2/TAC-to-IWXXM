# CAR_SAM — Caribbean / South America regional exchange overlay

> **Profile id**: `CAR_SAM` · **Kind**: exchange · **Priority**: P2 · **Status**: **stub** (EV-086 P0 / EV-090 mining promote / [#921](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/921))  
> **Catalog row**: [`catalog.yaml`](../catalog.yaml) · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

Regional **exchange** overlay for ICAO CAR/SAM. P0 stub delegates to the
`GLOBAL_AFS` COLLECT baseline. Shared AFS exchange baseline is the OPMET Guidelines;
CAR/SAM-specific handbook sources remain TBD (#913).

## Owns (target)

| Area | Scope |
|------|-------|
| Regional packaging | CAR/SAM bulletin conventions atop COLLECT |
| Registry id | `CAR_SAM` wire + `car_sam` canonical |

## Does not own

- TAC grammar (semantic profiles)
- Dissemination credentials (F16–F19)
- Regional handbook rule matrix (deferred until region-specific sources mined)

## Authoritative sources

| Source | Access | Proves |
|--------|--------|--------|
| [OPMET IWXXM Exchange Guidelines (5th Ed.)](https://www.icao.int/sites/default/files/METP/Documents/Guidlines-for-the-Implementation-of-OPMET-Data-Exchange-using-IWXXM_5th-Edition.pdf) | public | Shared COLLECT / AFS baseline |
| CAR/SAM-specific exchange handbook | gap | Regional overlay rules |

## Mining notes

- [`OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md`](../../mining/OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md)

## Implementation (EV-086 P0)

| Target | Location |
|--------|----------|
| Registry | `exchange_registry.py` — `CANONICAL_CAR_SAM` |
| Packaging | `packaging.py` — COLLECT wrap via `GLOBAL_AFS` baseline |
| Tests | TC-EV086-001..002 |

## Gaps

- Authoritative CAR/SAM-specific exchange source row in catalog
- Regional rules beyond GLOBAL_AFS COLLECT baseline
