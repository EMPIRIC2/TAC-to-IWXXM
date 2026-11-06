# UX-2026-10-29-drop-groups-chips

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-29-drop-groups-chips` |
| Session | `UX-drop-groups-chips` (local session store) |
| Surface | Convert / workbench TAC notes (under the TAC editor, above the notes summary) |
| Journeys touched | Convert primary path (tests only — not UI copy) |
| Status | closed |

## Desired change

Remove the horizontal **Groups** chip strip (`data-testid="tac-group-chips"`) from the Convert TAC notes / soft-preview area. No empty “Groups” label left behind. Decoder-tab natural-language grouping stays (sibling work).

## Acceptance

- [x] After live decode returns segments, `tac-group-chips` is not in the document.
- [x] The “Groups” heading and “Recognised groups” chip row are gone.
- [x] TAC notes summary (`tac-lint-summary`) and issue jumps still render.
- [x] Decode data / `selectedTrace` for Decoder and editor highlights may remain; only the chip strip UI is removed.

## Must not break

- Decoder tab / `DecodePanel` selection and residuals.
- TAC lint summary and jump list.
- Live decode / convert API wire keys (`decode_tac` unchanged).
- Sibling polish on issue severity, Issue details wrap, EV scrub.

## Style-guide impact

Norm appended ([Corpus: ui-style]):

> Convert TAC notes: no Groups chip strip under the editor; group selection lives in Decoder, not as horizontal chips above the notes summary.

Target section: Layout / density

## Regression test

| Field | Value |
|-------|-------|
| Kind | Vitest |
| Path | `apps/frontend/src/app/components/FileConverter.test.tsx` (`omits the Groups chip strip under TAC notes after live decode`) |
| Red date | 2026-10-29 |
| Green date | 2026-10-29 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-29 | AskQuestion unavailable; locked default from operator “Drop these groups” + skill recommended path. Spec→Build opened. |
| 2026-10-29 | Strip lived only in `FileConverter.tsx` (`tac-group-chips`). Decoder uses `DecodePanel` separately — left alone. |
| 2026-10-29 | Red: `queryByTestId('tac-group-chips')` still found the strip. Green after deleting the render block. |
| 2026-10-29 | Mid-session race briefly stripped unrelated mass-ingest from FileConverter; restored from HEAD and re-applied Groups-only delete. Spec→Build open; session closed / HANDOFF written. No commit. |

## Intake defaults (locked)

| Probe | Choice |
|-------|--------|
| Desired change | Layout / density — drop Groups chips |
| Surface | Convert / workbench primary path |
| Acceptance | Agent AC above |
| Must-not-break | Decoder, TAC notes summary/jumps, decode wire |
| Style norm | Append one-line changelog row |
| Test kind | Vitest |
| Proceed | Documenting → build after gate open |

## Fix

Removed the `tac-group-chips` block under the TAC editor in `FileConverter.tsx`. Kept `decodeSegments` / `selectedTrace` / `DecodePanel` wiring. Updated the prior Groups selection Vitest into an absence assertion; style-guide Layout + Changelog row for this UX id.

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [x] Session closed / HANDOFF written
