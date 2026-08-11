# 01-requirements — EV-056 / S066 (delta)

**Mode**: delta (deepen F7.q — #988)  
**Status**: **completed** (`D-S066-01-ac=1`)  
**Corpus**: [Corpus: product §F7.q] [Corpus: journeys §UJ-056] [Corpus: tests] [Corpus: decisions]

## Document manifest (approved)

| Doc | Action |
|-----|--------|
| `docs/feature-list.md` | F7 / F7.q EV-056 deepen + AC1–AC5 |
| `docs/user-journeys.md` | UJ-056 deepen (detail route + hunk fold) |
| `docs/test-plan.md` | TC-EV056-001..005; UJ-056 map |
| `docs/decisions/requirements-decisions.md` | §EV-056 |
| `docs/decisions/evolve-decisions.md` | §EV-056 |
| api-contract / config / system-spec | **skip** — no API/`match_status` change |

## Acceptance (approved `D-S066-01-ac=1`)

| ID | Criterion |
|----|-----------|
| AC1 | List → `/quality/:stem` shareable + back-to-list |
| AC2 | Official/Converted/TAC panes; pretty C14N normalized |
| AC3 | Collapsible equal-context hunks (default 3; expand hunk/all) |
| AC4 | Unequal SIGMET stems navigable/readable on staging |
| AC5 | UJ-056 / TC-EV056; FE unit + Playwright; H4–H5 via 13 |

## Phase 0 locked

| ID | Choice |
|----|--------|
| D-S066-route-shape | 1 — `/quality/:stem` |
| D-S066-context-n | 1 — 3 lines |
| D-S066-list | 1 — navigate; back to list |
| D-S066-ui-preview | 1 — http://127.0.0.1:18000/ |

## Out of scope

- C14N / `match_status` / corpus regen
- New npm diff library
- Promote to main
