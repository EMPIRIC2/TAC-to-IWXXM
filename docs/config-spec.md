# Configuration Specification

> **Project**: METAR to IWXXM Converter  
> **Last updated**: 2026-07-18 (S014 / EV-010 — PyPI publish + msgspec Render redeploy)  
> **Session**: S003-supabase-keys-config (base); S008; S011-f7-operator-ui

## Precedence Order

Configuration values resolve in this order (highest priority first):

1. Environment variables (secrets only — see below)
2. `config/{env}.json` selected by `METAR_CONFIG_ENV`
3. Built-in defaults in `packages/shared`

**Secrets never belong in `config/*.json`.** Publishable keys load from env at runtime and are
injected into the frontend bootstrap config by the deploy pipeline.

## BYO credentials (S011 / R6 / #697)

Operators configure **their** Supabase project URL (in `config/*.json`) and inject **their**
`SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SECRET_KEY`, and `DATABASE_URL` via deploy/env. There is
**no** in-app paste-keys UI and **no** shared multi-tenant admin product surface. Example URLs in
committed `config/prod.json` / docs reflect the current deploy — not a fixed product tenancy.

## Configuration Files

### `config/prod.json`

- **Format**: JSON
- **Location**: `config/prod.json` (committed; non-secrets)
- **Purpose**: Production URLs, CORS, validation flags, observability, live-test URLs
- **Selected when**: `METAR_CONFIG_ENV=prod` (default on Render API + static deploy)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `environment` | string | Yes | `"prod"` |
| `api.baseUrl` | string (URL) | Yes | Public API origin (`/api/v1`, `/auth`) — **no** `/admin` |
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
| `SUPABASE_PUBLISHABLE_KEY` | Yes* | `sb_publishable_*` — client + server JWT validation | Operator Supabase → API Keys |
| `SUPABASE_SECRET_KEY` | Yes* | `sb_secret_*` — Auth Admin API scripts only | Operator Supabase → API Keys |
| `DATABASE_URL` | Yes* | Postgres pooler / SQL URI | Operator Supabase → Database → Connect |
| `METAR_CONFIG_ENV` | No | `local` \| `prod` — selects `config/*.json` | Default `local` |
| `E2E_USER_EMAIL` | Live tests | Ordinary user for `POST /auth/login` in live harness | Operator test user |
| `E2E_USER_PASSWORD` | Live tests | Password for that user | Operator |

\* Required when `api.disableAuth` / auth is enabled for that environment.

### Deprecated / removed (S011)

| Name | Status | Replacement |
|------|--------|-------------|
| `ADMIN_EMAIL` | **Deprecated — remove** | `E2E_USER_EMAIL` (live/E2E login only; not an admin role) |
| `ADMIN_PASSWORD` | **Deprecated — remove** | `E2E_USER_PASSWORD` |
| Product `/admin/*` APIs | **Removed** | — |

`create_admin_user.py` / bootstrap scripts (if retained) must not imply a shared multi-tenant
admin dashboard; prefer documenting operator Supabase dashboard invite policy (G2).

### Deprecated aliases (read with warning; remove after one release)

| Deprecated | Canonical |
|------------|-----------|
| `SUPABASE_ANON_KEY` | `SUPABASE_PUBLISHABLE_KEY` |
| `SUPABASE_SERVICE_ROLE_KEY` | `SUPABASE_SECRET_KEY` (API Auth Admin scripts) — **F8 worker** still uses service role under its own worker env name per env-contract |
| `VITE_SUPABASE_URL` | `config.*.supabase.url` + runtime `/config.json` |
| `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY` | `SUPABASE_PUBLISHABLE_KEY` via runtime config |
| `VITE_API_BASE_URL` | `config.*.api.baseUrl` |
| `VITE_APP_URL` | `config.*.api.frontendUrl` |
| `METAR_CORS_ORIGINS` | `config.*.api.corsOrigins` |
| `DISABLE_AUTH` | `config.*.api.disableAuth` (env alias may remain for local shell) |
| `FRONTEND_VITE_*` (GitHub secrets) | `SUPABASE_PUBLISHABLE_KEY` / URL in config |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` |

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

## F6 — tac2iwxxm conversion (S008)

No new `config/*.json` keys and **no new environment variables** for F6.

| Concern | Where it lives | Notes |
|---------|----------------|-------|
| Default IWXXM version | Existing shared/app constants | Not a new config field |
| Default profile | Code constant `annex3` | API omits → annex3; not in JSON config |
| Product | **Required** on convert multipart | No server default; UI may auto-detect then send |
| Feature / cutover flag | **None** | Hard cutover in one PR (ADR-014) |
| IWXXM-US enable | Request `profile=iwxxm_us` | Not an env kill switch |
| Converter engine | Code path (`tac2iwxxm`) | Not env-selected |

**Connectivity**: Frontend and API remain different origins on Render. Keep `api.corsOrigins`
correct; redeploy **API before** frontend sign-off when CORS/API contract changes. F6 UI pickers
use runtime `/config.json` — no new `VITE_*` required.

**`.env.example`**: Unchanged for F6.

## F7 — operator UI / BYO (S011 / EV-008)

No new `config/*.json` keys for decode/preview/spans. **No new secrets** for F7 APIs.

| Concern | Where it lives | Notes |
|---------|----------------|-------|
| BYO Supabase / Postgres | `config.*.supabase.url` + env secrets | Operator-owned; clean cut (G3) |
| Admin UI / `/admin` | Removed | UJ-019 / TC-F7-006 |
| Live harness login | `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` | Replaces `ADMIN_*` |
| Workbench debounce | Frontend code | Not config |
| CodeMirror 6 | Frontend dependency | See dependency-inventory |

**Connectivity**: Live workbench increases browser→API call volume; keep CORS correct; H4–H5 gates
apply. Redeploy API before frontend when contract changes.

## F11–F14 — msgspec HTTP + PyPI publish (S014 / EV-010)

No new `config/*.json` keys for msgspec response encoding. **PyPI publish uses GitHub
OIDC trusted publishing** — no long-lived PyPI API token in repo secrets when OIDC is configured
([Real Python](https://realpython.com/pypi-publish-python-package/)).

| Concern | Where it lives | Notes |
|---------|----------------|-------|
| msgspec vs pydantic | Code + ADR-026 | Response encode msgspec; multipart Form intake unchanged |
| OpenAPI aliases | `apps/backend` schemas | Thin pydantic mirrors for docs only |
| PyPI trusted publishing | GitHub Environment + PyPI project | OIDC; **one** workflow + package matrix; tags `*-v0.1.0` |
| PyPI project names | Package metadata | `tac-validate`, `iwxxm-validate`, `tac2iwxxm` |
| Schema bundle size | `iwxxm-validate` wheel build | From `vendor/schemas/*` pins; not an env var |
| Render redeploy | Existing API/static secrets | Required this cycle (E10-15); CORS unchanged |

**GitHub Actions (publish)** — configure in GitHub UI (not committed secrets):

| Setting | Purpose |
|---------|---------|
| Environment e.g. `pypi` | Optional protection rules for publish jobs |
| PyPI Trusted Publisher | Links each PyPI project to the **same** matrix workflow + that package's tag filter |
| `id-token: write` | Workflow permission for OIDC |

**Runtime API/FE env**: Unchanged for F11–F14. Redeploy **API before** frontend when response
JSON shapes change (H4–H5).

## F16–F19 — Dissemination (S019 / EV-014)

No new `config/*.json` keys for sink credentials (memory-only paste). **One new API env var**:

| Concern | Where it lives | Notes |
|---------|----------------|-------|
| Egress allowlist | `DISSEMINATION_EGRESS_ALLOWLIST` | Host/CIDR list; empty = fail-closed (ADR-029; E14-08=A). Local/CI: `wis2box,127.0.0.1,127.0.0.0/8,localhost`. Live BYOC demos: exact hostnames only. |
| Destination creds | Request body only | Never env / never F5 persistence |
| wis2box harness | `docker-compose` (+ CI) | Not a Render web service (E14-04=B) |
| Dissemination HTTP | msgspec encode | Align ADR-026 (E14-07=A) |
| CORS | Existing `corsOrigins` | No new origins; H4–H5 when drawer ships (E14-10=A) |

**`.env.example`**: Local/CI recommended allowlist set; Render/prod guidance in comments.

### Session changelog

- S008 (2026-07-12): F6 — no new config/env; profile default in code; hard cutover
- S011 / EV-008 (2026-07-13): BYO; deprecate `ADMIN_*` → `E2E_USER_*`; drop `/admin` from baseUrl docs
- S014 / EV-010 (2026-07-18): PyPI OIDC trusted publishing notes; no new runtime secrets;
  matrix workflow clarification (05 S2.M1)
- S019 / EV-014 (2026-07-21): `DISSEMINATION_EGRESS_ALLOWLIST` (E14-08=A); no config JSON for sinks
- S019 / EV-014 T6.6 (2026-07-21): document local/CI recommended allowlist value; Render live value still operator-set (no `RENDER_API_KEY` in cloud agent)

## References

- [env-contract.md](env-contract.md) — per-environment matrix
- [env-sync-runbook.md](ops/env-sync-runbook.md) — operator rotation steps
- [ADR-010](adr/ADR-010-supabase-keys-config-split.md)
- [ADR-014](adr/ADR-014-tac2iwxxm-rust-gifts-removal.md)
- [ADR-026](adr/ADR-026-msgspec-http-openapi.md)
- [ADR-020](adr/ADR-020-unified-tac-work-sessions.md)
- [ADR-021](adr/ADR-021-byo-credentials-admin-removal.md)
- [ADR-029](adr/ADR-029-dissemination-ssrf-allowlist.md)
- [ADR-030](adr/ADR-030-dissemination-package-architecture.md)
- [deploy.md](deploy.md) §Integration
- [api-contract.md](api-contract.md)
- Supabase: [API keys](https://supabase.com/docs/guides/api/api-keys)
