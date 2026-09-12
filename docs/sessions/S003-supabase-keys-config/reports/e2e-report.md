# E2E Behavior Report — S003 / Supabase keys & config (10-e2e delta)

> Generated: 2026-06-23  
> Session: S003-supabase-keys-config  
> Branch: `fix/supabase-service-key-leak`  
> Mechanism: mixed (env gate + in-process pytest + Playwright T2 + live HTTP)  
> Scope: Auth/admin smoke + env contract (F3, M4) — per routing-plan delta note

## Summary

| # | Journey / gate | Mechanism | T0 | T2 connectivity | T3 browser/live | Status |
|---|----------------|-----------|----|-----------------|-----------------|--------|
| 1 | H0e env-check | shell | — | — | — | **PASS** (legacy key WARN) |
| 2 | Supabase env helpers | pytest | ✓ | — | — | **PASS** (30/30) |
| 3 | H0i auth+wiring | pytest | ✓ | — | — | **PARTIAL** (5/7) |
| 4 | UJ-003 auth integration | Playwright API | — | ✓ | — | **PASS** (4/4) |
| 5 | UJ-003 login UI | Playwright browser | — | ✗ | — | **FAIL** (0/3) |
| 6 | H4–H5 staging connectivity | curl + pytest | — | ✓ | — | **PASS** |
| 7 | H3 live auth API | pytest live | — | — | partial | **BLOCKED** (8 skipped) |

**Overall (S003 delta)**: **FAIL** — canonical key migration code passes local gates; login UI T2 and live UJ-003 blocked until `disableAuth:false` harness + Render secret rotation land.

---

## Journey Details

### H0e — Env contract sync (`make env-check`)

- **Feature**: F3, M4
- **Mechanism**: `scripts/env/verify-sync.sh`
- **Steps**:
  1. Validate `config/local.json` structure — **PASS**
  2. Check canonical `SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_SECRET_KEY` — **PASS** (publishable present)
  3. Legacy shim warning — **WARN**: `SUPABASE_SERVICE_ROLE_KEY` set without `SUPABASE_SECRET_KEY`
- **Result**: Gate passes; local `.env` still carries legacy service_role key pending full migration (T2 in 07-build).

### Supabase env unit tests (`packages/shared`, `packages/auth`)

- **Feature**: F3
- **Mechanism**: pytest
- **Result**: **30/30 PASS** — canonical + legacy fallback for publishable/secret keys; auth proxy init/sign-in/out with publishable key.

### H0i — In-process connectivity (`test_h0i_connectivity.py`)

- **Feature**: M4
- **Mechanism**: TestClient (no live Supabase)
- **Steps**:
  1. `test_convert_requires_auth_when_enforced` — **PASS**
  2. `test_convert_returns_iwxxm_when_authenticated` — **PASS**
  3. `test_auth_login_route_on_same_host` — **PASS**
  4. `test_health_endpoint` / `test_versions_endpoint` — **PASS**
  5. CORS preflight `OPTIONS /api/v1/convert` with `Origin: http://localhost:5173` — **FAIL** (400)
  6. CORS preflight `OPTIONS /auth/login` with `Origin: http://localhost:5173` — **FAIL** (400)
- **Note**: Config-driven CORS now allows `http://localhost:18000`; H0i fixture still uses port 5173. Auth wiring unaffected; preflight origin mismatch is a test/config drift item for 09-qa.

### UJ-003 — Merged API auth integration (`auth-service-integration.e2e.spec.ts`)

- **Feature**: F3, M4
- **Mechanism**: Playwright (request + page console)
- **Command**: `PLAYWRIGHT_BASE_URL=http://localhost:18000 PLAYWRIGHT_API_BASE_URL=http://localhost:18001 pnpm exec playwright test auth-service-integration.e2e.spec.ts`
- **Steps**:
  1. Frontend boots without `Missing VITE_AUTH_SERVICE_URL` / `Missing VITE_BACKEND_URL` console errors — **PASS**
  2. `GET /health` on merged API — **PASS**
  3. `POST /auth/login` reachable on merged host (4xx, not connection error) — **PASS**
  4. No 400 responses on `/auth/*` during page load — **PASS**
- **T2 connectivity**: **PASS** — config.json + publishable key wiring works for merged API.

### UJ-003 — Login UI (`auth.e2e.spec.ts`)

- **Feature**: F3
- **Mechanism**: Playwright browser
- **Steps**:
  1. Login page loads (`METAR Converter` heading) — **FAIL** (heading not found)
  2. Empty-field validation — **FAIL** (same root cause)
  3. Admin login → admin dashboard — **FAIL** (same root cause)
- **Root cause**: `config/local.json` and generated `apps/frontend/public/config.json` set `api.disableAuth: true`. Playwright `webServer` starts stack with auth disabled; login route never renders. `DISABLE_AUTH=false` env does not override runtime config today.
- **Mitigation**: Run UJ-003 UI specs with `disableAuth: false` in active config (or dedicated E2E config overlay) — tracked for 07-build/09-qa.

### T3 — Staging connectivity (H4–H5)

- **Feature**: UJ-OPS-001 / M4
- **Command**: `make test-live-connectivity`
- **Steps**:
  1. H0c CORS policy unit tests — **PASS** (6/6)
  2. H4 live CORS preflight from staging frontend origin — **PASS**
  3. H5 deployed bundle references `https://metar-to-iwxxm-api.onrender.com` — **PASS**

### T3 — Live API auth (H3 subset)

- **Feature**: UJ-003
- **Command**: `make test-live-api`
- **Result**: **13 passed, 8 skipped**
- **Blocker**: `POST /auth/login` on staging returns `Authentication failed: Legacy API keys are disabled`. Staging Render env still uses retired JWT keys; S003 publishable/secret keys not deployed (expected until 12-verify-deploy / 14-hotfix deploy step).
- **Public paths** (health, versions, schema, CORS headers): **PASS**

---

## Tier matrix (connectivity gates)

| Tier | Command | Result | Notes |
|------|---------|--------|-------|
| T0 | `pytest packages/shared/tests/test_supabase_env.py packages/auth/tests/test_supabase_proxy_unit.py` | PASS | 30/30 |
| H0e | `make env-check` | PASS | Legacy key WARN |
| H0i | `pytest apps/backend/tests/integration/test_h0i_connectivity.py` | PARTIAL | 5/7; CORS origin drift |
| T2 product (auth API) | `auth-service-integration.e2e.spec.ts` | PASS | 4/4 |
| T2 product (auth UI) | `auth.e2e.spec.ts` | FAIL | `disableAuth:true` in config |
| T2 connectivity | H4+H5 via `make test-live-connectivity` | PASS | Staging bundle + CORS |
| T3 live auth | `make test-live-api` auth cases | BLOCKED | Legacy keys disabled on Render |

---

## Findings for 11-verify-impl

1. **E2E-S003-001** — Local auth UI specs require `disableAuth: false` in runtime config; env var alone insufficient after config.json split.
2. **E2E-S003-002** — H0i CORS preflight tests use `localhost:5173`; config CORS uses `localhost:18000` — update fixture or test plan.
3. **E2E-S003-003** — Staging auth blocked until Render `SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_SECRET_KEY` rotated (T3 UJ-003 deferred post-deploy).
4. **Positive** — Merged API auth routes, publishable key loading, and frontend boot (no legacy `VITE_AUTH_SERVICE_URL` errors) verified locally.

## Waivers

| Journey | T3 waiver |
|---------|-----------|
| UJ-001, UJ-002 | Out of S003 delta scope; not re-run |
| UJ-003 live browser | Deferred — blocked on Render secret rotation (see E2E-S003-003) |
