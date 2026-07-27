# 01-requirements report — S021 / EV-016

**Stage**: 01-requirements (delta)  
**Date**: 2026-07-22  
**Feature**: F7.g deepen (#780)  
**Status**: completed

## Intake (Batch 2)

| ID | Decision |
|----|----------|
| E16-5 | UJ-032 + TC-F7-008 |
| E16-6 | F7 stays Planned; slice F7.g |
| E16-7 | Happy-path IWXXM only; skip soft-fail + file-upload queue |
| E16-8 | Thin hazard fixtures: in-repo only; allow 1 + document gap |
| E16-9 | Spec set: feature-list, user-journeys, test-plan, light spec |

## Artifacts updated

| Doc | Delta |
|-----|-------|
| `docs/feature-list.md` | F7.g slice; golden-examples deepen; F7.g AC; source #780 |
| `docs/user-journeys.md` | UJ-032 index + journey body |
| `docs/test-plan.md` | UJ-032 map; TC-F7-008; connection row; F7.g gate |
| `docs/spec.md` | F7.g frontend + component notes |
| `docs/decisions/evolve-decisions.md` | Batch 2 E16-5..E16-9 |
| `docs/decisions/requirements-decisions.md` | EV-016 / F7.g table |

## Non-updates (by design)

- `api-contract.md`, `config-spec.md`, `deploy.md` env — no changes
- No new ADR (static FE catalog; reuse ADR-024 modes)

## Next

02-verify-plan consistency pass on F7.g / UJ-032 / TC-F7-008 deltas.
