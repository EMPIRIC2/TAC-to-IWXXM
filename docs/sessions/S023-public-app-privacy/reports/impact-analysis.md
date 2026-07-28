# Impact analysis — EV-017 / #783

**Session**: S023-public-app-privacy  
**Date**: 2026-07-27

## Docs to update (this cycle)

| Corpus | Path | Status after 01 |
|--------|------|-----------------|
| product | `docs/feature-list.md` | delta done |
| system-spec | `docs/spec.md` | delta done |
| journeys | `docs/user-journeys.md` | delta done |
| tests | `docs/test-plan.md` | delta done |
| api | `docs/api-contract.md` | delta done |
| decisions | `docs/decisions/*` | delta done |
| adr | `docs/adr/ADR-0xx-public-app.md` | pending 04 |
| tech | `docs/env-contract.md`, staging secrets | pending 04/12 |
| config | rate-limit env names | pending 04 |

## Routing (approved Standard)

`00 → 16 → 01 → 02 → 04 → 07 → 08 → 09 → 10 → 11 → 12 → 13`  
Skipped: 03, 05, 06 (unless ADR needs new hooks).

## Milestone sketch (for 04)

1. ADR + inventory  
2. IndexedDB F5/F7 + export/import  
3. Abuse controls on public APIs  
4. FE auth removal  
5. BE `/auth/*` + work-sessions teardown  
6. Privacy center + GPC  
7. Env/E2E/docs cleanup  
