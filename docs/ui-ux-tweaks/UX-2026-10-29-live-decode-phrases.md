# UX-2026-10-29-live-decode-phrases

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-29-live-decode-phrases` |
| Session | `UX-live-decode-phrases` (local session store) |
| Surface | Results → Decoder → Live decode (SIGMET and other products via `DecodePanel`) |
| Journeys touched | UJ-015 / F9 live decode (tests/docs only — not UI copy) |
| Status | closed |

## Desired change

Live decode currently lists one Code \| Explanation row per TAC token. Adjacent
tokens that already form a meteorological phrase (observation time and place,
CB top / flight level, tropical cyclone name, FIR name + FIR, movement) should
render as fewer natural-language list items. Wire `decode_tac` response keys stay
unchanged — FE display composition only. [Corpus: product §F9] [Corpus: ui-style]

## Acceptance

- [x] Adjacent SIGMET-style token runs render as phrase rows (fewer rows than
      raw segment count for the sample OBS / CB TOP / TC / FIR / MOV groups).
- [x] Phrase explanation is readable English (not “Token → gloss” pairs).
- [x] Phrase Code column still shows the joined TAC codes so tokens stay findable.
- [x] Click / highlight still maps to a contiguous character span
      (`start` of first member → `end` of last member).
- [x] Ungroupable tokens (and METAR/SPECI rows that do not match phrase patterns)
      keep one-row-per-segment behavior.
- [x] Vitest covers the compositor helper and DecodePanel phrase rendering.

## Proposed before → after (SIGMET sample)

| Before (atomic rows) | After (phrase row) |
|----------------------|--------------------|
| `TC` → Tropical cyclone; `IN-FA` → Tropical cyclone (IN-FA) | `TC IN-FA` → Tropical cyclone IN-FA |
| `OBS` → Observed; `AT` → At …; `1800Z` → Time 18:00 UTC; `N1540` → Latitude …; `E15620` → Longitude … | `OBS AT 1800Z N1540 E15620` → Observed at 18:00 UTC near 15°40′N 156°20′E |
| `CB` → Cumulonimbus; `TOP` → Top; `FL510` → Flight level 510 | `CB TOP FL510` → Cumulonimbus top at flight level 510 |
| `FUKUOKA` → FIR name …; `FIR` → Flight information region | `FUKUOKA FIR` → FUKUOKA flight information region |
| `MOV` → Moving; `W` → Movement direction (West); `15KT` → Speed 15 kt | `MOV W 15KT` → Moving west at 15 kt |

## Must not break

- Public `decode_tac` keys / shapes (no nested `children` or `role` on the wire).
- Plain-language summary block, residuals, selection API (`onSelect` span).
- Sibling polish surfaces (TAC issue severity, Issue details wrap, EV scrub).
- No planning ids in operator-visible strings.

## Style-guide impact

Norm appended ([Corpus: ui-style] Layout / Copy):

> Live decode may group adjacent TAC tokens into natural-language phrase rows
> (joined Code, one Explanation); do not change the decode wire contract.

Target section: Changelog of norms

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/utils/groupDecodeSegments.test.ts`; `apps/frontend/src/app/components/DecodePanel.test.tsx` (phrase rows) |
| Red date | 2026-10-29 (phrase assertions fail without compositor) |
| Green date | 2026-10-29 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-29 | Intake: Live decode SIGMET atomic glossary rows; FE-only grouping preferred. |
| 2026-10-29 | Sample decode confirms OBS/AT/time/lat/lon, CB/TOP/FL, TC+name, FIR name+FIR, MOV runs. |
| 2026-10-29 | Spec→Build open; helper + DecodePanel wired; Vitest green. |

## Fix

- `apps/frontend/src/utils/groupDecodeSegments.ts` — pattern-match adjacent segments.
- `DecodePanel.tsx` — render `groupDecodeSegments(segments)`; selection uses span overlap.
- Vitest: `groupDecodeSegments.test.ts` + DecodePanel phrase-row case.

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [x] Session closed / HANDOFF written

## Implementing verify

| Angle | Verdict | Note |
|-------|---------|------|
| lint-format-typecheck | PASS | Pack `make lint`; touch-set prettier/eslint/tsc also PASS |
| tests | PASS | Vitest phrases suite green; full `make test-fast` FAIL is unrelated `tac-validate` coverage (94.59%) |
| security | PASS | wired |
| human-readable | PASS | |
