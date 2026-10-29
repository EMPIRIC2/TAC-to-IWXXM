# UX-2026-10-29-brand-tac-to-iwxxm

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-29-brand-tac-to-iwxxm` |
| Session | `UX-brand-tac-to-iwxxm` (local session store) |
| Surface | Login card header brand (`Login` h1) |
| Journeys touched | Optional sign-in chrome (F21; tests/docs only — not UI copy) |
| Status | closed |

## Desired change

Login header brand that currently reads **METAR Converter** (CSS `uppercase`
shows **METAR CONVERTER**) should read **TAC-to-IWXXM** exactly — product name
as given, no forced all-caps transform on that mark.

## Acceptance

- [x] Login `h1` text content is `TAC-to-IWXXM`.
- [x] Brand mark is not forced through CSS `uppercase` (so “to” stays lowercase).
- [x] Vitest asserts the new brand string; old “METAR Converter” assertion removed.
- [x] Subtitle “Optional sign-in for long-term work history” unchanged.
- [x] No planning ids in operator-facing strings.

## Must not break

- Login form controls, validation, and auth submit.
- Theme toggle / Display Mode chrome.
- Switch to register / forgot password flows.
- Do not rename storage keys, Register page title, or repo-wide historical “METAR Converter” strings outside this login brand mark.

## Style-guide impact

Norm to append ([Corpus: ui-style]):

> Login (and matching auth card) brand mark uses the product name **TAC-to-IWXXM** exactly; do not CSS-uppercase that mark.

Target section: Copy / tone

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/app/components/auth/Login.test.tsx` |
| Red date | 2026-10-29 |
| Green date | 2026-10-29 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-29 | Screenshot: bold METAR CONVERTER + subtitle on login card; source `Login.tsx` h1 with `uppercase`. |
| 2026-10-29 | Doc title on convert path already “TAC to IWXXM”; out of scope for this brand mark. |
| 2026-10-29 | Red Vitest: heading name TAC-to-IWXXM missing; uppercase still on h1. |
| 2026-10-29 | Fix: h1 text TAC-to-IWXXM; drop `uppercase` class. Login.test 12/12 green. |

## Fix

- `Login.tsx`: brand h1 → `TAC-to-IWXXM`; remove `uppercase` so casing stays exact.
- `Login.test.tsx`: assert h1 name + no `uppercase` class; keep subtitle assertion.
- `docs/ui-style-guide.md`: Changelog of norms row.

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [x] Session closed / HANDOFF written
