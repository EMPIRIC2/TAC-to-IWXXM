# BUG-2026-06-22 — Admin E2E User Approvals heading mismatch

**Status**: resolved  
**Severity**: high  
**Feature**: F3 (auth/admin) / H6 E2E  
**Reported**: 2026-06-22  

## Summary

`make test-live-e2e` fails on `workflow-auth-admin-readiness.e2e.spec.ts` test
"admin panel navigation loop remains stable across repeated transitions". Playwright
cannot find a second heading named exactly `User Approvals` after clicking the User
Approvals panel card — the panel content h2 is `Pending User Approvals`.

## Error description

Playwright assertion timeout at line 71: expected
`getByRole('heading', { name: 'User Approvals', exact: true }).nth(1)` to be visible;
element(s) not found.

## Error logs

```
Error: expect(locator).toBeVisible() failed
Locator: getByRole('heading', { name: 'User Approvals', exact: true }).nth(1)
Expected: visible
Timeout: 5000ms
Error: element(s) not found
  at workflow-auth-admin-readiness.e2e.spec.ts:71:9
```

Backend during failure (all 200 OK):

```
POST /auth/login HTTP/1.1" 200 OK
GET /admin/settings HTTP/1.1" 200 OK
GET /admin/all-users HTTP/1.1" 200 OK
GET /admin/stats HTTP/1.1" 200 OK
```

## Symptoms & reproduction

1. Run `make test-live-e2e` (or `DISABLE_AUTH=false npx playwright test workflow-auth-admin-readiness.e2e.spec.ts:47`)
2. Test logs in as admin, loops panel navigation
3. Fails when asserting User Approvals panel content heading after click

**Frequency**: every time (local repro confirmed 2026-06-22)

## Remediation path

local-first — no production deploy (test-only fix)

## Investigation

| Time | Finding |
|------|---------|
| 2026-06-22 | User report via terminal excerpt — test 24 failed in live E2E run |
| 2026-06-22 | Local repro with Playwright webServer — same assertion at line 71 |
| 2026-06-22 | `AdminDashboard.tsx` card h3 uses title `User Approvals` |
| 2026-06-22 | `UserApprovalPanel.tsx:159` panel h2 is `Pending User Approvals` — no second exact match |
| 2026-06-22 | System Settings / System Monitoring assertions use matching card + panel titles |

## Root cause

**Test bug (regression in E2E spec)** — assertion expects panel heading `User Approvals`
but UI intentionally renders `Pending User Approvals` in the panel body.

## Spec conformance

| Check | Result |
|-------|--------|
| `docs/test-plan.md` H6 / UJ admin | Test should verify panel navigation stability — pass after locator fix |
| `docs/spec.md` admin UI | No spec mandating exact panel h2 text; card vs panel naming differs |
| Blocking drift | none |

## Repro test

| Path | Status |
|------|--------|
| `apps/e2e/workflow-auth-admin-readiness.e2e.spec.ts:47` | RED (pre-fix) |

No separate `tests/bugs/` pytest module — failure is Playwright-only; the spec is the repro/regression test.

## TDD iteration log

| # | Action | Result |
|---|--------|--------|
| 1 | Run Playwright spec with webServer | RED — User Approvals nth(1) not found |

## Fix

1. **UI alignment**: Renamed `UserApprovalPanel` h2 from `Pending User Approvals` to `User Approvals`
   (matches card title; enables `.nth(1)` panel assertion pattern used by other panels).
2. **E2E locators**: Added `.first()` on initial dashboard checks in `auth.e2e.spec.ts`,
   `admin-navigation.e2e.spec.ts`, and `workflow-auth-admin-readiness.e2e.spec.ts` to avoid
   Playwright strict-mode violations when card + panel headings both match.
3. **Docs**: Added admin locator note to `docs/test-plan.md` §User Journeys.

## Verification

### Layer 1 — Automated

- [x] Repro spec green after fix (6/6 admin specs, 2026-06-22)
- [x] Related admin-navigation spec green

### Layer 2 — Reproduction

- [x] Local Playwright with DISABLE_AUTH=false — pass

### CI

- [ ] Not required per user verification plan (E2E only)

## Prevention & countermeasures

| Question | Answer |
|----------|--------|
| Recurrence risk | Possible on similar card/panel title drift |
| Detect earlier | Run auth-admin E2E before release |
| Automated | Fixed Playwright spec (regression test) |
| Code hardening | Aligned panel h2 with card title (done) |
| Process | test-plan locator note (done) |
| When | Same session |
| Owner | Agent |

## Interview record

- Intent: new issue
- Symptom: Playwright assertion error, local `make test-live-e2e`
- Severity: high
- Remediation: local-first
- Verification: spec passes; E2E-only checks; no deploy
