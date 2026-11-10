# Test plan

> Matrix: [test-plan.csv](test-plan.csv) 
> Journeys: [user-journeys.csv](user-journeys.csv) 
> Last updated: 2026-11-10

The CSV matrix is the source of truth for test-case and coverage rows.
This file defines columns, test tiers, and linkage rules.

## Columns

| Column | Meaning |
|--------|---------|
| `id` | Stable test id or coverage id |
| `title` | Short title |
| `level` | Unit, API, browser, live, coverage, or other |
| `feature` | Related capability name when known |
| `journey_id` | Linked journey id when known |
| `assert` | Assertion summary when extracted |
| `test_path` | File or module path when known |
| `command` | Makefile or CI command when known |
| `gate` | Quality gate label when known |
| `status` | documented, mapped, active, or deprecated |
| `notes` | Extraction notes or extra links |

## Live test tiers

| Tier | Scope | Typical command |
|------|-------|-----------------|
| Local unit and package CI | Libraries and backend without live hosts | `make test-unit` |
| Live API | Health, convert, and validate against a live API | `make test-live-api` |
| Live connectivity | CORS preflight and frontend bundle URLs | `make test-live-connectivity` |
| Live browser | Playwright operator journeys | `make test-live-e2e` |
| Live bulletin | Multi-report bulletin split, convert, and Schematron | `make test-live-bulletin` |
| Full live sequence | Connectivity, then API, then browser, then bulletin | `make test-live` |

## Rules

1. New tests that prove a journey must update both CSVs in the same change set.
2. Prefer concrete paths in `test_path` over prose descriptions.
3. Coverage rows summarize journey-to-test maps. Prefer executable test rows for
 cases that run in CI.
4. Full legacy narrative may exist under local `docs/local-feeders/`.
5. Some extracted rows still have empty assert or path cells. Treat those as
 open backfill work in [issues.csv](issues.csv).

## Coverage metrics

CI enforces **100%** line+branch coverage on the inventoried Python, Vitest, and
`scripts/` surfaces (`fail_under = 100`). Standing gate docs:
TC-EV080-009 and ADR-007 (local architecture decision copy when present).

