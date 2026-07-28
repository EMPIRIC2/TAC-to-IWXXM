# Staging Secrets & Connectivity Matrix

> **⚠️ Superseded for env naming** — use [env-contract.md](../env-contract.md) and
> [config-spec.md](../config-spec.md) (S003, 2026-06-23; **F21 rewrite S023 / EV-017**). This file
> retained for historical staging URL reference until fully migrated.

> **Project**: METAR to IWXXM Converter
> **Generated**: 2026-06-15 (04-tech-plan)
> **Updated**: 2026-07-28 (S023 / EV-017 — F21 rate-limit stubs; Auth retired)
> **Platform**: Render

## Origin Map

Post-migration topology uses **two deployables** on existing onrender.com URLs (env var names updated only).

| Role | Service name (Render) | URL |
|------|----------------------|-----|
| API (public `/api/v1/*`) | `metar-to-iwxxm-api` | `https://metar-to-iwxxm-api.onrender.com` |
| Frontend (static site) | `metar-to-iwxxm-frontend-v4-web` | `https://metar-to-iwxxm-frontend-v4-web.onrender.com` |

**Removed post-migration**: `metar-to-iwxxm-auth-v2` (auth merged into API per ADR-002).
**F21**: Operator `/auth/*` removed (404); no separate Auth secrets on API for convert paths.

## Build-Time (Frontend Static Site)

Set on Render static site build environment:

| Variable | Staging value | Required | Notes |
|----------|---------------|----------|-------|
| `VITE_API_BASE_URL` | `https://metar-to-iwxxm-api.onrender.com` | Yes* | Prefer runtime `/config.json` `api.baseUrl` (`/api/v1` only) |
| `VITE_APP_URL` | `https://metar-to-iwxxm-frontend-v4-web.onrender.com` | Optional | Public frontend URL |

\* Prefer committed `config/prod.json` + runtime config over build-time `VITE_*` when possible.

### Retired (F21 — do not set for Auth)

| Variable | Notes |
|----------|-------|
| `VITE_SUPABASE_URL` | FE Auth removed (ADR-031) |
| `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY` | FE Auth removed (ADR-031) |
| `VITE_BACKEND_URL` / `VITE_AUTH_SERVICE_URL` | Historical — use `VITE_API_BASE_URL` / config |

## Runtime (API Web Service)

| Variable | Staging value | Required | Notes |
|----------|---------------|----------|-------|
| `METAR_CORS_ORIGINS` | `https://metar-to-iwxxm-frontend-v4-web.onrender.com` | Yes | Or `config.*.api.corsOrigins` |
| `RATE_LIMIT_PUBLIC_PER_MIN` | `60` (default) | No | F21 / ADR-031 — convert+lint+decode |
| `RATE_LIMIT_DISSEMINATION_PER_MIN` | `10` (default) | No | F21 dissemination stricter bucket |
| `MAX_REQUEST_BODY_BYTES` | `2097152` (default) | No | 2 MiB body cap |
| `PORT` | Render-injected | Yes | Bind `0.0.0.0:$PORT` |
| `DISSEMINATION_EGRESS_ALLOWLIST` | *(dashboard — sync: false)* | Yes (F16–F19) | Host/CIDR allowlist; **empty = fail-closed** (ADR-029 / E14-08). **Local/CI recommended:** `wis2box,127.0.0.1,127.0.0.0/8,localhost` (see `.env.example` + CI harness default). **Render:** keep empty until live BYOC demos, then exact Postgres/WIS2/EDIS hostnames only. Secrets never stored — hosts/CIDRs only. |
| `DATABASE_URL` | *(dashboard)* | Ops/F8 only | Legacy archive / F8 — not operator Auth |

### Retired (F21 — do not set on API for operator product)

| Variable | Notes |
|----------|-------|
| `DISABLE_AUTH` | Public by default (ADR-031) |
| `SUPABASE_URL` / `SUPABASE_ANON_KEY` (operator JWT) | Auth path removed |
| `FRONTEND_URL` (Auth redirects) | No Auth redirects |
| `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` | Public convert; no login harness |
| `ALLOWED_ORIGINS` / `AUTH_SERVICE_URL` / `CORS_ORIGINS` | Historical — use `METAR_CORS_ORIGINS` |
| `LOKI_*`, `OBSERVABILITY_ENV` | Observability removed from Blueprint |

## Local Development

| Variable | Default |
|----------|---------|
| `VITE_API_BASE_URL` | `http://localhost:18001` |
| `VITE_APP_URL` | `http://localhost:18000` |
| `METAR_CORS_ORIGINS` | `http://localhost:18000,http://localhost:5173` |
| `RATE_LIMIT_PUBLIC_PER_MIN` | `60` |
| `RATE_LIMIT_DISSEMINATION_PER_MIN` | `10` |
| `MAX_REQUEST_BODY_BYTES` | `2097152` |

## Local Live Test Runs (manual)

Populate `.env` from `.env.example` before `make test-live*`:

| Variable | Live value |
|----------|------------|
| `LIVE_API_URL` | `https://metar-to-iwxxm-api.onrender.com` |
| `LIVE_FRONTEND_URL` | `https://metar-to-iwxxm-frontend-v4-web.onrender.com` |
| `PLAYWRIGHT_BASE_URL` | Same as `LIVE_FRONTEND_URL` |

F21: no `E2E_USER_*` / `ADMIN_*` — public convert smoke + `TC-F21-auth-gone`.

See [deploy.md](../deploy.md) §Live test harness and ADR-009 / ADR-031.

## Connectivity Verification

| Tier | Command |
|------|---------|
| H0c | `pytest apps/backend/tests/unit/test_cors_policy.py` |
| H0i | `pytest apps/backend/tests/integration/test_h0i_connectivity.py` |
| H4 | CORS preflight from frontend origin → API |
| H5 | `bash scripts/deploy/verify_connectivity.sh` |

### EV-004 / F5 work history (2026-06-24) — **historical**

Pre-F21 server `tac_work_sessions` used Supabase JWT. **F21 / ADR-031**: local IndexedDB only;
legacy rows archive ~30 days then delete (no public API). Ops runbook:
[`legacy-tac-work-sessions-archive.md`](legacy-tac-work-sessions-archive.md). H0i work-sessions CORS checks retire
with M5.

### Redeploy order (F21)

1. Deploy API with CORS + rate-limit/body env (Auth + work-sessions routes gone).
2. Rebuild static frontend with IndexedDB history (no Auth bootstrap).
3. Run H4 + H5 (public convert; Auth-gone negatives).

## References

- docs/env-contract.md (**canonical F21**)
- docs/config-spec.md §F21
- docs/deploy.md §Integration
- docs/test-plan.md §Connectivity
- `.cursor/skills/connectivity-gates.md`
- ADR-031
