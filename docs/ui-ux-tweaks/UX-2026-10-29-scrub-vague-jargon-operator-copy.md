# UX-2026-10-29-scrub-vague-jargon-operator-copy

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-29-scrub-vague-jargon-operator-copy` |
| Session | `UX-scrub-vague-jargon-operator-copy` (local session store) |
| Surface | Operator lint messages, Issue details, tags, FE/OpenAPI planning guards |
| Journeys touched | Lint / workbench issue detail (docs/tests only — not UI copy) |
| Status | closed |

## Desired change

Operators must not see meaningless planning prefixes or vague filler on public surfaces:
feature shorthand (`F26`, `f26` tags), journey ids (`UJ-…`), research theme crumbs
(`theme V1`), or filler like `stuff`. Prefer concrete plain English. Keep grammatical
articles (`a` / `an` / `the`) and domain terms (METAR, SIGMET, TAC, IWXXM, ICAO).

## Acceptance

- [x] Lint / Issue details for VAA/TCA/SWXA/VONA messages have no `F26` / `F27` / `F28` / `F32` or `theme V1` / `theme T1` / `theme SX1`
- [x] Catalog tags omit compact feature ids (`f26`, `f32`, …) and lone theme tokens (`v1`, `t1`, `sx1`)
- [x] Shared FE guard detects / scrubs `UJ-…` and vague filler `stuff` (does not strip grammatical articles)
- [x] Vitest + pytest prove scrub / registry cleanliness
- [x] Style-guide Changelog of norms row added

## Must not break

- Domain codes, Annex cites (`A2-1`), severity labels
- Sibling EV scrub + severity / Source-link polish
- Readable English (no mass article deletion)

## Style-guide impact

Norm appended:

> Operator copy stays concrete: no feature/journey/theme shorthand (`F26`, `UJ-…`, `theme V1`) and no vague filler (`stuff`); keep normal English articles.

Target section in `[Corpus: ui-style]`: Copy

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest (+ pytest emit/registry) |
| Path | `apps/frontend/src/utils/internalDocRefGuard.test.ts`, `issueDetail.test.ts`; `packages/tac-validate/tests/test_strip_research_refs.py`, `test_tc_ev_verify_005_research_tokens.py` |
| Red date | 2026-10-29 |
| Green date | 2026-10-29 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-29 | Intake locked: do not mass-delete `a`/`an`/`the`; scrub jargon + vague filler only. |
| 2026-10-29 | Leaks: registry / emit strings `F26 theme V1`; tags `f26`/`v1`; FE guard missing `UJ-`. |
| 2026-10-29 | Extended shared FE/Python scrubbers; cleaned registry + product-rule emit strings; `make catalog-regen`. |

## Fix

**Display layer (shared scrubbers):**

- `internalDocRefGuard`: `UJ-`, `FnTheme` / `theme` crumbs, vague filler `stuff`; `isPlanningEvolveTag` also drops `f26` / `v1` / `sx1`-style tags
- `WorkbenchConsole` tag picker uses shared `isPlanningEvolveTag`
- OpenAPI / attribution note guards gain `UJ-`

**Source (belt-and-suspenders):**

- Clean VAA/TCA/SWXA/VONA/AIRMET emit + registry templates; drop planning tags
- `_strip_research_refs` strips Fn+theme, bare `F\d+`, `UJ-`, `stuff`
- `make catalog-regen`

### Before → after (examples)

| Surface | Before | After |
|---------|--------|--------|
| Message | `VAA forecast NO VA EXP - status NO_VOLCANIC_ASH_EXPECTED (F26 theme V1)` | `VAA forecast NO VA EXP - status NO_VOLCANIC_ASH_EXPECTED` |
| Rule | `VAA missing VOLCANO: template field - F26 theme V1 / A2-1` | `VAA missing VOLCANO: template field - A2-1` |
| Tags | `forecast, no_va_exp, vaa, v1, f26` | `forecast, no_va_exp, vaa` |
| Articles | *(unchanged)* `Paste the TAC into the editor` | `Paste the TAC into the editor` |

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [x] Session closed / HANDOFF written
