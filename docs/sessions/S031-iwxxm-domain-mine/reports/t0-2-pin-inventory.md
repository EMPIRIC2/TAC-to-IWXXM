# T0.2 — Vendor pin + examples inventory seed

**Date**: 2026-07-30 · **Task**: T0.2 · **Cycle**: EV-024

## Pin

| Field | Value |
|-------|-------|
| Bundle | `iwxxm` |
| Tag | `v2025-2` |
| SHA | `35180cbe3bec0bc536a78714dd78d2e7ba60931f` |
| Path | `vendor/schemas/iwxxm/2025-2/IWXXM/` |
| Upstream | `wmo-im/iwxxm` |

`master` tip is **informative for drift only** — do not treat as equal to pin without sync PR.

## FIXTURE_GAPS (current FE)

| Product | Catalog count | Gap note |
|---------|---------------|----------|
| METAR | 1 | Second WMO METAR deferred |
| SPECI | 1 | Second WMO SPECI deferred |
| TAF | 2 | none |
| SIGMET | 2 | A6-1a + A6-1b; VA/TC stems not in menu |
| AIRMET | 1 | CNL peer deferred |
| VAA | 1 | Second WMO VAA deferred |
| TCA | 1 | Second WMO TCA deferred |

## Implication for UJ-039

Product-in-scope stems with TAC peers that are **not** yet in the catalog are the primary
M5 wiring targets (as `wmoPass` if already equal, else `wmoReference`). No invented TAC —
copy from vendor / annex3 mirrors only.

See [domain-mine-theme-map.md](./domain-mine-theme-map.md) for full stem seed table.
