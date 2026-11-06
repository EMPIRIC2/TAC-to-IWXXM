# UX-2026-10-29-center-button-text

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-29-center-button-text` |
| Session | `UX-center-button-text` (local session store) |
| Surface | Convert primary action strip (New TAC / Convert / Download) via shared `Button` |
| Journeys touched | Convert primary path (tests only — not UI copy) |
| Status | closed |

## Desired change

Labels and icons in Convert toolbar buttons sit vertically and horizontally centered in the control. Fix the shared button base so outline and primary variants match; do not invent a new design system.

## Acceptance

- [x] Shared `Button` size `default` uses fixed height + flex centering without vertical padding that crowds the line box.
- [x] Default size classes include `items-center` and `justify-center` (existing flex pattern).
- [x] Convert strip buttons (New TAC / Convert / Download) inherit the shared fix.

## Must not break

- Existing button variants (`default`, `outline`, `destructive`, …) and sizes (`sm`, `lg`, `icon`).
- Convert primary-action labels and `data-testid`s.
- Sibling FE edits on feature-specific files — prefer shared `ui/button` only.

## Style-guide impact

Norm to append ([Corpus: ui-style]):

> Shared `Button` default size: fixed height + flex center; no vertical padding that fights the line box (labels/icons stay optically centered).

Target section: Layout / density

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/app/components/ui/button.test.tsx` |
| Red date | 2026-10-29 |
| Green date | 2026-10-29 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-29 | Intake: center Convert toolbar labels; shared Button suspected. |
| 2026-10-29 | Root cause: size `default` uses `h-9` + `py-2` + `border` while `text-sm` line-height needs ~20px; content box shrinks and labels look bottom-heavy. `sm`/`lg` already omit vertical padding. |
| 2026-10-29 | Fix: drop `py-2` from default size; keep `inline-flex items-center justify-center` + `h-9`. |

## Fix

- `apps/frontend/src/app/components/ui/button.tsx` — remove `py-2` from size `default`.
- `apps/frontend/src/app/components/ui/button.test.tsx` — assert flex center classes and absence of `py-2`.
- `docs/ui-style-guide.md` — changelog row for this UX id.

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [x] Session closed / HANDOFF written
