# S012 — 14-hotfix report

**Session:** S012-empty-bearer-lint-tac  
**Date:** 2026-07-15  
**PR:** https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/721 (merged)

## Issue

Production live assist sent `Authorization: Bearer` (empty) to `/api/v1/lint-tac`
and `/decode-tac` → `Missing authorization credentials`. Lint console showed only
`N issue(s)`.

## Fix

Hydrate `accessToken` on App reload; align `api.ts` with `access_token`; richer
lint console; surface FastAPI string `detail`.

## Verification

- Vitest repros red→green
- PR + main CI success (including Deploy)
- User confirmed production fixed

## Prevention

Cursor rule: `.cursor/rules/optional/frontend-auth-token-hydrate.mdc`
