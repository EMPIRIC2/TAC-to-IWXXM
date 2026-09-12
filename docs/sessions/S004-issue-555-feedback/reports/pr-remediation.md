# PR Remediation — #687 (19-address-pr-review)

**Date:** 2026-06-24
**Cycle:** PRM-006 (links PRR-007)
**PR:** https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/687
**Head:** `feat/S004-issue-555-feedback`
**Base:** `main`
**Scope:** Blocker only (user-confirmed)
**Outcome:** Blocker resolved; 3 advisories deferred; 1 new out-of-scope CI failure tracked as #688

## Scope decision

User scoped this cycle to the **blocker only** (F-001 Prettier `format-check`). For the
`config.json` finding the user directed restoring the e2e fixture values.

## Findings

| ID | Sev | Status | Commit | Note |
|----|-----|--------|--------|------|
| F-001 | 🔴 Blocker | **fixed** | `c2d4ed4` | Prettier `format-check` on 6 files |
| F-002 | 🟡 Advisory | deferred | — | Empty PR description / no `Closes #555` |
| F-003 | 🟡 Advisory | **fixed** | `c2d4ed4` | `config.json` restored to e2e fixture (folded into F-001 commit) |
| F-004 | 🟡 Advisory | deferred | — | Admin `user_email` vs contract |
| F-005 | 🟡 Advisory | deferred | — | `useWorkSessionSync` 409 user guidance |

## Fix detail (F-001 + F-003)

- Ran `prettier --write` on the 5 flagged test/spec files:
  `apps/e2e/metar-work-history.e2e.spec.ts`, `apps/frontend/src/app/App.test.tsx`,
  `apps/frontend/src/app/components/ErrorLogPanel.test.tsx`,
  `apps/frontend/src/app/components/MyMetarsPage.test.tsx`,
  `apps/frontend/src/app/components/WorkHistorySidebar.test.tsx` — formatting-only reflows.
- Restored `apps/frontend/public/config.json` to the `main`/e2e fixture values
  (`environment: e2e`, `disableAuth: false`, `publishableKey: test`), removing the committed
  `sb_publishable_*` key (resolves F-003).

## Verification

- `make format-check` → **green** (Prettier + ruff).
- Touched frontend tests: **40/40 pass** (`vitest run` on the 4 test files).
- Remote CI run `28128930947` @ `c2d4ed4`:
  - **Validate (format-check): PASS** ← blocker resolved
  - Test (backend / auth / shared / gifts / frontend): PASS
  - **Test (integration): FAIL** ← see follow-up below

## GitHub

- Replied + **resolved** blocker thread `PRRT_kwDOQW-3CM6MAhjW` citing `c2d4ed4`.
- Replied + **resolved** `config.json` thread `PRRT_kwDOQW-3CM6MAhlK` citing `c2d4ed4`.

## Follow-up (out of scope)

**Issue [#688](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/688)** — `Test (integration)`
fails building the frontend Docker image: `apps/frontend/Dockerfile` runs `npm install` but
`package.json` depends on `@metar/shared: "workspace:*"` (npm can't resolve `workspace:*`; the
`apps/frontend`-only build context lacks the workspace package). Pre-existing monorepo-migration
infra bug, **not** introduced by this PR — it was masked because the prior commit failed at the
`Validate` gate before the test matrix ran. User chose to track as a separate follow-up.

## Not merged

Per skill: the user merges manually after re-review passes.
