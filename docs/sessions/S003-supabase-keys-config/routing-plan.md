# Routing Plan — S003-supabase-keys-config

| Stage | Required | Status | Skip rationale |
|-------|----------|--------|----------------|
| 00-context (scoped) | yes | completed | — |
| 01-requirements (delta) | yes | completed | S003 spec delta 2026-06-23 |
| bug-investigation | yes | completed | BUG-2026-06-23 already filed |
| 14-hotfix | yes | pending | Key rotation + deploy wiring |
| 07-build | yes | pending | Code migration (keys, config loader, admin RLS) |
| 08-verify-build | yes | pending | — |
| 09-qa | yes | pending | — |
| 10-e2e | delta | pending | Auth/admin smoke only |
| 11-verify-impl | yes | pending | — |
| 12-verify-deploy | optional | pending | After Render secret updates |
| 13-deploy-smoke | optional | pending | — |

## Suggested task breakdown (07-build)

1. **T1** — Introduce `packages/shared` config loader + `config/prod.json`; slim `.env.example`
2. **T2** — `SUPABASE_SECRET_KEY` helper; deprecate `SUPABASE_SERVICE_ROLE_KEY` reads
3. **T3** — Refactor `admin_api.py` to user-JWT + RLS (drop secret client for profile ops)
4. **T4** — Refactor `evaluation.py` to user-JWT + RLS or `DATABASE_URL`
5. **T5** — Update `create_admin_user.py` + Render/CI secret names
6. **T6** — Apply/publish migration `005_supabase_advisor_remediation.sql` for remaining METAR lints
7. **T7** — Auth dashboard: enable leaked-password protection; rotate keys post-merge
8. **T8** — Docs: `deploy.md`, `api-contract.md`, `staging-secrets-matrix.md`
9. **T9** — Env sync contract + `make env-check` / `scripts/env/verify-sync.sh`
10. **T10** — Align `render.yaml`, `docker-compose.yml`, CI, `start-dev-servers.sh` to canonical names

## Gate criteria

- No tracked file references `SUPABASE_SERVICE_ROLE_KEY` without deprecation shim
- `.env.example` ≤ 8 lines (secrets + pointer to config)
- `make test` / `make ci` green
- `make env-check` passes for local `.env` + `config/prod.json` alignment
- Supabase Security Advisor: zero ERROR/WARN on METAR `user_profiles` and auth tables
  (org-wide CogniChem tables out of scope)
