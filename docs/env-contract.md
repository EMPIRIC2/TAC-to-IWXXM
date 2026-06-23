# Environment Contract — Render ↔ Supabase ↔ Local

> **Project**: METAR to IWXXM Converter  
> **Session**: S003-supabase-keys-config  
> **Supabase project**: `ktvxijislbtgqapllmuk`  
> **Last updated**: 2026-06-23

Single source of truth for **what** each layer owns and **which name** to use everywhere.

## Source of truth by layer

| Layer | Owns | Does not own |
|-------|------|--------------|
| **Supabase** | Project URL, publishable key, secret key, `DATABASE_URL`, auth dashboard settings | Render URLs, CORS |
| **Render** | Deploy URLs, `PORT`, runtime secret injection, static `/config.json` build | Key generation (copy from Supabase) |
| **Repo** | `config/*.json` (non-secrets), `.env.example` (secret names), canonical contract | Live secret values |
| **Local** | `.env` (gitignored secrets), `METAR_CONFIG_ENV=local` | Production URLs unless testing live |

## Canonical names (one name per concern)

| Concern | Canonical | Where set |
|---------|-----------|-----------|
| Supabase project URL | `config.*.supabase.url` | `config/{local,prod}.json` |
| Publishable key | `SUPABASE_PUBLISHABLE_KEY` | `.env` / Render API / GitHub CI |
| Secret key | `SUPABASE_SECRET_KEY` | `.env` / Render API only — **never** static frontend |
| Postgres | `DATABASE_URL` | `.env` / Render API |
| API public URL | `config.*.api.baseUrl` | `config/*.json` |
| Frontend public URL | `config.*.api.frontendUrl` | `config/*.json` |
| CORS | `config.*.api.corsOrigins` | `config/*.json` |
| Auth bypass (dev) | `config.*.api.disableAuth` | `config/local.json` only |
| Operator bootstrap | `ADMIN_EMAIL`, `ADMIN_PASSWORD` | local `.env` only |

## Per-environment matrix

### Production (Render + Supabase `ktvxijislbtgqapllmuk`)

| Setting | Render API | Render static | Supabase dashboard |
|---------|------------|---------------|-------------------|
| `SUPABASE_PUBLISHABLE_KEY` | env (`sync: false`) | inject into `/config.json` at build | API Keys |
| `SUPABASE_SECRET_KEY` | env (`sync: false`) | **never** | API Keys |
| `DATABASE_URL` | env (`sync: false`) | **never** | Database → Connect |
| `config/prod.json` | loaded via `METAR_CONFIG_ENV=prod` | copied to `public/config.json` | — |
| Auth redirect URLs | — | — | Must include `api.frontendUrl` |
| Legacy JWT keys | — | — | **Disable** after migration |

### Local (`METAR_CONFIG_ENV=local`)

| Setting | Value |
|---------|-------|
| `config/local.json` | Ports **18000** (frontend) / **18001** (API) |
| `.env` | Five secret placeholders (see [config-spec.md](config-spec.md)) |
| `api.disableAuth` | `true` |
| `api.corsOrigins` | `["http://localhost:18000"]` |

### CI (GitHub Actions)

| Setting | Canonical secret name (target) |
|---------|-------------------------------|
| Publishable key | `SUPABASE_PUBLISHABLE_KEY` |
| Supabase URL | In `config/prod.json` or test fixture — not duplicated in CI env |
| Integration job | Maps canonical names only; deprecate `FRONTEND_VITE_*` prefix |

## Drift problems addressed (S003)

| Issue | Remediation |
|-------|-------------|
| Same key, 4+ env names | Single `SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_SECRET_KEY` |
| URL in `.env` and `VITE_*` | `config.*.supabase.url` only |
| Secret key missing in compose | Pass `SUPABASE_SECRET_KEY` to API service |
| Non-secrets in `.env` | Move to `config/*.json` |
| Port 5173/8001 vs 18000/18001 | Standardize on compose ports (S003-R4) |
| `FRONTEND_VITE_*` CI secrets | Rename to canonical |
| Render `sync: false` drift | `make env-check` + [env-sync-runbook.md](env-sync-runbook.md) |

## Verification

```bash
make env-check              # local: .env + config JSON valid
make env-check LIVE=1       # optional: probe Render /health + Supabase auth health
```

## References

- [config-spec.md](config-spec.md)
- [env-sync-runbook.md](env-sync-runbook.md)
- [deploy.md](deploy.md)
- [staging-secrets-matrix.md](staging-secrets-matrix.md) — **deprecated**; use this document instead
