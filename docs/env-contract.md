# Environment Contract — DOKS / Auth-only Supabase / DO Postgres (F30 / F31)

> **Project**: METAR to IWXXM Converter  
> **Session**: S038-platform-independence-842 / EV-031 (F30/F31)  
> **Supersedes**: F21-only public-app contract (S023) for Auth + data-plane topology  
> **Last updated**: 2026-08-03 (T0.3 — JWKS-only verify names)  
> **Status**: **Accepted** for Auth/DB names (Gate B / T0.3); DOKS host placeholders → T0.4/M6

Single source of truth for **what** each layer owns and **which name** to use everywhere.

## Model (EV-031)

- **Convert / lint / validate / disseminate** remain **public** (no JWT).
- **Optional Supabase Auth** for long-term work sessions only (JWT → `/api/v1/work-sessions*`).
- **Guests**: IndexedDB + persistent loss-of-progress notice; F22 privacy gates.
- **Product DB**: DigitalOcean Postgres via `DATABASE_URL` (sessions + F8).
- **Supabase**: Auth URL + keys only — **not** product PostgREST / hosted app tables.
- **Compute**: DOKS primary after F30 cutover; Render **suspended** (T6.5 / `D-S038-t65-waive`).
- **Dissemination** BYOC credentials remain **memory-only** (ADR-021/029).

## Source of truth by layer

| Layer | Owns | Does not own |
|-------|------|--------------|
| **DOKS API** | Deploy URL, `PORT`, `DATABASE_URL`, rate-limit/body env, dissemination allowlist, Supabase Auth verify secrets | Supabase DB / service-role PostgREST product writes |
| **DOKS static** | Frontend URL; `/config.json` with `api.baseUrl` + Auth publishable bootstrap | Service-role / `DATABASE_URL` |
| **DOKS worker (F8)** | `DATABASE_URL`, poller URL/interval, machine credentials | Operator JWT; Supabase DB writers |
| **Supabase project** | Auth users / JWT issuance | App tables for sessions or F8 |
| **Repo** | `config/*.json`, `.env.example`, this contract | Live secret values |
| **Local** | `.env` (gitignored), `METAR_CONFIG_ENV=local` | Production URLs unless live testing |

## Canonical names (one name per concern)

| Concern | Canonical | Where set |
|---------|-----------|-----------|
| API public URL | `config.*.api.baseUrl` | `config/*.json` (`/api/v1` **and** `/auth`) |
| Frontend public URL | `config.*.api.frontendUrl` | `config/*.json` |
| CORS | `config.*.api.corsOrigins` | `config/*.json` (include DOKS FE origin) |
| Product Postgres | `DATABASE_URL` | API + worker env (**required** for sessions + F8) |
| Supabase Auth URL | `SUPABASE_URL` / `config.*.supabase.url` | API + FE bootstrap |
| FE Auth publishable key | `SUPABASE_PUBLISHABLE_KEY` → `/config.json` | Static deploy inject |
| Auth JWKS URL (server) | `SUPABASE_JWKS_URL` **or** default `{SUPABASE_URL}/auth/v1/.well-known/jwks.json` | API only — never FE (`D-S038-04-b1` Q2=2) |
| Auth JWT verify (server) | **JWKS-only** (PyJWT + fetched JWKS); cache keys with TTL | API only; **`SUPABASE_JWT_SECRET` retired** for product verify |
| Public rate limit | `RATE_LIMIT_PUBLIC_PER_MIN` | API / `.env` (default **60**) |
| Dissemination rate limit | `RATE_LIMIT_DISSEMINATION_PER_MIN` | API / `.env` (default **10**) |
| Max request body | `MAX_REQUEST_BODY_BYTES` | API / `.env` (default **2097152** = 2 MiB) |
| Dissemination egress allowlist | `DISSEMINATION_EGRESS_ALLOWLIST` | API / `.env` (ADR-029) |
| F8 poller feed URL | `INGEST_POLLER_URL` | Worker / local `.env` |
| F8 poll interval | `INGEST_POLL_INTERVAL_SEC` | Worker (default `30`) |
| Live API URL | `LIVE_API_URL` | Local/CI live harness (provisional DOKS Host-header placeholders) |
| Live frontend URL | `LIVE_FRONTEND_URL` | Local/CI live harness |
| DOKS placeholders (prod + live) | `http://api.doks.placeholder.metar-iwxxm.local` / `http://app.doks.placeholder.metar-iwxxm.local` | `config/prod.json` + `LIVE_*` under `D-S038-t63-waive` until real DNS |
| E2E Auth fixture | `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` | Live/local Auth session tests only |

### Retired / do not use for product data plane

| Retired for product DB | Replacement |
|------------------------|-------------|
| Supabase Postgres pooler as app SoT | `DATABASE_URL` → DigitalOcean Postgres |
| `SUPABASE_SERVICE_ROLE_KEY` as F8 **DB** writer | SQL via `DATABASE_URL` (ADR-018 amend) |
| Operator product tables on Supabase | Migrated once — [ops note](ops/supabase-to-do-postgres-migration.md) |
| `SUPABASE_JWT_SECRET` / HS256 verify | JWKS-only (`SUPABASE_JWKS_URL` or derived) |

### Still retired (F21 keep)

| Retired | Notes |
|---------|-------|
| `DISABLE_AUTH` dual path | Public convert is default; Auth is additive for sessions only |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Already retired (S011) |
| In-app paste of Supabase **auth** keys | Dest BYOC paste remains F16–F19 only |

## Per-environment matrix

### Production (DOKS — target)

| Setting | API | Static | Worker |
|---------|-----|--------|--------|
| `DATABASE_URL` | required | — | required |
| `SUPABASE_URL` + JWKS verify | required for Auth (`SUPABASE_JWKS_URL` optional override) | — | — |
| Publishable key inject | — | `/config.json` | — |
| Rate limits / body / allowlist | env | — | — |
| `METAR_CONFIG_ENV=prod` | yes | copy → `public/config.json` | — |
| F8 poller | — | — | env |

### Render (historical — TC-F30-005 complete)

Suspended 2026-08-03. Archive: [ops/render-decommission-archive.md](ops/render-decommission-archive.md).
Do not point `LIVE_*` or `config/prod.json` at onrender.com.

### Local (`METAR_CONFIG_ENV=local`)

| Setting | Value |
|---------|-------|
| Ports | **18000** frontend / **18001** API |
| CORS | `["http://localhost:18000"]` |
| `DATABASE_URL` | Local/DO Postgres for session + F8 integration tests |
| Auth | Optional; use project Auth + publishable key for UJ-046 |

### CI (GitHub Actions)

| Setting | Notes |
|---------|-------|
| Public convert | No Auth required |
| Session / Auth tests | Fixture user or mocked JWKS/JWT (M1/M2) |
| Postgres + Alembic | Service container `DATABASE_URL`; **`alembic upgrade head`** before schema tests (idempotent) |
| F8 / dissemination | `DATABASE_URL` + allowlist fixtures |

## Verification

```bash
make env-check              # local: .env + config JSON valid
make env-check LIVE=1       # optional: probe LIVE_API_URL /health
make test-live-connectivity # H4–H5 — required this cycle (D-S038-tp)
```

## References

- [ADR-033](adr/ADR-033-platform-independence-auth-do-doks.md)
- [ADR-031](adr/ADR-031-public-app-indexeddb-history.md) (partially superseded)
- [ADR-018](adr/ADR-018-f8-worker-template.md) (amended)
- [config-spec.md](config-spec.md)
- [deploy.md](deploy.md)
- [ops/supabase-to-do-postgres-migration.md](ops/supabase-to-do-postgres-migration.md)
