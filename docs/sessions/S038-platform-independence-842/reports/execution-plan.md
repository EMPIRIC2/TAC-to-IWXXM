# Execution plan — S038 / EV-031 (F30/F31 platform independence / #842 #830 #712)

> **Status**: **approved** — Gate B PASS (`D-S038-04-plan`=1); ADR-033 Accepted  
> **Branch**: `evolve/EV-031-platform-independence-842`  
> **Evolve cycle**: EV-031  
> **Features**: **F30**, **F31**; deepen F5 / F7 / F8 / F21 / F22 / M4  
> **Mode**: delta  
> **Spec sources**: feature-list F30/F31; spec; UJ-045..048; TC-F30/F31/EV031;
> api-contract; env-contract; ADR-033; ADR-020 shapes; ops/supabase-to-do-postgres-migration.md;
> `D-S038-04-b1` / `D-S038-04-b2`

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase C — 07-build |
| **Active milestone** | M4 — FE hybrid + F22 deepen |
| **Active task** | T4.5 — `/config.json` Auth bootstrap + CORS (next) |
| **Tasks** | 21 / 38 completed |
| **Last updated** | 2026-08-03 |

## Tech Stack Summary

| Area | Choice | Source |
|------|--------|--------|
| Template | `static+api+worker` | template |
| Auth package | Restore from `c9cebfa^`; strip admin; Auth-only `/auth/*` | `D-S038-04-b1` Q4=1 |
| JWT verify | **JWKS-only** (Supabase Auth JWKS URL); no HS256 secret path for product | `D-S038-04-b1` Q2=2 |
| Product DB | DigitalOcean Postgres `DATABASE_URL` | E31-data |
| Migrations | Alembic under `apps/backend/` (or `apps/database/`); **CI auto `upgrade head`**; **idempotent** | `D-S038-04-b2` Q3+ |
| Session API | Restore `/api/v1/work-sessions*` — **ADR-020 JSON shapes** | `D-S038-04-b2` Q4=1 |
| Session repo | SQLAlchemy in `apps/backend` against DO | `D-S038-04-b1` Q3=1 |
| F8 | Writers → `DATABASE_URL` (not Supabase PostgREST) | E31-f8 |
| FE | Hybrid: IndexedDB guest + Auth login + auto-upload; F22 deepen | F31 |
| Data migrate | `pg_dump`/`pg_restore` (+ verify script); one-time | `D-S038-04-b2` Q3=1 |
| Hostnames | Placeholder DOKS URLs until M6 pins DNS | `D-S038-04-b2` Q1=1 |
| Soak | **7 days** dual-traffic after DOKS primary → Render decommission | `D-S038-04-b2` Q2=1 |
| ADR | Accept **ADR-033** at Gate B | `D-S038-04-b2` Q4=1 |
| Connectivity | H4–H5 **required** | `D-S038-tp` |
| Deploy | DOKS cutover (`doks-depth`=3); Render transitional | E31-host |

## Interview locks

| ID | Decision |
|----|----------|
| D-S038-04-b1 | **1,2,1,1** — M0–M7; JWKS-only; Alembic in backend; restore auth from git |
| D-S038-04-b2 | **1,1,1(+CI),1** — placeholder DNS; 7d soak; pg_dump + **CI auto idempotent Alembic**; ADR-020 wire + ADR-033 @ Gate B |
| D-S038-04-plan | **1** — Approve plan + accept ADR-033 → 07 @ T0.1 |

## Feature ↔ Milestone Mapping

| Fn / AC | Milestone | Deliverable |
|---------|-----------|-------------|
| ADR-033 + #830 amend | M0 | Accepted ADR; issue rewrite; env/deps pins |
| F31 Auth / M4 | M1 | `packages/auth` + JWKS `/auth/*` |
| F31 sessions + F30 DB | M2 | Alembic + work-sessions on DO; CI migrate |
| F8 / F30 | M3 | Worker `DATABASE_URL` writers |
| F31 FE + F22 | M4 | Hybrid UI + guest notice + privacy deepen |
| F30 migrate | M5 | Supabase product → DO one-time |
| F30 DOKS | M6 | IaC + cutover + 7d soak |
| Verify | M7 | H4–H5 + TC-F30/F31 live + Render decommission gate |

## Data Dependencies

| Asset | Staging | Needed By |
|-------|---------|-----------|
| Pre-delete `packages/auth` tree (`c9cebfa^`) | git history | M1 |
| ADR-020 `tac_work_sessions` / wire shapes | docs + legacy | M2 |
| Legacy Supabase product rows | ops export | M5 |
| DO Postgres + DOKS cluster | provision | M2 / M6 |
| Model weights / corpora | **N/A** | — |

## CI migration contract (Batch 2 amend)

1. PR/CI jobs that need Postgres run **`alembic upgrade head`** against the job’s `DATABASE_URL` (service container) before tests that touch schema.
2. Migrations must be **idempotent**: re-running `upgrade head` on an already-migrated DB is a no-op (Alembic revision table); revisions themselves must be safe to apply once (no destructive unguarded DDL on re-apply beyond Alembic’s model).
3. Deploy path (DOKS / transitional Render): migrate step before/with API rollout (`upgrade head` in release job or init container) — same command as CI.
4. Unit test: double-`upgrade head` green (TC-EV031-002 deepen).

## Milestones & Tasks (TDD order)

`evolve_cycle_id: EV-031` · `feature_ids: [F30, F31]`

**Work order:** #830 (M0–M5) → #712 DOKS (M6) → verify (M7).

### M0 — Baseline / ADR / #830 amend

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T0.1 | Docs | Accept ADR-033; note ADR-031 partial supersession; ADR-020 shapes restored for server sessions | ADR-033; `D-S038-04-b2` | — | completed |
| T0.2 | Docs | Amend #830 acceptance (Auth-kept; strip data plane); link F30/F31 | `D-S038-830-amend` | T0.1 | completed |
| T0.3 | Docs | Pin deps: `alembic`, SQLAlchemy, JWKS client stack; update dependency-inventory + env-contract (JWKS-only; drop secret-as-primary) | `D-S038-04-b1` Q2=2 | T0.1 | completed |
| T0.4 | Docs | Placeholder DOKS hostnames in deploy/env; soak=7d checklist stub | `D-S038-04-b2` Q1/Q2 | T0.1 | completed |

### M1 — Auth restore (JWKS)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T1.1 | Test | Auth unit: JWKS fetch/verify happy + reject bad/expired; `/auth/login|me` contract (no admin) | TC-F31-001; TC-EV031-004 | T0.3 | completed |
| T1.2 | Code | Restore `packages/auth` from `c9cebfa^`; strip admin; JWKS-only verify; mount `/auth/*` on backend | F31; ADR-033 | T1.1 | completed |
| T1.3 | Config | Workspace/uv/Makefile/Docker/CI wire `packages/auth`; Auth env for JWKS URL | env-contract | T1.2 | completed |
| T1.4 | Test | Convert/lint/validate remain JWT-free (TC-EV031-003 / amend TC-F21) | TC-EV031-003 | T1.2 | completed |

### M2 — DO Postgres + Alembic + work-sessions

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T2.1 | Test | Alembic: empty DB → head; **second `upgrade head` no-op** (idempotent); schema matches `tac_work_sessions` | TC-EV031-002 | T0.3 | completed |
| T2.2 | Code | Alembic tree under `apps/backend/` (or `apps/database/`); initial revision for sessions (+ F8 tables if co-located) | F30; ADR-033 | T2.1 | completed |
| T2.3 | Config | CI: Postgres service + auto `alembic upgrade head` before schema-touching tests; document make target | `D-S038-04-b2` CI amend | T2.2 | completed |
| T2.4 | Test | Work-sessions API CRUD + JWT gate (ADR-020 wire); guest path untouched | TC-F31-002..004; UJ-046 | T1.2, T2.2 | completed |
| T2.5 | Code | SQLAlchemy session repository + restore `/api/v1/work-sessions*` (pydantic) | api-contract; ADR-020 | T2.4 | completed |
| T2.6 | Test | No Supabase PostgREST product writes from API (TC-F30-001) | TC-F30-001 | T2.5 | completed |

### M3 — F8 → DATABASE_URL

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T3.1 | Test | Worker store/quarantine against Postgres URL (no service-role PostgREST) | TC-F30-003; UJ-014 | T2.2 | completed |
| T3.2 | Code | Retarget F8 writers to SQLAlchemy/`DATABASE_URL`; drop Supabase DB client path | F30; ADR-018 amend | T3.1 | completed |
| T3.3 | Config | Worker env + deploy docs: `DATABASE_URL` required; remove product Supabase DB secrets from worker | env-contract | T3.2 | completed |

### M4 — FE hybrid + F22 deepen

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T4.1 | Test | Vitest/Playwright: guest IndexedDB + persistent loss notice; login → auto-upload; privacy gates | TC-F31-005; UJ-045..047 | T2.5 | completed |
| T4.2 | Code | Restore optional Auth FE client (publishable); wire login UX; keep public convert | F31; F21 amended | T4.1 | completed |
| T4.3 | Code | Auto-upload eligible local drafts on login; server session list for logged-in | `D-S038-guest-merge`=2 | T4.2 | completed |
| T4.4 | Code | F22 deepen: gate guest IndexedDB; disclose Auth cookies | F22; UJ-047 | T4.2 | completed |
| T4.5 | Config | `/config.json`: `api.baseUrl` + Auth bootstrap; CORS origins for DOKS FE (placeholder OK) | config-spec | T4.2 | pending |

### M5 — One-time Supabase → DO migrate

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T5.1 | Docs | Finalize table/column map in `ops/supabase-to-do-postgres-migration.md` | TC-EV031-001 | T2.5, T3.2 | pending |
| T5.2 | Code | Verify script: row counts / sample checksum after restore | TC-EV031-001 | T5.1 | pending |
| T5.3 | Ops | Run `pg_dump`/`pg_restore` (or SQL export) into DO; dry-run then cut | F30; ops note | T5.2 | pending |
| T5.4 | Test | Post-migrate login session CRUD against DO; zero product Supabase DB traffic | TC-EV031-004; TC-F30-002 | T5.3 | pending |

### M6 — DOKS IaC + cutover + soak (#712)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T6.1 | Infra | DOKS manifests/Helm/Blueprint: API + FE static + worker; secrets (`DATABASE_URL`, Auth JWKS/url) | #712; F30 | T3.3, T4.5 | pending |
| T6.2 | Config | Release job: **idempotent** `alembic upgrade head` before/with API deploy | CI migration contract | T2.3, T6.1 | pending |
| T6.3 | Ops | Pin real DNS / `LIVE_*` / `config/prod.json`; CORS for DOKS FE | `D-S038-04-b2` Q1 | T6.1 | pending |
| T6.4 | Ops | Cutover smoke UJ-048 / TC-F30-004..005; start **7-day** soak | UJ-048; soak=7d | T6.2, T6.3 | pending |
| T6.5 | Ops | After soak: Render decommission checklist; archive Render `LIVE_*` as historical | doks-depth=3 | T6.4 | pending |

### M7 — H4–H5 / live verify / close

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T7.1 | Test | Playwright + live: public convert + Auth session + guest notice | TC-F31-*; H6 | M4, M6 | pending |
| T7.2 | Test | H4–H5 connectivity on DOKS URLs | connectivity-gates; `D-S038-tp` | T6.3 | pending |
| T7.3 | Test | TC-F30-006 / TC-EV031-* green on target topology | test-plan | T5.4, T6.4 | pending |
| T7.4 | Docs | CHANGELOG / deploy-report / evolve-summary stubs; CORPUS parity note | docs corpus | T7.1–T7.3 | pending |

## Phase Gate Check (B → C)

| Criterion | Status |
|-----------|--------|
| Execution plan tasks cover F30/F31 ACs + UJ-045..048 | **PASS** (`D-S038-04-plan`=1) |
| ADR-033 Accepted at Gate B | **PASS** |
| CI auto + idempotent Alembic in plan | **yes** (T2.1/T2.3/T6.2) |
| H4–H5 tasks present | **yes** (T7.2) |
| #830 before #712 ordering | **yes** (M0–M5 → M6) |
| 05/06 skipped unless new dep forces re-add | **PASS** — 05/06 remain skipped |

## PR Plan

| PR | From → To | When | Status |
|----|-----------|------|--------|
| Evolve PR | `evolve/EV-031-…` → `main` | After Phase D / cycle close | pending |

## Git Strategy

- Branch: `evolve/EV-031-platform-independence-842`
- One task ≈ one atomic commit where practical; milestone PRs optional
- Commit message: `[Tm.n] type: …` or `[EV-031] …` for docs/plan

## Risks

| Risk | Mitigation |
|------|------------|
| JWKS outage breaks login | Cache JWKS keys with TTL; convert stays public |
| Migrate data loss | Dry-run checksum; keep Supabase dump archive |
| Dual-host CORS confusion during soak | Document primary DOKS; Render read-only or drain |
| Alembic drift vs legacy Supabase schema | Map columns explicitly in T5.1 before load |
