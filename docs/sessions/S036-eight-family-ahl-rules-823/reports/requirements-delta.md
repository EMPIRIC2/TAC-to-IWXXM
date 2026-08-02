# 01-requirements delta — EV-029 / S036

**Date**: 2026-08-01  
**Mode**: delta / multi-Fn  
**UI preview**: N/A (`D-S036-open` Q6=1)

## Locked intake

| Gate | Decision |
|------|----------|
| Phase 0 | `D-S036-open` = 1,1,1,1,1,1 |
| Phase 1 Fn | `D-S036-fn` = 1,1,1,1 — F28 + deepen set; absorb #738/#820/#740; start 01; commit open |

## Document Manifest (proposed — lean)

### Mandatory (delta only)

| # | Document | Change |
|---|----------|--------|
| 1 | Feature List | **F28** Planned + EV-029 deepen block |
| 2 | Spec | F28 + S036/EV-029 sections; F27 non-goal amend |
| 3 | User Journeys | **UJ-043** |
| 4 | Test Plan | UJ-043 map; **TC-EV029-001..008**; **TC-F28-001..006** |

### Recommended

| # | Document | Relevance | Proposal |
|---|----------|-----------|----------|
| 5 | evolve-decisions.md | High | Already has Phase 0–1; refresh acceptance |
| 6 | API Contract | Low | Skip unless 04 finds missing `swxa` product enum |
| 7 | Config Spec | Low | Skip (no new env) |
| 8 | Deploy | Low | Skip until behavior ships (12/13) |
| 9 | Dependency Inventory | Low | Skip unless new deps in 04 |
| 10 | ADR | Medium | Only if AHL shared-model needs new ADR (else amend existing) |

### Excluded

- Data Management Plan — no new external weights/datasets
- Roadmap regen — umbrella tracked via #823 children

## Artifacts updated this stage

| Path | Change |
|------|--------|
| `docs/feature-list.md` | F28 + EV-029 deepen + F23/F26/F27/F6.bulletin notes |
| `docs/spec.md` | F28 + S036/EV-029; F27 #738 note |
| `docs/user-journeys.md` | UJ-043 |
| `docs/test-plan.md` | TC-EV029 + TC-F28 + UJ map |
| `docs/decisions/evolve-decisions.md` | E29-7..10 + acceptance draft |

## Session-open commit

- `49e2a62` — `[EV-029] docs: open S036 eight-family AHL rules cycle (#823)`

## Open for AskQuestion

1. Approve lean Document Manifest (as above)
2. Close 01 → **02-verify-plan**
)
