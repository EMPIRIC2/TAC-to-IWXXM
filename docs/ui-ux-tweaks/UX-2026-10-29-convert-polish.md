# UX-2026-10-29-convert-polish

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-29-convert-polish` |
| Session | `UX-session-convert-polish` (local session store) |
| Surface | Convert workbench / status strip / TAC input summary / profile help copy |
| Journeys touched | UJ-088, UJ-089 (tests/docs only — not UI copy) |
| Status | closed |

## Desired change

Frame operator-visible TAC INFO / severity feedback as **notes on TAC input** (awareness),
not “TAC lint …” / “lint failures.” Merged calm / declutter Convert shell remains on `stage`
(#1469 family). Empty-state affordances unify (`CalmConvertEmptyAffordances` wire) is
deferred — see HANDOFF leftovers.

## Acceptance

- [x] Operator-visible status / summary / jump labels use “notes on TAC input” / “TAC input: …” (not “TAC lint: …”).
- [x] Profile / library help copy says “TAC input checks” where it previously said “TAC lint.”
- [x] Vitest covers status strip, summary labels, and FileConverter summary string.
- [ ] FileConverter empty path uses shared affordances inside one shell (leftover — HANDOFF).

## Must not break

- Convert primary path, Results drawer tabs, live assist.
- EV-048 / no planning ids in operator copy.
- Do not wrap SIGMET hyphenated TC decode (`IN-FA`) as a UX tweak.

## Style-guide impact

Norm to append ([Corpus: ui-style]):

> Frame TAC INFO / severity feedback as notes on TAC input (not “lint failures” / “TAC lint: …”).

Target section: Copy

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/utils/liveConvertTrace.test.ts`; `LiveConvertStatusStrip.test.tsx`; `FileConverter.test.tsx` (TAC input notes) |
| Red date | 2026-10-29 (prior “TAC lint” assertions) |
| Green date | 2026-10-29 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-29 | Inventory: notes-copy dirty on worktree; declutter already on `stage` via #1469. |
| 2026-10-29 | `CalmConvertEmptyAffordances` left unwired — excluded from this PR for a coherent green ship. |

## Fix

- `liveConvertTrace.ts`, `LiveConvertStatusStrip.tsx`, `TacLintJumps.tsx`, `FileConverter.tsx` (summary), `conversionProfilesCopy.ts`, matching tests.
- Already on `stage`: Convert declutter / calm chrome (#1466–#1469).

## Close checklist

- [x] Regression green for notes-copy suite
- [x] Style-guide changelog row added
- [x] No planning ids in operator-facing strings
- [x] Empty-affordances wire deferred (HANDOFF)
