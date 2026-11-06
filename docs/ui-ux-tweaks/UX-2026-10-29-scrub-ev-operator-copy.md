# UX-2026-10-29-scrub-ev-operator-copy

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-29-scrub-ev-operator-copy` |
| Session | `UX-scrub-ev-operator-copy` (local session store) |
| Surface | TAC lint issue list + Issue details (message, tags) |
| Journeys touched | Lint / workbench issue detail (docs/tests only — not UI copy) |
| Status | closed |

## Desired change

Operators must not see evolve / planning vocabulary on lint surfaces: `EV-…`, `TC-EV…`, GitHub `#NNN` planning tickets, or tags like `ev030`. Domain codes (`MISSING_TC_IDENTITY`) and product wording stay.

## Acceptance

- [x] Lint list / Issue details Message for TC SIGMET identity issues has no `#829`, `TC-EV030-004`, or `EV-` tokens
- [x] Issue details Tags omit `ev030` (and sibling `evNNN` evolve tags)
- [x] Vitest proves scrub / guard for those patterns on issue detail fields
- [x] Style-guide Changelog of norms row added

## Must not break

- Domain codes and severity labels
- Sibling polish (Error vs Note prevalence; Issue details wrap + Source hyperlink)
- Catalog attribution that already omits planning notes

## Style-guide impact

Norm appended:

> Lint issue list, Issue details, and tags show operator language only — never evolve ids, test ids, or ticket shorthand.

Target section in `[Corpus: ui-style]`: Copy

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest (+ pytest for emit path) |
| Path | `apps/frontend/src/utils/issueDetail.test.ts`, `internalDocRefGuard.test.ts`; `packages/tac-validate/tests/test_strip_research_refs.py`, `test_tc_ev_verify_005_research_tokens.py` |
| Red date | 2026-10-29 |
| Green date | 2026-10-29 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-29 | Leaks in `sigmet_airmet.py` messages (`#829 / TC-EV030-004`) and registry tags `ev030`; list renders raw `issue.message`. |
| 2026-10-29 | Default: scrub source + FE display filter / guard (no AskQuestion wait). |
| 2026-10-29 | Parent: prefer display-layer scrub; keep source clean as belt-and-suspenders. |

## Fix

**Display layer (primary):**

- `scrubInternalDocRefs` / `isPlanningEvolveTag` in `internalDocRefGuard.ts`
- `buildIssueDetail` scrubs message/rule/source/hint; drops `evNNN` tags
- List surfaces: `ErrorLogPanel`, `TacLintJumps`, `resultCard.assessResultCard`
- Catalog helpers: `formatCatalogEntryCopy`, `resolveLintIssueTooltip`; Workbench tag picker omits `evNNN`

**Source (secondary):**

- Clean TC SIGMET / NSC emit strings; drop `ev023`/`ev030`/`ev050` registry tags
- `_strip_research_refs` also strips planning tokens at emit
- `make catalog-regen` + mined `tac_validation_rules.yaml` + quality metrics regen

### Before → after (examples)

| Surface | Before | After |
|---------|--------|--------|
| Error / Message | `TC SIGMET missing cyclone identity (TC … PSN) - #829 / TC-EV030-004` | `TC SIGMET missing cyclone identity (TC … PSN)` |
| Tags | `tc, cyclone, sigmet, ev030` | `tc, cyclone, sigmet` |
| Info message | `… WI … OF TC CENTRE - #829 / TC-EV030-004` | `… WI … OF TC CENTRE` |

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [x] Session closed / HANDOFF written
