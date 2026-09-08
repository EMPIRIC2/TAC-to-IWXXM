# Bug report: authenticated save failed uses wrong target

**ID:** BUG-2026-09-08-authenticated-save-failed-wrong-target  
**Date:** 2026-09-08  
**PR:** pending  
**Session:** EV-staging-adversarial-e2e

## Error description

After sign-in on staging, the converter can show a persistent `Save failed` indicator even
though authenticated work history remains visible. The active draft is hydrated from the
server, but subsequent converter autosaves are still routed to local IndexedDB.

## Error logs

```text
[App] initializeWorkSessions(token) -> listWorkSessions(token) -> active server draft id
[FileConverter] useWorkSessionSync({ accessToken, sessionId: activeWorkSessionId, ... })
[useWorkSessionSync] persist failed: Error: Work session not found: <server-session-id>
```

Live evidence:

- Signed-in staging converter shows authenticated shell controls and server-backed recent work.
- The converter hook still uses `updateLocalWorkSession(activeServerId, payload)` when a
  `sessionId` is present.

## Investigation

1. `App.tsx` hydrates logged-in drafts with `listWorkSessions(token)` and stores the active
   server session id in `activeWorkSessionId`.
2. `FileConverter.tsx` passes both `accessToken` and `activeWorkSessionId` into
   `useWorkSessionSync`.
3. `useWorkSessionSync.ts` ignores `accessToken` and always persists to IndexedDB via
   `createLocalWorkSession` / `updateLocalWorkSession`.
4. `updateLocalWorkSession()` throws when the authenticated server session id does not exist
   in IndexedDB, which flips the autosave indicator to `error`.

**Root cause:** authenticated autosave is still bound to the guest/local storage path instead
of the restored F31 remote work-session API.

## Repro test

- Path: `apps/frontend/src/hooks/useWorkSessionSync.test.ts`
- Status: red before fix; green after fix

## Fix

Teach `useWorkSessionSync` to persist to `createWorkSession` / `updateWorkSession` whenever a
real access token is present, while preserving guest/local IndexedDB behavior without a token.

## Interview record

- Intent: New bug: reproduce, fix, and verify.
- Symptom class: Frontend/API integration regression in work-session save flow.
- Repro environment: Local reproducible test with live staging verification.
- Severity: High.
- Root cause confirmation: approved before patching.

## Prevention & countermeasures

- Add authenticated hook tests for remote create and remote update paths.
- Keep guest/local and authenticated/remote persistence behavior explicitly separated in the hook.

## Cursor rule

- No new rule proposed yet; existing F31 API contract and bug-investigation workflow were sufficient.
