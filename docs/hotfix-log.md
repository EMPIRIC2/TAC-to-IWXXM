# Hotfix Log

| # | Date | Type | Summary | Bug report | Branch | Commit | Deployed | Verified |
|---|------|------|---------|------------|--------|--------|----------|----------|
| 1 | 2026-06-21 | config/infra | Production login Failed to fetch — CORS + missing Supabase env on API | [BUG-2026-06-20-login-cors-failed-fetch.md](bug-reports/BUG-2026-06-20-login-cors-failed-fetch.md) | — (Render API) | — | Yes | L1–4 pass |
| 2 | 2026-06-21 | code bug | Production scoped logout fails — missing Bearer on POST /auth/logout | [BUG-2026-06-21-logout-failed-production.md](bug-reports/BUG-2026-06-21-logout-failed-production.md) | fix/logout-missing-auth-header | af10574 | No | L1 pass; L4 pending deploy |
| 3 | 2026-06-21 | regression | Main CI red — unformatted bug repro test failed Quality Gates ruff format | — (docs/hooks only) | main | 63c72d7 | N/A | L1 pass; prevention hooks added |
| 4 | 2026-06-22 | test bug | Live E2E admin navigation loop — User Approvals heading mismatch | [BUG-2026-06-22-admin-e2e-user-approvals-heading.md](bug-reports/BUG-2026-06-22-admin-e2e-user-approvals-heading.md) | — (uncommitted) | — | No | L1–2 pass |
| 5 | 2026-06-24 | config/infra | Production login 401 — legacy Supabase JWT key on Render API after legacy keys disabled | [BUG-2026-06-24-login-legacy-api-keys-disabled.md](bug-reports/BUG-2026-06-24-login-legacy-api-keys-disabled.md) | — (Render config) | — | Yes | L1–4 pass; code hardening uncommitted |
| 6 | 2026-06-24 | code bug | F5 work session persist 502 — supabase-py 2.28 lacks `.select()` on insert/update | [BUG-2026-06-24-work-session-persist-select-chain.md](bug-reports/BUG-2026-06-24-work-session-persist-select-chain.md) | fix/work-session-persist-select-chain | 0cbfe51 | No | L1 pass; PR #690 open |
