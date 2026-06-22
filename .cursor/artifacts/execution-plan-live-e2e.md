# Execution Plan — Live E2E & Integration Testing

> **Snapshot status (2026-06-22):** Implementation complete on branch `feat/live-test-harness` (PR #682).
> Task statuses below reflect delivery; this artifact is retained for traceability, not active tracking.

> **Project**: METAR to IWXXM Converter  
> **Generated**: 2026-06-22  
> **Skill**: 04-tech-plan (delta)  
> **Evolve cycle**: LIVE-E2E-001  
> **Feature IDs**: F1, F2, F3 (UJ-001–003 T3), UJ-OPS-001  
> **Specs consumed**: `docs/test-plan.md`, `docs/context/live-e2e-integration.md`, `docs/deploy.md`, `docs/staging-secrets-matrix.md`, `docs/requirements-decisions.md`, `.cursor/artifacts/config-spec-live-e2e.md`

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase LIVE-4: Cleanup & Signoff (complete) |
| **Active milestone** | M7: Documentation & ADR (complete) |
| **Active task** | — |
| **Tasks completed** | 22 / 22 |
| **Last updated** | 2026-06-22 |

### Live environment (verified 2026-06-22)

| Role | URL | Status |
|------|-----|--------|
| API | `https://metar-to-iwxxm-api.onrender.com` | `/health` 200, `gifts_available: true` |
| Frontend | `https://metar-to-iwxxm-frontend-v4-web.onrender.com` | HTTP 200 |
| Auth | `POST /auth/login` on merged API | 401 for bad creds (route present) |

### Gap summary

| Component | Local | Live | Gap |
|-----------|-------|------|-----|
| H3 pytest | — | `test_live_api_health.py` exists | No Makefile target; no login JWT fixture; `live_api` marker missing from root `pyproject.toml` |
| H4–H5 | H0c unit | `verify_connectivity.sh` + `test_staging_connectivity.py` | Uses `STAGING_*` env vars; no `make test-live-connectivity` |
| H6 Playwright | 12 specs, local `webServer` | — | `webServer` always starts; no remote mode |
| Legacy | — | `tests/test_playwright_e2e.py` | Still targets suspended `auth-v2` |

**Prerequisite note**: E2E-001 schema path fix applied locally (per `docs/implementation-verification.md`); live validate must be re-verified after harness lands.

## Tech Stack Summary

| Category | Choice | Source |
|----------|--------|--------|
| Live API tests | pytest + httpx (`live_api` marker) | `test-plan.md` H3 |
| Connectivity | `verify_connectivity.sh` + pytest `live` marker | H4–H5 |
| Live UI tests | Playwright (`apps/e2e/`) | H6, UJ-001–003 |
| Auth token | Runtime JWT via `POST /auth/login` | LIVE-003, ADR-002 |
| Resilience | 3× retry, 30s backoff; 429 exponential backoff | LIVE-008, LIVE-009 |
| CI policy | Manual/Makefile only — no GHA live job | LIVE-002, LIVE-012 |
| Env naming | Canonical `LIVE_*`; deprecate `STAGING_*` / `E2E_*` | LIVE-005 |

## Data Dependencies

| Asset | Type | Staging Status | Needed By |
|-------|------|----------------|-----------|
| Admin credentials | secret (`.env`) | user-provided | T3.1+, T4.4, T6.2 |
| METAR fixtures | repo `test-data/` | verified | T3.3, H6 specs |
| Live JWT | runtime | obtained at test time | T3.2, H3 auth tests |

No new external datasets required.

## Implementation Phases

### Phase LIVE-1: Live Harness Foundation

**Objective**: Makefile targets, env var consolidation, pytest markers.  
**Entry gate**: User approves this execution plan.  
**Exit gate**: `make test-live-connectivity` runs H4–H5 against Render with `LIVE_*` vars.

#### M1: Env & Makefile Scaffold

| # | Task | Type | Status | Spec Source | Depends On |
|---|------|------|--------|-------------|------------|
| T1.1 | Add `live_api` marker to root `pyproject.toml` | Config | completed | test-plan.md H3 | — |
| T1.2 | Document `LIVE_*` vars in `.env.example` | Config | completed | config-spec-live-e2e.md | — |
| T1.3 | Add Makefile targets: `test-live-connectivity`, `test-live-api`, `test-live-e2e`, `test-live` | Config | completed | LIVE-007, deploy.md | T1.1 |
| T1.4 | Write unit test: Makefile targets exist and export correct env | Test | completed | test-plan.md TC-LIVE-003 | T1.3 |

**Parallelizable**: T1.1, T1.2

#### M2: H4–H5 Connectivity Migration

| # | Task | Type | Status | Spec Source | Depends On |
|---|------|------|--------|-------------|------------|
| T2.1 | Migrate `test_staging_connectivity.py` to accept `LIVE_API_URL` / `LIVE_FRONTEND_URL` with `STAGING_*` fallback | Code | completed | LIVE-005, TC-LIVE-003 | — |
| T2.2 | Update `verify_connectivity.sh` to prefer `LIVE_*` env vars | Config | completed | connectivity-gates.md | T2.1 |
| T2.3 | Write test: connectivity script skips H4 when env unset, runs when set | Test | completed | test-plan.md H4 | T2.2 |
| T2.4 | Add cold-start wake (curl retry 3×30s) to connectivity script preamble | Code | completed | LIVE-008 | T2.2 |

**Acceptance**: `LIVE_API_URL=https://metar-to-iwxxm-api.onrender.com LIVE_FRONTEND_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com VITE_API_BASE_URL=https://metar-to-iwxxm-api.onrender.com make test-live-connectivity` exits 0.

#### Phase LIVE-1 Gate Check

- [ ] T1.1–T1.4 completed
- [ ] T2.1–T2.4 completed
- [ ] H4 CORS preflight passes against live URLs
- [ ] H5 bundle embeds `VITE_API_BASE_URL` host

---

### Phase LIVE-2: Live API Integration (H3)

**Objective**: Full pytest live API suite with runtime JWT.  
**Entry gate**: Phase LIVE-1 gate passed.  
**Exit gate**: `make test-live-api` green with admin credentials in `.env`.

#### M3: Live API Auth Fixture & Resilience

| # | Task | Type | Status | Spec Source | Depends On |
|---|------|------|--------|-------------|------------|
| T3.1 | Write test: `live_api_token` fixture obtains JWT from `POST /auth/login` | Test | completed | TC-LIVE-001, LIVE-003 | T1.1 |
| T3.2 | Implement `conftest.py` session fixture: login → bearer token | Code | completed | test-plan.md H3 | T3.1 |
| T3.3 | Wire `live_client` fixture to use runtime token (drop manual `LIVE_API_TOKEN`) | Code | completed | config-spec-live-e2e.md | T3.2 |
| T3.4 | Add `test_auth_me_endpoint` to live suite | Test | completed | LIVE-010, TC-003 | T3.2 |
| T3.5 | Add retry/backoff helper for 429 and cold-start in live pytest conftest | Code | completed | LIVE-008, LIVE-009 | T3.2 |

#### M4: Live Validation Verification

| # | Task | Type | Status | Spec Source | Depends On |
|---|------|------|--------|-------------|------------|
| T4.1 | Run live validate test against Render; confirm E2E-001 fix holds in prod | Test | completed | TC-LIVE-002, LIVE-013 | T3.3 |
| T4.2 | Fix any live-only schema path drift if T4.1 fails | Code | completed | e2e-report.md E2E-001 | T4.1 |

#### Phase LIVE-2 Gate Check

- [ ] All `live_api` tests pass with runtime JWT
- [ ] Convert + validate endpoints return 200 for known-good METAR
- [ ] Unauthorized convert returns 401

---

### Phase LIVE-3: Live Playwright (H6)

**Objective**: UJ-001–003 against Render frontend with real auth.  
**Entry gate**: Phase LIVE-2 gate passed.  
**Exit gate**: `make test-live-e2e` runs UJ-001–003 specs green.

#### M5: Playwright Remote Mode

| # | Task | Type | Status | Spec Source | Depends On |
|---|------|------|--------|-------------|------------|
| T5.1 | Write test/config check: `webServer` disabled when `PLAYWRIGHT_BASE_URL` is HTTPS remote | Test | completed | TC-LIVE-004 | — |
| T5.2 | Update `playwright.config.ts`: skip `webServer` for remote base URL; set `DISABLE_AUTH=false` | Code | completed | live-e2e-integration.md G3 | T5.1 |
| T5.3 | Extend `00-preflight.e2e.spec.ts`: cold-start retry + API health probe | Code | completed | LIVE-008 | T5.2 |
| T5.4 | Add `test-live-e2e` Makefile target: `PLAYWRIGHT_BASE_URL=${LIVE_FRONTEND_URL}` + product spec subset | Config | completed | LIVE-004, LIVE-007 | T5.2, T1.3 |

**H6 scope** (user-approved): All 12 Playwright specs in `apps/e2e/` against live Render (`DISABLE_AUTH=false`).

#### Phase LIVE-3 Gate Check

- [ ] Preflight authenticates against live frontend
- [ ] UJ-001 conversion UI passes live
- [ ] UJ-003 auth gate passes live

---

### Phase LIVE-4: Cleanup & Signoff

**Objective**: Remove stale references; document runbook; manual release gate.  
**Entry gate**: Phase LIVE-3 gate passed.  
**Exit gate**: `make test-live` sequential run documented and verified.

#### M6: Stale Test Migration

| # | Task | Type | Status | Spec Source | Depends On |
|---|------|------|--------|-------------|------------|
| T6.1 | Fix `tests/test_playwright_e2e.py`: merged API at `LIVE_API_URL`, not auth-v2 | Code | completed | TC-LIVE-005, LIVE-011 | — |
| T6.2 | Migrate `E2E_*` env var reads to `LIVE_*` with deprecation warnings | Code | completed | LIVE-005 | T6.1 |

#### M7: Documentation & ADR

| # | Task | Type | Status | Spec Source | Depends On |
|---|------|------|--------|-------------|------------|
| T7.1 | Write ADR-009: Live test harness strategy (manual, LIVE_* env, Makefile tiers) | Docs | completed | LIVE-002, LIVE-012 | — |
| T7.2 | Update `docs/staging-secrets-matrix.md` with `LIVE_*` local test section | Docs | completed | config-spec-live-e2e.md | T1.2 |
| T7.3 | Manual signoff: run `make test-live` end-to-end; record in qa-report | Docs | completed | LIVE-012, TC-LIVE-001–004 | T1.3, T3.5, T5.4 |

#### Phase LIVE-4 Gate Check

- [ ] No tests reference `metar-to-iwxxm-auth-v2.onrender.com`
- [ ] `make test-live` runs H4–H5 → H3 → H6 sequentially
- [ ] ADR-009 recorded
- [ ] Manual signoff logged

---

## Git Strategy

| Change type | Branch | Base |
|-------------|--------|------|
| Live E2E harness | `feat/live-e2e-harness` | `main` |

### PR Plan

| PR | Title | Milestones | Status |
|----|-------|------------|--------|
| PR-LIVE-1 | `[LIVE-E2E] Live test harness (H3–H6)` | M1–M7 | open |

Atomic commits per task: `[T1.1] config: register live_api pytest marker`, etc.

## Task Tracking (master)

| Task | Phase | Milestone | Status |
|------|-------|-----------|--------|
| T1.1–T1.4 | LIVE-1 | M1 | completed |
| T2.1–T2.4 | LIVE-1 | M2 | completed |
| T3.1–T3.5 | LIVE-2 | M3 | completed |
| T4.1–T4.2 | LIVE-2 | M4 | completed |
| T5.1–T5.4 | LIVE-3 | M5 | completed |
| T6.1–T6.2 | LIVE-4 | M6 | completed |
| T7.1–T7.3 | LIVE-4 | M7 | completed |

## Phase Gate Log

| Phase | Date | Result | Notes |
|-------|------|--------|-------|
| LIVE-1 | 2026-06-22 | pass | PR #682 |
| LIVE-2 | 2026-06-22 | pass | PR #682 |
| LIVE-3 | 2026-06-22 | pass | PR #682 |
| LIVE-4 | 2026-06-22 | pass | PR #682 — manual signoff documented in qa-report |

## References

- [docs/test-plan.md](../../docs/test-plan.md) — TC-LIVE-001 through TC-LIVE-005
- [docs/context/live-e2e-integration.md](../../docs/context/live-e2e-integration.md)
- [.cursor/artifacts/config-spec-live-e2e.md](config-spec-live-e2e.md)
- [docs/requirements-decisions.md](../../docs/requirements-decisions.md) — LIVE-001 through LIVE-013
