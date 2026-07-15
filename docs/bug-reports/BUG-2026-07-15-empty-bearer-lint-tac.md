# BUG-2026-07-15 — Empty Bearer on lint-tac/decode-tac + thin lint console

| Field | Value |
|-------|-------|
| **Status** | resolved |
| **Feature** | F6/F7 (lint-tac / decode-tac live assist) + M4 auth |
| **Severity** | critical / blocked (user) |
| **Classification** | code bug (auth hydrate + storage key + UX) |
| **Remediation path** | local-first — deploy only after explicit approval |
| **Session** | S012-empty-bearer-lint-tac |
| **Branch** | fix/S012-empty-bearer-lint-tac |
| **PR** | https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/721 |
| **Merge commit** | `6412b21` |

## Error description

On production, live workbench calls to `POST /api/v1/lint-tac` and
`POST /api/v1/decode-tac` send `Authorization: Bearer` with **no JWT**, and the API
returns `{"detail":"Missing authorization credentials"}`. Separately, when lint
does return issues, the workbench console only shows `[lint-tac] N issue(s)`
without codes/messages.

## Error logs

Browser Network (user paste, production):

```
POST https://metar-to-iwxxm-api.onrender.com/api/v1/lint-tac
authorization: Bearer
→ {"detail":"Missing authorization credentials"}

POST https://metar-to-iwxxm-api.onrender.com/api/v1/decode-tac
authorization: Bearer
→ {"detail":"Missing authorization credentials"}
```

Referrer: `https://metar-to-iwxxm-frontend-v4-web.onrender.com/`
Body: `manual_text=fjgfjf`, `product=METAR`

UI: `[lint-tac] 1 issue(s)` — not descriptive of the actual issue(s).

## Interview record

| Step | Answer |
|------|--------|
| Session gate | Open new hotfix session (close/archive S011) |
| Intent | Report new issue |
| symptom_type | Error / crash (401 + thin lint message) |
| where_seen | Production Render |
| when_started | After last deploy |
| repro_frequency | Every time |
| repro_environment | Production only |
| user_severity | Critical / blocked |
| evidence_available | None beyond fetch paste |
| already_tried | Nothing |
| Remediation path | Fix locally first — deploy after approval |
| Scope | One hotfix covering auth + descriptive lint UX |
| confirm_hotfix_plan | Proceed |
| verification_plan | success=JWT Bearer + descriptive lint UI; checks=full CI parity; monitoring=user watches prod |
| repro_test_matches_symptom | Yes |
| investigation_root_cause | Agree — proceed to fix |
| hotfix_commit_pr | Commit + push + open PR |
| hotfix_pr_merge | Approve merge |
| deploy_hotfix | User verifies production |
| production_verified | Production fixed |
| monitoring_followup | User will monitor |
| prevention | CI repros enough; Cursor rule created |

## Verification plan

| Item | Choice |
|------|--------|
| Success criterion | Logged-in calls carry a real Bearer JWT **and** lint UI shows issue messages/codes |
| Checks | Full main CI parity (local) + gh on main after merge |
| Monitoring | User watches production after deploy |

## Symptoms & reproduction

- **Environment:** Production frontend → API (every time)
- **Trigger:** Enter TAC text so live lint/decode fire (often after hard-refresh while still “logged in”)
- **Expected:** Authenticated request with JWT; console lists issue text/codes
- **Actual:** `Authorization: Bearer` empty → 401; thin console summary when issues exist

## Investigation

### Hypotheses (2026-07-15)

| # | Hypothesis | Evidence | Status |
|---|------------|----------|--------|
| H1 | `App` initializes `accessToken` to `''` on reload even when `isLoggedIn()` is true | `App.tsx` | **Confirmed** |
| H2 | `api.ts` `getAccessToken()` reads `supabase_access_token` while `authService` stores `access_token` | Key mismatch | **Confirmed** |
| H3 | Empty token → `Authorization: Bearer ` → FastAPI `HTTPBearer` returns `None` | Matches API detail | **Confirmed** |
| H4 | Console summary omits issue messages | `useLiveWorkbenchAssist` count-only | **Confirmed** |
| H5 | 401 `detail` string not surfaced in thrown Error | `error.detail?.message` | **Confirmed** |

### Spec conformance

| Corpus | Section | Finding |
|--------|---------|---------|
| product F7 | Live assist JWT lint/decode | Implementation drift — fixed |
| system-spec | Frontend debounced JWT calls; auth middleware | Implementation drift — fixed |
| api | lint-tac / decode-tac auth | 401 correct for missing creds; client now sends token |
| M4 | Auth merged; tokens in localStorage | Drift fixed (aligned key + hydrate) |

Spec conformance: **no blocking Contradiction** — code bug / UX drift.

## Root cause (confirmed)

1. **Reload auth gap:** Session token in `localStorage.access_token`, but React `accessToken` not hydrated on reload → empty Bearer.
2. **Wrong storage key fallback** in `api.ts` (`supabase_access_token` vs `access_token`).
3. **Thin lint console:** summary message was count-only; opaque 401 client message.

## Repro test

| Field | Value |
|-------|-------|
| Path | `apps/frontend/src/test/bug-2026-07-15-empty-bearer-lint-tac.test.tsx` + `…-lint-tac-console-detail.test.tsx` |
| CI | Frontend job (`npm test`) |
| Status | **GREEN** (was RED before fix) |

### TDD iteration log

| Time | Action | Result |
|------|--------|--------|
| 2026-07-15 | Wrote Vitest repros | **RED** |
| 2026-07-15 | User confirmed match + root cause | Proceed |
| 2026-07-15 | Fix applied | **GREEN** |

## Fix

- `App.tsx`: initialize `accessToken` from `getAccessToken()`.
- `api.ts`: read `access_token` (+ legacy fallback); `apiErrorMessage` for lint/decode.
- `useLiveWorkbenchAssist.ts`: console `N issue(s): [code] message; …`.
- Cursor rule: `.cursor/rules/optional/frontend-auth-token-hydrate.mdc`

## Verification

### Layer 1 — Automated
- [x] Repro red→green
- [x] Full frontend `npm test`
- [x] PR CI + main CI success ([run](https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/runs/29459061581))

### Layer 2 — Reproduction
- [x] Encoded in Vitest (localStorage key + App hydrate + console)

### Layer 3 — Pre-deploy smoke
- [x] Covered by main CI Deploy job after merge

### Layer 4 — Production
- [x] User confirmed production fixed (2026-07-15)

### CI

| Check | Result |
|-------|--------|
| PR branch CI | success — https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/runs/29458826429 |
| Main CI + Deploy | success — https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/runs/29459061581 |

## Post-deploy monitoring

User monitors production lint-tac auth header + descriptive console lines.

## Prevention & countermeasures

| Topic | Decision |
|-------|----------|
| Recurrence risk | Possible on similar auth wiring |
| Detect earlier | Main CI frontend Vitest |
| Automated | Bug repro only (done) |
| Code hardening | Hotfix only |
| Process | None |
| Follow-ups | Accept residual risk |
| Cursor rule | `.cursor/rules/optional/frontend-auth-token-hydrate.mdc` |

## Follow-ups

- Resume S011 / EV-008 later if needed (PR #716 already merged to main as of hotfix base)
