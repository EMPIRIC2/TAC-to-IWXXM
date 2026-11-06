# UX-2026-10-31-drop-console-chrome

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-31-drop-console-chrome` |
| Session | `UX-drop-console-chrome` (local session store) |
| Surface | Results → Console panel (`WorkbenchConsole`) in the operator workbench |
| Journeys touched | UJ-017 (tests/docs only — not UI copy) |
| Status | fixed |

## Desired change

The operator workbench wrapped the conversion/validation messages and the Lint issue
catalog inside a collapsible "Console" panel: a bordered shell with a terminal icon, a
**Console (N)** heading, a collapse chevron, and a **Clear log** control. The shell framed
the real content and hid the log behind a toggle by default.

Drop the Console chrome. Promote the content it framed — the conversion/validation log
lines and the Lint issue catalog — so they read directly without a "Console" shell or
heading. Keep **Clear log** only as a small control (no Console label), and keep the log
and lint catalog fully usable.

## Acceptance

- [x] No "Console" heading / label and no collapse toggle on the panel.
- [x] The conversion/validation log lines render by default (not hidden behind a toggle).
- [x] The Lint issue catalog remains present and openable.
- [x] **Clear log** remains available (small control, no Console wording) and still clears.
- [x] Log-code tooltips, Issue details, and terminator quick-fix actions still work.

## Must not break

- Issue/conversion log lines and their code tooltips.
- Lint issue catalog link / list and tag filter.
- Issue details drawer (`IssueDetailDialog`).
- Recent work sidebar (unrelated; not touched).
- No `EV-` / `UJ-` / `ADR-` / `docs/…` strings in operator-facing copy.

## Style-guide impact

Norm to append:

> Operator log surfaces (conversion/validation log + Lint issue catalog) render inline —
> no collapsible "Console" shell/heading framing them. A **Clear log** affordance may
> remain as a small standalone control without a "Console" label.

Target section in `[Corpus: ui-style]`: Layout.

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/app/components/WorkbenchConsole.no-console-chrome.test.tsx` |
| Red date | 2026-10-31 |
| Green date | 2026-10-31 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-31 | Located chrome in `WorkbenchConsole.tsx` header row (Terminal icon + `Console` + count + collapse toggle) wrapping a gray bordered `<section>`; lines gated behind `open` state (default collapsed). |
| 2026-10-31 | Wrote red Vitest regression asserting no `Console` heading / toggle and lines visible by default; confirmed red on pre-change component. |
| 2026-10-31 | Removed header/toggle/shell; lines always render; Clear log kept as small standalone control; lint catalog unchanged. Regression green. |

## Fix

Files / approach:

- `apps/frontend/src/app/components/WorkbenchConsole.tsx` — remove the collapsible header
  (chevron + terminal icon + "Console" + count), drop the `open` collapse state so the log
  lines always render, remove the gray "console shell" border/background framing, and keep
  **Clear log** as a small right-aligned control. Accessible region name changed from
  "Workbench console" to "Conversion and validation log". The Lint issue catalog panel and
  Issue details dialog are unchanged.
- `apps/frontend/src/app/components/WorkbenchConsole.test.tsx` — update legacy assertions
  that clicked the removed toggle / read the removed header count.
- `apps/frontend/src/app/components/FileConverter.test.tsx` — drop clicks on the removed
  `workbench-console-toggle` (lines now render by default).

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added
- [x] No planning ids in operator-facing strings
- [ ] Session closed / HANDOFF written
