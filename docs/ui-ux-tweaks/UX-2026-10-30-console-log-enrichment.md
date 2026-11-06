# UX-2026-10-30-console-log-enrichment

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-30-console-log-enrichment` |
| Session | `UX-console-log-enrichment` (local session store) |
| Surface | Results → Console → Conversion / validation log Notes |
| Journeys touched | Convert / soft-preview console notes (docs/tests only — not UI copy) |
| Status | closed |

## Desired change

Sparse Notes cards (title + Code only) should match the UNKNOWN_ICAO pattern: a
plain-language reason/consequence sentence under the title, with acronym glosses
(RVR, NSW, and similar) when relevant. Prefer existing `hint` and catalog
`message_template`. Do not redesign the issue registry.

## Acceptance

- [x] `RVR_PRESENT` Note shows title + reason/consequence text that glosses RVR (Runway Visual Range)
- [x] `NSW_PRESENT` Note shows title + reason/consequence text that glosses NSW (No Significant Weather / nil significant weather)
- [x] Catalog-backed enrichment works for other sparse coded rows when `hint` is missing
- [x] Explicit `hint` (e.g. UNKNOWN_ICAO) is unchanged
- [x] No planning ids (`EV-`, `UJ-`, `ADR-`, `docs/…`) in operator-visible log copy
- [x] Vitest regression green

## Must not break

- Convert / decode primary path and other Results tabs (IWXXM, Decoder, Map, Downloads)
- Calm empty / filtered log states
- Catalog jump buttons and Issue details dialog

## Style-guide impact

Norm appended:

> Conversion / validation log Notes: when a coded issue has no `hint`, show a scrubbed catalog reason/consequence line (acronym gloss when the template provides it); never leave title+Code-only for catalogued codes.

Target section in `[Corpus: ui-style]`: Copy / tone

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/utils/conversionLogEnrichment.test.ts`; `apps/frontend/src/app/components/ErrorLogPanel.test.tsx` |
| Red date | 2026-10-30 |
| Green date | 2026-10-30 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-30 | Intake defaults applied (AskQuestion unavailable). Lint path `_append_pre_convert_lint_issues` omits `hint`; UNKNOWN_ICAO has backend `suggestion`→`hint`. |
| 2026-10-30 | Micro FE: `resolveConversionLogHint` — explicit hint → cleaned catalog template → RVR/NSW fallbacks. Wired in `ErrorLogPanel`. |

## Fix

- `apps/frontend/src/utils/conversionLogEnrichment.ts` (+ unit tests)
- `apps/frontend/src/app/components/ErrorLogPanel.tsx` — display derived hint; pass into Issue details
- `docs/ui-style-guide.md` — Copy/tone bullet + Changelog of norms row

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [x] Session closed / HANDOFF written
