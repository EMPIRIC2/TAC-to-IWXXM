# UX-2026-10-29-examples-bar-above-tac

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-29-examples-bar-above-tac` |
| Session | `UX-examples-bar-above-tac` (local session store) |
| Surface | Convert live chrome — catalog Examples (`GoldenExamplesSelect`) vs TAC editor |
| Journeys touched | F7.g golden examples / UJ-088 empty chips (tests/docs only — not UI copy) |
| Status | closed |

## Desired change

Catalog Examples sat in the Settings product/profile panel (Product type / Profile /
Customize each step). Move that control into a compact horizontal bar immediately above
the TAC editor. Keep one place only — remove from the settings sidebar. Empty-state product
chips (sibling one-interface tweak) stay; this moves the full catalog select. [Corpus: ui-style]

## Acceptance

- [x] `convert-examples-bar` holds `examples-select` immediately above the TAC editor
      (inside `live-convert-panes`, before `tac-editor`).
- [x] `product-profile-bar` / Settings dialog no longer contain `examples-select`.
- [x] Choosing an example still loads TAC into the editor (existing golden-example path).
- [x] Validate IWXXM mode still omits Examples.
- [x] No planning ids in operator-facing strings.

## Must not break

- Golden example load, demo banner, product/input-mode switches.
- Empty-state example chips inside the convert card (one-interface examples).
- Product type, Profile Change, Customize each step in Settings.
- Soft-preview / live IWXXM / convert primary path.

## Style-guide impact

Norm appended ([Corpus: ui-style] Layout / density):

> Convert catalog Examples sit in a compact bar above the TAC editor — not inside the Settings product/profile panel.

Target section: Layout / density

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/app/components/FileConverter.test.tsx` (examples bar placement) |
| Red date | 2026-10-29 |
| Green date | 2026-10-29 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-29 | Intake APPROVED; Spec→Build OPEN. Screenshot: Examples under Product type / Profile in Settings overlay. Sibling closed empty-state chips in-card; this relocates catalog `GoldenExamplesSelect`. |
| 2026-10-29 | Red: missing `convert-examples-bar`. Green after moving select out of `product-profile-bar` into bar above `tac-editor` in `live-convert-panes`. Settings blurb no longer lists examples. |

## Intake defaults (locked)

| Probe | Choice |
|-------|--------|
| Desired change | Layout / density — Examples bar above TAC |
| Surface | Convert / workbench primary path |
| Acceptance | Agent AC above |
| Must-not-break | Example load; empty chips; Settings product/profile |
| Style norm | Append one-line changelog row |
| Test kind | Vitest |
| Proceed | Documenting → build after gate open |

## Fix

- `FileConverter.tsx`: remove `GoldenExamplesSelect` from `product-profile-bar`; render
  `data-testid="convert-examples-bar"` with the same select above `TacEditor` in
  `live-convert-panes` (skipped for Validate IWXXM).
- `ConvertSettingsCog.tsx`: drop “examples” from the Settings description.
- `FileConverter.test.tsx`: placement regression (bar contains select; Settings/profile
  bar do not; document order before `tac-editor`).
- `docs/ui-style-guide.md`: Layout bullet + Changelog of norms row.

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [x] Session closed / HANDOFF written
