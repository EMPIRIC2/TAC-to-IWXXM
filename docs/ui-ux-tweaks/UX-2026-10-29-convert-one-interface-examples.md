# UX-2026-10-29-convert-one-interface-examples

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-29-convert-one-interface-examples` |
| Session | `UX-convert-one-interface-examples` (local session store) |
| Surface | Convert empty / calm state (`CalmConvertEmptyHero` + `CalmConvertEmptyAffordances`) |
| Journeys touched | UJ-088 / F21 public convert (tests/docs only — not UI copy) |
| Status | closed |

## Desired change

Convert empty state stacks the TAC card, then a distant **Try an example** pill row, then **Other tasks**. Fold example chips into the main convert surface as a bar above the TAC editor so empty Convert reads as one composition. Keep Other tasks in a tight secondary row under the card. Align with sibling catalog Examples bar (`convert-examples-bar` above TAC). [Corpus: ui-style] [Corpus: product §F21]

## Acceptance

- [x] Example chips render inside `convert-empty-card` in `convert-examples-bar` above the TAC editor.
- [x] Example chips are not a disconnected strip far below the card.
- [x] Other tasks stay under the hero, outside the card, with tighter spacing.
- [x] Chip click still loads the example; Other-task links still switch input mode.
- [x] No planning ids in operator-facing strings.

## Must not break

- Calm empty Convert primary CTA, browse, profile Change.
- Golden example load path / demo banner after chip click.
- Sibling `UX-2026-10-29-examples-bar-above-tac` catalog select bar (same `convert-examples-bar` id on live panes).
- Sibling Convert chrome polish (drop zone, footer, Mass Ingest, Groups).
- No new products or routes.

## Style-guide impact

Norm appended ([Corpus: ui-style] Layout / density):

> Convert empty state: example chips sit in a bar above the TAC editor inside the main convert card; Other tasks sit in one tight row under that card — not a separate far strip.

Target section: Layout / density

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/app/components/tcUxCalmConvert.test.tsx` (examples bar above TAC); `CalmConvertEmptyAffordances.test.tsx` |
| Red date | 2026-10-29 |
| Green date | 2026-10-29 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-29 | Intake defaults approved; Spec→Build open. Screenshot: chips + Other tasks below card with large gap (`gap-7` in hero). |
| 2026-10-29 | Moved chips into card via Affordances; then coordinated with sibling: prefer bar **above** TAC (`convert-examples-bar`), not between editor and Convert footer. |
| 2026-10-29 | Full `bin/verify` tests angle runs `make test` (long); scoped Vitest + lint PASS used for close. |

## Intake defaults (locked)

| Probe | Choice |
|-------|--------|
| Desired change | Layout / density — one Convert composition |
| Surface | Convert / workbench primary path |
| Acceptance | Agent AC above |
| Must-not-break | Empty CTA, examples load, other-task modes; sibling examples bar |
| Style norm | Append one-line changelog row |
| Test kind | Vitest |
| Proceed | Documenting → build after gate open |

## Fix

- `CalmConvertEmptyHero`: `convert-empty-card` order is examples bar → TAC children → drop/browse + Convert. Section gap `gap-7` → `gap-3`.
- `CalmConvertEmptyAffordances`: shared chip / Other tasks / profile markup; examples-only embed for the bar.
- Other tasks + profile remain outside the card under it.
- Style-guide Layout + Changelog row for this UX id.
- Compatible with sibling live-pane `convert-examples-bar` (catalog select).

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [x] Session closed / HANDOFF written
