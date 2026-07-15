# BUG-2026-07-15 — Empty Bearer on lint-tac/decode-tac + thin lint console

| Field | Value |
|-------|-------|
| **Status** | verifying |
| **Feature** | F6/F7 (lint-tac / decode-tac live assist) + M4 auth |
| **Severity** | critical / blocked (user) |
| **Classification** | code bug (auth hydrate + storage key + UX) |
| **Remediation path** | local-first — deploy only after explicit approval |
| **Session** | S012-empty-bearer-lint-tac |
| **Branch** | fix/S012-empty-bearer-lint-tac |

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

## Verification plan

| Item | Choice |
|------|--------|
| Success criterion | Logged-in calls carry a real Bearer JWT **and** lint UI shows issue messages/codes (not only “[lint-tac] N issue(s)”) |
| Checks | Full main CI parity (local) + gh on main after merge |
| Monitoring | User will watch production after deploy |

## Symptoms & reproduction

- **Environment:** Production frontend → API (every time)
- **Trigger:** Enter TAC text (e.g. `fjgfjf`) so live lint/decode fire
- **Expected:** Authenticated request with JWT; console lists issue text/codes
- **Actual:** `Authorization: Bearer` empty → 401; thin console summary when issues exist
- **Local:** Not reproduced yet (production-only per intake)

## Investigation

### Hypotheses (2026-07-15)

| # | Hypothesis | Evidence | Status |
|---|------------|----------|--------|
| H1 | `App` initializes `accessToken` to `''` on reload even when `isLoggedIn()` is true | `App.tsx` L52–60: `isAuthenticated` from `isLoggedIn()`, but `accessToken` only set via login handlers | Likely |
| H2 | `api.ts` `getAccessToken()` reads `supabase_access_token` while `authService` stores `access_token` | Key mismatch — fallback never sees JWT | Likely |
| H3 | Empty token → `Authorization: Bearer ` → FastAPI `HTTPBearer` returns `None` → “Missing authorization credentials” | Matches `security.py` L91–93 + Starlette empty-credentials behavior | Likely |
| H4 | Console summary omits issue messages by design of `useLiveWorkbenchAssist` | L150–152: `` `${n} issue(s)` `` only | Likely (UX) |
| H5 | 401 `detail` string not surfaced in thrown Error | `error.detail?.message` misses string `detail` | Contributing |

### Spec conformance

| Corpus | Section | Finding |
|--------|---------|---------|
| product F7 | Live assist JWT lint/decode | Implementation drift — requests must be authorized |
| system-spec | Frontend debounced JWT calls; auth middleware | Implementation drift vs U1b/U2 |
| api | lint-tac / decode-tac auth | No blocking contradiction — 401 is correct for missing creds; client should send token |
| M4 | Auth merged; tokens in localStorage | Drift: dual localStorage keys |

Spec conformance: **no blocking Contradiction** — code bug / UX drift.

## Root cause (proposed)

_(pending user confirmation after red repro)_

1. **Reload auth gap:** Session cookie/token exists in `localStorage.access_token`, but React `accessToken` state is not hydrated → empty Bearer.
2. **Wrong storage key fallback** in `api.ts` (`supabase_access_token` vs `access_token`).
3. **Thin lint console:** summary message is count-only.

## Repro test

| Field | Value |
|-------|-------|
| Path | `apps/frontend/src/test/bug-2026-07-15-empty-bearer-lint-tac.test.tsx` + `…-lint-tac-console-detail.test.tsx` |
| CI | Frontend job (`npm test`) — not pytest `tests/bugs/` |
| Status | **GREEN** (5/5) after fix 2026-07-15 |
| Asserts | (1) lint/decode send Bearer from `access_token`; (2) App reload hydrates token into FileConverter; (3) console includes issue message; (4) 401 string detail surfaced |

### TDD iteration log

| Time | Action | Result |
|------|--------|--------|
| 2026-07-15 | Phase 0 intake + branch + report | — |
| 2026-07-15 | Wrote Vitest repros (auth Bearer + App hydrate + console detail + 401 detail) | **RED** — `Bearer ` / empty token / `1 issue(s)` / `HTTP 401` as expected |
| 2026-07-15 | User `repro_test_matches_symptom`=Yes; `investigation_root_cause`=Agree | Confirmed |
| 2026-07-15 | Fix: App hydrate + api.ts `access_token` + apiErrorMessage + lint console detail | **GREEN** 5/5 + related suites |

## Root cause (confirmed)

1. **Reload auth gap:** `App` set `isAuthenticated` from `isLoggedIn()` but left `accessToken` as `''` until a login handler ran.
2. **Wrong storage key:** `api.ts` read `supabase_access_token`; `authService` stores `access_token`.
3. **Thin lint console / opaque 401:** count-only summary; string FastAPI `detail` not used in thrown Error.

## Fix

- `App.tsx`: initialize `accessToken` from `getAccessToken()`.
- `api.ts`: read `access_token` (legacy fallback); `apiErrorMessage` for lint/decode.
- `useLiveWorkbenchAssist.ts`: console `N issue(s): [code] message; …`.

## Verification

### Layer 1 — Automated
- [ ] Repro red→green
- [ ] CI parity local
- [ ] Frontend tests

### Layer 2 — Reproduction
- [ ] Pending

### Layer 3 — Pre-deploy smoke
- [ ] N/A until deploy approved

### Layer 4 — Production
- [ ] Deferred (local-first)

## Prevention & countermeasures

_(Phase 5)_

## Follow-ups

- Resume S011 / EV-008 / PR #716 after hotfix closes
