# BUG-2026-06-23 — Supabase service role key leaked in git history

| Field | Value |
|-------|-------|
| Status | `fixing` |
| Severity | Critical |
| Feature | F3 / auth ops (admin user script) |
| Reported | 2026-06-23 |
| Remediation path | local-first — rotate key, close GitHub alert |

## Error description

GitHub Secret Scanning alert [#1](https://github.com/joseph-c-mcguire/metar-to-IWXXM/security/secret-scanning/1)
detected a **Supabase service role key** hardcoded in `scripts/create_admin_user.py` at orphaned
commit `1eaf3e9` (Jan 15, 2026). The key was marked **publicly leaked**.

## Error logs

```
GitHub secret-scanning alert #1 — supabase_service_key
Path: scripts/create_admin_user.py (commit 1eaf3e9)
SUPABASE_URL = "https://ktvxijislbtgqapllmuk.supabase.co"
SERVICE_KEY = "eyJhbGci...<redacted>..."
ADMIN_EMAIL = "admin@metar.local"
ADMIN_PASSWORD = "Admin123456!"
```

## Investigation

| Step | Finding |
|------|---------|
| Current code | `scripts/utilities/create_admin_user.py` already reads `SUPABASE_SERVICE_ROLE_KEY` from env (commit `282a47c`) |
| Local `.env` | Repo-root `.env` is gitignored and already defines `SUPABASE_SERVICE_ROLE_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` |
| Reachable history | `git log -S` on `origin/main` and all remote branch tips: **no** hardcoded service key |
| Orphan commit | `1eaf3e9` fetchable from GitHub by SHA but **not** ancestor of any remote branch — leftover from pre-rewrite history |
| Blob | Leaked blob `4a078a2` not present in local object store |

**Root cause:** One-off operator script committed credentials before env-var refactor; old commit
remains on GitHub as unreachable object.

## Spec conformance

| Check | Result |
|-------|--------|
| `docs/DEVELOPMENT.md` §Environment variables | `.env.example` was missing `SUPABASE_SERVICE_ROLE_KEY` — **fixed** |
| `scripts/utilities/README.md` | Documents env vars — pass |
| `.gitignore` | `.env` ignored — pass |

## Fix

1. `scripts/utilities/create_admin_user.py` — uses `SUPABASE_SECRET_KEY` (legacy shim); URL from config
2. `.env.example` — minimal secrets-only template
3. `config/prod.json` / `config/local.json` — non-secret settings; `METAR_CONFIG_ENV` selector
4. `packages/shared` — `config_loader.py`, `supabase_env.py` canonical key helpers
5. `packages/auth/admin_api.py` — user JWT + RLS (no service role for admin routes)
6. `apps/backend/evaluation_store.py` — `DATABASE_URL` for eval jobs (no service role REST)
7. `render.yaml`, `docker-compose.yml`, CI — canonical `SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_SECRET_KEY`
8. `scripts/env/verify-sync.sh` + `make env-check` — local/Render/Supabase drift gate
9. Migration `supabase/migrations/20250614000006_supabase_advisor_remediation.sql` — evaluation_results insert-own + function search_path
10. Frontend runtime `/config.json` bootstrap (ADR-010 / S003-R2)

## Operator (post-merge)

1. Create Publishable + Secret keys in Supabase (METAR `ktvxijislbtgqapllmuk`)
2. Update Render API: `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SECRET_KEY`, `DATABASE_URL`, `METAR_CONFIG_ENV=prod`
3. Update Render static: `SUPABASE_PUBLISHABLE_KEY` (injected into `/config.json` at build)
4. Apply migrations 003–005 in Supabase SQL editor if not already applied
5. Auth dashboard: enable leaked-password protection
6. Revoke legacy `service_role` JWT; close GitHub secret-scanning alert #1

## Repro test

Config-only / secret-removal hotfix — repro test waived per 14-hotfix (no behavioral assertion).

## Verification plan

| Layer | Check | Status |
|-------|-------|--------|
| L1 | Script has no hardcoded JWT; `grep` clean on tracked files | pending |
| L2 | `create_admin_user.py` loads vars from repo-root `.env` | pending |
| L3 | User rotates Supabase service role key | **pending (user)** |
| L4 | GitHub secret scanning alert #1 closed as revoked | **pending (user)** |

## Prevention & countermeasures

- Rotate leaked key before closing alert (user chose: rotate after code cleanup)
- `.env.example` documents `SUPABASE_SERVICE_ROLE_KEY` so scripts never need inline keys
- Existing `gitleaks` CI gate on push

## Follow-ups

- Update `SUPABASE_SERVICE_ROLE_KEY` in Render (`render.yaml` references it) after rotation
- Consider removing stale remote branches that predate monorepo migration if still unused
