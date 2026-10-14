# Context — vicinity showers and thunderstorms

**Session:** `EV-1396-regional-tester-gaps`
**Date:** 2026-10-14
**Mode:** standard evolve, first slice of epic #1396
**Ticket:** [#1397](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1397)
**Corpus:** [Corpus: product §F6] [Corpus: api] [Corpus: tests]

## Goal

Accept `VCSH`, `VCTS`, and bare `TS` on METAR, SPECI, and TAF under the default ICAO profile, and encode them as present weather.

## Out of scope

- Remarks policy and US-only remark weather
- Other epic children as this session's build (#1398–#1412)
- Operator UI, connectivity tiers H4–H5, and a `stage` → `main` promote

## Locked intake

| Topic | Lock |
|-------|------|
| Scale | Standard. Spec→Build gate **closed** |
| Users | Caribbean NMHS testers (Jamaica, Belize, Guyana, St Kitts, St Maarten, Saint Lucia) |
| Fence | Existing weather codes and remarks stay. No PII. No UI |
| Docs | Delta only where product, api, or tests do not already say these tokens convert |
| Build intent | `packages/tac2iwxxm` and `packages/tac-validate` tests. Pull request into `stage` |
| e2e | Proposed skip, approved |
| Memory | Neo4j unavailable. Historical retrieve skipped |

## Problem

Issue #1397 says staging on 2026-10-14 returns `INVALID_WEATHER` and no `presentWeather` for `METAR TTPP 080700Z 00000KT 9000 VCSH FEW015 27/24 Q1013 NOSIG=`, and the same for `VCTS` and bare `TS`. That note was last updated at 2026-10-14T01:32:26Z.

## Inventory

| Piece | State on `stage` at `e4258697` |
|-------|--------------------------------|
| `tac_validate` R3 | `VCSH`, `VCTS`, and `TS` produce no `INVALID_WEATHER` |
| `tac2iwxxm.convert` annex3 METAR | `ok` true and `presentWeather` href `…/306/4678/VCSH`, `VCTS`, or `TS` |
| Bulletin wrapper of the same METAR | `ok` true and the `VCSH` href is present |
| [#1413](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1413) | Merged to `stage` at 2026-10-14T15:54:44Z. Summary includes `VCSH`, `TS` / `VCTS`, recent weather, and `FEW///CB`. Closing-issue list is empty. Deploy and staging smoke on that PR were skipped |

## Next

Confirm whether #1397 is already satisfied by #1413 before writing a new requirements delta or changing code.
