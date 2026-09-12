# Routing Plan — S004-issue-555-feedback (EV-004 merged)

| Stage | Required | Status | Notes |
|-------|----------|--------|-------|
| 00-context (scoped) | yes | completed | `issue-555-feedback.md`, `metar-work-history.md` |
| 16-evolve | yes | completed | EV-004 intake approved 2026-06-23 |
| 01-requirements (delta) | yes | completed | F1 #555 + F5 + S003 config delta |
| 02-verify-plan | yes | completed | Consistency after spec delta |
| 04-tech-plan | yes | completed | Migration, API, shared types; ADR-011/012 |
| 05-verify-tech | yes | pending | Execution plan review |
| 07-build | yes | completed | 36/38 tasks — see `07-build-progress.md` |
| 08-verify-build | yes | completed | Initial FAIL → fixed (lint + Vitest green) |
| 09-qa | yes | completed | Initial FAIL → fixed post-build |
| 10-e2e (delta) | yes | completed | Delta Playwright 4/4 green with dev stack |
| 11-verify-impl | yes | completed | UJ-001 + UJ-004 approved |
| 12-verify-deploy | optional | pending | T1.3 migrations, H4 CORS, S003 key rotation |
| 13-deploy-smoke | optional | pending | If user requests deploy |

**Skipped**

| Stage | Rationale |
|-------|-----------|
| 03-plan-tooling | No new guardrails unless 02 surfaces gaps |
| 06-tech-tooling | Stack unchanged (Supabase + FastAPI + React) |
| 14-hotfix | S003 merged into EV-004, not separate hotfix session |
| bug-investigation | Feature work, not regression bug report |

**Features in scope**

| ID | Scope |
|----|-------|
| F1 | Replace results panel; error log preview; session row sync on re-convert |
| F5 | `metar_work_sessions`, REST API, sidebar + My METARs, lifecycle |
| S003 | Supabase service-key + runtime config (prerequisite for F5) |

**Paused session**

| Session | Status | Note |
|---------|--------|------|
| S003-supabase-keys-config | merged into EV-004 | Hotfix work folded into S004 branch |
