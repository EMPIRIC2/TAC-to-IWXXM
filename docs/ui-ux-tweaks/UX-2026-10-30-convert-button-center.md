# UX-2026-10-30-convert-button-center

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-30-convert-button-center` |
| Session | `UX-convert-button-center` (local session store) |
| Surface | Convert page primary action strip (New TAC / Convert / Download latest) |
| Journeys touched | Convert primary path (tests/docs only — not UI copy) |
| Status | closed |

## Desired change

CONVERT sits visually centered in the primary action row: equal-width flanking actions with balanced gaps (not a left-packed cluster of uneven button widths). Staging screenshot showed New TAC | Convert | Download latest left-clustered with Convert off the optical center of the strip.

## Acceptance

- [x] `convert-primary-actions` uses a full-width three-column layout so Convert occupies the middle column.
- [x] New TAC, Convert, and Download latest each stretch to equal column width (`w-full` on the controls).
- [x] Convert click behavior, Download latest, draft-saved chrome, calm empty affordances, and mobile wrap remain intact.

## Must not break

- Convert / Validate click handlers and disabled/`aria-busy` states.
- Calm empty hero (strip stays hidden when empty).
- Download latest enablement when a result exists.
- Autosave "Draft saved" indicator above the strip.
- Mobile: columns may stack; desktop keeps three equal columns.

## Style-guide impact

Norm to append ([Corpus: ui-style]):

> Convert primary action strip: full-width three equal columns (New TAC | Convert | Download latest); Convert stays in the middle column. Do not left-pack unequal min-widths.

Target section: Layout / density

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/app/components/FileConverter.test.tsx` (`UX-2026-10-30: primary actions keep Convert centered in equal columns`) |
| Red date | 2026-10-30 |
| Green date | 2026-10-30 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-30 | Intake: staging screenshot; Convert off-center in left-packed flex row. |
| 2026-10-30 | Root cause: `convert-primary-actions` was `flex` + unequal `min-w-*` (7.5rem / 11rem / 11rem), so Convert was not the geometric center of the strip. Leftover from convert-polish HANDOFF item 4. |
| 2026-10-30 | Invisible in-flow `Loader2` also shifted the Convert label; moved spinner to `absolute left-3` so the label stays centered in the middle column. |
| 2026-10-30 | Fix: `grid w-full sm:grid-cols-3` + `w-full` controls; Vitest asserts layout classes. |

## Fix

- `apps/frontend/src/app/components/FileConverter.tsx` — equal-column primary strip; absolute Convert spinner.
- `apps/frontend/src/app/components/FileConverter.test.tsx` — layout class regression.
- `docs/ui-style-guide.md` — Layout bullet + Changelog of norms row.

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [x] Session closed / HANDOFF written
