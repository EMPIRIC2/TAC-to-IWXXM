# BUG-2026-06-20-login-cors-failed-fetch

| Field | Value |
|-------|-------|
| **Status** | resolved |
| **Feature** | F1 (auth gate for converter) / M4 |
| **Severity** | critical |
| **Classification** | config / infra (connectivity) |
| **Remediation path** | local-first — deploy after user approval |

## Error description

Production login fails every time with browser console:

```
[Auth Service] Initialized with URL: https://metar-to-iwxxm-api.onrender.com
[Auth Service] Logging in user: Object
[Auth Service] Login exception: TypeError: Failed to fetch
Login error: TypeError: Failed to fetch
```

User cannot authenticate on `https://metar-to-iwxxm-frontend-v4-web.onrender.com`.

## Error logs

```
index-4jeNk9Bi.js:217 [Auth Service] Initialized with URL: https://metar-to-iwxxm-api.onrender.com
index-4jeNk9Bi.js:217 [Auth Service] Logging in user: Object
installHook.js:1 [Auth Service] Login exception: TypeError: Failed to fetch
installHook.js:1 Login error: TypeError: Failed to fetch
```

### Live probe (2026-06-21)

```bash
# API health OK
curl -sS -o /dev/null -w "%{http_code}" https://metar-to-iwxxm-api.onrender.com/health
# -> 200

# CORS preflight from production frontend origin — FAIL
curl -sS -X OPTIONS https://metar-to-iwxxm-api.onrender.com/auth/login \
  -H "Origin: https://metar-to-iwxxm-frontend-v4-web.onrender.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type"
# -> 400 Disallowed CORS origin

# Only default dev origins accepted (METAR_CORS_ORIGINS unset on deployed API)
curl -sS -X OPTIONS https://metar-to-iwxxm-api.onrender.com/health \
  -H "Origin: http://localhost:8000" \
  -H "Access-Control-Request-Method: GET"
# -> 200 OK
```

## Symptoms & reproduction

| Field | User answer |
|-------|-------------|
| Symptom | Error / crash — Failed to fetch |
| Where | Production Render |
| When | After last deploy |
| Frequency | Every time |
| Repro env | Production only |
| Severity | Critical — cannot log in |
| Evidence | Console logs (above) |
| Tried | Nothing |

## Investigation

### Timeline

| When | Event |
|------|-------|
| 2026-06-20 | E2E report notes T3_auth partial; H4 recorded pass (may be stale) |
| 2026-06-21 | User reports login Failed to fetch; live H4 repro **RED** |

### Hypotheses

| # | Hypothesis | Result |
|---|------------|--------|
| H1 | Wrong `VITE_API_BASE_URL` in frontend bundle (H5) | **Rejected** — bundle embeds correct API URL |
| H2 | CORS preflight blocked — `METAR_CORS_ORIGINS` missing on API | **Confirmed** — only localhost defaults allowed |
| H3 | Auth route not deployed | **Rejected** — `/auth/login` exists (405 on OPTIONS without preflight headers) |
| H4 | Supabase misconfig causes 500 after CORS fixed | **Open** — POST returns 500 even with allowed origin |

### Root cause (provisional)

Deployed API service `metar-to-iwxxm-api` does not have `METAR_CORS_ORIGINS` (and likely `FRONTEND_URL`) applied. `get_cors_origins()` falls back to `http://localhost:8000` defaults per `apps/backend/src/api.py`. Browser blocks cross-origin login → `TypeError: Failed to fetch`.

`render.yaml` specifies the correct values; Render dashboard env appears out of sync with Blueprint.

## Spec conformance

| Spec | Section | Result |
|------|---------|--------|
| docs/spec.md | CORS via METAR_CORS_ORIGINS | implementation drift (deploy config) |
| docs/deploy.md | Redeploy order §1 | METAR_CORS_ORIGINS required on API |
| docs/ops/staging-secrets-matrix.md | Runtime API vars | drift — values not on live service |
| docs/api-contract.md | Access-Control-Allow-Origin | fail live H4 |

No blocking spec contradiction.

## Repro test

| Path | Status |
|------|--------|
| `tests/bugs/test_bug_2026_06_20_login_cors_failed_fetch.py` | RED (live) |

## Verification plan

| Field | Choice |
|-------|--------|
| Success criterion | Original error gone — login succeeds in production browser |
| Checks | Full main CI parity (local) + gh on main after merge |
| Monitoring | User watches production |

## Verification

### Layer 1 — Automated

- [x] Repro test red → green (2026-06-21)
- [ ] CI parity local (pending — config-only hotfix)

### Layer 2 — Reproduction

- [x] H4 live CORS preflight pass (`verify_connectivity.sh`)
- [x] POST `/auth/login` returns 401 (not 500) for invalid credentials

### Layer 3 — Pre-deploy smoke

- [x] CORS + auth endpoint smoke pass

### Layer 4 — Production

- [x] User confirms browser login succeeds (2026-06-21)

## Prevention & countermeasures

| Item | Action |
|------|--------|
| Detection | Run `verify_connectivity.sh` with staging env before auth sign-off (H4 catches CORS drift) |
| Deploy script | `scripts/deploy/apply_render_cors_env.sh` — sync CORS from `.env` + Render API |
| Follow-up | Ensure Blueprint sync applies `render.yaml` env vars; `SUPABASE_*` marked `sync: false` must stay set in dashboard |

### CI

| Check | Result |
|-------|--------|
| Local parity | pending |
| PR branch CI | pending |
| Main CI | pending |

## Interview record

See Phase 0 AskQuestion batches (hotfix_intent=new_issue, remediation=local_first, success=error_gone).

## Fix

**Applied 2026-06-21 via Render API:**

1. Set `METAR_CORS_ORIGINS` and `FRONTEND_URL` on `metar-to-iwxxm-api` (`srv-d69v688gjchc73cn9kg0`) — deploy `dep-d8s0psvavr4c73f6175g`
2. Set `SUPABASE_URL` and `SUPABASE_ANON_KEY` (were missing) — deploy `dep-d8s0q9kvikkc7393s580`

**Automation:** `scripts/deploy/apply_render_cors_env.sh` (loads `RENDER_API_KEY` from `.env`)

## Prevention & countermeasures

(pending Phase 5)

## Cursor rule

(pending Phase 5.1)

## Follow-ups

- Investigate `/auth/login` 500 after CORS fix (possible Supabase env gap)
