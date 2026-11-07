# UX-2026-11-07-convert-chrome-polish

| Field | Value |
|-------|--------|
| Id | `UX-2026-11-07-convert-chrome-polish` |
| Session | `UX-convert-chrome-polish` (local session store) |
| Surface | Convert empty chrome / toolbar / Results console / operator footer |
| Journeys touched | Convert primary path (tests/docs only — not UI copy) |
| Status | fixed |

## Desired change

1. Drop the marketing empty hero (`convert-empty-hero`); always show the same bordered converter chrome as the filled TAC state (`convert-body` + toolbar).
2. Move Settings cog to the rightmost side of `convert-chrome-toolbar`.
3. Keep product type always visible on the toolbar (promote out of settings-only).
4. Icon toolbar controls (Settings cog and peers): slow-fade hover alt text in a small card (not native `title` alone).
5. Remove `workbench-console` and `lint-issue-catalog-panel` from Results chrome entirely.
6. Operator footer spans the full bottom; collapsible to a right-edge clickable reveal bar.
7. Preferences `output-extension` select: nudge the dropdown caret slightly left.

**Deferred:** map as a separate page (evolve); blank map on main (hotfix).

## Acceptance

- [x] Empty TAC still shows bordered converter chrome; no `convert-empty-hero`
- [x] Product type control present in toolbar without opening Settings
- [x] Settings cog is rightmost in `convert-chrome-toolbar`
- [x] Hover card fades in slowly on Settings (and peer icon controls)
- [x] No `workbench-console` / `lint-issue-catalog-panel` in the DOM on Results
- [x] Footer is full-bleed bottom; collapses to a right-edge handle
- [x] Output-extension caret is optically left of the prior default

## Must not break

- Convert, examples, download, advanced Settings options
- Live map tab (kept; page split out of scope)
- No planning ids in operator-facing strings

## Style-guide impact

Norm to append:

> Convert empty state uses the same bordered converter chrome as the filled state (no marketing hero). Product type stays on the toolbar. Settings cog is rightmost; icon affordances use slow-fade hover cards. Operator footer is full-bleed and collapsible to a right-edge handle. Conversion/validation log and lint catalog panels are removed from the workbench Results chrome.

Target section in `[Corpus: ui-style]`: Layout / Motion (supersedes inline-console framing from UX-2026-10-31 for these panels).

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest + Playwright |
| Path | `apps/frontend/src/app/components/UX-2026-11-07-convert-chrome-polish.test.tsx`; `apps/e2e/ux-2026-11-07-convert-chrome-polish.e2e.spec.ts` |
| Red date | 2026-11-07 |
| Green date | 2026-11-07 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-11-07 | Intake locked: chrome polish only; map page → evolve; blank map → ignore |
| 2026-11-07 | Implemented: empty chrome always on; product on toolbar; settings rightmost + hover card; drop console/catalog; full-bleed collapsible footer; caret nudge |

## Fix

- `deriveCalmConvertUi` never shows marketing empty hero
- `FileConverter` toolbar: product select left, Settings cog right; remove `WorkbenchConsole`
- `OperatorFooter` fixed full-bleed + collapse/reveal
- `ConvertSettingsCog` slow-fade hover card; Preferences output-extension custom caret

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [ ] Session closed / HANDOFF written
