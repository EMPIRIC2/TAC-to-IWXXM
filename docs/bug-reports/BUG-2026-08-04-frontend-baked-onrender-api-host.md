# BUG-2026-08-04 — Frontend calls suspended Render API host (ignores `/config.json`)

| Field | Value |
|-------|-------|
| **Status** | fixed (deployed) |
| **Feature** | F15 / F21 connectivity (H5 API host) |
| **Severity** | critical (production operator UI blocked) |
| **Classification** | connectivity / config / deploy |
| **Remediation path** | local-first — wire `apiBase` → `/config.json` + inject publishable key; deploy after approval |
| **Branch** | `fix/frontend-runtime-api-host` |
| **PR** | https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/862 |

## Error description

On `https://app.tac-to-iwxxm.com/`, operator flows fail: `lint-issue-catalog`, `lint-tac`,
and `decode-tac` return **503 Service Unavailable**. DevTools also shows CORS
`No 'Access-Control-Allow-Origin'` and a console warning that the Supabase publishable
key is not set.

## Error logs

```
Request URL: https://metar-to-iwxxm-api.onrender.com/api/v1/lint-issue-catalog?product=metar
Status Code: 503 Service Unavailable
x-render-routing: suspend-by-user
content-type: text/html; charset=utf-8

⚠️ Supabase publishable key not set. Supabase integration will not work.

Access to fetch at 'https://metar-to-iwxxm-api.onrender.com/api/v1/lint-issue-catalog?product=metar'
from origin 'https://app.tac-to-iwxxm.com' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

Render HTML body for the same host:

```html
<title>Service Suspended</title>
This service has been suspended by its owner.
```

## Symptoms & reproduction

| Field | User answer |
|-------|-------------|
| Symptom | Error / crash — API 503 + CORS in browser |
| Where | Production (`app.tac-to-iwxxm.com`) |
| When | After last frontend deploy / DOKS cutover (intake 2 = first option) |
| Frequency | Every time (probe-confirmed) |
| Repro env | Production |
| Severity | Critical / blocked |
| Evidence | DevTools network + console (pasted) |
| Tried | Nothing prior; hotfix intake 2026-08-04 |

### Intake (Phase 0)

- Intent: new production issue
- Remediation: **A+D** — code-fix `apiBase` → runtime config **and** fix missing Supabase publishable key
- Plan: Proceed
- Verification (defaults; AskQuestion tool unavailable): live app must call `https://api.tac-to-iwxxm.com`; frontend vitest + H5 live smoke; user re-checks UI after deploy

## Investigation

### Live probes (2026-08-04)

| Target | Result |
|--------|--------|
| `GET https://metar-to-iwxxm-api.onrender.com/health` | **503** `x-render-routing: suspend-by-user` |
| Render API `metar-to-iwxxm-api` (`srv-d69v688gjchc73cn9kg0`) | `suspended=suspended`, `suspenders=["user"]` |
| `GET https://api.tac-to-iwxxm.com/health` | **200** healthy |
| `GET https://api.tac-to-iwxxm.com/api/v1/lint-issue-catalog?product=metar` | **200** (issues payload) |
| OPTIONS same + `Origin: https://app.tac-to-iwxxm.com` | CORS allow-origin present |
| `GET https://app.tac-to-iwxxm.com/config.json` | `api.baseUrl` = `https://api.tac-to-iwxxm.com` (correct); **no** `supabase.publishableKey` |
| Live bundles `App-BkEPMp_C.js` / `index-*.js` | Bake-time `VITE_API_BASE_URL` = `https://metar-to-iwxxm-api.onrender.com` |

### Hypotheses

1. **Primary (confirmed):** Frontend `apps/frontend/src/utils/apiBase.ts` reads bake-time
   `import.meta.env.VITE_API_BASE_URL` and **does not** use `runtime-config` /
   `/config.json`. Production static assets were built with the old Render URL; that
   Render web service is suspended by the account owner → 503 HTML → browser reports
   missing CORS headers (secondary symptom).
2. **Secondary:** `/config.json` omits `supabase.publishableKey` → console warning
   (auth/Supabase client path); separate from the 503s on lint/decode.
3. **Not root cause:** CORS misconfiguration on the healthy custom-domain API (OPTIONS
   succeeds for `app.tac-to-iwxxm.com`).

### Root cause (confirmed)

1. `apiBase.ts` read bake-time `VITE_API_BASE_URL` only; ignored `/config.json`
   loaded by `main.tsx` → `initRuntimeConfig()`.
2. CI `FRONTEND_VITE_*` defaults and `config/prod.json` still pointed at suspended
   Render hosts after DOKS cutover.
3. Frontend Dockerfile wrote `supabase.url` but never `publishableKey` into
   `config.json` (secondary console warning).

## Repro test

| Path | Status |
|------|--------|
| `apps/frontend/src/test/bug-2026-08-04-frontend-baked-onrender-api-host.test.ts` | green (was red) |
| `tests/bugs/test_bug_2026_08_04_frontend_baked_onrender_api_host.py` | green (was red) |

## Fix

- `apiBase.ts` → prefer `runtime-config` / `/config.json`
- `runtime-config.ts` → do not cache Vite fallback; trim URLs
- `Dockerfile` → inject `publishableKey` into `config.json`
- `ci-cd.yml` + `config/prod.json` → DOKS hosts (`api` / `app.tac-to-iwxxm.com`)
- CORS unit assertion updated for new prod origin

## Verification plan

- Success: live app calls `https://api.tac-to-iwxxm.com` (lint/decode 200)
- Checks: frontend vitest + bug pytest + H5 live smoke after DOKS FE rollout
- Follow-up: user re-checks UI in browser after deploy

## Deploy (2026-08-04)

| Step | Result |
|------|--------|
| PR #862 merged | `134e924` |
| Main CI Validate/Tests | **PASS** |
| Main CI Deploy (Render) | **FAIL expected** — service suspended |
| GHCR FE image | `frontend:20260804230100-134e924` |
| DOKS FE rollout | **PASS** |
| DOKS ConfigMap `metar-frontend-runtime-config` | added `supabase.publishableKey` (was overriding image `config.json`) |
| Live bundles | `api.tac-to-iwxxm.com` only — no `metar-to-iwxxm-api.onrender.com` |
| Live `/config.json` | DOKS API host + publishableKey present |

## Prevention

*(pending Phase 5 — recommend: keep ConfigMap publishableKey in sync / document DOKS override)*
