# Environment Contract — Render ↔ Local (F21 public app)

> **Project**: METAR to IWXXM Converter  
> **Session**: S023-public-app-privacy / EV-017 (F21/F22)  
> **Example deploy project** (historical ref only): `ktvxijislbtgqapllmuk`  
> **Last updated**: 2026-07-28 (S023 / EV-017 — **F21 rewrite**; closes C-EV017.5)

Single source of truth for **what** each layer owns and **which name** to use everywhere.

## Model (F21)

- **Operator product** is **public and unauthenticated** — no browser JWT, no `/auth/*`,
  no `E2E_USER_*` login harness for convert paths.
- **Work history** lives in the browser (IndexedDB) — not in server session tables.
- **F8 worker** remains a private machine path with service-role credentials (ADR-018).
- **Dissemination** BYOC credentials are **memory-only** (ADR-021/029); egress allowlist required.

## Source of truth by layer

| Layer | Owns | Does not own |
|-------|------|--------------|
| **Render API** | Deploy URL, `PORT`, rate-limit/body env, dissemination allowlist, F8-unrelated API secrets if any remain for legacy ops | Browser Auth keys |
| **Render static** | Frontend URL; `/config.json` with **`api.baseUrl`** (+ cors-related non-secrets) | Supabase publishable key for Auth (removed) |
| **Render worker (F8)** | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, poller URL/interval | Operator JWT |
| **Repo** | `config/*.json`, `.env.example`, this contract | Live secret values |
| **Local** | `.env` (gitignored), `METAR_CONFIG_ENV=local` | Production URLs unless live testing |

## Canonical names (one name per concern)

| Concern | Canonical | Where set |
|---------|-----------|-----------|
| API public URL | `config.*.api.baseUrl` | `config/*.json` (`/api/v1` **only** — no `/auth`) |
| Frontend public URL | `config.*.api.frontendUrl` | `config/*.json` |
| CORS | `config.*.api.corsOrigins` | `config/*.json` |
| Public rate limit | `RATE_LIMIT_PUBLIC_PER_MIN` | Render API / `.env` (default **60**) |
| Dissemination rate limit | `RATE_LIMIT_DISSEMINATION_PER_MIN` | Render API / `.env` (default **10**) |
| Max request body | `MAX_REQUEST_BODY_BYTES` | Render API / `.env` (default **2097152** = 2 MiB) |
| Dissemination egress allowlist | `DISSEMINATION_EGRESS_ALLOWLIST` | Render API / `.env` (ADR-029) |
| Converter engine (F6) | *(code — `packages/tac2iwxxm`)* | Not an env var |
| F8 worker Supabase URL | `SUPABASE_URL` | Render worker / local `.env` |
| F8 worker service role | `SUPABASE_SERVICE_ROLE_KEY` | Render worker / local `.env` |
| F8 poller feed URL | `INGEST_POLLER_URL` | Render worker / local `.env` |
| F8 poll interval | `INGEST_POLL_INTERVAL_SEC` | Render worker (default `30`) |

### Optional / legacy ops (not required for public FE)

| Concern | Canonical | Notes |
|---------|-----------|-------|
| Postgres | `DATABASE_URL` | F8 ingest store / legacy archive ops only — **not** operator Auth |
| Supabase secret | `SUPABASE_SECRET_KEY` | Server ops / archive scripts only — **never** frontend |

### Dissemination egress (F16–F19)

| Setting | Rules |
|---------|-------|
| `DISSEMINATION_EGRESS_ALLOWLIST` | Comma-separated hostnames and/or CIDRs. **Empty ⇒ fail-closed**. Local/CI: `wis2box,127.0.0.1,127.0.0.0/8,localhost`. |
| User-pasted dest creds | **Not** env vars — memory-only on preflight/send |

## Retired (F21 — do not set for operator product)

| Retired | Replacement |
|---------|-------------|
| `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` | None — public convert; use `TC-F21-auth-gone` |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Already retired (S011) |
| `DISABLE_AUTH` / `config.*.api.disableAuth` | Public by default — dual path removed |
| Browser `SUPABASE_PUBLISHABLE_KEY` in `/config.json` for Auth | Removed from FE Auth path |
| `config.*.api.baseUrl` including `/auth` | `/api/v1` only |
| Operator `/auth/*` | 404 |

## Per-environment matrix

### Production (Render)

| Setting | Render API | Render static | Render worker |
|---------|------------|---------------|---------------|
| `RATE_LIMIT_PUBLIC_PER_MIN` | env (default 60) | — | — |
| `RATE_LIMIT_DISSEMINATION_PER_MIN` | env (default 10) | — | — |
| `MAX_REQUEST_BODY_BYTES` | env (default 2097152) | — | — |
| `DISSEMINATION_EGRESS_ALLOWLIST` | env | — | — |
| `config/prod.json` | `METAR_CONFIG_ENV=prod` | copy → `public/config.json` (`api.baseUrl` only) | — |
| F8 secrets | — | — | `SUPABASE_*`, poller |

### Local (`METAR_CONFIG_ENV=local`)

| Setting | Value |
|---------|-------|
| Ports | **18000** frontend / **18001** API |
| CORS | `["http://localhost:18000"]` |
| Rate limits | Defaults OK; may raise for local soak |
| Auth bypass | **N/A** (no Auth) |

### CI (GitHub Actions)

| Setting | Notes |
|---------|-------|
| Live login secrets | **Not required** for public path |
| F8 / dissemination integration | Use allowlist + worker fixtures as today |

## Verification

```bash
make env-check              # local: .env + config JSON valid
make env-check LIVE=1       # optional: probe Render /health (no Auth health)
```

## References

- [ADR-031](adr/ADR-031-public-app-indexeddb-history.md)
- [ADR-018](adr/ADR-018-f8-worker-template.md)
- [ADR-029](adr/ADR-029-dissemination-ssrf-allowlist.md)
- [config-spec.md](config-spec.md)
- [deploy.md](deploy.md)
