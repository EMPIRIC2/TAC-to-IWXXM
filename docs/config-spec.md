# Configuration Specification

> **Project**: METAR to IWXXM Converter  
> **Last updated**: 2026-08-03 (S038 / EV-031 — F30/F31 Auth-only Supabase + DO Postgres + DOKS)  
> **Session**: S003-supabase-keys-config (base); S008; S011; S023-public-app-privacy; **S038**

## Precedence Order

Configuration values resolve in this order (highest priority first):

1. Environment variables (secrets + abuse-control knobs — see below)
2. `config/{env}.json` selected by `METAR_CONFIG_ENV`
3. Built-in defaults in `packages/shared`

**Secrets never belong in `config/*.json`.** FE may receive **publishable** Auth bootstrap via
deploy-time `/config.json` inject. Product DB secrets are **`DATABASE_URL` only** (DigitalOcean).
Supabase **service-role must not** be used as the product data plane (ADR-033).

## BYO credentials (S011 / R6 / #697) — amended EV-031

Operators may still BYO **their** Supabase **Auth** project (URL + publishable + JWT verify).
Product Postgres is **DigitalOcean** (`DATABASE_URL`) — not Supabase hosted DB. F8 worker uses
`DATABASE_URL` + poller env (ADR-018 amend).

## Configuration Files

### `config/prod.json`

- **Format**: JSON
- **Location**: `config/prod.json` (committed; non-secrets)
- **Purpose**: Production URLs, CORS, validation flags, observability, live-test URLs
- **Selected when**: `METAR_CONFIG_ENV=prod` (default on Render API + static deploy)

| Field                            | Type         | Required | Description                                              |
| -------------------------------- | ------------ | -------- | -------------------------------------------------------- |
| `environment`                    | string       | Yes      | `"prod"`                                                 |
| `api.baseUrl`                    | string (URL) | Yes      | Public API origin (`/api/v1` **and** `/auth`) — **no** `/admin` |
| `api.frontendUrl`                | string (URL) | Yes      | Public static site URL (Auth redirects / CORS peer)      |
| `api.corsOrigins`                | string[]     | Yes      | Allowed browser origins for API CORS (DOKS FE after cutover) |
| `supabase.url`                   | string (URL) | Yes*     | Supabase **Auth** project URL (*required when Auth enabled) |
| `validation.wmoOnline`           | boolean      | No       | WMO online validation toggle                             |
| `validation.wmoTimeoutSeconds`   | number       | No       | WMO request timeout                                      |
| `validation.schematronUseDocker` | boolean      | No       | Docker-backed Schematron                                 |
| `observability.logLevel`         | string       | No       | Python log level                                         |
| `observability.enableStatistics` | boolean      | No       | Translation statistics                                   |
| `liveE2e.apiUrl`                 | string (URL) | No       | Canonical live API for `make test-live*`                 |
| `liveE2e.frontendUrl`            | string (URL) | No       | Canonical live frontend for H4–H6                        |

### `config/local.json`

- **Format**: JSON
- **Location**: `config/local.json` (committed)
- **Purpose**: Local dev URLs and flags
- **Selected when**: `METAR_CONFIG_ENV=local` (default for `make dev` / docker compose)

Same schema as `prod.json` with local values:

| Field             | Local value                                |
| ----------------- | ------------------------------------------ |
| `api.baseUrl`     | `http://localhost:18001`                   |
| `api.frontendUrl` | `http://localhost:18000`                   |
| `api.corsOrigins` | `["http://localhost:18000"]`               |
| `supabase.url`    | project URL                                |
| `supabase.url`    | `https://ktvxijislbtgqapllmuk.supabase.co` |

**Port standard (S003-R4):** Frontend `18000`, API `18001` everywhere — compose, config, and
`start-dev-servers.sh`.

### Frontend runtime `/config.json`

- **Format**: JSON (subset of environment config + publishable key)
- **Location**: Served from static host at `/config.json` (copied from `config/prod.json` at build)
- **Purpose**: Replace build-time `VITE_*` for URLs; fetch at app bootstrap (S003-R2)

Injected at deploy time (`scripts/frontend/prepare-config.sh` — publishable key not committed):

```json
{
  "environment": "prod",
  "api": {
    "baseUrl": "https://metar-to-iwxxm-api.onrender.com",
    "frontendUrl": "https://metar-to-iwxxm-frontend-v4-web.onrender.com",
    "corsOrigins": [
      "https://metar-to-iwxxm-frontend-v4-web.onrender.com",
      "https://app.doks.placeholder.metar-iwxxm.local"
    ]
  },
  "supabase": {
    "url": "https://ktvxijislbtgqapllmuk.supabase.co",
    "publishableKey": "<from SUPABASE_PUBLISHABLE_KEY env>"
  }
}
```

**Auth bootstrap (F31):** `supabase.url` + `supabase.publishableKey` drive the optional FE Auth
client. **`api.baseUrl`** is the single origin for `/api/v1/*` and `/auth/*`. DOKS FE placeholder
may appear in `corsOrigins` before real DNS. **`D-S038-t63-waive`**: `liveE2e.*` may point at
provisional DOKS placeholders (LB + `/etc/hosts` / Host-header) while public `api.baseUrl` /
`frontendUrl` remain Render until real DNS is pinned.

## Environment Variables (secrets + abuse controls)

Minimal `.env.example` — copy to repo-root `.env`. **Canonical names:** [env-contract.md](env-contract.md).

| Variable                                            | Required      | Description                                                  | Source                    |
| --------------------------------------------------- | ------------- | ------------------------------------------------------------ | ------------------------- |
| `RATE_LIMIT_PUBLIC_PER_MIN`                         | No            | Convert/lint/decode/validate/preview — default **60**/min/IP | ADR-031 / E17-19          |
| `RATE_LIMIT_DISSEMINATION_PER_MIN`                  | No            | Dissemination preflight/send — default **10**/min/IP         | ADR-031 / E17-19          |
| `MAX_REQUEST_BODY_BYTES`                            | No            | Max request body — default **2097152** (2 MiB)               | ADR-031 / E17-19          |
| `DISSEMINATION_EGRESS_ALLOWLIST`                    | Yes (F16–F19) | Host/CIDR allowlist; empty = fail-closed                     | ADR-029                   |
| `METAR_CONFIG_ENV`                                  | No            | `local` \| `prod` — selects `config/*.json`                  | Default `local`           |
| `DATABASE_URL`                                      | Yes (F30/F31) | DigitalOcean Postgres — sessions + F8 store/quarantine       | ADR-033                   |
| `SUPABASE_URL`                                      | Yes (Auth)    | Supabase Auth project URL                                    | ADR-010 / ADR-033         |
| `SUPABASE_PUBLISHABLE_KEY`                          | Yes (FE Auth) | Injected into `/config.json` for login bootstrap             | ADR-033                   |
| `SUPABASE_JWT_SECRET` (or JWKS via project)         | Yes (API Auth)| Server JWT verify — **never** FE                             | ADR-010 / ADR-033         |

### Do not use for product data plane (F30)

| Variable | Notes |
|----------|-------|
| `SUPABASE_SERVICE_ROLE_KEY` as DB writer | **Retired** for F8/product tables — use `DATABASE_URL` |
| Supabase Postgres pooler URI as app SoT | Migrate to DO — [ops note](ops/supabase-to-do-postgres-migration.md) |

### Optional live / E2E

| Variable | Notes |
|----------|-------|
| `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` | **Restored** for UJ-046 / session live tests only |
| `LIVE_API_URL` / `LIVE_FRONTEND_URL` | DOKS after cutover; Render until soak |

### Still retired / removed

| Name                                        | Status             | Notes                                  |
| ------------------------------------------- | ------------------ | -------------------------------------- |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD`            | **Removed** (S011) | —                                      |
| `DISABLE_AUTH` / `config.*.api.disableAuth` | **Retired**        | Public convert default; Auth additive  |
| Product `/admin/*` APIs                     | **Removed** (S011) | —                                      |

`create_admin_user.py` / bootstrap scripts (if retained) must not imply a shared multi-tenant
admin dashboard; prefer documenting operator Supabase Auth invite policy.

### Deprecated aliases (read with warning; remove after one release)

| Deprecated                              | Canonical                                      |
| --------------------------------------- | ---------------------------------------------- |
| `SUPABASE_ANON_KEY`                     | `SUPABASE_PUBLISHABLE_KEY`                     |
| `SUPABASE_SERVICE_ROLE_KEY` (as DB writer) | `DATABASE_URL` (ADR-033)                    |
| `VITE_SUPABASE_URL`                     | `config.*.supabase.url` / `/config.json`       |
| `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY` | `SUPABASE_PUBLISHABLE_KEY` inject              |
| `VITE_API_BASE_URL`                     | `config.*.api.baseUrl`                         |
| `VITE_APP_URL`                          | `config.*.api.frontendUrl`                     |
| `METAR_CORS_ORIGINS`                    | `config.*.api.corsOrigins`                     |
| `DISABLE_AUTH`                          | Do not set — public convert + optional Auth    |
| `FRONTEND_VITE_*` (GitHub secrets)      | Prefer `/config.json` inject                   |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD`        | Already retired (S011)                         |

## CLI / Makefile

| Target                  | Action                                                           |
| ----------------------- | ---------------------------------------------------------------- |
| `make env-check`        | Run `scripts/env/verify-sync.sh` — validate `.env` + config JSON |
| `make dev`              | `METAR_CONFIG_ENV=local`                                         |
| `make test-integration` | Requires secrets in `.env` + local config                        |

No new CLI flags.

## Validation Rules

- Rate-limit / body knobs must be positive integers when set (`RATE_LIMIT_*`, `MAX_REQUEST_BODY_BYTES`)
- `config/*.json` must parse as valid JSON; `api.corsOrigins` must be a non-empty array in prod
- `api.baseUrl` is the single API origin for `/api/v1/*` **and** `/auth/*` (F31 / ADR-033) — **no** `/admin`
- `make env-check` fails if Auth bootstrap is required without `supabase.url` / publishable key when Auth is enabled
- Secret / service-role keys must never appear in frontend build env or committed files
- Product DB writers use `DATABASE_URL` (DO Postgres) — not Supabase PostgREST service-role (F30)
- `DISSEMINATION_EGRESS_ALLOWLIST` empty ⇒ fail-closed (ADR-029)

## F6 — tac2iwxxm conversion (S008)

No new `config/*.json` keys and **no new environment variables** for F6.

| Concern                | Where it lives                    | Notes                                           |
| ---------------------- | --------------------------------- | ----------------------------------------------- |
| Default IWXXM version  | Existing shared/app constants     | Not a new config field                          |
| Default profile        | Code constant `annex3`            | API omits → annex3; not in JSON config          |
| Product                | **Required** on convert multipart | No server default; UI may auto-detect then send |
| Feature / cutover flag | **None**                          | Hard cutover in one PR (ADR-014)                |
| IWXXM-US enable        | Request `profile=iwxxm_us`        | Not an env kill switch                          |
| Converter engine       | Code path (`tac2iwxxm`)           | Not env-selected                                |

**Connectivity**: Frontend and API remain different origins on Render. Keep `api.corsOrigins`
correct; redeploy **API before** frontend sign-off when CORS/API contract changes. F6 UI pickers
use runtime `/config.json` — no new `VITE_*` required.

**`.env.example`**: Unchanged for F6.

## F7 — operator UI / BYO (S011 / EV-008)

No new `config/*.json` keys for decode/preview/spans. **No new secrets** for F7 APIs.

| Concern                 | Where it lives                        | Notes                            |
| ----------------------- | ------------------------------------- | -------------------------------- |
| BYO Supabase / Postgres | `config.*.supabase.url` + env secrets | Operator-owned; clean cut (G3)   |
| Admin UI / `/admin`     | Removed                               | UJ-019 / TC-F7-006               |
| Live harness login      | ~~`E2E_USER_*`~~                      | **Retired F21** — public convert |
| Workbench debounce      | Frontend code                         | Not config                       |
| CodeMirror 6            | Frontend dependency                   | See dependency-inventory         |
| Local sessions (F7.h)   | Browser IndexedDB (`idb`)             | ADR-031 — not server env         |

**Connectivity**: Live workbench increases browser→API call volume; keep CORS correct; H4–H5 gates
apply. Redeploy API before frontend when contract changes.

## F11–F14 — msgspec HTTP + PyPI publish (S014 / EV-010)

No new `config/*.json` keys for msgspec response encoding. **PyPI publish uses GitHub
OIDC trusted publishing** — no long-lived PyPI API token in repo secrets when OIDC is configured
([Real Python](https://realpython.com/pypi-publish-python-package/)).

| Concern                 | Where it lives                    | Notes                                                    |
| ----------------------- | --------------------------------- | -------------------------------------------------------- |
| msgspec vs pydantic     | Code + ADR-026                    | Response encode msgspec; multipart Form intake unchanged |
| OpenAPI aliases         | `apps/backend` schemas            | Thin pydantic mirrors for docs only                      |
| PyPI trusted publishing | GitHub Environment + PyPI project | OIDC; **one** workflow + package matrix; tags `{pkg}-v*` (e.g. `0.1.0`, `0.1.1`) |
| PyPI project names      | Package metadata                  | `tac-validate`, `iwxxm-validate`, `tac2iwxxm`            |
| Schema bundle size      | `iwxxm-validate` wheel build      | From `vendor/schemas/*` pins; not an env var             |
| Render redeploy         | Existing API/static secrets       | When API contract changes; CORS unchanged                |

**GitHub Actions (publish)** — configure in GitHub UI (not committed secrets):

| Setting                 | Purpose                                                                             |
| ----------------------- | ----------------------------------------------------------------------------------- |
| Environment e.g. `pypi` | Optional protection rules for publish jobs                                          |
| PyPI Trusted Publisher  | Per project: Owner `EMPIRIC2`, Repository `TAC-to-IWXXM`, Workflow `pypi-publish.yml`, Environment `pypi` (EV-028 / #781) |
| `id-token: write`       | Workflow permission for OIDC                                                        |

**Runtime API/FE env**: Unchanged for F11–F14. Redeploy **API before** frontend when response
JSON shapes change (H4–H5).

## F16–F19 — Dissemination (S019 / EV-014)

No new `config/*.json` keys for sink credentials (memory-only paste). **One new API env var**:

| Concern            | Where it lives                   | Notes                                                                                                                                                |
| ------------------ | -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Egress allowlist   | `DISSEMINATION_EGRESS_ALLOWLIST` | Host/CIDR list; empty = fail-closed (ADR-029; E14-08=A). Local/CI: `wis2box,127.0.0.1,127.0.0.0/8,localhost`. Live BYOC demos: exact hostnames only. |
| Destination creds  | Request body only                | Never env / never F5 persistence                                                                                                                     |
| wis2box harness    | `docker-compose` (+ CI)          | Not a Render web service (E14-04=B)                                                                                                                  |
| Dissemination HTTP | msgspec encode                   | Align ADR-026 (E14-07=A)                                                                                                                             |
| CORS               | Existing `corsOrigins`           | No new origins; H4–H5 when drawer ships (E14-10=A)                                                                                                   |

**`.env.example`**: Local/CI recommended allowlist set; Render/prod guidance in comments.

## F21 / F22 — Public convert + privacy (S023; **amended S038 / EV-031**)

IndexedDB + privacy prefs remain client-side. **EV-031** restores optional Auth + server sessions
on DO Postgres while keeping public convert and abuse-control env knobs:

| Concern                        | Where it lives                     | Notes                                     |
| ------------------------------ | ---------------------------------- | ----------------------------------------- |
| Public rate limit              | `RATE_LIMIT_PUBLIC_PER_MIN`        | Default 60/min/IP (slowapi; E17-19)       |
| Dissemination rate limit       | `RATE_LIMIT_DISSEMINATION_PER_MIN` | Default 10/min/IP                         |
| Max body                       | `MAX_REQUEST_BODY_BYTES`           | Default 2 MiB                             |
| Optional Auth                  | `SUPABASE_*` + `packages/auth`     | JWT for work-sessions only (ADR-033)      |
| Work sessions API              | `DATABASE_URL` + JWT               | Guest path remains IndexedDB              |
| Privacy prefs / GPC            | FE `localStorage` + headers        | F22 — deepen storage/Auth disclosure      |

**Connectivity**: H4–H5 **required** this cycle for FE Auth + guest notice + DOKS URLs.

## F30 / F31 — Platform independence (S038 / EV-031)

| Concern | Where it lives | Notes |
|---------|----------------|-------|
| Product DB | `DATABASE_URL` | DO Postgres — sessions + F8 |
| Hosting | DOKS | Render transitional until soak (TC-F30-005) |
| Legacy migrate | Ops runbook | [supabase-to-do-postgres-migration.md](ops/supabase-to-do-postgres-migration.md) |
| Live URLs | `LIVE_*` / `config.prod.liveE2e` | Point at DOKS after cutover |

### Session changelog

- S008 (2026-07-12): F6 — no new config/env; profile default in code; hard cutover
- S011 / EV-008 (2026-07-13): BYO; deprecate `ADMIN_*` → `E2E_USER_*`; drop `/admin` from baseUrl docs
- S014 / EV-010 (2026-07-18): PyPI OIDC trusted publishing notes; no new runtime secrets;
  matrix workflow clarification (05 S2.M1)
- S019 / EV-014 (2026-07-21): `DISSEMINATION_EGRESS_ALLOWLIST` (E14-08=A); no config JSON for sinks
- S019 / EV-014 T6.6 (2026-07-21): document local/CI recommended allowlist value; Render live value still operator-set (no `RENDER_API_KEY` in cloud agent)
- S023 / EV-017 (2026-07-28): F21 — rate-limit + body env; retire `DISABLE_AUTH` / `E2E_USER_*` / FE Auth keys (ADR-031)
- S026 / EV-020 (2026-07-29): F9 glossary package data + optional override; F3/OpenAIP reuse for
  decode names (ADR-032) — see §F24/F25/F9 below
- S027 / EV-021 (2026-07-29): F26/F27 VAA+TCA WMO goldens — **no new env vars**; see §F26/F27
- S038 / EV-031 (2026-08-03): F30/F31 — `DATABASE_URL` required; Auth keys restored; DOKS live URLs;
  F8 off Supabase DB (ADR-033)

## F24 / F25 / F9 deepen — WMO goldens + glossary (S026 / EV-020)

No new Render secrets required for convert goldens (package-side). Decode glossary ships as
**package data**; optional override for operators/maintainers:

| Concern | Where it lives | Notes |
|---------|----------------|-------|
| WMO golden defaults | Code defaults | `profile=annex3`, pinned default `iwxxm_version` — ADR-032 |
| Decode glossary | Official/near-official sources + YAML **overrides** | E20-E2; ADR-032 |
| Glossary override path | Packaged `decode_glossary.yaml` + optional `TAC2IWXXM_DECODE_GLOSSARY_PATH` | Overlay only |
| OpenAIP / F3 names | Existing F3 / OpenAIP config | Enrich decode when available; miss → ICAO only |
| FE Examples catalog | Static FE fixtures | No env; WMO-passers only |

**Connectivity**: H4–H5 when FE catalog / decode copy changes. Redeploy API before frontend if
decode-tac string behavior ships in API image.

## F26 / F27 — VAA + TCA quality (S027 / EV-021)

No new Render secrets or env vars. Package-side goldens under ADR-032 defaults; FE Examples
catalog remains static fixtures (WMO-passers only for VAA/TCA when F26/F27 green — E21-3).

| Concern | Where it lives | Notes |
|---------|----------------|-------|
| WMO golden defaults | Code defaults | `profile=annex3`, pinned default `iwxxm_version` — ADR-032 |
| VAA/TCA lint codes | `tac-validate` ADR-028 registry | Additive codes only; no new HTTP config |
| FE Examples catalog | Static FE fixtures | No env; hide non-passers until goldens green |

**Connectivity**: H4–H5 when FE catalog changes. Redeploy API before frontend if convert/lint
behavior ships in API image.

## S030 / EV-023 — APAC encode deltas + translationCentre gate (#800)

| Parameter | Source | Notes |
|-----------|--------|-------|
| Default `translationCentre*` | Code default **omit** | In-State / self-produced convert — FAQ §14.5 |
| Emit `translationCentreDesignator` / `translationCentreName` | Optional convert request/config flag (name TBD in 04) | Cross-State / Translation Centre only |
| Dual-register / nil hrefs | Offline vendor RDF/CSV under `vendor/` | No live codes.wmo.int HTML in CI |
| Informative translation suite | CI or nightly marker | No 2023-1 XML byte-match required |

No new Render secrets required for P0/P1 library fixtures. Redeploy API before claiming
13-deploy-smoke if convert quarantine / nil / NSC behavior changes.

## References

- [env-contract.md](env-contract.md) — per-environment matrix (**canonical F30/F31**)
- [env-sync-runbook.md](ops/env-sync-runbook.md) — operator rotation steps
- [ADR-010](adr/ADR-010-supabase-keys-config-split.md)
- [ADR-033](adr/ADR-033-platform-independence-auth-do-doks.md)
- [ADR-031](adr/ADR-031-public-app-indexeddb-history.md) — partially superseded (guest IndexedDB + public convert kept)
- [ADR-020](adr/ADR-020-unified-tac-work-sessions.md) — session shape; host = DO Postgres under ADR-033
- [ADR-014](adr/ADR-014-tac2iwxxm-rust-gifts-removal.md)
- [ADR-026](adr/ADR-026-msgspec-http-openapi.md)
- [ADR-021](adr/ADR-021-byo-credentials-admin-removal.md)
- [ADR-029](adr/ADR-029-dissemination-ssrf-allowlist.md)
- [ADR-030](adr/ADR-030-dissemination-package-architecture.md)
- [ADR-032](adr/ADR-032-wmo-default-golden-glossary.md) — WMO default goldens + glossary
- [deploy.md](deploy.md) §Integration
- [api-contract.md](api-contract.md)
- Supabase Auth: [API keys](https://supabase.com/docs/guides/api/api-keys)
