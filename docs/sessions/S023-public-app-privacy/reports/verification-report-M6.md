# Verification report — M6 Privacy preference center (S023 / EV-017)

**Branch**: `evolve/EV-017-public-app-privacy`  
**Date**: 2026-07-28  
**Milestone**: M6 — Privacy preference center (F22)

## Tasks

| Task | Status | Notes |
|------|--------|-------|
| T6.1 | completed | TC-F22-001..003 Vitest contract + stub (`1926e19`) |
| T6.2 | completed | Notice + settings + localStorage prefs (`84917df`) |
| T6.3 | completed | GPC detect/apply + load/save overrides (this commit) |

## Checks

| Check | Result |
|-------|--------|
| `pnpm exec vitest run src/utils/privacyPreferences.test.ts` | **13/13 PASS** (TC-F22-001..003) |
| `make validate-fast` | PASS (format / typecheck / lint / secrets / yaml / catalog) |

## Deliverables

- `apps/frontend/src/utils/privacyPreferences.ts` — versioned prefs, inventory, GPC
- `PrivacyNotice` + `PrivacySettingsDialog` wired in `FileConverter` (footer + first-visit)
- Storage inventory discloses IndexedDB work history + localStorage prefs

## Next

M7 — E2E / docs / connectivity @ **T7.1** (or 08-verify-build at M6 boundary).  
Draft PR [#786](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/786) still stale until push.
