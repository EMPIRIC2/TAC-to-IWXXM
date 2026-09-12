# PR Review — #687 (18-pr-review)

**Date:** 2026-06-24  
**PR:** https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/687  
**Head:** `feat/S004-issue-555-feedback` @ `338baa6`  
**Base:** `main`  
**Verdict:** REQUEST_CHANGES  
**Blockers:** 1 | **Advisories:** 4 | **Praise:** 4

## Summary

Large EV-004 / F5 feature PR: work-sessions REST API, Supabase migration + RLS, frontend sync/history UI, docs/ADRs, and session artifacts. Implementation quality and test breadth are strong, but **remote CI is red** on Prettier `format-check` (6 files), which blocks merge.

## CI

| Check | Status |
|-------|--------|
| Validate (`make validate-ci`) | **FAIL** — `format-check` / Prettier on 6 TS/JSON files |
| Test matrix | Skipped (Validate failed) |
| Local `format-check` | **FAIL** (same 6 files) |
| Local backend unit (+ work-session) | **PASS** (1148 tests, 98% cov) |
| Local Vitest | **PASS** (504/504) |

## Subagents

| Agent | Status | Notes |
|-------|--------|-------|
| Bugbot | Skipped | Could not compute branch diff in workspace |
| Security review | Skipped | Could not compute branch diff in workspace |

Manual security triage: JWT-forwarding + RLS per ADR-011; `require_admin()` on admin route; no secret keys in app code; migration policies consistent with contract.

## Findings

### Blocking

1. **Prettier format-check** — `apps/e2e/metar-work-history.e2e.spec.ts`, `apps/frontend/public/config.json`, `App.test.tsx`, `ErrorLogPanel.test.tsx`, `MyMetarsPage.test.tsx`, `WorkHistorySidebar.test.tsx`.

### Advisory

1. Empty PR description; no `Closes #555` linkage.
2. `public/config.json` drift from e2e fixture (`disableAuth`, real publishable key).
3. Admin `user_email` not implemented (contract vs UI/backend).
4. `useWorkSessionSync` logs 409 WIP conflicts but does not toast/guide user.

## Checklist

| Section | Result |
|---------|--------|
| A Intake | Partial — no PR body / issue link |
| B Code quality | Pass (style CI except Prettier) |
| C Tests | Pass locally |
| D CI | **Fail** (format-check) |
| E Hygiene | Pass |
| F Connectivity | Pass (CORS in render.yaml; contract docs) |
| G Subagents | Manual only |
| H Delivery | Posted to GitHub |
