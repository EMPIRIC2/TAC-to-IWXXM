# Context — Supabase keys, minimal env, advisor remediation

> **Mode**: scoped | **Slug**: supabase-keys-config | **Generated**: 2026-06-23  
> **Feature / workflow**: Security hardening on `fix/supabase-service-key-leak` | **Status**: active

## Executive Summary

The METAR monorepo still relies on **legacy JWT-style Supabase keys**: `SUPABASE_ANON_KEY` on the
server, `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY` on the frontend, and `SUPABASE_SERVICE_ROLE_KEY`
for admin API, evaluation REST, operator scripts, and legacy edge functions. A service role key
was leaked in git history (BUG-2026-06-23); remediation is in progress on branch
`fix/supabase-service-key-leak`.

Supabase’s **Publishable/Secret Key** system (`sb_publishable_*` / `sb_secret_*`) replaces
`anon` and `service_role` JWT keys. Migration is primarily naming + rotation, but the real
security win is **reducing secret-key usage** by routing admin/evaluation DB access through
user JWT + existing RLS policies (already proven in `UserApprovalPanel.tsx`).

`.env.example` currently mixes 20+ secrets and non-secrets. A split into **secrets-only `.env`**
and **`config/prod.json`** for URLs, feature flags, and timeouts is feasible for the backend;
the frontend needs a **runtime config** decision because Vite embeds `VITE_*` at build time.

Repo SQL migrations `003` and `004` already target Supabase database linter issues for METAR
tables (`user_profiles`, uploads, evaluation). Live advisor data for project `ktvxijislbtgqapllmuk`
was not available via MCP (org projects differ); remediation plan is derived from repo migrations
plus auth dashboard settings.

**Env sync gap:** The same Supabase values are duplicated under **six or more names** across
Render dashboard, GitHub Actions secrets, local `.env`, `render.yaml`, `docker-compose.yml`, and
`start-dev-servers.sh` — with no automated drift check. Local dev also uses **different ports**
(5173/8001 via `start-dev-servers.sh` vs 18000/18001 via compose) while sharing one `.env.example`.

## Resolution Log

| ID | Category | Decision |
|----|----------|----------|
| R1 | Decision | User chose: `SUPABASE_SECRET_KEY` (canonical; deprecate `SUPABASE_SERVICE_ROLE_KEY` with fallback shim) |
| R2 | Decision | User chose: **runtime `config.json` fetch** at frontend bootstrap — true minimal `.env`; single config source for URLs/flags |
| R3 | Decision | User chose: METAR prod project **`ktvxijislbtgqapllmuk`** — advisor remediation targets this project (MCP not linked; apply migrations via dashboard/SQL) |
| R6 | Decision | User chose: **align and sync env vars** across Render, Supabase, and local with improved integration process |
| R4 | Advisory | ⚠️ Assumed: Keep secret key only for Auth Admin API (`create_admin_user.py`) until Supabase offers alternative |
| R5 | Advisory | ⚠️ Assumed: Org-wide CogniChem Supabase advisor lints (jobs, wallets) are **out of scope** for this repo |

## Scope & Constraints

**In scope** (maps to F3 / M4, hotfix on existing branch):

- Disable `SUPABASE_SERVICE_ROLE_KEY` in favor of `SUPABASE_SECRET_KEY` (new publishable/secret pair)
- Minimal `.env.example`; `config/prod.json` for non-secrets (prod assumed)
- METAR database + auth advisor remediation (migrations + dashboard auth settings)
- Update Render, CI, docker-compose secret names
- **Three-environment env contract** — canonical names, `config/{local,prod}.json`, sync verify script

**Out of scope** (REQ-016 / non-goals):

- Retiring `apps/frontend/supabase/functions/` entirely (upload path still active — follow-up)
- CogniChem org Supabase projects (`lrbhxyikeiwmuanqwdya`, `uysuznqtbajeejjvszxc`) — different products
- `dev` / `stage` config.json until user requests

## Environment / Topology

| Role | Host (prod) | Notes |
|------|-------------|-------|
| API | `https://metar-to-iwxxm-api.onrender.com` | Auth + `/admin/*` merged (M4) |
| Frontend | `https://metar-to-iwxxm-frontend-v4-web.onrender.com` | Static Vite build |
| Supabase | `https://ktvxijislbtgqapllmuk.supabase.co` | Per bug report + legacy edge source |

**Browser integration**: Frontend uses publishable key directly against Supabase Auth; API calls
go to `VITE_API_BASE_URL` for `/auth/*` and `/admin/*`. CORS via `METAR_CORS_ORIGINS`.

### Current key usage

| Key env var | Consumers | Privilege |
|-------------|-----------|-----------|
| `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY` | Frontend `createClient` | Publishable / anon |
| `SUPABASE_ANON_KEY` | `supabase_proxy.py`, JWT validation | Same as publishable (duplicated name) |
| `SUPABASE_SERVICE_ROLE_KEY` | `admin_api.py`, `evaluation.py`, `create_admin_user.py`, edge functions | Bypasses RLS |
| `DATABASE_URL` | `packages/auth/database.py`, `apps/backend/services/database.py` | Direct Postgres |

**Gap**: `docker-compose.yml` does not pass service/secret key to backend — admin routes 503
when `DISABLE_AUTH=false`.

## Three-environment env alignment (Render ↔ Supabase ↔ local)

### Source of truth

| Layer | Owns | Does not own |
|-------|------|--------------|
| **Supabase** (`ktvxijislbtgqapllmuk`) | Project URL, publishable key, secret key, `DATABASE_URL`, auth settings | Render URLs, CORS |
| **Render** | Deploy URLs, `PORT`, runtime secret injection | Key generation (copy from Supabase) |
| **Repo** | `config/*.json` (non-secrets), `.env.example` (secret names), canonical contract | Live secret values |
| **Local** | `.env` (gitignored secrets), `METAR_CONFIG_ENV=local` | Production URLs unless testing live |

### Current drift (problems)

| Issue | Evidence | Impact |
|-------|----------|--------|
| **Same key, many names** | `SUPABASE_ANON_KEY` = `SUPABASE_PUBLISHABLE_KEY` = `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY` = CI `FRONTEND_VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY` | Rotation requires 4+ dashboard updates |
| **URL duplicated** | `SUPABASE_URL` + `VITE_SUPABASE_URL` in Makefile gate, compose, CI | Easy to set one and forget the other |
| **Secret key missing locally** | `docker-compose.yml` has no `SUPABASE_SECRET_KEY`; `render.yaml` has `SUPABASE_SERVICE_ROLE_KEY` | Admin 503 in compose; prod-only admin |
| **Non-secrets in `.env`** | `WMO_*`, `LIVE_*`, `METAR_CORS_ORIGINS`, ports | Bloated template; prod values in dev file |
| **Local port inconsistency** | `start-dev-servers.sh`: 8001/5173; compose: 18001/18000; `.env.example`: 18001/18000 | CORS mismatches if mixing runners |
| **CI secret naming** | `FRONTEND_VITE_*` prefix in GitHub; mapped to `SUPABASE_ANON_KEY` in workflow | Undiscoverable for new operators |
| **Render `sync: false`** | Supabase keys in `render.yaml` but values only in dashboard | Blueprint ≠ live state; no repo check |
| **Stale secondary templates** | `packages/auth/.env.example` (120 lines, demo users) | Conflicts with minimal root pattern |

### Target: canonical env contract

After migration, **one name per concern** everywhere:

| Concern | Canonical name | Where set | Notes |
|---------|----------------|-----------|-------|
| Supabase project URL | `config.*.supabase.url` | `config/{local,prod}.json` | Not in `.env` |
| Publishable key | `SUPABASE_PUBLISHABLE_KEY` | Supabase → `.env` / Render / GitHub | Frontend reads via runtime config injection |
| Secret key | `SUPABASE_SECRET_KEY` | Supabase → `.env` / Render API only | Never on static frontend build |
| Postgres | `DATABASE_URL` | Supabase → `.env` / Render API | Pooler URL from dashboard Connect |
| API public URL | `config.*.api.baseUrl` | `config/{local,prod}.json` | Replaces `VITE_API_BASE_URL` |
| Frontend public URL | `config.*.api.frontendUrl` | config | Replaces `VITE_APP_URL`, `FRONTEND_URL` |
| CORS | `config.*.api.corsOrigins` | config | Replaces `METAR_CORS_ORIGINS` |
| Auth bypass (dev) | `config.*.api.disableAuth` | config | Replaces `DISABLE_AUTH` env |
| Operator bootstrap | `ADMIN_EMAIL`, `ADMIN_PASSWORD` | local `.env` only | Never Render |

**Deprecated aliases** (read with warning, remove after one release):

- `SUPABASE_ANON_KEY` → `SUPABASE_PUBLISHABLE_KEY`
- `SUPABASE_SERVICE_ROLE_KEY` → `SUPABASE_SECRET_KEY`
- `VITE_SUPABASE_*`, `VITE_API_BASE_URL`, `VITE_APP_URL` → runtime `config.json`
- `FRONTEND_VITE_*` GitHub secrets → `SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_URL`

### Per-environment matrix (target state)

| Setting | Local (`config/local.json`) | Render API | Render static | Supabase dashboard |
|---------|----------------------------|------------|---------------|-------------------|
| `supabase.url` | `https://ktvxijislbtgqapllmuk.supabase.co` | — (from config mount or env) | — | Project URL |
| `SUPABASE_PUBLISHABLE_KEY` | `.env` | env (dashboard) | — (injected into `/config.json` at deploy) | API Keys |
| `SUPABASE_SECRET_KEY` | `.env` | env (dashboard) | **never** | API Keys |
| `DATABASE_URL` | `.env` | env (dashboard) | **never** | Database → Connect |
| `api.baseUrl` | `http://localhost:18001` | same as prod path | — | — |
| `api.frontendUrl` | `http://localhost:18000` | prod URL | — | Auth redirect URLs |
| `api.corsOrigins` | `localhost:18000,5173` | prod frontend URL | — | — |
| `api.disableAuth` | `true` | `false` | — | — |

### Sync workflow (improved process)

```
Supabase Dashboard (keys + DATABASE_URL)
        │
        ▼ copy once per rotation
┌───────────────────┐     ┌────────────────────┐
│  Local .env       │     │  Render dashboard   │
│  (secrets only)   │     │  API + static svc   │
└─────────┬─────────┘     └──────────┬─────────┘
          │                          │
          └──────────┬───────────────┘
                     ▼
          make env-check  (scripts/env/verify-sync.sh)
                     │
     ┌───────────────┼───────────────┐
     ▼               ▼               ▼
 config/local   config/prod    GitHub secrets
     │               │          (CI integration)
     └───────────────┴───────────┘
              same canonical names
```

**Operator steps (document in `docs/env-sync-runbook.md`):**

1. **Rotate in Supabase** — create new publishable + secret; note `DATABASE_URL` from Connect.
2. **Update local** — edit repo-root `.env` (5 keys max).
3. **Update Render** — API service: `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SECRET_KEY`, `DATABASE_URL`; static: deploy copies `config/prod.json` (no secrets in build env).
4. **Update GitHub** — rename secrets to canonical names; drop `FRONTEND_VITE_*` prefix.
5. **Verify** — `make env-check` (local file present, config JSON valid, optional live probe).
6. **Revoke** old JWT keys in Supabase; close secret-scanning alert.

**Automation targets (T9–T10):**

| Deliverable | Purpose |
|-------------|---------|
| `docs/env-contract.md` | Standing spec — single matrix (replaces scattered tables) |
| `scripts/env/verify-sync.sh` | Fail if required secrets missing, config invalid, URL/key mismatch |
| `make env-check` | CI + local gate; optional `--live` probes Render health + Supabase `/auth/v1/health` |
| `config/local.json` | Local non-secrets (ports 18000/18001 — **standardize** on compose ports) |
| Render deploy hook | Copy `config/prod.json` → static `public/config.json` at build |
| Deprecate `start-dev-servers.sh` port 8001/5173 OR align to 18001/18000 | Eliminate port drift |

### Render ↔ Supabase integration notes

- Render web services are **stateless** — all secrets via dashboard env vars (not committed).
- Use Render **environment variable groups** (optional v2) to share `SUPABASE_PUBLISHABLE_KEY` + `DATABASE_URL` if a second API is added; v1 documents manual parity.
- Supabase **Auth redirect URLs** must include `config.*.api.frontendUrl` for each environment.
- CORS on API (`METAR_CORS_ORIGINS` → config) must list every browser origin (local + prod).
- After key migration, **disable legacy JWT keys** in Supabase to prevent dual-key confusion.


| Asset | Path | Relevance |
|-------|------|-----------|
| Bug report | `docs/bug-reports/BUG-2026-06-23-supabase-service-key-leak.md` | Leak + rotation checklist |
| Admin API (service role) | `packages/auth/src/admin_api.py` | Primary refactor target |
| Evaluation REST (service role) | `apps/backend/src/routers/evaluation.py` | Refactor to JWT+RLS |
| Auth proxy (anon) | `packages/auth/src/supabase_proxy.py` | Rename to publishable key |
| Admin script | `scripts/utilities/create_admin_user.py` | Legitimate secret-key use (Auth Admin API) |
| RLS migrations | `apps/frontend/supabase/migrations/001–004_*.sql` | Advisor remediation baseline |
| SQL optimization | `docs/sql-optimization/ALL_PHASES_CONSOLIDATED.sql` | Reference runbook |
| Config spec (ephemeral) | `.cursor/artifacts/config-spec-monorepo.md` | Pre-migration env table |
| Render blueprint | `render.yaml` | `SUPABASE_SERVICE_ROLE_KEY` sync:false |
| CI mapping | `.github/workflows/ci-cd.yml` | Maps publishable secret → `SUPABASE_ANON_KEY` |
| Hardcoded leak risk | `apps/frontend/utils/supabase/info.tsx` | Legacy projectId + anon JWT — delete |
| Edge functions (partial) | `apps/frontend/supabase/functions/` | Still used for database upload |

## Cross-Reference Matrix

| Topic | Bug report | Code | Migrations | Deploy docs | Advisor (live) |
|-------|-----------|------|------------|-------------|----------------|
| Service role leak | ✅ root cause | ✅ env-based now | — | ⚠️ render still lists key | — |
| Publishable key naming | — | `VITE_*` + `SUPABASE_ANON_KEY` duplicate | — | ✅ staging matrix | — |
| Admin bypasses RLS | — | `admin_api._get_service_client()` | RLS allows admin via `is_admin()` | api-contract says service role | — |
| Advisor RLS initplan | — | — | ✅ 003, 004 | — | ⚠️ not verified on METAR project |
| Leaked password protection | — | — | — | — | WARN on org projects; enable in dashboard |
| config.json pattern | — | ❌ not implemented | — | ❌ | — |
| Render ↔ local env drift | — | ⚠️ 6+ alias names | — | ⚠️ matrix stale | — |

## Implementation Backlog

### Phase A — Config split (minimal env)

1. Add `config/prod.json` with non-secrets (example shape below).
2. Add loader in `packages/shared` (Python + TS) — env `METAR_CONFIG_ENV=prod` default.
3. Slim `.env.example` to secrets only; document `config/README.md`.
4. **Decision**: Frontend — either (a) keep `VITE_*` for build-time URLs/keys, or (b) serve
   `/config.json` from static host and fetch at bootstrap (enables single config source).

**Proposed `config/prod.json` (non-secrets)**

```json
{
  "environment": "prod",
  "api": {
    "baseUrl": "https://metar-to-iwxxm-api.onrender.com",
    "corsOrigins": ["https://metar-to-iwxxm-frontend-v4-web.onrender.com"],
    "frontendUrl": "https://metar-to-iwxxm-frontend-v4-web.onrender.com",
    "disableAuth": false
  },
  "supabase": {
    "url": "https://ktvxijislbtgqapllmuk.supabase.co"
  },
  "validation": {
    "wmoOnline": true,
    "wmoTimeoutSeconds": 5,
    "schematronUseDocker": false
  },
  "observability": {
    "logLevel": "INFO",
    "enableStatistics": true
  },
  "liveE2e": {
    "apiUrl": "https://metar-to-iwxxm-api.onrender.com",
    "frontendUrl": "https://metar-to-iwxxm-frontend-v4-web.onrender.com"
  }
}
```

**Proposed minimal `.env.example` (secrets only)**

```bash
# Secrets — copy to .env; never commit
SUPABASE_PUBLISHABLE_KEY=
SUPABASE_SECRET_KEY=
DATABASE_URL=
ADMIN_EMAIL=
ADMIN_PASSWORD=
```

Note: `SUPABASE_URL` is public but may stay in config.json; publishable key must remain secret
in practice for abuse prevention even though it is "client-safe."

### Phase B — Key migration (disable service_role)

| Step | Action |
|------|--------|
| B1 | Shared helper `get_supabase_secret_key()` — reads `SUPABASE_SECRET_KEY`, fallback `SUPABASE_SERVICE_ROLE_KEY` (deprecation warning) |
| B2 | Rename `SUPABASE_ANON_KEY` → `SUPABASE_PUBLISHABLE_KEY` with fallback |
| B3 | CI/Render: rotate to `sb_publishable_*` / `sb_secret_*`; remove old JWT keys from dashboard |
| B4 | `admin_api.py`: replace `_get_service_client()` with user-JWT client using publishable key + `Authorization` header from `require_admin` |
| B5 | `evaluation.py`: same pattern or use `DATABASE_URL` + SQLAlchemy |
| B6 | `create_admin_user.py`: use `SUPABASE_SECRET_KEY` only |
| B7 | Update tests in `packages/auth/tests/test_admin_api_unit.py` |
| B8 | Delete `apps/frontend/utils/supabase/info.tsx` (hardcoded credentials) |

### Phase C — Supabase advisor remediation (METAR)

**Already in repo** (`apps/frontend/supabase/migrations/`):

| Migration | Addresses |
|-----------|-----------|
| 001 | `user_profiles` RLS baseline |
| 002 | `is_admin()` SECURITY DEFINER, privilege escalation trigger |
| 003 | Initplan-safe `(SELECT auth.uid())`, FK indexes, translation_statistics RLS, service_role policies |
| 004 | Consolidated `user_profiles_select_access` / `user_profiles_update_access` |

**Verify applied on live METAR project** — run in SQL Editor or via `apply_migration`:

- Confirm migrations 003–004 applied (check `supabase_migrations` or policy names).
- Run `docs/sql-optimization/PHASE_4_UNINDEXED_FKS.sql` if evaluation/upload FKs still flagged.

**Auth section (dashboard, not SQL)**

| Lint | Remediation |
|------|-------------|
| Leaked password protection disabled | Enable in Supabase Dashboard → Authentication → Password Security → [HaveIBeenPwned check](https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection) |
| Legacy API keys | Dashboard → API Keys → create Publishable + Secret; disable/rotate legacy `service_role` JWT |

**Expected METAR table lints after 003–004** (if applied):

| Lint type | METAR tables | Status if migrations applied |
|-----------|--------------|------------------------------|
| `auth_rls_initplan` | `user_profiles`, uploads, evaluation | Fixed via `(SELECT auth.uid())` |
| `multiple_permissive_policies` | `user_profiles` | Fixed in 004 |
| `rls_disabled_in_public` | METAR tables | Should be enabled in 001–003 |
| `function_search_path_mutable` | `handle_new_user`, `is_admin`, etc. | Partially fixed in 003 |

**Cannot fix from this repo** (org CogniChem projects only — out of scope):

- `jobs`, `user_wallet`, `compute_credit_vouchers`, etc. on `lrbhxyikeiwmuanqwdya`

### Phase D — Deploy / operator checklist

1. Create new Publishable + Secret keys in Supabase dashboard (METAR project).
2. Update Render: replace `SUPABASE_ANON_KEY` + `SUPABASE_SERVICE_ROLE_KEY` with new names.
3. Rotate and revoke leaked service role JWT (BUG-2026-06-23 L3/L4).
4. Close GitHub secret-scanning alert #1 as revoked.
5. `make test-integration` with new keys.

### Phase E — Env sync (Render ↔ Supabase ↔ local)

| Step | Action |
|------|--------|
| E1 | Add `docs/env-contract.md` — canonical matrix (supersedes fragmented tables in deploy.md) |
| E2 | Add `config/local.json` + `config/prod.json`; loader respects `METAR_CONFIG_ENV` |
| E3 | `scripts/env/verify-sync.sh` + `make env-check` — validate `.env` + config + optional live |
| E4 | Align `render.yaml`: rename keys, document `config/prod.json` copy in static buildCommand |
| E5 | Align `docker-compose.yml`: pass `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SECRET_KEY`, mount config |
| E6 | Align CI: rename GitHub secrets; integration job uses canonical names only |
| E7 | Align `start-dev-servers.sh` + Makefile `test-integration` gate to canonical names |
| E8 | Add `docs/env-sync-runbook.md` — operator rotation checklist (Supabase → local → Render → GitHub) |
| E9 | Standardize local ports on **18000/18001** across compose, config, and dev scripts |

## Data & Credentials

| Secret | Source | Never commit |
|--------|--------|--------------|
| `SUPABASE_SECRET_KEY` | Supabase Dashboard → API Keys | ✅ |
| `SUPABASE_PUBLISHABLE_KEY` | Same | Low risk but treat as secret in CI |
| `DATABASE_URL` | Supabase → Database settings | ✅ |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Operator | ✅ |

Render secrets (`sync: false` in `render.yaml`) must be updated manually after code merge.

## Unresolved Gaps

1. **METAR project MCP access** — Connected org projects are CogniChem-wide, not `ktvxijislbtgqapllmuk`.
   User must confirm whether migrations 003–004 are applied in production.
2. **Edge function upload path** — Still needs secret key until migrated to backend route.
3. **`packages/auth/.env.example`** — Stale demo-user bloat; should align with root minimal pattern.
4. **Render env-var groups** — Optional follow-up; v1 uses documented manual parity + `make env-check`.
5. **Local port standardization** — Recommend 18000/18001 everywhere; confirm before changing `start-dev-servers.sh` defaults.

## Sources

- [Repo: docs/bug-reports/BUG-2026-06-23-supabase-service-key-leak.md]
- [Repo: packages/auth/src/admin_api.py]
- [Repo: apps/frontend/supabase/migrations/003_supabase_advisor_remediation.sql]
- [Repo: render.yaml]
- [Repo: .env.example]
- [Docs: Supabase API keys migration](https://supabase.com/docs/guides/api/api-keys)
- [Docs: Supabase password security](https://supabase.com/docs/guides/auth/password-security)
- [Docs: Render environment variables](https://render.com/docs/configure-environment-variables)
- [Docs: Supabase managing environments](https://supabase.com/docs/guides/deployment/managing-environments)
- Live probe: Supabase MCP `get_advisors` on org projects `lrbhxyikeiwmuanqwdya`, `uysuznqtbajeejjvszxc` (2026-06-23) — **not METAR project**
