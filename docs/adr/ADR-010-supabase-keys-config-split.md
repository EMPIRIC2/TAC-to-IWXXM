# ADR-010: Supabase Publishable/Secret Keys and Runtime Config Split

## Status: Accepted

## Context

GitHub secret-scanning detected a leaked Supabase **service role** JWT in git history
(BUG-2026-06-23). The monorepo duplicated Supabase credentials under six or more env var names
across Render, GitHub Actions, local `.env`, and Vite build-time variables. Admin API routes used
`SUPABASE_SERVICE_ROLE_KEY` to bypass RLS even though `user_profiles` RLS policies already support
admin operations via `is_admin()`.

Supabase now recommends **Publishable/Secret** API keys (`sb_publishable_*` / `sb_secret_*`) over
legacy JWT `anon` / `service_role` keys.

## Decision

1. **Canonical key names** — `SUPABASE_PUBLISHABLE_KEY` and `SUPABASE_SECRET_KEY`; deprecate
   `SUPABASE_ANON_KEY` and `SUPABASE_SERVICE_ROLE_KEY` with one-release fallback shims (S003-R1).
2. **Minimal secrets-only `.env`** — five variables max; all non-secrets move to `config/{local,prod}.json`.
3. **Runtime frontend config** — fetch `/config.json` at bootstrap instead of `VITE_*` embed
   (S003-R2); static build copies `config/prod.json` and injects publishable key at deploy.
4. **Reduce secret-key usage** — refactor `admin_api.py` and `evaluation.py` to user-JWT +
   existing RLS; reserve `SUPABASE_SECRET_KEY` for Auth Admin API (`create_admin_user.py`) only.
5. **Env sync contract** — `docs/env-contract.md` + `make env-check` + operator runbook (S003-R6).
6. **Local ports** — standardize on `18000`/`18001` (S003-R4).
7. **Advisor remediation** — apply migrations 003–004 to METAR project; enable leaked-password
   protection in Supabase Auth dashboard.

## Consequences

- One rotation updates fewer dashboard fields; `make env-check` catches drift.
- Frontend deploy adds a config-injection build step; no secrets in committed JSON.
- Breaking change for operators using old env names — mitigated by deprecation warnings.
- METAR Supabase MCP not linked to org account; migrations applied manually via dashboard.
- Edge functions under `apps/frontend/supabase/functions/` still use secret key until follow-up.

## Alternatives Considered

| Alternative | Rejected because |
|-------------|------------------|
| Keep `VITE_*` build-time only | Duplicates URLs/keys; rotation requires rebuild + API dashboard |
| Rename service role only | Does not adopt Supabase publishable/secret pair |
| Keep service role for all admin ops | Bypasses RLS unnecessarily; increases blast radius |
| Render Environment Groups (v1) | Manual parity + verify script sufficient for two services |

## References

- S003 session: `docs/sessions/S003-supabase-keys-config/`
- [config-spec.md](../config-spec.md)
- [env-contract.md](../env-contract.md)
- Supabase [API keys](https://supabase.com/docs/guides/api/api-keys)
- BUG-2026-06-23-supabase-service-key-leak
