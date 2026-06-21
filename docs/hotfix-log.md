# Hotfix Log

| # | Date | Type | Summary | Bug report | Branch | Commit | Deployed | Verified |
|---|------|------|---------|------------|--------|--------|----------|----------|
| 1 | 2026-06-21 | config/infra | Production login Failed to fetch — CORS + missing Supabase env on API | [BUG-2026-06-20-login-cors-failed-fetch.md](bug-reports/BUG-2026-06-20-login-cors-failed-fetch.md) | — (Render API) | — | Yes | L1–4 pass |
| 2 | 2026-06-21 | code bug | Production scoped logout fails — missing Bearer on POST /auth/logout | [BUG-2026-06-21-logout-failed-production.md](bug-reports/BUG-2026-06-21-logout-failed-production.md) | fix/logout-missing-auth-header | af10574 | No | L1 pass; L4 pending deploy |
