# Staging Secrets & Connectivity Matrix

> **⚠️ Superseded for env naming** — use [env-contract.md](../env-contract.md) and
> [config-spec.md](../config-spec.md) (S003, 2026-06-23). This file retained for historical
> staging URL reference until fully migrated.

> **Project**: METAR to IWXXM Converter
> **Generated**: 2026-06-15 (04-tech-plan)
> **Platform**: Render

## Origin Map

Post-migration topology uses **two deployables** on existing onrender.com URLs (env var names updated only).

| Role | Service name (Render) | URL |
|------|----------------------|-----|
| API (backend + auth) | `metar-to-iwxxm-api` | `https://metar-to-iwxxm-api.onrender.com` |
| Frontend (static site) | `metar-to-iwxxm-frontend-v4-web` | `https://metar-to-iwxxm-frontend-v4-web.onrender.com` |

**Removed post-migration**: `metar-to-iwxxm-auth-v2` (auth merged into API per ADR-002).

## Build-Time (Frontend Static Site)

Set on Render static site build environment:

| Variable | Staging value | Required | Notes |
|----------|---------------|----------|-------|
| `VITE_API_BASE_URL` | `https://metar-to-iwxxm-api.onrender.com` | Yes | Single origin for `/api/v1/*` and `/auth/*` |
| `VITE_SUPABASE_URL` | *(Render dashboard — sync: false)* | Yes | Supabase project URL |
| `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY` | *(Render dashboard — sync: false)* | Yes | Supabase anon/publishable key |
| `VITE_APP_URL` | `https://metar-to-iwxxm-frontend-v4-web.onrender.com` | Yes | Public frontend URL for redirects |

### Deprecated (remove after migration)

| Variable | Replaced by |
|----------|-------------|
| `VITE_BACKEND_URL` | `VITE_API_BASE_URL` |
| `VITE_AUTH_SERVICE_URL` | `VITE_API_BASE_URL` |

## Runtime (API Web Service)

| Variable | Staging value | Required | Notes |
|----------|---------------|----------|-------|
| `METAR_CORS_ORIGINS` | `https://metar-to-iwxxm-frontend-v4-web.onrender.com` | Yes | Comma-separated if multiple origins |
| `FRONTEND_URL` | `https://metar-to-iwxxm-frontend-v4-web.onrender.com` | Yes | Redirects / email links |
| `SUPABASE_URL` | *(dashboard)* | Yes | Server-side auth |
| `SUPABASE_ANON_KEY` | *(dashboard)* | Yes | JWT validation |
| `DISABLE_AUTH` | `false` | Yes | Production auth enabled per 04-tech-plan |
| `PORT` | Render-injected | Yes | Bind `0.0.0.0:$PORT` |
| `DATABASE_URL` | *(dashboard)* | If used | Postgres connection |
| `DISSEMINATION_EGRESS_ALLOWLIST` | *(dashboard — sync: false)* | Yes (F16–F19) | Host/CIDR allowlist; **empty = fail-closed** (ADR-029 / E14-08). Staging lists Compose/CI wis2box hosts when harness runs. Documented in `.env.example`; secrets never stored — hosts/CIDRs only. |

### Deprecated (remove after migration)

| Variable | Replaced by |
|----------|-------------|
| `ALLOWED_ORIGINS` | `METAR_CORS_ORIGINS` |
| `AUTH_SERVICE_URL` | — (auth inlined) |
| `CORS_ORIGINS` (auth service) | `METAR_CORS_ORIGINS` |
| `LOKI_*`, `OBSERVABILITY_ENV` | — (observability removed from Blueprint) |

## Local Development

| Variable | Default |
|----------|---------|
| `VITE_API_BASE_URL` | `http://localhost:18001` |
| `VITE_APP_URL` | `http://localhost:18000` |
| `METAR_CORS_ORIGINS` | `http://localhost:18000,http://localhost:5173` |
| `DISABLE_AUTH` | `true` (local dev convenience) |

## Local Live Test Runs (manual)

Populate `.env` from `.env.example` before `make test-live*`:

| Variable | Live value |
|----------|------------|
| `LIVE_API_URL` | `https://metar-to-iwxxm-api.onrender.com` |
| `LIVE_FRONTEND_URL` | `https://metar-to-iwxxm-frontend-v4-web.onrender.com` |
| `PLAYWRIGHT_BASE_URL` | Same as `LIVE_FRONTEND_URL` |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Supabase admin user (runtime JWT) |

See [deploy.md](../deploy.md) §Live test harness and ADR-009.

## Connectivity Verification

| Tier | Command |
|------|---------|
| H0c | `pytest apps/backend/tests/unit/test_cors_policy.py` |
| H0i | `pytest apps/backend/tests/integration/test_h0i_connectivity.py` (includes work-sessions CORS) |
| H4 | CORS preflight from frontend origin → API |
| H5 | `bash scripts/deploy/verify_connectivity.sh` |

### EV-004 / F5 work history (2026-06-24)

No new Render secrets for F5 — work sessions use the existing Supabase JWT + publishable key
pattern (ADR-011). Operator steps before enabling F5 in production:

1. Apply Supabase migrations through `20250623000007_metar_work_sessions.sql` (`supabase db push` or dashboard).
2. Redeploy API so `/api/v1/work-sessions` and `/admin/work-sessions` routes are live.
3. Confirm H0i work-sessions CORS preflight (PATCH/DELETE) and H4 staging origin pass after redeploy.

See [deploy.md](../deploy.md) §Migrations (F5) and ADR-012 for pg_cron retention.

### Redeploy order

1. Deploy API with `METAR_CORS_ORIGINS` and `DISABLE_AUTH=false`.
2. Rebuild static frontend with `VITE_API_BASE_URL` pointing to live API.
3. Run H4 + H5.

## References

- docs/deploy.md §Integration
- docs/test-plan.md §Connectivity
- `.cursor/skills/connectivity-gates.md`
