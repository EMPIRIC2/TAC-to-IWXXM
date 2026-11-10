# UX-2026-11-10-live-decode-drawer-fill

| Field | Value |
|-------|--------|
| Id | `UX-2026-11-10-live-decode-drawer-fill` |
| Session | `UX-live-decode-drawer-fill` (local session store) |
| Surface | Convert Results → Decoder / pinned Live decode |
| Journeys touched | UJ-089 Results drawer (tests/docs only — not UI copy) |
| Status | closed |

## Desired change

Pinned Live decode sits short inside Results because of stacked `max-h-96` /
`max-h-80` clamps. Operators want the panel to fill the Results drawer body
height; long content should scroll inside the panel.

## Acceptance

- [x] Pinned `decode-panel` / `decode-pane` have no `max-h-80` / `max-h-96` squat clamps
- [x] Flex / `h-full` chain lets the panel occupy the drawer body height
- [x] Long content scrolls inside the panel body
- [x] Results chrome + tab strip remain outside the body

## Must not break

- Results tabs, Hide/Show, vertical resize
- IWXXM Expand/Collapse, Console, Map, Downloads
- Collapsible (non-pinned) DecodePanel elsewhere
- No planning ids in operator-facing copy

## Style-guide impact

Norm to append ([Corpus: ui-style]):

> Results Decoder tab: pinned Live decode fills the drawer body height; scroll inside the panel (no squat max-height clamp).

Target section in `[Corpus: ui-style]`: Layout / density

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/app/components/DecodePanel.test.tsx`, `apps/frontend/src/app/components/ConvertResultsDrawer.test.tsx` |
| Red date | 2026-11-10 |
| Green date | 2026-11-10 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-11-10 | Intake locked: stretch-to-fill (not Expand/Collapse). Clamps on `decode-pane` (`max-h-96`) and pinned `DecodePanel` (`max-h-80`). |
| 2026-11-10 | Red Vitest: pinned still `max-h-80`; drawer body lacked `flex flex-col` / TabsContent fill classes. |
| 2026-11-10 | Green: removed clamps; drawer body + active TabsContent + decode-pane + pinned panel use `h-full` / flex column chain. |

## Fix

- `DecodePanel.tsx` — pinned root `max-h-80` → `h-full`
- `FileConverter.tsx` — `decode-pane` `max-h-96` → `h-full`
- `ConvertResultsDrawer.tsx` — body `flex flex-col`; active `TabsContent` `flex h-full min-h-0 flex-col`
- Vitest coverage in `DecodePanel.test.tsx` + `ConvertResultsDrawer.test.tsx`
- `docs/ui-style-guide.md` Changelog of norms row

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [x] Session closed / HANDOFF written
