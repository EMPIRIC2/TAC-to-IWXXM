# ADR-009: Live Test Harness Strategy

## Status: Accepted

## Context

The monorepo has strong local E2E coverage (Playwright T2, H0i integration) but needed a
unified manual harness for verifying the deployed Render stack at:

- API: `https://metar-to-iwxxm-api.onrender.com`
- Frontend: `https://metar-to-iwxxm-frontend-v4-web.onrender.com`

Prior live tests used inconsistent env var names (`STAGING_*`, `E2E_*`), a legacy
`tests/test_playwright_e2e.py` targeting suspended auth-v2, and Playwright always starting
local dev servers even when a remote base URL was configured.

## Decision

1. **Manual/Makefile only** — Live tiers H3–H6 run via `make test-live*` from developer
   machines; no GitHub Actions job (Render cold-start + credential handling).
2. **Canonical env vars** — `LIVE_API_URL`, `LIVE_FRONTEND_URL`, `PLAYWRIGHT_BASE_URL`;
   deprecated names remain as fallbacks with warnings.
3. **Runtime JWT** — Authenticated H3 tests obtain tokens via `POST /auth/login` using
   `ADMIN_EMAIL` / `ADMIN_PASSWORD` from local `.env`; no long-lived `LIVE_API_TOKEN`.
4. **Makefile umbrella** — `test-live-connectivity` (H4–H5), `test-live-api` (H3),
   `test-live-e2e` (H6, all 12 Playwright specs), `test-live` (sequential all tiers).
5. **Playwright remote mode** — When `PLAYWRIGHT_BASE_URL` is a non-local HTTPS URL,
   skip local `webServer`; set `DISABLE_AUTH=false` for real login flows.
6. **Resilience** — 3× wake retry (30s) for Render spin-down; exponential backoff on 429.

## Consequences

- Pre-release signoff is explicit and manual — not a PR merge gate.
- Developers must populate `.env` with admin credentials; secrets never committed.
- Live Playwright runs are slower (serial, retries) but exercise full UJ-001–003 on Render.
- CI remains fast (T2 local only).

## Alternatives Considered

| Alternative | Rejected because |
|-------------|------------------|
| Scheduled GHA live job | Cold-start flakiness; secrets in CI; cost |
| Persist `LIVE_API_TOKEN` in `.env` | Token expiry; security risk |
| H6 product subset only | User chose full 12-spec coverage for release signoff |
| BFF/gateway for CORS | ADR-002 merged auth into API; direct CORS sufficient |

## References

- `docs/test-plan.md` — TC-LIVE-001 through TC-LIVE-005
- `.cursor/artifacts/execution-plan-live-e2e.md`
- `docs/requirements-decisions.md` — LIVE-001 through LIVE-013
