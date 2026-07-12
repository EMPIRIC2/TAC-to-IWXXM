# Configuration Specification

> **Project**: METAR to IWXXM Converter  
> **Session**: S003-supabase-keys-config (delta)  
> **Last updated**: 2026-06-23

## Precedence Order

Configuration values resolve in this order (highest priority first):

1. Environment variables (secrets only — see below)
2. `config/{env}.json` selected by `METAR_CONFIG_ENV`
3. Built-in defaults in `packages/shared`

**Secrets never belong in `config/*.json`.** Publishable keys load from env at runtime and are
injected into the frontend bootstrap config by the deploy pipeline.

## Configuration Files

### `config/prod.json`

- **Format**: JSON
- **Location**: `config/prod.json` (committed; non-secrets)
- **Purpose**: Production URLs, CORS, validation flags, observability, live-test URLs
- **Selected when**: `METAR_CONFIG_ENV=prod` (default on Render API + static deploy)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `environment` | string | Yes | `"prod"` |
| `api.baseUrl` | string (URL) | Yes | Public API origin (`/api/v1`, `/auth`, `/admin`) |
| `api.frontendUrl` | string (URL) | Yes | Public static site URL (auth redirects) |
| `api.corsOrigins` | string[] | Yes | Allowed browser origins for API CORS |
| `api.disableAuth` | boolean | Yes | `false` in production |
| `supabase.url` | string (URL) | Yes | Supabase project URL (public) |
| `validation.wmoOnline` | boolean | No | WMO online validation toggle |
| `validation.wmoTimeoutSeconds` | number | No | WMO request timeout |
| `validation.schematronUseDocker` | boolean | No | Docker-backed Schematron |
| `observability.logLevel` | string | No | Python log level |
| `observability.enableStatistics` | boolean | No | Translation statistics |
| `liveE2e.apiUrl` | string (URL) | No | Canonical live API for `make test-live*` |
| `liveE2e.frontendUrl` | string (URL) | No | Canonical live frontend for H4–H6 |

### `config/local.json`

- **Format**: JSON
- **Location**: `config/local.json` (committed)
- **Purpose**: Local dev URLs and flags
- **Selected when**: `METAR_CONFIG_ENV=local` (default for `make dev` / docker compose)

Same schema as `prod.json` with local values:

| Field | Local value |
|-------|-------------|
| `api.baseUrl` | `http://localhost:18001` |
| `api.frontendUrl` | `http://localhost:18000` |
| `api.corsOrigins` | `["http://localhost:18000"]` |
| `api.disableAuth` | `true` |
| `supabase.url` | `https://ktvxijislbtgqapllmuk.supabase.co` |

**Port standard (S003-R4):** Frontend `18000`, API `18001` everywhere — compose, config, and
`start-dev-servers.sh`.

### Frontend runtime `/config.json`

- **Format**: JSON (subset of environment config + publishable key)
- **Location**: Served from static host at `/config.json` (copied from `config/prod.json` at build)
- **Purpose**: Replace build-time `VITE_*` for URLs; fetch at app bootstrap (S003-R2)

Injected at deploy time (not committed):

```json
{
  "supabase": {
    "url": "https://ktvxijislbtgqapllmuk.supabase.co",
    "publishableKey": "<from SUPABASE_PUBLISHABLE_KEY env>"
  }
}
```

## Environment Variables (secrets only)

Minimal `.env.example` — copy to repo-root `.env`:

| Variable | Required | Description | Source |
|----------|----------|-------------|--------|
| `SUPABASE_PUBLISHABLE_KEY` | Yes | `sb_publishable_*` — client + server JWT validation | Supabase → API Keys |
| `SUPABASE_SECRET_KEY` | Yes | `sb_secret_*` — Auth Admin API only (`create_admin_user.py`) | Supabase → API Keys |
| `DATABASE_URL` | Yes | Postgres pooler URL | Supabase → Database → Connect |
| `ADMIN_EMAIL` | Local only | Operator bootstrap user | Operator |
| `ADMIN_PASSWORD` | Local only | Operator bootstrap password | Operator |
| `METAR_CONFIG_ENV` | No | `local` \| `prod` — selects `config/*.json` | Default `local` |

### Deprecated aliases (read with warning; remove after one release)

| Deprecated | Canonical |
|------------|-----------|
| `SUPABASE_ANON_KEY` | `SUPABASE_PUBLISHABLE_KEY` |
| `SUPABASE_SERVICE_ROLE_KEY` | `SUPABASE_SECRET_KEY` |
| `VITE_SUPABASE_URL` | `config.*.supabase.url` + runtime `/config.json` |
| `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY` | `SUPABASE_PUBLISHABLE_KEY` via runtime config |
| `VITE_API_BASE_URL` | `config.*.api.baseUrl` |
| `VITE_APP_URL` | `config.*.api.frontendUrl` |
| `METAR_CORS_ORIGINS` | `config.*.api.corsOrigins` |
| `DISABLE_AUTH` | `config.*.api.disableAuth` |
| `FRONTEND_VITE_*` (GitHub secrets) | `SUPABASE_PUBLISHABLE_KEY` / URL in config |

## CLI / Makefile

| Target | Action |
|--------|--------|
| `make env-check` | Run `scripts/env/verify-sync.sh` — validate `.env` + config JSON |
| `make dev` | `METAR_CONFIG_ENV=local` |
| `make test-integration` | Requires secrets in `.env` + local config |

No new CLI flags.

## Validation Rules

- `SUPABASE_PUBLISHABLE_KEY` and `SUPABASE_SECRET_KEY` must not be empty when `DISABLE_AUTH=false`
- `config/*.json` must parse as valid JSON; `api.corsOrigins` must be a non-empty array in prod
- `make env-check` fails if deprecated-only names are set without canonical names (warning mode during transition)
- Secret key must never appear in frontend build env or committed files

## References

- [env-contract.md](env-contract.md) — per-environment matrix
- [env-sync-runbook.md](ops/env-sync-runbook.md) — operator rotation steps
- [ADR-010](adr/ADR-010-supabase-keys-config-split.md)
- [deploy.md](deploy.md) §Integration
- Supabase: [API keys](https://supabase.com/docs/guides/api/api-keys)
