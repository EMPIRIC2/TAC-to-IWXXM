# BUG-2026-06-21 — Admin panels fail to load settings/monitoring

| Field | Value |
|-------|-------|
| **Status** | fixing |
| **Feature** | M4 (auth merged into backend API) |
| **Severity** | high |
| **Classification** | connectivity / implementation drift |
| **Remediation path** | local-first — deploy after user approval |

## Error description

After successful admin login on production, **System Settings** and **System Monitoring**
panels fail to load. Console shows:

```
Error loading settings: Error: Failed to load settings
Error loading monitoring data: Error: Failed to load monitoring data
```

Login via `https://metar-to-iwxxm-api.onrender.com/auth/login` succeeds (200).

## Error logs

```
[Auth Service] Initialized with URL: https://metar-to-iwxxm-api.onrender.com
[Auth Service] Login response status: 200
🔐 AdminDashboard mounted for user: admin@metar.local {hasAccessToken: true, ...}
Error loading settings: Error: Failed to load settings
Error loading monitoring data: Error: Failed to load monitoring data
```

## Symptoms & reproduction

| Field | User answer |
|-------|-------------|
| Symptom | Error / crash — fetch fails |
| Where | Production Render |
| When | After last deploy / CORS fix |
| Frequency | Every time |
| Repro env | Production only (panels call wrong host) |
| Severity | High — admin config/monitoring unavailable |
| Evidence | Console logs |
| Tried | Nothing |

## Investigation

### Root cause

M4 migrated `/auth/*` to the merged API host (`VITE_API_BASE_URL`), but
`SystemSettingsPanel` and `MonitoringPanel` still fetch Supabase Edge Function
URLs:

`https://{projectId}.supabase.co/functions/v1/make-server-2e3cda33/admin/*`

Those functions are not the active auth/admin path post-migration; requests fail
(non-OK response) while login uses the backend correctly.

### Fix

1. Add `/admin/*` routes to `packages/auth/src/admin_api.py` on the merged API.
2. Add `adminUrl()` helper in `apps/frontend/src/utils/apiBase.ts`.
3. Point admin panels at `VITE_API_BASE_URL/admin/*`.

## Spec conformance

| Spec | Section | Result |
|------|---------|--------|
| docs/spec.md | M4 auth on backend host | implementation drift (admin panels) |
| docs/api-contract.md | — | no prior `/admin/*` contract; added with fix |

## Repro test

- `tests/bugs/test_bug_2026_06_21_admin_panels_wrong_api_host.py`
- `packages/auth/tests/test_admin_api_unit.py`

## Verification plan

| Layer | Check | Status |
|-------|-------|--------|
| L1 | pytest + frontend unit tests | pending |
| L2 | User repro — panels load on merged API | pending |
| L3 | Pre-deploy smoke | pending |
| L4 | Production after deploy | pending |
