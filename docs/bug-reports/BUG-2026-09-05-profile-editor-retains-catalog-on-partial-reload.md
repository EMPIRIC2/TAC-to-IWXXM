# BUG-2026-09-05 — Profile editor should retain catalog view on partial reload failure

## Error description

The ConversionProfile editor regressed in its degraded-load handling after EV-1149.
On the first load, the new partial-failure UX works as intended, but a later
save-triggered reload can still hide the summary and inspector even when the page
already has a usable catalog cached from an earlier successful load.

This was caught during PR review for [#1150](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1150).

## Error logs

Review finding:

```text
Reload currently clears previously loaded catalog state on any later catalog fetch
failure. After a successful save, onSave()/onSaveOverlay() calls load(), and if
fetchProfileCatalog() rejects once, nextCatalog becomes null and setCatalog(nextCatalog)
collapses the existing summary/inspector even though the page had usable catalog
data moments earlier.
```

Frontend repro failure:

```text
FAIL  src/app/components/ConversionProfilePage.test.tsx > ConversionProfilePage > preserves the last successful catalog view when a save-triggered reload degrades
TestingLibraryElementError: Unable to find an element by: [data-testid="conversion-profiles-summary-primary"]
```

## Investigation

| Time | Note |
|---|---|
| 2026-09-05 | PR review identified that the new `Promise.allSettled()` path in `ConversionProfilePage` still drops the usable catalog view after a later partial refresh failure. |
| 2026-09-05 | Repro plan: extend the existing Vitest suite to simulate a successful initial catalog load followed by a failed catalog request during the save-triggered refresh. |
| 2026-09-05 | Repro confirmed: the new frontend test failed because the summary card disappeared after the save-triggered reload error. |
| 2026-09-05 | Root cause confirmed: rejected refreshes overwrote successful slices with `null`, and the render branches prioritized `loadErrors.catalog` over cached catalog data that was still valid. |
| 2026-09-05 | Fix applied: preserve the last successful catalog/packs/overlays slices on rejected refreshes, and only replace the summary/inspector/blocks with the unavailable shell when no cached catalog exists yet. |

## Repro test

- Path: `apps/frontend/src/app/components/ConversionProfilePage.test.tsx`
- Red: `cd apps/frontend && pnpm exec vitest run src/app/components/ConversionProfilePage.test.tsx` -> failed (`conversion-profiles-summary-primary` disappeared after save-triggered reload failure)
- Green: `cd apps/frontend && pnpm exec vitest run src/app/components/ConversionProfilePage.test.tsx` -> passed
- Expectation: a later catalog refresh failure should show degraded messaging without hiding the last successful catalog summary and inspector

## Fix

- `apps/frontend/src/app/components/ConversionProfilePage.tsx`
  - Preserve previously loaded slices when catalog, rule-pack, or overlay refreshes reject
  - Render the catalog-unavailable warning without collapsing cached catalog content
- `apps/frontend/src/app/components/ConversionProfilePage.test.tsx`
  - Add a regression test covering a successful load followed by a failed save-triggered catalog reload

## Interview record

- `19-address-pr-review` target: remediate PR #1150
- Remediation tracking: start a new remediation cycle
- Scope: blockers first, then advisories if any
- Finding approach: fix with a repro-first test, preserve last successful data on partial reload failure, then reply on the PR thread
- Remediation path: fix locally first, then push and watch CI
- Repro confirmation: yes, preserve the last successful catalog view and continue to fix
- Root cause confirmation: keep the last successful catalog slice on partial reload failure, and only fall back to the unavailable shell when no cached catalog exists yet

## Prevention & countermeasures

- Add regression coverage for both first-load degradation and refresh-after-success degradation whenever a UI introduces partial-failure handling.
- Prefer warning banners over destructive fallback shells when cached operator data is still usable.

## Cursor rule

- Deferred unless this pattern repeats across other operator pages
