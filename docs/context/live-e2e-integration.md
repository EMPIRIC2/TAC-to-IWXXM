# Context — Live E2E & Integration Testing

> **Mode**: scoped | **Slug**: live-e2e-integration | **Generated**: 2026-06-22  
> **Feature / workflow**: Unified live test harness for Render deployment | **Status**: active

## Executive Summary

The monorepo has strong **local** E2E coverage (Playwright T2 in `apps/e2e/`, H0i in
`apps/backend/tests/integration/`) and partial **live** pytest smoke. The Render stack at
`https://metar-to-iwxxm-api.onrender.com` + `https://metar-to-iwxxm-frontend-v4-web.onrender.com`
is healthy: `/health` 200, auth on merged API, H4 CORS and H5 bundle checks pass.

The gap is a **unified live harness** for H3 (API), H4–H5 (connectivity), and H6 (Playwright
UJ-001–003) — manual Makefile runs with credentials from local `.env`. Playwright still
auto-starts local dev servers; `tests/test_playwright_e2e.py` targets suspended auth-v2.

## Resolution Log

| ID | Category | Decision |
|----|----------|----------|
| R1 | Scope | All tiers — H3 + H4–H5 + H6 full Playwright (UJ-001–003) |
| R2 | CI | Manual/local only — Makefile targets; no GitHub Actions live job |
| R3 | Credentials | Local `.env` — `ADMIN_EMAIL` / `ADMIN_PASSWORD` |

## Scope & Constraints

**In scope**: Live pytest smokes, connectivity script, Playwright against Render URLs, Makefile
targets, env var documentation. Maps to `docs/test-plan.md` H3–H6 and UJ-001–003.

**Out of scope (R2)**: Scheduled CI live runs. **Out of scope (separate)**: Schema path
regression (E2E-001) — see `docs/e2e-report.md`.

Template/deploy topology: `workflow-state.yaml` §template (`static+api`); see
`docs/staging-secrets-matrix.md`, `docs/deploy.md` §Integration.

## Environment / Topology

| Role | URL | Verified (2026-06-22) |
|------|-----|------------------------|
| API (backend + auth) | `https://metar-to-iwxxm-api.onrender.com` | `/health` 200, `gifts_available: true` |
| Frontend | `https://metar-to-iwxxm-frontend-v4-web.onrender.com` | H5 bundle OK |
| Deprecated | `metar-to-iwxxm-auth-v2.onrender.com` | Suspended (503) — do not target |

| Direction | Mechanism | Status |
|-----------|-----------|--------|
| Frontend → API | `VITE_API_BASE_URL` | PASS (H5) |
| API → Frontend CORS | `METAR_CORS_ORIGINS` | PASS (H4) |
| Live auth | `POST /auth/login` on merged API | PASS |
| Auth mode | `DISABLE_AUTH=false` on Render | Real login required for H6 |

Key paths: `/health`, `/api/v1/convert`, `/api/v1/validation/validate`, `/auth/login`, `/auth/me`.

## Existing Infrastructure

### H3 — Live API (pytest)

| Module | Marker | Env vars | Notes |
|--------|--------|----------|-------|
| `apps/backend/tests/infrastructure/test_live_api_health.py` | `live_api` | `LIVE_API_URL`, `LIVE_API_TOKEN` | Full health/convert/validate suite |
| `tests/smoke/test_staging_connectivity.py` | `live` | `STAGING_API_URL`, `STAGING_FRONTEND_ORIGIN` | H4 CORS |
| `tests/bugs/test_bug_2026_06_20_login_cors_failed_fetch.py` | `live` | `STAGING_*` | CORS regression |
| `tests/test_playwright_e2e.py` | — | `E2E_*`, `ADMIN_*` | **Stale** — hits auth-v2 |

### H4–H5 — `scripts/deploy/verify_connectivity.sh`

Passing as of 2026-06-22 (H0c 6/6, H4 1/1, H5 OK).

### H6 — Playwright (`apps/e2e/`)

12 specs; local `webServer` + `DISABLE_AUTH=true` default. `PLAYWRIGHT_BASE_URL` supported
but does not disable `webServer`. Makefile: `test-e2e-playwright`, `test-e2e-t2-product`.

### Not live

`apps/backend/tests/integration/` — H0i local stack only.

## Cross-Reference Matrix

| Capability | Local T2 | Live H3 | Live H4–H5 | Live H6 |
|------------|----------|---------|-------------|---------|
| Health check | ✓ | ✓ | ✓ | — |
| CORS preflight | H0c | — | ✓ | — |
| Bundle API URL | — | — | ✓ | — |
| Auth login API | ✓ | partial/stale | — | blocked |
| Auth login UI | ✓ mock | — | — | needs work |
| METAR conversion UI | ✓ | — | — | needs work |
| Validation API | ✓ | ✓ w/ token | — | — |

## Implementation Backlog

1. Playwright live mode — disable `webServer` when `PLAYWRIGHT_BASE_URL` is remote; `DISABLE_AUTH=false`.
2. Makefile targets — `test-live-connectivity`, `test-live-api`, `test-live-e2e`.
3. Env var consolidation — `STAGING_*`, `LIVE_API_*`, `E2E_*`, `PLAYWRIGHT_*` in `.env.example`.
4. Fix `tests/test_playwright_e2e.py` — merged API host, not auth-v2.
5. Register `live_api` marker in `pyproject.toml`.
6. Live API token helper — login fixture → `LIVE_API_TOKEN`.
7. Cold-start retries for Render spin-down.
8. Run `00-preflight.e2e.spec.ts` first in live suite.

## Data & Credentials

| Asset | Source | Notes |
|-------|--------|-------|
| Admin credentials | `.env` | `ADMIN_EMAIL`, `ADMIN_PASSWORD` |
| Playwright aliases | Optional | `PLAYWRIGHT_ADMIN_*` |
| Live JWT | Runtime | `POST /auth/login` |
| METAR fixtures | `test-data/` | No secrets |

Never commit `.env`. Manual runs only (R2).

## Unresolved Gaps

| ID | Item | Recommendation |
|----|------|----------------|
| G1 | Schema path (E2E-001) | Track separately; may block live validation |
| G2 | Render rate limits | Backoff on 429 |
| G3 | Full 12-spec live Playwright | Start with `test-e2e-t2-product` + preflight |

## Sources

- [Repo: apps/e2e/playwright.config.ts] — local-first; needs live mode
- [Docs: docs/e2e-report.md] — T3 auth gap superseded by 2026-06-22 probe
- [Docs: docs/staging-secrets-matrix.md] — canonical URLs
- [Docs: docs/test-plan.md] — H tiers, UJ mapping
- Live probe 2026-06-22 — health, CORS, OpenAPI 31 paths, verify_connectivity pass
