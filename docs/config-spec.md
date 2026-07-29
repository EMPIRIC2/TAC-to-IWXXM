# Configuration Specification

> **Project**: METAR to IWXXM Converter  
> **Last updated**: 2026-07-28 (S023 / EV-017 — F21 public app rate-limit env + Auth retirement)  
> **Session**: S003-supabase-keys-config (base); S008; S011; S023-public-app-privacy

## Precedence Order

Configuration values resolve in this order (highest priority first):

1. Environment variables (secrets + abuse-control knobs — see below)
2. `config/{env}.json` selected by `METAR_CONFIG_ENV`
3. Built-in defaults in `packages/shared`

**Secrets never belong in `config/*.json`.** Publishable keys for **operator Auth** are
**retired (F21)** — FE no longer bootstraps Supabase Auth. F8 worker still uses service-role
env on the Render Background Worker only (ADR-018).

## BYO credentials (S011 / R6 / #697) — **historical; F21 supersedes operator Auth**

Pre-F21 operators configured **their** Supabase project for JWT Auth. **F21 / ADR-031** removes
operator Auth and browser publishable-key injection. Retain this section only for archive/
F8 worker context: worker still needs service-role + poller URL (see [env-contract.md](env-contract.md)).

## Configuration Files

### `config/prod.json`

- **Format**: JSON
- **Location**: `config/prod.json` (committed; non-secrets)
- **Purpose**: Production URLs, CORS, validation flags, observability, live-test URLs
- **Selected when**: `METAR_CONFIG_ENV=prod` (default on Render API + static deploy)

| Field                            | Type         | Required | Description                                              |
| -------------------------------- | ------------ | -------- | -------------------------------------------------------- |
| `environment`                    | string       | Yes      | `"prod"`                                                 |
| `api.baseUrl`                    | string (URL) | Yes      | Public API origin (`/api/v1`, `/auth`) — **no** `/admin` |
| `api.frontendUrl`                | string (URL) | Yes      | Public static site URL (auth redirects)                  |
| `api.corsOrigins`                | string[]     | Yes      | Allowed browser origins for API CORS                     |
| `supabase.url`                   | string (URL) | Yes      | Supabase project URL (public; edge helpers)              |
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

Injected at deploy time (not committed):

```json
{
  "supabase": {
    "url": "https://ktvxijislbtgqapllmuk.supabase.co",
    "publishableKey": "<from SUPABASE_PUBLISHABLE_KEY env>"
  }
}
```

## Environment Variables (secrets + abuse controls)

Minimal `.env.example` — copy to repo-root `.env`. **Canonical names:** [env-contract.md](env-contract.md).

| Variable                                            | Required      | Description                                                  | Source                    |
| --------------------------------------------------- | ------------- | ------------------------------------------------------------ | ------------------------- |
| `RATE_LIMIT_PUBLIC_PER_MIN`                         | No            | Convert/lint/decode/validate/preview — default **60**/min/IP | ADR-031 / E17-19          |
| `RATE_LIMIT_DISSEMINATION_PER_MIN`                  | No            | Dissemination preflight/send — default **10**/min/IP         | ADR-031 / E17-19          |
| `MAX_REQUEST_BODY_BYTES`                            | No            | Max request body — default **2097152** (2 MiB)               | ADR-031 / E17-19          |
| `DISSEMINATION_EGRESS_ALLOWLIST`                    | Yes (F16–F19) | Host/CIDR allowlist; empty = fail-closed                     | ADR-029                   |
| `METAR_CONFIG_ENV`                                  | No            | `local` \| `prod` — selects `config/*.json`                  | Default `local`           |
| `DATABASE_URL`                                      | Ops/F8 only   | Postgres pooler / SQL URI                                    | Legacy archive / F8 store |
| `SUPABASE_SECRET_KEY` / `SUPABASE_SERVICE_ROLE_KEY` | F8 worker     | Service-role for ingest — **never** FE                       | ADR-018                   |

### Retired (F21 — do not set for operator product)

| Name                                        | Status             | Replacement                        |
| ------------------------------------------- | ------------------ | ---------------------------------- |
| `E2E_USER_EMAIL` / `E2E_USER_PASSWORD`      | **Retired F21**    | Public convert; `TC-F21-auth-gone` |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD`            | **Removed** (S011) | —                                  |
| `DISABLE_AUTH` / `config.*.api.disableAuth` | **Retired F21**    | Public by default (ADR-031)        |
| `SUPABASE_PUBLISHABLE_KEY` (browser Auth)   | **Retired F21**    | No FE Auth bootstrap               |
| Product `/admin/*` APIs                     | **Removed** (S011) | —                                  |

`create_admin_user.py` / bootstrap scripts (if retained) must not imply a shared multi-tenant
admin dashboard; prefer documenting operator Supabase dashboard invite policy for **F8/ops only**.

### Deprecated aliases (read with warning; remove after one release)

| Deprecated                              | Canonical                                      |
| --------------------------------------- | ---------------------------------------------- |
| `SUPABASE_ANON_KEY`                     | Retired for FE Auth; ops-only if still present |
| `SUPABASE_SERVICE_ROLE_KEY`             | F8 worker env (see env-contract)               |
| `VITE_SUPABASE_URL`                     | Retired for Auth path (F21)                    |
| `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY` | Retired for Auth path (F21)                    |
| `VITE_API_BASE_URL`                     | `config.*.api.baseUrl`                         |
| `VITE_APP_URL`                          | `config.*.api.frontendUrl`                     |
| `METAR_CORS_ORIGINS`                    | `config.*.api.corsOrigins`                     |
| `DISABLE_AUTH`                          | **Retired F21** — do not set                   |
| `FRONTEND_VITE_*` (GitHub secrets)      | Retired for Auth path                          |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD`        | Already retired (S011)                         |
| `E2E_USER_EMAIL` / `E2E_USER_PASSWORD`  | **Retired F21**                                |

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
- `api.baseUrl` must be `/api/v1` only (no `/auth`) under F21
- `make env-check` fails if deprecated Auth-only names are required without F21 replacements
- Secret / service-role keys must never appear in frontend build env or committed files
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
| PyPI trusted publishing | GitHub Environment + PyPI project | OIDC; **one** workflow + package matrix; tags `*-v0.1.0` |
| PyPI project names      | Package metadata                  | `tac-validate`, `iwxxm-validate`, `tac2iwxxm`            |
| Schema bundle size      | `iwxxm-validate` wheel build      | From `vendor/schemas/*` pins; not an env var             |
| Render redeploy         | Existing API/static secrets       | Required this cycle (E10-15); CORS unchanged             |

**GitHub Actions (publish)** — configure in GitHub UI (not committed secrets):

| Setting                 | Purpose                                                                             |
| ----------------------- | ----------------------------------------------------------------------------------- |
| Environment e.g. `pypi` | Optional protection rules for publish jobs                                          |
| PyPI Trusted Publisher  | Links each PyPI project to the **same** matrix workflow + that package's tag filter |
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

## F21 / F22 — Public app + privacy (S023 / EV-017)

No new `config/*.json` keys for IndexedDB or privacy prefs (client-only). **New API env knobs**
(non-secret; defaults in ADR-031):

| Concern                        | Where it lives                     | Notes                                     |
| ------------------------------ | ---------------------------------- | ----------------------------------------- |
| Public rate limit              | `RATE_LIMIT_PUBLIC_PER_MIN`        | Default 60/min/IP (slowapi; E17-19)       |
| Dissemination rate limit       | `RATE_LIMIT_DISSEMINATION_PER_MIN` | Default 10/min/IP                         |
| Max body                       | `MAX_REQUEST_BODY_BYTES`           | Default 2 MiB                             |
| Operator Auth / `DISABLE_AUTH` | **Removed**                        | ADR-031; `/auth/*` → 404                  |
| Work sessions API              | **Removed**                        | IndexedDB FE (ADR-031 supersedes ADR-020) |
| Privacy prefs / GPC            | FE `localStorage` + headers        | F22 — not server env                      |

**Connectivity**: Public convert increases anonymous API traffic — keep CORS + H4–H5; rate limits
apply. Single-deploy cutover with Auth strip (E17-18).

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

## References

- [env-contract.md](env-contract.md) — per-environment matrix (**canonical F21**)
- [env-sync-runbook.md](ops/env-sync-runbook.md) — operator rotation steps
- [ADR-010](adr/ADR-010-supabase-keys-config-split.md)
- [ADR-014](adr/ADR-014-tac2iwxxm-rust-gifts-removal.md)
- [ADR-026](adr/ADR-026-msgspec-http-openapi.md)
- [ADR-020](adr/ADR-020-unified-tac-work-sessions.md) — **Superseded by ADR-031**
- [ADR-031](adr/ADR-031-public-app-indexeddb-history.md) — public app + IndexedDB
- [ADR-021](adr/ADR-021-byo-credentials-admin-removal.md)
- [ADR-029](adr/ADR-029-dissemination-ssrf-allowlist.md)
- [ADR-030](adr/ADR-030-dissemination-package-architecture.md)
- [ADR-032](adr/ADR-032-wmo-default-golden-glossary.md) — WMO default goldens + glossary
- [deploy.md](deploy.md) §Integration
- [api-contract.md](api-contract.md)
- Supabase: [API keys](https://supabase.com/docs/guides/api/api-keys)
