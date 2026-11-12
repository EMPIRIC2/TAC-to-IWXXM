# Environment variables

This document lists environment variable **names** and which layer owns each
concern. Use the same name in profile JSON, deploy secrets, local `.env`, and
docs.

**Terms**

| Term | Meaning |
|------|---------|
| DOKS | DigitalOcean Kubernetes Service, primary compute after the platform cutover |
| Supabase Auth | Login and JWT issue only. Not the product database. |
| Product DB | DigitalOcean Postgres reached via `DATABASE_URL` |
| JWKS | JSON Web Key Set, public keys the API uses to verify Auth JWTs |
| BYOC | Bring Your Own Credentials, one-shot pasted destination secrets (memory-only) |

## Model

- Convert, lint, validate, and disseminate routes stay **public**. Those routes
 need no JWT.
- Optional Supabase Auth covers long-term work sessions only. A JWT is required
 for `/api/v1/work-sessions*`.
- Guests use browser IndexedDB and see a persistent loss-of-progress notice.
 Feature privacy settings gates still apply.
- Product DB is DigitalOcean Postgres via `DATABASE_URL` (sessions + feature ingest worker
 ingest store).
- Supabase is Auth URL + keys only. It is **not** product PostgREST / hosted app
 tables.
- Compute is DOKS as primary after the platform cutover. Render is suspended.
- Dissemination BYOC credentials stay memory-only.

## Source of truth by layer

| Layer | Owns | Does not own |
|-------|------|--------------|
| DOKS API | Deploy URL, `PORT`, `DATABASE_URL`, rate-limit and body env, dissemination allowlist, Supabase Auth verify secrets | Supabase DB / service-role PostgREST product writes |
| DOKS static | Frontend URL; `/config.json` with `api.baseUrl` + Auth publishable bootstrap | Service-role / `DATABASE_URL` |
| DOKS worker (ingest worker) | `DATABASE_URL`, poller URL and interval, machine credentials | Operator JWT; Supabase DB writers |
| Supabase project | Auth users JWT issuance | App tables for sessions or ingest worker |
| Repo | `config/deploy/profiles/*.json`, `.env.example`, this document | Live secret values |
| Local | `.env` (gitignored), `METAR_CONFIG_ENV=local` | Production URLs unless live testing |

## Canonical names

| Concern | Canonical | Where set |
|---------|-----------|-----------|
| API public URL | `config.*.api.baseUrl` | `config/deploy/profiles/*.json` (`/api/v1` and `/auth`) |
| Frontend public URL | `config.*.api.frontendUrl` | `config/deploy/profiles/*.json` |
| CORS | `config.*.api.corsOrigins` | `config/deploy/profiles/*.json` (include DOKS FE origin) |
| Product Postgres | `DATABASE_URL` | API + worker env (required for sessions + ingest worker) |
| Supabase Auth URL | `SUPABASE_URL` / `config.*.supabase.url` | API + FE bootstrap |
| FE Auth publishable key | `SUPABASE_PUBLISHABLE_KEY` → `/config.json` | Static deploy inject |
| Auth JWKS URL (server) | `SUPABASE_JWKS_URL` or default `{SUPABASE_URL}/auth/v1/.well-known/jwks.json` | API only, never FE |
| Auth JWT verify (server) | JWKS-only (PyJWT + fetched JWKS); cache keys with TTL | API only; `SUPABASE_JWT_SECRET` retired for product verify |
| Public rate limit | `RATE_LIMIT_PUBLIC_PER_MIN` | API / `.env` (default **60**) |
| mass file ingest rate limit | `RATE_LIMIT_MASS_INGEST_PER_MIN` | API / `.env` (default **10**) |
| Dissemination rate limit | `RATE_LIMIT_DISSEMINATION_PER_MIN` | API / `.env` (default **10**) |
| Shared rate-limit store (Upstash) | `REDIS_URL` | API DOKS secret, Upstash `rediss://…`; unset → in-memory slowapi + warning |
| Sentry DSN (API / worker) | `SENTRY_DSN` | API + worker env DOKS secret, unset = disabled |
| Sentry DSN (frontend) | `sentryDsn` in `/config.json` (or `VITE_SENTRY_DSN` local) | Static deploy inject, unset = disabled |
| Max request body | `MAX_REQUEST_BODY_BYTES` | API / `.env` (default **2097152** = 2 MiB) |
| mass file ingest max files | `MASS_INGEST_MAX_FILES` | API / `.env` (default **200**) |
| mass file ingest max file bytes | `MASS_INGEST_MAX_FILE_BYTES` | API / `.env` (default **5242880** = 5 MiB) |
| mass file ingest max total bytes | `MASS_INGEST_MAX_TOTAL_BYTES` | API / `.env` (default **52428800** = 50 MiB unzipped) |
| Dissemination egress allowlist | `DISSEMINATION_EGRESS_ALLOWLIST` | API / `.env`; local multi-database dissemination LIVE recipe: `wis2box,127.0.0.1,127.0.0.0/8,localhost` |
| ingest worker poller feed URL | `INGEST_POLLER_URL` | Worker secrets / local `.env`, https only; reject `REPLACE_ME_*` |
| ingest worker poll interval | `INGEST_POLL_INTERVAL_SEC` | Worker ConfigMap (default `30`) |
| Live API URL | `LIVE_API_URL` | Local/CI live harness |
| Live frontend URL | `LIVE_FRONTEND_URL` | Local/CI live harness |
| DOKS prod DNS (prod + live) | `https://api.tac-to-iwxxm.com` / `https://app.tac-to-iwxxm.com` | `config/deploy/profiles/prod.json` + `LIVE_*` |
| E2E Auth fixture | `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` | Live/local Auth session tests only |
| Default semantic profile (semantic and exchange profiles) | `DEFAULT_SEMANTIC_PROFILE` | API / `.env`, default `ICAO_2025` |
| Default exchange profile (semantic and exchange profiles) | `DEFAULT_EXCHANGE_PROFILE` | API / `.env`, default `GLOBAL_AFS` when packaging invoked |
| Profile wire v2 cutover (semantic and exchange profiles) | `PROFILE_WIRE_V2` | API / `.env`, `true` prefers nested semantic/exchange fields |
| Live map timer (live TAC map) | `LIVE_MAP_REFRESH` | Staging API is `0` when `metar-map-translator` owns the loop |
| Live map refresh (live TAC map) | `LIVE_MAP_REFRESH_SECONDS` | Translator API, default `300` |
| Live map import cap (live TAC map) | `LIVE_MAP_IMPORT_LIMIT` | API timer only, default `40` |
| Live map cache (live TAC map) | `LIVE_MAP_CACHE_URL` | Same product database as `DATABASE_URL` |

Profile ids are not secrets. An exchange profile must not imply dissemination
credentials.

**ingest worker non-prod fixture:** 
`https://raw.githubusercontent.com/EMPIRIC2/TAC-to-IWXXM/main/apps/worker/tests/fixtures/ingest_feed.json` 
Validate: `python3 scripts/deploy/validate_ingest_poller_url.py --probe "$INGEST_POLLER_URL"`.

### Retired for product data plane

| Retired | Replacement |
|---------|-------------|
| Supabase Postgres pooler as app SoT | `DATABASE_URL` → DigitalOcean Postgres |
| `SUPABASE_SERVICE_ROLE_KEY` as ingest worker DB writer | SQL via `DATABASE_URL` |
| Operator product tables on Supabase | Migrated once |
| `SUPABASE_JWT_SECRET` HS256 verify | JWKS-only (`SUPABASE_JWKS_URL` or derived) |

### Still retired

| Retired | Notes |
|---------|-------|
| `DISABLE_AUTH` dual path | Public convert is default; Auth is additive for sessions only |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Already retired |
| In-app paste of Supabase auth keys | Dest BYOC paste remains multi-database dissemination–AMHS/SWIM/AFS dissemination only |

## Per-environment matrix

### Production (DOKS)

| Setting | API | Static | Worker |
|---------|-----|--------|--------|
| `DATABASE_URL` | required |, | required |
| `SUPABASE_URL` + JWKS verify | required for Auth |, |, |
| Publishable key inject |, | `/config.json` |, |
| Rate limits / body / allowlist | env |, |, |
| `METAR_CONFIG_ENV=prod` | yes | copy → `public/config.json` |, |
| ingest worker poller |, |, | env |
| `OPENAIP_API_KEY` | required for station names |, |, |

Staging (`metar-iwxxm-staging`) uses the same `OPENAIP_API_KEY` entry on
`metar-api-secrets`.

### Local (`METAR_CONFIG_ENV=local`)

| Setting | Value |
|---------|-------|
| Ports | **18000** frontend18001** API |
| CORS | `["http://localhost:18000"]` |
| `DATABASE_URL` | Local/DO Postgres for session + ingest worker integration tests |
| Auth | Optional; use project Auth + publishable key for |
| `PROFILE_OVERLAY_HMAC_SECRET` | Required to create/verify ConversionProfile overlays |

### CI (GitHub Actions)

| Setting | Notes |
|---------|-------|
| Public convert | No Auth required |
| Session Auth tests | Fixture user or mocked JWKS/JWT |
| Postgres + Alembic | Service container `DATABASE_URL`; `alembic upgrade head` before schema tests |
| ingest worker / dissemination | `DATABASE_URL` + allowlist fixtures |
| OpenAIP station names | `OPENAIP_API_KEY` on the OpenAIP station lookup job |
| Weekly validation catalog | Workflow `weekly-validation-catalog.yml` on Environment `staging` |

## Verification

```bash
make env-check # local: .env + profile JSON valid
make env-check LIVE=1 # optional: probe LIVE_API_URL /health
make test-live-connectivity # – connectivity
```

## References

- [AGENTS.md](../AGENTS.md) (``, ``)
- [docs/tech-spec.md](tech-spec.md)
- [config/deploy/profiles/](../config/deploy/profiles)
- [config/deploy/doks/](../config/deploy/doks)
