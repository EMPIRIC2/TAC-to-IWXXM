# Environment Sync Runbook — Supabase → Local → Render → GitHub

> **Session**: S003-supabase-keys-config  
> **Supabase project**: `ktvxijislbtgqapllmuk` (`https://ktvxijislbtgqapllmuk.supabase.co`)  
> **Last updated**: 2026-06-23

Operator checklist for keeping secrets and config aligned across environments.

## When to run

- After creating or rotating Supabase API keys
- After changing production URLs in `config/prod.json`
- Before closing GitHub secret-scanning alert #1 (service role leak)
- After merging S003 build changes

## Prerequisites

- Access to Supabase dashboard (METAR project)
- Access to Render dashboard (API + static services)
- Access to GitHub repo secrets (for CI)
- Local repo-root `.env` (gitignored)

## Step 1 — Supabase (source of truth for keys)

1. Open [Supabase Dashboard](https://supabase.com/dashboard) → project `ktvxijislbtgqapllmuk`.
2. **API Keys** → create **Publishable** (`sb_publishable_*`) and **Secret** (`sb_secret_*`) keys.
3. **Database → Connect** → copy **Transaction pooler** `DATABASE_URL`.
4. **Authentication → URL configuration** → set redirect URLs:
   - `https://metar-to-iwxxm-frontend-v4-web.onrender.com/**`
   - `http://localhost:18000/**` (local)
5. **Authentication → Password Security** → enable **Leaked password protection** (HaveIBeenPwned).
6. Apply SQL migrations `003` and `004` if not yet applied (see §Database advisor below).
7. After all services updated → **disable legacy JWT keys** (`anon` / `service_role`).

## Step 2 — Local `.env`

Copy from minimal template:

```bash
cp .env.example .env
```

Set exactly these secrets:

```bash
SUPABASE_PUBLISHABLE_KEY=<sb_publishable_*>
SUPABASE_SECRET_KEY=<sb_secret_*>
DATABASE_URL=<pooler url>
ADMIN_EMAIL=<operator email>
ADMIN_PASSWORD=<operator password>
```

Verify:

```bash
export METAR_CONFIG_ENV=local
make env-check
```

## Step 3 — Render API (`metar-to-iwxxm-api`)

Dashboard → Environment:

| Key | Value |
|-----|-------|
| `SUPABASE_PUBLISHABLE_KEY` | from Supabase |
| `SUPABASE_SECRET_KEY` | from Supabase |
| `DATABASE_URL` | from Supabase |
| `METAR_CONFIG_ENV` | `prod` |

Remove deprecated keys after one release:

- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `METAR_CORS_ORIGINS`, `FRONTEND_URL`, `DISABLE_AUTH` (now in `config/prod.json`)

Redeploy API. Confirm `GET /health` returns 200.

## Step 4 — Render static (`metar-to-iwxxm-frontend-v4-web`)

Build must:

1. Copy `config/prod.json` → `public/config.json`
2. Inject `supabase.publishableKey` from `SUPABASE_PUBLISHABLE_KEY` build env (secret — dashboard only)

Remove deprecated build env after migration:

- `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY`, `VITE_APP_URL`

Redeploy static site.

## Step 5 — GitHub Actions secrets

Rename / set:

| Secret | Purpose |
|--------|---------|
| `SUPABASE_PUBLISHABLE_KEY` | Integration tests |
| `SUPABASE_SECRET_KEY` | Admin/integration fixtures (if needed) |
| `DATABASE_URL` | Integration DB tests |

Deprecate: `FRONTEND_VITE_SUPABASE_URL`, `FRONTEND_VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY`.

## Step 6 — Verify end-to-end

```bash
# Local integration
make test-integration

# Optional live signoff (credentials in .env)
export LIVE_API_URL=https://metar-to-iwxxm-api.onrender.com
export LIVE_FRONTEND_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com
make test-live-connectivity
```

## Step 7 — Revoke leaked key & close alert

1. Confirm no code references hardcoded JWTs: `grep -r "eyJhbGci" --include='*.py' --include='*.ts' .`
2. Revoke old `service_role` JWT in Supabase.
3. Close [GitHub secret-scanning alert #1](https://github.com/joseph-c-mcguire/metar-to-IWXXM/security/secret-scanning/1) as **revoked**.

## Database advisor remediation (METAR tables)

Migrations live in **`supabase/migrations/`** (timestamp-ordered, per
[Supabase local development](https://supabase.com/docs/guides/local-development/overview)).

**Local:** `make supabase-reset` applies all migrations + `supabase/seed.sql`.

**Production:** migrations **004–006 not yet applied** (S003-R3). Migrations **001–003** may
already exist on the live database from earlier manual deploys — do **not** re-run
`20250614000001`–`000003` on prod unless you have confirmed they are missing.

Apply advisor migrations via:

```bash
supabase link --project-ref ktvxijislbtgqapllmuk   # once, from repo root
bash scripts/supabase/apply-advisor-migrations.sh --apply
```

The apply script pushes only **004–006** (advisor remediation). For a greenfield
database, run `make supabase-reset` locally or `supabase db push` for the full chain.

Or paste into Supabase Dashboard → SQL Editor in order:

| Migration | File | Addresses |
|-----------|------|-----------|
| 004 | `supabase/migrations/20250614000004_supabase_advisor_remediation.sql` | `auth_rls_initplan`, FK indexes, `translation_statistics` RLS, `search_path` on METAR functions |
| 005 | `supabase/migrations/20250614000005_supabase_advisor_policy_cleanup.sql` | `multiple_permissive_policies` on `user_profiles` |
| 006 | `supabase/migrations/20250614000006_supabase_advisor_remediation.sql` | `function_search_path_mutable`, evaluation_results RLS |

Post-apply verification in Supabase **Database → Advisors**:

- Zero ERROR on `user_profiles`, upload, evaluation tables
- WARN on `function_search_path_mutable` cleared for `handle_new_user`, `is_admin`

**Out of scope:** CogniChem org tables (`jobs`, `user_wallet`, etc.) on other Supabase projects.

## Auth advisor remediation (dashboard)

| Lint | Action |
|------|--------|
| Leaked password protection disabled | Enable in Authentication → Password Security |
| Legacy API keys active | Disable after new keys deployed everywhere |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Admin routes 503 | `SUPABASE_SECRET_KEY` missing on API | Set on Render + local `.env` |
| CORS errors after deploy | `config.prod.api.corsOrigins` stale | Update `config/prod.json`, redeploy API |
| Frontend auth fails | `/config.json` missing publishable key | Rebuild static with inject step |
| `make env-check` fails | Deprecated-only env names | Add canonical names per [env-contract.md](env-contract.md) |

## References

- [BUG-2026-06-23-supabase-service-key-leak.md](bug-reports/BUG-2026-06-23-supabase-service-key-leak.md)
- [env-contract.md](env-contract.md)
- [config-spec.md](config-spec.md)
