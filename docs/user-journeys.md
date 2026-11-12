# User journeys

> Matrix: [user-journeys.csv](user-journeys.csv) 
> Tests: [test-plan.csv](test-plan.csv) 
> Last updated: 2026-11-10

The CSV matrix is the source of truth for journey rows.
This file defines columns and linkage rules only.

## Columns

| Column | Meaning |
|--------|---------|
| `id` | Stable journey id used by tests and automation |
| `name` | Short journey name in plain language |
| `entry_point` | UI, API, worker, or maintainer entry |
| `feature` | Related capability name from [product-requirements.md](product-requirements.md) |
| `e2e_tier` | How far automation goes (unit, API, browser, live, or CI) |
| `primary_test_ids` | Test ids from [test-plan.csv](test-plan.csv) |
| `test_paths` | Concrete test modules or specs when known |
| `status` | active, amended, superseded, or planned |
| `notes` | Extra linkage detail (for example a Makefile target) |

## Rules

1. Do not put journey ids in operator-visible UI copy.
2. Every active operator journey must list at least one test id or test path.
3. Sign off end-to-end work against CSV ids, not against local feeder prose.
4. Full narrative dumps may exist under local `docs/local-feeders/`.
