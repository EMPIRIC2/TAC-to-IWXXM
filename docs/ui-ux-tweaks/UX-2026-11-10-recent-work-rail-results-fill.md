# UX-2026-11-10-recent-work-rail-results-fill

| Field | Value |
|-------|--------|
| Id | `UX-2026-11-10-recent-work-rail-results-fill` |
| Session | `UX-recent-work-rail-results-fill` (local session store) |
| Surface | Convert workbench — Recent work aside + Results IWXXM / Decoder |
| Journeys touched | UJ-088 / UJ-089 (tests/docs only — not UI copy) |
| Status | closed |

## Desired change

1. **Recent work:** Collapsed state becomes a sticky ~½″ vertical rail on the
   right that stays with the viewport and spans the workbench column up to the
   primary action strip (Download latest / Convert / New TAC). Expanded restores
   the 280px panel; collapsed lets convert-body and Results reclaim width.
2. **Results IWXXM + Decoder:** By default fill the Results drawer body height
   with one scroll experience — no squat `max-h-80` / `max-h-96` clamps nesting
   a second scrollport inside `convert-results-drawer-body`.

## Acceptance

- [x] Collapsed Recent work renders `data-testid="recent-work-expand"` as a thin
      vertical sticky rail (~`w-12` / 48px), not a full-width horizontal chip
- [x] Collapsed workbench grid uses a slim right column; expanded keeps 280px
- [x] Rail remains sticky while scrolling (stays with the operator’s view)
- [x] IWXXM preview default has no squat `max-h-80`; fills parent (`h-full`)
- [x] Decoder / decode-pane keep fill-without-squat (no `max-h-80` / `max-h-96`)
- [x] Expand preview may still grow past the drawer; collapse returns to fill
      (not squat)

## Must not break

- Results Hide/Show, tab strip, vertical resize handle
- My METARs / session select when expanded
- Auto-collapse while editing TAC / opening Examples
- No planning ids in operator-facing copy

## Style-guide impact

Norms appended ([Corpus: ui-style]):

> Collapsed Recent work is a sticky ~½″ vertical rail on the right spanning the
> workbench up to the primary action strip; expand restores the 280px panel and
> main column reclaims width when collapsed.

> Results IWXXM preview fills the drawer body by default (no squat max-height);
> Expand may grow further; Collapse returns to fill.

Target section in `[Corpus: ui-style]`: Layout / density

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/app/components/WorkHistorySidebar.test.tsx`, `apps/frontend/src/app/components/IwxxmPreviewPane.test.tsx`, `apps/frontend/src/app/components/FileConverter.test.tsx`, `apps/frontend/src/app/components/DecodePanel.test.tsx` |
| Red date | 2026-11-10 |
| Green date | 2026-11-10 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-11-10 | Intake: sticky vertical rail to Download latest strip; IWXXM+Decoder single scroll fill. |
| 2026-11-10 | Red: rail still horizontal `w-full`; IWXXM default `max-h-80`; grid always 280px. |
| 2026-11-10 | Green: sticky `w-12` rail; grid `3rem` when collapsed; IWXXM `h-full` default; decode overflow single scrollport. |

## Fix

- `WorkHistorySidebar.tsx` — collapsed = sticky vertical ~½″ rail with vertical label
- `FileConverter.tsx` — grid / aside width follow `recentWorkCollapsed`; iwxxm + decode fill chain
- `IwxxmPreviewPane.tsx` — default fill (`h-full`); Expand grows; Collapse returns to fill
- `DecodePanel.tsx` — pinned outer `overflow-hidden` (scroll in body only)
- Vitest + `[Corpus: ui-style]` changelog / Layout norms

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [x] Session closed / HANDOFF written
