# UX-2026-10-29-downloads-file-mgmt

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-29-downloads-file-mgmt` |
| Session | `UX-downloads-file-mgmt` (local session store) |
| Surface | Convert Results drawer — Downloads vs IWXXM tabs |
| Journeys touched | Convert results drawer (tests/docs only — not UI copy) |
| Status | closed |

## Desired change

Downloads should only list converted files for manage actions (download / copy / remove / zip). Source TAC, full validation notes, and IWXXM XML must not live in Downloads. The IWXXM tab always shows the conversion result (preview XML), including after a hard convert and when the operator picks a file from Downloads.

## Acceptance

- [x] Downloads panel has no “Source TAC” region and no inline converted XML dump
- [x] After convert, IWXXM tab shows the converted XML in the Live IWXXM preview
- [x] Choosing a file in Downloads updates the IWXXM preview to that file’s XML (and switches to IWXXM)
- [x] Download / Copy / Remove / Download all as ZIP still work; publish-blocked still disables Download

## Must not break

- Auto-open Results drawer on first convert; default tab remains IWXXM
- Console / Decoder / Map tabs
- Soft-preview / soft-fail preview badges and failed-span cues
- Calm convert empty affordances and primary Convert path

## Style-guide impact

Norm to append:

> Results → Downloads is file management only (title, status chip, download/copy/remove). Conversion XML and Source TAC belong on Results → IWXXM (and the editor), not in Downloads.

Target section in `[Corpus: ui-style]`: Layout / density

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/app/components/FileConverter.test.tsx` (`UX-2026-10-29-downloads-file-mgmt`) |
| Red date | 2026-10-29 |
| Green date | 2026-10-29 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-29 | Screenshots: Downloads embeds ResultCard (status, notes, Source TAC, XML); IWXXM already has Live IWXXM. Hard convert only set `previewXml` for soft-preview paths. |
| 2026-10-29 | Slimmed Downloads to file rows; moved `ConvertResultStatus` onto IWXXM; always set `previewXml` after hard convert; Downloads row click focuses IWXXM. |

## Fix

- `FileConverter.tsx`: Downloads manage-only rows; IWXXM hosts status + preview; `focusConvertedForPreview`; hard convert always fills preview
- Tests updated for missing Source TAC in Downloads; new UX describe
- Style-guide changelog row appended

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [x] Session closed / HANDOFF written
