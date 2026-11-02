# UX-2026-11-02-sticky-results-header

| Field            | Value                                                  |
| ---------------- | ------------------------------------------------------ |
| Id               | `UX-2026-11-02-sticky-results-header`                  |
| Session          | `UX-sticky-results-header` (local session store)       |
| Surface          | Convert Results drawer chrome (`ConvertResultsDrawer`) |
| Journeys touched | UJ-089 (tests/docs only — not UI copy)                 |
| Status           | fixed                                                  |

## Desired change

While scrolling Results panel content (the panel’s right scrollbar), keep the
**Results** title and **Hide** control visible at the top of the panel. Also keep
the IWXXM / Console / Decoder / Map / Downloads tab strip sticky under that row
when it fits the existing shell without a redesign.

## Acceptance

- [x] Results title + Hide remain visible while the drawer body scrolls
- [x] Tab strip remains visible under the header while body content scrolls
- [x] Vitest asserts sticky chrome / non-scrolling container structure
- [x] Tab switch, Hide/Show, Map and Downloads panel content still work

## Must not break

- Tab switching among IWXXM / Console / Decoder / Map / Downloads
- Hide / Show toggle and collapsed chrome
- Map and Downloads tab bodies
- Vertical resize handle
- No planning ids in operator-facing copy

## Style-guide impact

Norm to append:

> Results drawer: title + Hide and the results tab strip stay pinned above the
> scrolling tab body (chrome outside the overflow scrollport).

Target section in `[Corpus: ui-style]`: Layout / density

## Regression test

| Field      | Value                                                            |
| ---------- | ---------------------------------------------------------------- |
| Kind       | Vitest                                                           |
| Path       | `apps/frontend/src/app/components/ConvertResultsDrawer.test.tsx` |
| Red date   | 2026-11-02                                                       |
| Green date | 2026-11-02                                                       |

## Change log (investigation)

| When       | Note                                                                                                                                |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| 2026-11-02 | Intake locked; shell is `ConvertResultsDrawer` — header already outside body; tabs previously scrolled inside `overflow-auto` body. |
| 2026-11-02 | Sibling session UX-cite-live-map-provider may touch Results/map; prefer shared shell edits carefully.                               |
| 2026-11-02 | Red Vitest (missing chrome/shell testids; tablist inside overflow body).                                                            |
| 2026-11-02 | Structural sticky: chrome + tab strip outside overflow-auto; tests green.                                                           |

## Fix

Files / approach:

- `ConvertResultsDrawer.tsx`: pin title+Hide (`convert-results-drawer-chrome`) and
  tab strip (`convert-results-drawer-tab-chrome`) outside the `overflow-auto` body;
  height applies to `convert-results-drawer-shell` flex column; only tab panels scroll.
- Vitest: asserts chrome/tablist are not inside the scrolling body.
- Style-guide Layout + Changelog of norms row.

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [ ] Session closed / HANDOFF written
