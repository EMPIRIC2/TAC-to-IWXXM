# Execution Plan — EV-004 (#555 UX + F5 Work History + S003)

> **Project**: METAR to IWXXM Converter  
> **Generated**: 2026-06-23  
> **Skill**: 04-tech-plan (delta)  
> **Session**: S004-issue-555-feedback  
> **Cycle**: EV-004  
> **Branch**: `feat/S004-issue-555-feedback`  
> **Specs consumed**: feature-list.md, spec.md, api-contract.md, test-plan.md, user-journeys.md,
> config-spec.md, env-contract.md, evolve-decisions.md §EV-004, context/issue-555-feedback.md,
> context/metar-work-history.md

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase 5 complete |
| **Active milestone** | M5: E2E & Verification (complete) |
| **Active task** | — (07-build complete) |
| **Tasks completed** | 36 / 38 (T1.3 operator deferred) |
| **Last updated** | 2026-06-24 |

## Tech Stack Summary (EV-004 delta)

Reuses monorepo pins from [execution-plan-monorepo.md](../../.cursor/artifacts/execution-plan-monorepo.md).
New choices for this cycle:

| Category | Choice | Source | Spec Reference |
|----------|--------|--------|----------------|
| Work history DB | Supabase Postgres `metar_work_sessions` | F5 spec | spec.md §F5 |
| Backend DB access | Supabase JWT client (RLS) | ADR-011 (proposed) | api-contract.md |
| Retention | pg_cron daily 03:00 UTC | ADR-012 (proposed) | F5-R8, F5-R11 |
| WIP constraint | Partial unique index per user | ADR-012 (proposed) | F5-R3 |
| Shared types | `packages/shared` TS + backend Pydantic | ADR-011 (proposed) | api-contract.md |
| Frontend sync | 3s debounce PATCH upsert | F5-R6 | user-journeys UJ-004 |
| Admin browse | `GET /admin/work-sessions` + admin page | F5-R14, F5-R31 | api-contract.md |

## Feature ↔ Milestone Mapping

| Feature | Milestone | Deliverable |
|---------|-----------|-------------|
| S003 | M1 | Runtime config, env-check, advisor migrations applied |
| F1 #555 UX | M2 | Replace results; error log panel |
| F5 backend | M3 | Migration, router, TC-004 |
| F5 frontend | M4 | Auto-save, sidebar, My METARs, admin page |
| UJ-001 / UJ-004 E2E | M5 | Playwright + live delta |

## Data Dependencies

| Asset | Type | Staging Status | Needed By |
|-------|------|----------------|-----------|
| Supabase METAR project | Postgres + Auth | present (`ktvxijislbtgqapllmuk`) | M1, M3 |
| Local `supabase db reset` | dev DB | verified | M3 tests |
| Golden METAR fixtures | test-data | verified | M2, M5 |
| `is_admin()` RLS helpers | migration | present | M3 |

**Gate**: S003 M1 complete before `metar_work_sessions` migration applied to production.

## Implementation Phases

### Phase 1: S003 Prerequisite Gate

**Objective**: Complete Supabase config hardening so F5 can rely on publishable-key + JWT pattern.  
**Entry gate**: EV-004 scope approved (16-evolve complete).  
**Exit gate**: `make env-check` pass; runtime `/config.json` loads on staging; migrations 003–006 applied locally.

#### M1: Supabase Config & Migrations Gate

| # | Task | Type | Status | Spec Source | Depends On |
|---|------|------|--------|-------------|------------|
| T1.1 | Test: `make env-check` + `test_h5_runtime_config` green | Test | completed | test-plan H0e | — |
| T1.2 | Config: verify `config/prod.json` COPY in Docker + static deploy inject | Config | completed | config-spec.md | — |
| T1.3 | Config: apply advisor migrations 003–006 to METAR Supabase (operator) | Config | deferred | ADR-010 | — |
| T1.4 | Test: admin_api uses publishable key only (no service role in routes) | Test | completed | ADR-010 | T1.1 |
| T1.5 | Docs: update deploy checklist for key rotation before F5 | Docs | completed | deploy.md | T1.3 |

**Phase 1 gate**: T1.1–T1.4 pass; production keys rotated or waiver recorded for staging-only build.

---

### Phase 2: #555 UX (F1 Delta)

**Objective**: Replace result cards on success; collapsible error log from API `errors`/`issues`.  
**Entry gate**: Phase 1 gate (local dev sufficient).  
**Exit gate**: FileConverter unit tests green; UJ-001 delta covered.

#### M2: Converter UX Polish

| # | Task | Type | Status | Spec Source | Depends On |
|---|------|------|--------|-------------|------------|
| T2.1 | Test: results replace (not append) on successful convert | Test | completed | issue-555 R1, TC-001 | — |
| T2.2 | Code: `setConvertedFiles` replace on success in FileConverter | Code | completed | feature-list F1 | T2.1 |
| T2.3 | Test: error log panel shows `errors` + `issues` on failure/partial | Test | completed | issue-555 R2, F1-R555-2 | — |
| T2.4 | Code: collapsible ErrorLogPanel component + wire partial failures | Code | completed | api-contract convert | T2.3 |
| T2.5 | Test: Vitest regression for conversionStatus + panel persistence until next convert | Test | completed | user-journeys UJ-001 | T2.4 |

**Phase 2 gate**: T2.1–T2.5 pass; no GIFTs/backend conversion changes.

---

### Phase 3: F5 Backend (Work Sessions API)

**Objective**: `metar_work_sessions` table, RLS, REST router, retention cron.  
**Entry gate**: Phase 1 gate.  
**Exit gate**: TC-004 integration tests pass.

#### M3: Database & API

| # | Task | Type | Status | Spec Source | Depends On |
|---|------|------|--------|-------------|------------|
| T3.1 | Test: schema + RLS policy SQL snapshot test | Test | completed | spec.md §F5 | T1.3 |
| T3.2 | Config: migration `20250623000007_metar_work_sessions.sql` (table, RLS, index, cron) | Config | completed | ADR-011, ADR-012 | T3.1 |
| T3.3 | Test: work session Pydantic schemas + status transition unit tests | Test | completed | api-contract.md | — |
| T3.4 | Test: router tests — CRUD, WIP 409, soft-delete, restore | Test | completed | TC-004 | T3.3 |
| T3.5 | Code: `WorkSessionService` via Supabase JWT client | Code | completed | ADR-011 | T3.4 |
| T3.6 | Code: `apps/backend` router `/api/v1/work-sessions` + wire in api.py | Code | completed | api-contract.md | T3.5 |
| T3.7 | Code: `GET /admin/work-sessions` with `require_admin` | Code | completed | F5-R14 | T3.6 |
| T3.8 | Test: integration TC-004 full lifecycle | Test | completed | test-plan TC-004 | T3.7 |

**Parallelizable**: T3.3 can start alongside T3.1–T3.2.

**Phase 3 gate**: TC-004 green; `supabase db reset` applies migration cleanly.

---

### Phase 4: F5 Frontend (Persistence UI)

**Objective**: Auto-save, resume-on-login, sidebar, My METARs, admin browse; integrate #555 error log persistence.  
**Entry gate**: Phase 3 gate (or T3.6 merged with mocked API for parallel UI).  
**Exit gate**: Vitest green; manual smoke login → draft → convert → WIP.

#### M4: Work History UI

| # | Task | Type | Status | Spec Source | Depends On |
|---|------|------|--------|-------------|------------|
| T4.1 | Code: `packages/shared/src/work-session.ts` types + exports | Code | completed | ADR-011 | T3.3 |
| T4.2 | Test: `workSessionApi` client unit tests | Test | completed | api-contract.md | T4.1 |
| T4.3 | Code: `workSessionApi.ts` — CRUD + list with filters | Code | completed | api-contract.md | T4.2 |
| T4.4 | Test: debounced auto-save (3s) + last-write-wins | Test | completed | F5-R6, F5-R25 | — |
| T4.5 | Code: FileConverter — session state, auto-save, status transitions | Code | completed | spec.md §F5 | T4.3, T2.4 |
| T4.6 | Code: WorkHistorySidebar — 5 recent, load session | Code | completed | F5-R19 | T4.5 |
| T4.7 | Code: `/history` My METARs page — status + date filters, trash/restore | Code | completed | user-journeys UJ-004 | T4.3 |
| T4.8 | Code: Admin work sessions read-only page | Code | completed | F5-R31 | T3.7 |
| T4.9 | Code: Guest login → Draft from converter state (F5-R33) | Code | completed | product-decisions S2.2 | T4.5 |
| T4.10 | Code: Finished read-only mode — disable convert/send (F5-R35) | Code | completed | product-decisions S2.4 | T4.5 |
| T4.11 | Test: Vitest workflow tests for M4 behaviors | Test | completed | test-plan | T4.10 |

**Phase 4 gate**: T4.1–T4.11 pass; sidebar + history page render with live API on local stack.

---

### Phase 5: E2E & Verification

**Objective**: Playwright UJ-001 delta + UJ-004; staging connectivity.  
**Entry gate**: Phase 2 + 4 gate.  
**Exit gate**: `make test-e2e` green; TC-LIVE-006 ready for 12-verify-deploy.

#### M5: E2E & Live Delta

| # | Task | Type | Status | Spec Source | Depends On |
|---|------|------|--------|-------------|------------|
| T5.1 | Test: `apps/e2e` UJ-001 delta — replace results + error log | Test | completed | test-plan TC-001 | T2.5 |
| T5.2 | Test: `metar-work-history.e2e.spec.ts` — UJ-004 lifecycle | Test | completed | test-plan TC-004 | T4.11 |
| T5.3 | Test: CORS preflight includes work-sessions routes | Test | completed | connectivity-gates | T3.6 |
| T5.4 | Config: `scripts/deploy/verify_connectivity.sh` work-sessions smoke | Config | completed | 04-tech-plan connectivity | T5.3 |
| T5.5 | Docs: staging-secrets-matrix delta if new env vars | Docs | completed | staging-secrets-matrix | T5.4 |

**Phase 5 gate**: E2E green locally; phase gate log recorded for 11-verify-impl.

---

## Git Strategy

| Item | Value |
|------|-------|
| Branch | `feat/S004-issue-555-feedback` |
| Base | `main` |
| Commit pattern | `[T3.4] test: work session router WIP conflict` |
| Minor PR | After M5 — title `[EV-004] #555 UX + F5 work history` |

### PR Plan

| PR | Scope | Status |
|----|-------|--------|
| EV-004 | Phases 1–5 complete | pending |

## Phase Gate Log

| Phase | Criteria | Status | Date |
|-------|----------|--------|------|
| 1 | env-check + runtime config + migrations | partial (T1.3 deferred) | 2026-06-24 |
| 2 | #555 UX tests green | pass | 2026-06-24 |
| 3 | TC-004 backend green | pass | 2026-06-24 |
| 4 | F5 UI vitest green | pass | 2026-06-24 |
| 5 | E2E UJ-001 + UJ-004 green | pass | 2026-06-24 |

## Task Tracking (master)

Total: **38 tasks** — 15 test, 18 code, 5 config/docs

Dependency graph (critical path):

```
T1.* → T3.2 → T3.6 → T4.5 → T4.11 → T5.2
T2.* (parallel after T1.1) → T4.5, T5.1
```

## Connectivity (04-tech-plan deliverable)

| Deliverable | Task |
|-------------|------|
| CORS on work-sessions routes | T5.3 |
| `tests/unit/test_cors_policy.py` update | T5.3 |
| `scripts/deploy/verify_connectivity.sh` | T5.4 |
| Staging secrets matrix | T5.5 (no new secrets expected — JWT only) |

## Handoff Checklist (04 → 05)

- [x] EV-004 decisions in evolve-decisions.md
- [x] F5 requirements in feature-list, spec, api-contract, user-journeys, test-plan
- [x] ADR-011, ADR-012 drafted
- [ ] User approves technical decisions (batch 1)
- [ ] User approves execution plan structure
- [ ] dependency-inventory.md back-add (supabase-py already listed)

## References

- [GitHub #555](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/555)
- [ADR-011](../../adr/ADR-011-work-sessions-data-access.md)
- [ADR-012](../../adr/ADR-012-metar-work-sessions-retention.md)
- [01-requirements summary](01-requirements-summary.md)
- [02-verify-plan delta](02-verify-plan-delta.md)
