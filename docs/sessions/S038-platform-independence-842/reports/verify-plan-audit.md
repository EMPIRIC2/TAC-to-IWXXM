# Verify Plan Audit — S038 / EV-031 (02-verify-plan delta)

**Session:** S038-platform-independence-842  
**Cycle:** EV-031  
**Branch:** `evolve/EV-031-platform-independence-842`  
**Corpus under audit:** `fc3bbe5` + C1–C5 fix-in-place  
**Started:** 2026-08-03  
**Completed:** 2026-08-03  
**Mode:** delta (F30/F31 + deepen F5/F7/F8/F21/F22/M4)  
**Verdict batch:** `D-S038-02-batch-c` = **1,1,1**

## Inventory

| # | Document | Path | Status |
|---|----------|------|--------|
| 1 | Feature List | `docs/feature-list.md` | audited + C3 fixed |
| 2 | Spec | `docs/spec.md` | audited + C2 fixed |
| 3 | User Journeys | `docs/user-journeys.md` | audited + C5 fixed |
| 4 | Test Plan | `docs/test-plan.md` | audited + C4 (TC-LIVE-004) fixed |
| 5 | Config Spec | `docs/config-spec.md` | audited + C1 fixed |
| 6 | Env Contract | `docs/env-contract.md` | audited |
| 7 | API Contract | `docs/api-contract.md` | audited + C4 historical labels |
| 8 | Deploy | `docs/deploy.md` | audited |
| 9 | Dependency Inventory | `docs/dependency-inventory.md` | audited |
| 10 | ADR-033 | `docs/adr/ADR-033-platform-independence-auth-do-doks.md` | audited (stays Proposed) |
| 11 | Migration note | `docs/ops/supabase-to-do-postgres-migration.md` | audited |

## Consistency checklist (Phase 4)

| Check | Result |
|-------|--------|
| Feature ↔ Spec (F30/F31) | **PASS** |
| Feature ↔ Journey | **PASS** — UJ-045..048 (+ deepen 001/003/004/033) |
| Journey ↔ Test | **PASS** — TC-F30/F31/EV031 mapped |
| Feature ↔ Test | **PASS** |
| Spec ↔ Config | **PASS** — C1 fixed (`api.baseUrl` + `/auth`) |
| Test ↔ Acceptance | **PASS** |
| Cross-doc naming | **PASS** — C2–C5 fixed |
| Scope boundaries | **PASS** |
| Connectivity H4–H5 | **PASS** — required this cycle (`D-S038-tp`) |
| Template `static+api+worker` | **PASS** |

## Auto-approved (high confidence)

| ID | Statement | Source |
|----|-----------|--------|
| H1 | Supabase is Auth/JWT only; product DB is DO Postgres | E31-auth/data |
| H2 | Convert/lint/validate/disseminate remain public (no JWT) | E31-F30 |
| H3 | Guests: IndexedDB + persistent loss notice; F22 gates | E31-session / uj |
| H4 | Logged-in: JWT → work-sessions on DO; auto-upload on login | E31-guest-merge |
| H5 | DOKS prod cutover; Render retire after soak | E31-host / doks=3 |
| H6 | F8 writers use `DATABASE_URL` (not Supabase DB) | E31-f8 |
| H7 | Restore `packages/auth` + `/auth/*` + work-sessions* | E31-spec-topo |
| H8 | One-time migrate Supabase product rows → DO | E31-spec-data |
| H9 | TC-F30/F31/EV031 accepted; H4–H5 required | D-S038-tp |
| H10 | Gaps (hostnames, JWT pin, soak, Alembic layout) deferred to 04 | D-S038-01-gate-a |

**Auto-approved count:** 10

## Contradictions — resolved (`D-S038-02-batch-c` Q1=1)

| ID | Verdict | Action |
|----|---------|--------|
| **C1** | modified | `config-spec.md` Validation Rules — `api.baseUrl` covers `/api/v1` + `/auth` |
| **C2** | modified | `spec.md` U2/U6 — optional Auth + guest IndexedDB + logged-in DO persist |
| **C3** | modified | `feature-list.md` F21 historical label; Non-Goals S023/S008 amended for F30/F31 |
| **C4** | modified | `api-contract.md` historical F21 rows labeled; `test-plan.md` TC-LIVE-004 Auth-gone → F31 amend |
| **C5** | modified | `user-journeys.md` T3 DOKS note; UJ-014 → `DATABASE_URL` writers |

## Medium statements — resolved (`D-S038-02-batch-c` Q2=1)

| ID | Verdict | Notes |
|----|---------|-------|
| **M1** | approved | ADR-033 remains **Proposed** until 04 / Gate B |
| **M2** | approved | Alembic in dependency-inventory as draft; pin in 04 |
| **M3** | approved | JWT secret vs JWKS both allowed until 04 pin |

## Gate A

| Criterion | Result |
|-----------|--------|
| 01-requirements completed | **PASS** (`fc3bbe5`) |
| 02 consistency + contradictions | **PASS** (C1–C5 fixed) |
| Medium/low reviewed | **PASS** (M1–M3 keep drafts) |
| 03-plan-tooling | **skipped** (Standard) |

**Gate A product: PASS** → handoff **04-tech-plan** (`D-S038-02-batch-c` Q3=1).

## Progress

- Pass 1 auto-approve: **done**
- Pass 2 C1–C5 + M1–M3: **done**
- Gate A: **PASS**
- Next: **04-tech-plan** (delta)
