# Execution Plan — Monorepo Migration

> **Project**: METAR to IWXXM Converter
> **Generated**: 2026-06-15
> **Skill**: 04-tech-plan
> **Specs consumed**: feature-list.md, spec.md, migration-plan.md, test-plan.md, user-journeys.md, deploy.md, api-contract.md, dependency-inventory.md, config-spec-monorepo.md

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase 4: CI, Deploy & Validate |
| **Active milestone** | M10: CI/CD |
| **Active task** | T10.3 complete — next T10.4 |
| **Tasks completed** | 53 / 63 |
| **Last updated** | 2026-06-20 |

## Tech Stack Summary

| Category | Choice | Source | Spec Reference |
|----------|--------|--------|----------------|
| Template | `static+api` | workflow-state.yaml | spec.md §System Architecture |
| Python | 3.12 (pinned) | User decision 04-tech-plan | dependency-inventory.md |
| Node | 22 (pinned) | User decision 04-tech-plan | dependency-inventory.md |
| Python workspace | uv | REQ-005 | spec.md §Repository |
| JS workspace | pnpm | REQ-005 | spec.md §Repository |
| API framework | FastAPI + uvicorn | existing | spec.md §apps/backend |
| Frontend | React 18 + Vite 6 + TS 5 | existing | spec.md §apps/frontend |
| Python linter | Ruff (all packages) | User decision | test-plan.md |
| Python formatter | Ruff format | User decision | — |
| Python typechecker | basedpyright | User decision | — |
| JS linter | ESLint 9 + typescript-eslint | existing | apps/frontend |
| JS test | Vitest 4 | existing | test-plan.md |
| E2E | Playwright 1.49 | existing | test-plan.md §E2E |
| Coverage gate | 95% all packages/apps | User decision | test-plan.md |
| Deployment | Render | REQ-009 | deploy.md |
| API deployable | Docker web service | deploy.md | render-platform |
| Frontend deployable | Render Static Site (CDN) | User decision | deploy.md |
| Observability | Render built-in logs only | User decision | — |
| Auth topology | packages/auth in API | ADR-002 | spec.md |
| Vendor sync | Weekly Action (wmo-im only) | User decision | M6, ADR-001 |
| GIFTs sync | Manual only | ADR-004 | REQ-014 |
| CI path filters | Deferred (P2) | User decision | feature-list.md P2 |
| CORS env | `METAR_CORS_ORIGINS` | config-spec | deploy.md |
| Frontend API env | `VITE_API_BASE_URL` | config-spec | deploy.md |
| Production auth | `DISABLE_AUTH=false` | User decision | deploy.md |

### Feature ↔ Milestone mapping

Platform features in `feature-list.md` use different milestone IDs than execution-plan milestones. Use this table when tracing scope:

| Feature (feature-list) | Execution milestone | Key tasks |
|------------------------|----------------------|-----------|
| M1 Monorepo layout | M1, M5, M6, M7, M11 | T1.4, T5.2, T6.2, T7.1, T11.1 |
| M2 Vendor snapshots | M2 | T2.1–T2.5 |
| M3 GIFTs package | M3 | T3.1–T3.5 |
| M4 Auth merged | M4, M5 | T4.2–T4.4, T5.3, T5.5 |
| M5 Workspace tooling | M1 | T1.2–T1.9, T1.6 |
| M6 Vendor upstream sync | M2, M10 | T2.3, T10.3 |
| F1–F4 (product) | M3, M5, M7 | T3.1, T5.7–T5.8, T7.3–T7.4 (regression only; REQ-016) |

## Data Dependencies

| Asset | Type | Size | Staging Status | Needed By Tasks |
|-------|------|------|----------------|-----------------|
| iwxxm schemas | vendor snapshot | ~50 MB | present (submodules) | T2.4, T5.2 |
| iwxxm-codelists | vendor snapshot | ~5 MB | present (submodules) | T2.4 |
| iwxxm-modelling | vendor snapshot | ~10 MB | present (submodules) | T2.4 |
| iwxxm-translation | vendor snapshot | ~2 MB | present (submodules) | T2.4 |
| Golden METAR fixtures | test-data | ~1 MB | verified | T3.1, T11.2 |

**Data management gate**: Vendor trees must reach `verified` under `vendor/schemas/` before T5.2.

## Implementation Phases

### Phase 1: Monorepo Scaffold

**Objective**: Root workspace tooling, shared package scaffold, quality gates (basedpyright, ruff, 95% coverage config).
**Entry gate**: Execution plan approved by user.
**Exit gate**: `make install` succeeds; workspace members resolve; basedpyright + ruff run clean on scaffold; coverage config present for all members.

#### M1: Workspace Root

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T1.1 | Write TC-M001 clone-smoke test skeleton | Test | completed | test-plan.md TC-M001 | — | — |
| T1.2 | Add root `pyproject.toml` uv workspace | Config | completed | spec.md §Repository, REQ-005 | T1.1 | — |
| T1.3 | Add `pnpm-workspace.yaml` | Config | completed | spec.md §Repository | T1.2 | — |
| T1.4 | Scaffold `packages/shared` (Python + TS exports) | Code | completed | spec.md §packages/shared | T1.2, T1.3 | — |
| T1.5 | Write workspace import smoke test | Test | completed | test-plan.md TC-M001 | T1.4 | — |
| T1.6 | Add Makefile `install`, `dev`, `test`, `test-unit`, `tests:e2e`, `vendor-sync` | Config | completed | config-spec-monorepo.md | T1.2, T1.3 | — |
| T1.7 | Configure basedpyright for workspace | Config | completed | User decision | T1.2 | — |
| T1.8 | Configure root ruff (shared rules) | Config | completed | User decision | T1.2 | — |
| T1.9 | Configure 95% coverage gates per package/app | Config | completed | User decision | T1.2 | — |
| T1.10 | Achieve 95% coverage on packages/shared | Test | completed | ADR-007 | T1.4, T1.9 | — |

**Parallelizable**: T1.7, T1.8, T1.9 (after T1.2); T1.10 after T1.4.

#### Phase 1 Gate Check

- [ ] All M1 tasks completed
- [ ] `uv sync` + `pnpm install` succeed at root
- [ ] basedpyright + ruff pass on scaffold
- [ ] Coverage config documented per workspace member

---

### Phase 2: Vendor & Packages

**Objective**: Populate read-only vendor tree; move GIFTs and auth into `packages/`.
**Entry gate**: Phase 1 gate passed.
**Exit gate**: TC-M002 green; TC-M003 baseline captured; packages/gifts and packages/auth at 95% coverage.

#### M2: Vendor Snapshots

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T2.1 | Write TC-M002 manifest integrity tests | Test | completed | test-plan.md TC-M002 | — | — |
| T2.2 | Create `vendor/manifest.json` from submodule SHAs | Config | completed | spec.md §vendor/schemas, ADR-001 | T2.1 | iwxxm-* |
| T2.3 | Implement `scripts/vendor/sync-iwxxm.sh` | Code | completed | migration-plan.md Step 1 | T2.2 | — |
| T2.4 | Populate `vendor/schemas/*` via sync script | Config | completed | M2 feature-list | T2.3 | iwxxm-* |
| T2.5 | Write vendor schema presence tests | Test | completed | test-plan.md §Vendor | T2.4 | vendor trees |

#### M3: GIFTs Package

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T3.1 | Write TC-M003 golden conversion regression tests | Test | completed | test-plan.md TC-M003 | T2.4 | golden fixtures |
| T3.2 | Move `GIFTs/` → `packages/gifts/` | Code | completed | migration-plan.md Step 2, M3 | T3.1 | — |
| T3.3 | Wire `packages/gifts` as uv workspace member | Config | completed | spec.md §packages/gifts | T3.2 | — |
| T3.4 | Migrate gifts lint to ruff; remove flake8/black/isort | Config | completed | User decision | T3.3 | — |
| T3.5 | Achieve 95% coverage on packages/gifts | Test | completed | User decision | T3.4 | — |

#### M4: Auth Package

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T4.1 | Write packages/auth middleware unit tests | Test | completed | test-plan.md TC-M005 | — | — |
| T4.2 | Move `auth/` → `packages/auth/` | Code | completed | migration-plan.md Step 2, M4 | T4.1 | — |
| T4.3 | Wire `packages/auth` as uv workspace member | Config | completed | ADR-002 | T4.2 | — |
| T4.4 | Achieve 95% coverage on packages/auth | Test | completed | User decision | T4.3 | — |

**Parallelizable**: M2 and M4 after T1 gate (independent until Phase 3).

#### Phase 2 Gate Check

- [ ] TC-M002 manifest integrity passes
- [ ] TC-M003 baseline green on packages/gifts
- [ ] packages/gifts + packages/auth ≥ 95% coverage
- [ ] vendor/schemas read-only (no hand edits)

---

### Phase 3: Apps & Auth Merge

**Objective**: Move deployables to `apps/`; merge auth into backend; unify frontend API URL.
**Entry gate**: Phase 2 gate passed.
**Exit gate**: TC-M005 green; docker-compose two services; E2E T2 passes locally.

#### M5: Backend App + Auth Merge

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T5.1 | Write `test_cors_policy.py` for `METAR_CORS_ORIGINS` | Test | completed | test-plan.md H0c | — | — |
| T5.2 | Move `backend/` → `apps/backend/` | Code | completed | migration-plan.md Step 3 | T2.4, T3.3, T4.3 | vendor |
| T5.3 | Mount auth routers at `/auth/*`; remove AUTH_SERVICE_URL | Code | completed | ADR-002, TC-M005 | T5.2, T4.3 | — |
| T5.4 | Rename `ALLOWED_ORIGINS` → `METAR_CORS_ORIGINS` | Config | completed | config-spec-monorepo.md | T5.1, T5.3 | — |
| T5.5 | Write TC-M005 auth-merge integration tests | Test | completed | test-plan.md TC-M005 | T5.4 | — |
| T5.6 | Achieve 95% coverage on apps/backend | Test | completed | User decision | T5.5 | — |
| T5.7 | Write H0i integration test suite | Test | completed | test-plan.md H0i | T5.5 | — |
| T5.8 | Product regression smoke (F2–F4 post-move) | Test | completed | feature-list F2–F4, REQ-016 | T5.6 | — |

#### M6: Frontend App

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T6.1 | Write Vitest tests for unified `VITE_API_BASE_URL` client | Test | completed | test-plan.md H5 | — | — |
| T6.2 | Move `frontend/` → `apps/frontend/` | Code | completed | migration-plan.md Step 3 | T6.1 | — |
| T6.3 | Replace split VITE URLs with `VITE_API_BASE_URL`; wire `VITE_SUPABASE_*`, `VITE_APP_URL` | Code | completed | deploy.md §Integration, config-spec | T6.2 | — |
| T6.4 | Migrate to pnpm; add `tsconfig.json` | Config | completed | REQ-005 | T6.3 | — |
| T6.5 | Achieve 95% coverage on apps/frontend | Test | completed | User decision | T6.4 | — |
| T6.6 | Update docker-compose to two app services (backend + frontend) | Config | completed | deploy.md §Local | T5.5, T6.5 | — |

#### M7: E2E Workspace

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T7.1 | Create `apps/e2e/`; relocate root `tests/*.e2e.spec.ts` | Code | completed | test-plan.md §E2E | T5.5, T6.5 | — |
| T7.2 | Update Playwright config for monorepo paths | Config | completed | user-journeys.md UJ-001–003 | T7.1 | — |
| T7.3 | Verify TC-001, TC-003 E2E pass locally (T2) | Test | completed | test-plan.md | T7.2 | — |
| T7.4 | Verify TC-002 validation pass (UJ-002) in E2E or integration | Test | completed | test-plan.md TC-002 | T7.2, T5.8 | — |

#### Phase 3 Gate Check

- [ ] TC-M005 auth merge passes
- [ ] docker-compose: backend + frontend only (no auth service) — T6.6
- [ ] H0c CORS unit tests green
- [ ] Playwright T2 suite green
- [ ] apps/backend + apps/frontend ≥ 95% coverage

---

### Phase 4: CI, Deploy & Validate

**Objective**: Update CI/CD and Render; remove submodules; enable production auth; connectivity gates.
**Entry gate**: Phase 3 gate passed.
**Exit gate**: CI green; render.yaml valid; H4/H5 pass on staging; TC-M001–M005 all green.

#### M8: Docker & Compose

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T8.1 | Update API Dockerfile (repo-root context, vendor+packages) | Config | completed | deploy.md §Docker | T6.6 | vendor |
| T8.2 | Remove auth Docker image/build from CI | Config | completed | ADR-002 | T8.1 | — |

#### M9: Render & Connectivity

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T9.1 | Rewrite render.yaml: API + static frontend; wire `SUPABASE_*`, `FRONTEND_URL`, `METAR_CORS_ORIGINS` | Config | completed | deploy.md, config-spec | T8.1 | — |
| T9.2 | Remove Loki/Prometheus/Grafana from Blueprint | Config | completed | User decision | T9.1 | — |
| T9.3 | Set `DISABLE_AUTH=false` for production API | Config | completed | User decision | T9.1 | — |
| T9.4 | Write `tests/smoke/test_staging_connectivity.py` | Test | completed | test-plan.md H4 | T9.1 | — |
| T9.5 | Add `scripts/deploy/verify_connectivity.sh` | Code | completed | connectivity-gates.md | T9.4 | — |
| T9.6 | Verify/update `docs/staging-secrets-matrix.md` against Render env | Docs | completed | 04-tech-plan connectivity | T9.1 | — |

#### M10: CI/CD

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T10.1 | Update ci-cd.yml paths; pin Python 3.12 + Node 22 | Config | completed | migration-plan.md Step 7 | T8.2 | — |
| T10.2 | Build frontend from in-repo `apps/frontend` (not external clone) | Config | completed | migration-plan.md | T10.1 | — |
| T10.3 | Add weekly vendor sync GitHub Action | Config | pending | M6, User decision | T2.3 | — |
| T10.4 | Write TC-M004 no-submodule reference tests | Test | pending | test-plan.md TC-M004 | T10.1 | — |

#### M11: Big-Bang Finalize

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T11.1 | Remove `.gitmodules`; deinit submodules | Config | pending | migration-plan.md Step 8, ADR-003 | T10.4 | — |
| T11.2 | Run full suite + TC-M001–M005 migration gate | Test | pending | migration-plan.md §Validation | T11.1 | — |
| T11.3 | Update README, DEVELOPMENT.md, archive stale deploy docs | Docs | pending | migration-plan.md Step 9 | T11.2 | — |
| T11.4 | Run H4/H5 connectivity on staging (UJ-OPS-001) | Test | pending | user-journeys.md UJ-OPS-001 | T9.5, T11.2 | — |

#### Phase 4 Gate Check

- [ ] `.gitmodules` absent (TC-M004)
- [ ] CI green on `feat/monorepo-big-bang` branch
- [ ] render.yaml validates; two deployables + no observability pservs
- [ ] TC-M001–M005 pass
- [ ] H4 CORS + H5 bundle verification pass on staging
- [ ] 95% coverage on all packages and apps
- [ ] `DISABLE_AUTH=false` verified on staging

---

## Connectivity Tasks (cross-cutting)

| Task | Deliverable | Milestone |
|------|-------------|-----------|
| configure_cors | `METAR_CORS_ORIGINS` + `test_cors_policy.py` | M5 (T5.1, T5.4) |
| unify_vite_api | `VITE_API_BASE_URL` in frontend + Render static build | M6 (T6.3) |
| staging_smoke | `tests/smoke/test_staging_connectivity.py` | M9 (T9.4) |
| verify_script | `scripts/deploy/verify_connectivity.sh` | M9 (T9.5) |
| secrets_matrix | `docs/staging-secrets-matrix.md` | M9 (T9.6) |

## Git Strategy

### Branch Workflow

```
main
 └── phase/1-monorepo-scaffold
      ├── feat/M1-workspace-root        → minor PR
      ├── feat/M2-vendor-snapshots      → minor PR
      ├── feat/M3-gifts-package         → minor PR
      └── ...
 └── phase/2-vendor-packages
 └── phase/3-apps-auth-merge
 └── phase/4-ci-deploy-validate
      └── (phase gate) → major PR → main
```

**Big-bang branch**: `feat/monorepo-big-bang` may absorb all milestone branches before single major PR per ADR-003.

### PR Plan

| PR | Type | Milestone/Phase | Branch | Target | Status |
|----|------|-----------------|--------|--------|--------|
| PR-1 | Minor | M1 | feat/M1-workspace-root | phase/1-monorepo-scaffold | open — https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/672 |
| PR-2 | Minor | M2 | feat/M2-vendor-snapshots | phase/2-vendor-packages | pending |
| PR-3 | Minor | M3 | feat/M3-gifts-package | phase/2-vendor-packages | open — https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/673 |
| PR-4 | Minor | M4 | feat/M4-auth-package | phase/2-vendor-packages | open — https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/674 |
| PR-5 | Minor | M5 | feat/M5-backend-auth-merge | phase/3-apps-auth-merge | open — https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/675 |
| PR-6 | Minor | M6 | feat/M6-frontend-app | phase/3-apps-auth-merge | pending |
| PR-7 | Minor | M7 | feat/M7-e2e-workspace | phase/3-apps-auth-merge | pending |
| PR-8 | Minor | M8–M10 | feat/M8-deploy-ci | phase/4-ci-deploy-validate | pending |
| PR-9 | Major | Phase 4 | phase/4-ci-deploy-validate | main | pending |

## Task Tracking

Statuses: `pending` | `in_progress` | `completed` | `blocked` | `deferred`

| Task | Milestone | Phase | Type | Status | Blocked By | Data Deps |
|------|-----------|-------|------|--------|------------|-----------|
| T1.1–T1.10 | M1 | 1 | mixed | pending | — | — |
| T2.1–T2.5 | M2 | 2 | mixed | pending | Phase 1 gate | iwxxm-* |
| T3.1–T3.5 | M3 | 2 | mixed | pending | T2.4 | golden fixtures |
| T4.1–T4.4 | M4 | 2 | mixed | pending | — | — |
| T5.1–T5.8 | M5 | 3 | mixed | pending | Phase 2 gate | vendor |
| T6.1–T6.6 | M6 | 3 | mixed | pending | — | — |
| T7.1–T7.4 | M7 | 3 | mixed | pending | T5.5, T6.5 | — |
| T8.1–T8.2 | M8 | 4 | Config | pending | Phase 3 gate | — |
| T9.1–T9.6 | M9 | 4 | mixed | pending | T8.1 | — |
| T10.1–T10.4 | M10 | 4 | mixed | pending | T8.2 | — |
| T11.1–T11.4 | M11 | 4 | mixed | pending | T10.4 | — |

## Phase Gate Log

| Phase | Gate Check Date | Result | Notes |
|-------|----------------|--------|-------|
| 1 | 2026-06-14 | pass | M1 complete: install, test-unit, ruff, basedpyright, coverage config |
| 2 | — | — | — |
| 3 | 2026-06-20 | pass | M5–M7 complete; docker-compose two services; Playwright T2 gates green |
| 4 | — | — | — |

## Hook Configuration

| Hook | Event | Tool | Config File | Purpose |
|------|-------|------|-------------|---------|
| Lint | afterFileEdit | ruff | `pyproject.toml` | Python style/errors |
| Format | afterFileEdit | ruff format | `pyproject.toml` | Python formatting |
| Typecheck | afterFileEdit | basedpyright | `pyproject.toml` | Python types |
| Scope check | afterFileEdit | scope_check.py | `.cursor/hooks/` | Plan adherence |

## TDD Exceptions (migration moves)

Per 05-verify-tech audit, the following code tasks intentionally lack preceding test tasks — structural moves with regression coverage elsewhere:

| Task | Rationale |
|------|-----------|
| T2.3 | Sync script — covered by T2.1 manifest tests + T2.5 presence tests |
| T2.4 | Vendor populate — T2.5 follows immediately |
| T5.3 | Auth router mount — T5.5 integration tests follow |
| T7.1 | E2E workspace scaffold — T7.3/T7.4 verify behavior |

## Open Questions

- [ ] Confirm Supabase env vars set on Render before T9.3 auth enable
- [ ] Archive legacy GitHub repos (REQ-019) — post-stable deploy, out of migration PR scope
