# Environment Contract — DOKS / Auth-only Supabase / DO Postgres (F30 / F31)

> **Project**: METAR to IWXXM Converter  
> **Session**: S038-platform-independence-842 / EV-031 (F30/F31)  
> **Supersedes**: F21-only public-app contract (S023) for Auth + data-plane topology  
> **Last updated**: 2026-08-03  
> **Status**: **Draft** (01-requirements) — finalize names in 04/06 as needed

Single source of truth for **what** each layer owns and **which name** to use everywhere.

## Model (EV-031)

- **Convert / lint / validate / disseminate** remain **public** (no JWT).
- **Optional Supabase Auth** for long-term work sessions only (JWT → `/api/v1/work-sessions*`).
- **Guests**: IndexedDB + persistent loss-of-progress notice; F22 privacy gates.
- **Product DB**: DigitalOcean Postgres via `DATABASE_URL` (sessions + F8).
- **Supabase**: Auth URL + keys only — **not** product PostgREST / hosted app tables.
- **Compute**: DOKS after F30 cutover (Render transitional until soak + decommission).
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
| Auth JWT verify (server) | **JWKS-only** via Supabase Auth JWKS URL (`D-S038-04-b1`) | API only — never FE; `SUPABASE_JWT_SECRET` not used for product verify |
| Public rate limit | `RATE_LIMIT_PUBLIC_PER_MIN` | API / `.env` (default **60**) |
| Dissemination rate limit | `RATE_LIMIT_DISSEMINATION_PER_MIN` | API / `.env` (default **10**) |
| Max request body | `MAX_REQUEST_BODY_BYTES` | API / `.env` (default **2097152** = 2 MiB) |
| Dissemination egress allowlist | `DISSEMINATION_EGRESS_ALLOWLIST` | API / `.env` (ADR-029) |
| F8 poller feed URL | `INGEST_POLLER_URL` | Worker / local `.env` |
| F8 poll interval | `INGEST_POLL_INTERVAL_SEC` | Worker (default `30`) |
| Live API URL | `LIVE_API_URL` | Local/CI live harness (DOKS after cutover) |
| Live frontend URL | `LIVE_FRONTEND_URL` | Local/CI live harness |
| E2E Auth fixture | `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` | Live/local Auth session tests only |

### Retired / do not use for product data plane

| Retired for product DB | Replacement |
|------------------------|-------------|
| Supabase Postgres pooler as app SoT | `DATABASE_URL` → DigitalOcean Postgres |
| `SUPABASE_SERVICE_ROLE_KEY` as F8 **DB** writer | SQL via `DATABASE_URL` (ADR-018 amend) |
| Operator product tables on Supabase | Migrated once — [ops note](ops/supabase-to-do-postgres-migration.md) |

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
| `SUPABASE_URL` + JWT verify | required for Auth | — | — |
| Publishable key inject | — | `/config.json` | — |
| Rate limits / body / allowlist | env | — | — |
| `METAR_CONFIG_ENV=prod` | yes | copy → `public/config.json` | — |
| F8 poller | — | — | env |

### Transitional (Render — until soak)

Same names; hosts remain onrender.com until TC-F30-005 decommission.

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
| Session / Auth tests | Fixture user or mocked JWT as designed in 04 |
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
