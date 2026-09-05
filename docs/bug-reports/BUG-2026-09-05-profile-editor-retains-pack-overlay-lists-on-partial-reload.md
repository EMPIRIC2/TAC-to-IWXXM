# BUG-2026-09-05 — Profile editor should retain pack and overlay lists on partial reload failure

## Error description

The follow-up remediation for EV-1149 preserved cached catalog state after a failed
refresh, but the Rule packs and Signed overlays sections still regressed on later
refresh failures. Their data stayed in React state, yet the UI replaced the cached
lists with unavailable-only messages instead of keeping the lists visible with a
degraded warning.

This was caught during the rerun review for [#1150](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1150).

## Error logs

Review finding:

```text
load() now preserves prior packs/overlays slices on rejected refreshes, but the
render branches still treat loadErrors.packs and loadErrors.overlays as exclusive.
After a later reload failure, operators lose visibility into previously loaded
packs/overlays instead of seeing the cached list with a degraded warning.
```

Frontend repro failure:

```text
FAIL  src/app/components/ConversionProfilePage.test.tsx > ConversionProfilePage > preserves the last successful pack and overlay lists when a later reload degrades
TestingLibraryElementError: Unable to find an element by: [data-testid="conversion-profiles-pack-list"]
```

## Investigation

| Time | Note |
|---|---|
| 2026-09-05 | Rerun PR review found that cached catalog data now survives a failed refresh, but cached pack and overlay lists still disappear from the UI on the same class of failure. |
| 2026-09-05 | Repro plan: extend the existing frontend Vitest suite to simulate a successful initial load followed by rejected rule-pack and overlay reloads during a later save-triggered refresh. |
| 2026-09-05 | Repro confirmed: the new test failed because the cached pack list was no longer rendered after the later refresh error. |
| 2026-09-05 | Root cause confirmed: the fallback setters already preserved `packs` and `overlays`, but the JSX still short-circuited to unavailable-only branches whenever `loadErrors.packs` or `loadErrors.overlays` was set. |
| 2026-09-05 | Fix applied: keep cached pack and overlay lists rendered when they exist, and show degraded warning text alongside them rather than replacing them. |

## Repro test

- Path: `apps/frontend/src/app/components/ConversionProfilePage.test.tsx`
- Red: `cd apps/frontend && pnpm exec vitest run src/app/components/ConversionProfilePage.test.tsx` -> failed (`conversion-profiles-pack-list` disappeared after later reload failure)
- Green: `cd apps/frontend && pnpm exec vitest run src/app/components/ConversionProfilePage.test.tsx` -> passed
- Expectation: later rule-pack or overlay refresh failures should keep the last successful lists visible while surfacing degraded-state warnings

## Fix

- `apps/frontend/src/app/components/ConversionProfilePage.tsx`
  - Keep cached pack and overlay lists visible when refreshes fail after an earlier successful load
  - Render unavailable warnings as banners only when cached list data still exists
- `apps/frontend/src/app/components/ConversionProfilePage.test.tsx`
  - Add a regression test covering retained pack and overlay lists on later degraded reloads

## Interview record

- Continue remediation scope: fix the remaining packs/overlays degraded-state blocker now
- Continue remediation path: repro-first test, then fix and reverify
- Repro confirmation: keep cached pack and overlay lists visible with degraded messaging
- Root cause confirmation: keep cached pack/overlay lists rendered when they exist, and show degraded warnings alongside them instead of replacing them

## Prevention & countermeasures

- When adding cached partial-failure UX, verify every affected section preserves both data and visibility across later refresh failures.
- Pair state-preservation changes with matching render-path tests so cached-data fallbacks and degraded banners stay in sync.

## Cursor rule

- Deferred unless this cached-state/degraded-render mismatch recurs on other operator pages
