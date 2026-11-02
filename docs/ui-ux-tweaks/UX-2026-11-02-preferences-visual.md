# UX-2026-11-02-preferences-visual

| Field | Value |
|-------|--------|
| Id | `UX-2026-11-02-preferences-visual` |
| Session | `UX-preferences-visual` (local session store) |
| Surface | Workbench header HELP / PREFERENCES chrome + User Preferences modal |
| Journeys touched | Display/output prefs path only (tests/docs — not UI copy) |
| Status | fixed |

## Desired change

Match dark-theme outline chrome for Help / Preferences header controls and the
User Preferences modal (blue outline borders, transparent fill, gear title,
Reset / Cancel outline + Save primary). Visual / ui-ux-tweak only — display name
and output file extension; **not** validation / Schematron / environment knobs.

## Acceptance

- [x] Help and Preferences header buttons use outline chrome (blue border, no gray fill)
- [x] Preferences modal has a subtle blue-tinted border on the dark card
- [x] Reset to Defaults / Cancel stay outline; Save Preferences stays solid primary
- [x] Modal still exposes only display/output name + output file extension (no validation controls)
- [x] Vitest asserts the chrome invariants

## Must not break

- Slim prefs persistence (display name, output extension)
- Theme toggle placement beside Preferences
- Help checklist open
- No planning ids in operator-facing copy
- Do not add iwxxm-validate / Schematron / env validation knobs

## Style-guide impact

Norm to append:

> Workbench Help / Preferences chrome and the User Preferences modal use dark
> outline controls (primary blue border, transparent fill); Preferences stays
> display-name + output-extension only.

Target section in `[Corpus: ui-style]`: Layout / density + Tokens / theme

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/app/components/UserPreferencesDialog.test.tsx` (+ header assert in `FileConverter.test.tsx`) |
| Red date | 2026-11-02 |
| Green date | 2026-11-02 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-11-02 | Screenshots are acceptance; header/modal outline buttons currently override with `dark:bg-gray-700` fill. |
| 2026-11-02 | Scope locked: visual only — no validation controls in Preferences. |
| 2026-11-02 | Red Vitest (missing `preferences-dialog-panel`; header still used `dark:bg-gray-700`). |
| 2026-11-02 | Outline chrome + blue modal border; tests green. |

## Fix

Files / approach:

- `FileConverter.tsx`: Help / Preferences outline buttons use transparent fill +
  primary border (drop gray fill overrides).
- `UserPreferencesDialog.tsx`: `preferences-dialog-panel` with
  `dark:border-blue-400/50`; Reset outline without gray fill.
- Vitest: outline chrome asserts on header + modal; no validation knobs.
- Style-guide Layout + Changelog of norms row.

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [ ] Session closed / HANDOFF written
