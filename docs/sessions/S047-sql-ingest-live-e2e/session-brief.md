---
session_id: S047-sql-ingest-live-e2e
type: feature
status: in_progress
branch: evolve/EV-039-sql-ingest-live-e2e
started_at: 2026-08-06
completed_at: null
intent: "Live local multi-DB SQL ingest Playwright verification (Postgres/MySQL/SQL Server/SQLite) plus teardown hygiene across integration, e2e, and local harnesses"
orchestrator: 16-evolve
evolve_cycle_id: EV-039
prior_session: S046-iwxxm-corpus-residuals
prior_evolve_cycle_id: EV-038
github_issues: []
context_briefs:
  - docs/context/sql-ingest-live-e2e.md
standing_docs_touched:
  - docs/feature-list.md
  - docs/test-plan.md
  - docs/user-journeys.md
  - docs/tech-spec.md
  - docs/decisions/evolve-decisions.md
feature_ids: []
deepen_feature_ids:
  - F16
feature_note: "Deepen F16 — live local BYOC SQL upload e2e + teardown; no new Fn expected"
route_status: in_progress
current_stage: 02-verify-plan
ui_preview: declined
decisions:
  D-S047-open: "Q1=1 Q2=1 Q3=1 Q4=1 Q5=2"
  D-S047-ac: "1"
---

# Session S047 — sql-ingest-live-e2e

## Intent

Pass on SQL ingest testing: stand up **local Postgres, MySQL, SQL Server, and SQLite**
(all F16-supported dialects), write **Playwright** tests that upload into those live local
DBs, and ensure **integration / e2e / local** suites tear down containers, files, and
processes so nothing lingers. [Corpus: product §F16] [Corpus: tests] [Corpus: journeys §UJ-027]

## Goal (one sentence)

Prove F16 multi-DB BYOC upload works against local live engines and leave zero leftover
artifacts or long-running processes after tests.

## Phase 0 (locked 2026-08-06 — chat `1,1,1,1,2`)

| ID | Decision |
|----|----------|
| Q1 | Open **S047** → **EV-039** (feature / deepen F16) |
| Q2 | **All four** DB engines: Postgres + MySQL + SQL Server + SQLite |
| Q3 | Teardown mandate: **integration + e2e + local** (audit + fix gaps) |
| Q4 | Live DBs via **Docker Compose profile** + Playwright against local stack |
| Q5 | UI preview: **No** — docs/repo only for now |

## Scope

### In

- Docker Compose overlay/profile for disposable Postgres, MySQL, SQL Server (SQLite file path)
- Playwright live (non-mocked) preflight + send against those URIs for each dialect
- Allowlist / SSRF posture for local compose hostnames (dev/test only) [Corpus: adr/ADR-029] [Corpus: adr/ADR-030]
- Teardown audit + fixes: pytest/integration fixtures, Playwright global teardown, compose `down -v` / container stop
- Test-plan / journey deltas for new TC / UJ rows [Corpus: tests] [Corpus: journeys]

### Out of scope

- New sink vendors beyond F16 four dialects
- Live WIS2 / EDIS / F19 BYOC destinations
- Production or staging deploy of SQL containers
- New product Fn (deepen F16 only unless 01 discovers a gap)
- Non-deployed UI preview this cycle (declined)

## Routing plan

See [routing-plan.md](./routing-plan.md). **Preset: Standard.**

## Links

- Standing: [feature-list.md](../../feature-list.md) §F16, [test-plan.md](../../test-plan.md), [user-journeys.md](../../user-journeys.md) UJ-027, [tech-spec.md](../../tech-spec.md)
- Prior: S019 / EV-014 (F16 mock BYOC close), package Testcontainers writer-contract tests
- Context: [sql-ingest-live-e2e.md](../../context/sql-ingest-live-e2e.md)
