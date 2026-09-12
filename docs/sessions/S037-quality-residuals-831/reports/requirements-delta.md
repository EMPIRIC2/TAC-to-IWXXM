# 01-requirements delta — EV-030 / S037

**Date**: 2026-08-02  
**Mode**: delta / multi-Fn  
**UI preview**: declined (`D-S037-open` Q3=2)

## Locked intake

| Gate | Decision |
|------|----------|
| Phase 0 | `D-S037-open` = 1,1,2,1 |
| Routing | `D-S037-route` = 1 — Standard |
| Phase 1 Fn | `D-S037-fn` = 1,1,1 — F29 + deepen F23/F12/F2/F13/F9/F26/F27; start 01; commit open `@ f88e9cb` |

## Document Manifest (proposed — lean)

### Mandatory (delta only)

| # | Document | Change |
|---|----------|--------|
| 1 | Feature List | **F29** Planned + EV-030 deepen blocks (#829/#820) |
| 2 | Spec | F29 + S037/EV-030; mark EV-029/F28 Done |
| 3 | User Journeys | **UJ-044** |
| 4 | Test Plan | UJ-044 map; **TC-EV030-001..006**; **TC-F29-001..007** |

### Recommended (locked `D-S037-E30-M` = 2)

| # | Document | Relevance | Decision |
|---|----------|-----------|----------|
| 5 | evolve-decisions.md | High | Included (E30-*) |
| 6 | API Contract | High | **Amend** — EV-030 endpoint review; #829 catalog/menu tier note (no new product enum) |
| 7 | Config Spec | Low | Skip (no new env) |
| 8 | Deploy | Low | Skip until 12/13 |
| 9 | Dependency Inventory | Low | Skip unless 04 adds deps |
| 10 | ADR | Medium | Session design note for #831; full ADR only if harness needs standing decision |

### Excluded

- Data Management Plan — no new external weights/datasets
- Roadmap regen — tracked via #831/#829/#820

## Artifacts updated this stage

| Path | Change |
|------|--------|
| `docs/feature-list.md` | F29 + EV-030 deepen notes |
| `docs/spec.md` | F29 + S037/EV-030; F28/EV-029 → Done |
| `docs/user-journeys.md` | UJ-044 |
| `docs/test-plan.md` | TC-EV030 + TC-F29 + UJ map |
| `docs/decisions/evolve-decisions.md` | E30-7..10 |
| `docs/api-contract.md` | S037 / EV-030 endpoint review + #829 catalog note |

## Commits

- `f88e9cb` — session open
- *(this commit)* — 01 delta + close → 02

## Gate

- Manifest **2** + close 01 **1** → **02-verify-plan** (`D-S037-E30-M`)
