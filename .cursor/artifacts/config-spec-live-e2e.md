# Config Spec — Live E2E & Integration Testing

> **Ephemeral artifact** — delta 01-requirements 2026-06-22  
> **Scope**: Manual live test harness (H3–H6) against Render  
> **Feature**: test-plan live tiers; maps to UJ-001–003 T3

## Overview

Live tests run manually via Makefile targets. Credentials stay in local `.env` (never committed).
JWT obtained at runtime from merged API auth routes.

**Prerequisite**: E2E-001 schema path fix must be merged before H3 validate and full H6 UJ-002 pass.

## Environment Variables

### Canonical (required for live runs)

| Variable | Default | Required | Validation | Used by |
|----------|---------|----------|------------|---------|
| `LIVE_API_URL` | — | Yes | HTTPS URL, no trailing slash | H3, H4, login fixture |
| `LIVE_FRONTEND_URL` | — | Yes | HTTPS URL, no trailing slash | H4, H5, H6 |
| `PLAYWRIGHT_BASE_URL` | `LIVE_FRONTEND_URL` | Yes (H6) | HTTPS URL | Playwright config |
| `ADMIN_EMAIL` | — | Yes (H6) | Valid Supabase user | `POST /auth/login` |
| `ADMIN_PASSWORD` | — | Yes (H6) | Non-empty | `POST /auth/login` |

### Optional aliases

| Variable | Maps to | Notes |
|----------|---------|-------|
| `PLAYWRIGHT_ADMIN_EMAIL` | `ADMIN_EMAIL` | Playwright-specific override |
| `PLAYWRIGHT_ADMIN_PASSWORD` | `ADMIN_PASSWORD` | Playwright-specific override |

### Deprecated (migrate away)

| Old | New |
|-----|-----|
| `STAGING_API_URL` | `LIVE_API_URL` |
| `STAGING_FRONTEND_ORIGIN` | `LIVE_FRONTEND_URL` |
| `STAGING_FRONTEND_URL` | `LIVE_FRONTEND_URL` |
| `E2E_API_URL` | `LIVE_API_URL` |
| `E2E_FRONTEND_URL` | `LIVE_FRONTEND_URL` |
| `LIVE_API_TOKEN` | Runtime JWT from login — do not persist |

## Makefile Targets

| Target | Tiers | Command (planned) |
|--------|-------|-------------------|
| `test-live-connectivity` | H4–H5 | `verify_connectivity.sh` + CORS pytest |
| `test-live-api` | H3 | `pytest -m live_api` with retry/backoff |
| `test-live-e2e` | H6 | Playwright remote mode, no local webServer |
| `test-live` | All | Sequential H4–H5 → H3 → H6 |

## Resilience

| Behavior | Setting |
|----------|---------|
| Cold-start retry | 3 attempts, 30s wait between |
| Rate limit (429) | Exponential backoff in live API pytest |
| Parallelism | Serial only for live requests |

## CI Policy

Live tests are **not** run in GitHub Actions. Manual signoff via `make test-live` before release.

## `.env.example` additions (implementation)

```bash
# Live E2E (manual — do not commit real credentials)
LIVE_API_URL=https://metar-to-iwxxm-api.onrender.com
LIVE_FRONTEND_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com
PLAYWRIGHT_BASE_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com
ADMIN_EMAIL=
ADMIN_PASSWORD=
```

## References

- [docs/test-plan.md](../../docs/test-plan.md) — TC-LIVE-001 through TC-LIVE-005
- [docs/deploy.md](../../docs/deploy.md) §Live test harness
- [docs/context/live-e2e-integration.md](../../docs/context/live-e2e-integration.md)
