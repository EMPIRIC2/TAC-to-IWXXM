# Environment Contract — Render ↔ Supabase ↔ Local

> **Project**: METAR to IWXXM Converter  
> **Session**: S003-supabase-keys-config; S011-f7-operator-ui (BYO)  
> **Example deploy project** (not product tenancy): `ktvxijislbtgqapllmuk`  
> **Last updated**: 2026-07-13 (S011 / EV-008)

Single source of truth for **what** each layer owns and **which name** to use everywhere.

## BYO model (S011 / R6 / #697)

Each operator deploy points at **their** Supabase project + Postgres/`DATABASE_URL`. The
committed example project ref / URLs document the current hosted deploy for this repo — they
are **not** a shared multi-tenant admin product. No in-app paste-keys UI.

## Source of truth by layer

| Layer | Owns | Does not own |
|-------|------|--------------|
| **Operator Supabase** | Project URL, publishable key, secret key, `DATABASE_URL`, auth dashboard settings (signup/invite — G2) | Render URLs, CORS |
| **Render** | Deploy URLs, `PORT`, runtime secret injection, static `/config.json` build | Key generation (copy from operator Supabase) |
| **Repo** | `config/*.json` (non-secrets), `.env.example` (secret names), canonical contract | Live secret values |
| **Local** | `.env` (gitignored secrets), `METAR_CONFIG_ENV=local` | Production URLs unless testing live |

## Canonical names (one name per concern)

| Concern | Canonical | Where set |
|---------|-----------|-----------|
| Supabase project URL | `config.*.supabase.url` | `config/{local,prod}.json` (operator-specific) |
| Publishable key | `SUPABASE_PUBLISHABLE_KEY` | `.env` / Render API / GitHub CI |
| Secret key | `SUPABASE_SECRET_KEY` | `.env` / Render API only — **never** static frontend |
| Postgres | `DATABASE_URL` | `.env` / Render API |
| API public URL | `config.*.api.baseUrl` | `config/*.json` (`/api/v1` + `/auth` only) |
| Frontend public URL | `config.*.api.frontendUrl` | `config/*.json` |
| CORS | `config.*.api.corsOrigins` | `config/*.json` |
| Auth bypass (dev) | `config.*.api.disableAuth` | `config/local.json` only (G1) |
| Live/E2E login user | `E2E_USER_EMAIL`, `E2E_USER_PASSWORD` | local `.env` / CI secrets for harness |
| Converter engine (F6) | *(code — `packages/tac2iwxxm`)* | Not an env var; hard cutover, no engine flag |
| F8 worker Supabase URL | `SUPABASE_URL` | Render worker / local `.env` |
| F8 worker service role | `SUPABASE_SERVICE_ROLE_KEY` | Render worker / local `.env` (writers only) |
| F8 poller feed URL | `INGEST_POLLER_URL` | Render worker / local `.env` |
| F8 poll interval | `INGEST_POLL_INTERVAL_SEC` | Render worker env (default `30`) |

### Deprecated (S011)

| Deprecated | Replacement |
|------------|-------------|
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` (ordinary user; **not** admin role) |
| Product `/admin/*` | Removed |

## Per-environment matrix

### Production (Render + operator Supabase)

| Setting | Render API | Render static | Supabase dashboard |
|---------|------------|---------------|-------------------|
| `SUPABASE_PUBLISHABLE_KEY` | env (`sync: false`) | inject into `/config.json` at build | API Keys |
| `SUPABASE_SECRET_KEY` | env (`sync: false`) | **never** | API Keys |
| `DATABASE_URL` | env (`sync: false`) | **never** | Database → Connect |
| `config/prod.json` | loaded via `METAR_CONFIG_ENV=prod` | copied to `public/config.json` | — |
| Auth redirect URLs | — | — | Must include `api.frontendUrl` |
| Legacy JWT keys | — | — | **Disable** after migration |

Example project historically used in this repo: `ktvxijislbtgqapllmuk` — replace when BYO.

### Local (`METAR_CONFIG_ENV=local`)

| Setting | Value |
|---------|-------|
| `config/local.json` | Ports **18000** (frontend) / **18001** (API) |
| `.env` | Secrets placeholders (see [config-spec.md](config-spec.md)) |
| `api.disableAuth` | `true` |
| `api.corsOrigins` | `["http://localhost:18000"]` |
| Live auth tests | Prefer `DISABLE_AUTH`/local; else `E2E_USER_*` |

### CI (GitHub Actions)

| Setting | Canonical secret name (target) |
|---------|-------------------------------|
| Publishable key | `SUPABASE_PUBLISHABLE_KEY` |
| Supabase URL | In `config/prod.json` or test fixture — not duplicated in CI env |
| Live login (if used) | `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` |
| Integration job | Maps canonical names only; deprecate `FRONTEND_VITE_*` prefix |

## Drift problems addressed (S003 + S011)

| Issue | Remediation |
|-------|-------------|
| Same key, 4+ env names | Single `SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_SECRET_KEY` |
| URL in `.env` and `VITE_*` | `config.*.supabase.url` only |
| Secret key missing in compose | Pass `SUPABASE_SECRET_KEY` to API service |
| Non-secrets in `.env` | Move to `config/*.json` |
| Port 5173/8001 vs 18000/18001 | Standardize on compose ports (S003-R4) |
| `FRONTEND_VITE_*` CI secrets | Rename to canonical |
| Render `sync: false` drift | `make env-check` + [env-sync-runbook.md](ops/env-sync-runbook.md) |
| Shared-admin assumption | BYO + remove `/admin` (ADR-021) |
| `ADMIN_*` confused with admin role | Rename to `E2E_USER_*` |

## Verification

```bash
make env-check              # local: .env + config JSON valid
make env-check LIVE=1       # optional: probe Render /health + Supabase auth health
```

## References

- [config-spec.md](config-spec.md)
- [env-sync-runbook.md](ops/env-sync-runbook.md)
- [deploy.md](deploy.md)
- [ADR-021](adr/ADR-021-byo-credentials-admin-removal.md)
- [staging-secrets-matrix.md](ops/staging-secrets-matrix.md) — **deprecated**; use this document instead
