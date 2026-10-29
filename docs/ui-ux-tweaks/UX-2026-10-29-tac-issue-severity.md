# UX-2026-10-29-tac-issue-severity

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-29-tac-issue-severity` |
| Session | `UX-tac-severity-tooltip` (local session store) |
| Surface | Convert workbench TAC notes / issues list (`TacLintJumps`) |
| Journeys touched | Convert primary path (tests only — not UI copy) |
| Status | closed |

## Desired change

Error rows in the TAC notes list stand out from Note / Warning rows at a glance.
Use existing destructive tokens: danger text, semibold weight, and a light destructive tint on the row. Do not change API or catalog issue message strings.

Tooltip plain-language / planning-id scrub is out of scope for this log (siblings).

## Acceptance

- [x] An `error` severity jump button uses destructive text color and semibold weight (existing theme tokens).
- [x] An `error` row has a light destructive background tint; Note / Warning rows do not.
- [x] Accessible name still includes the severity label + message (e.g. `Error: …`); message text is unchanged from the issue payload (display may scrub planning ids via shared guard — no API rewrite).
- [x] Severity is not conveyed by color alone (label text remains).

## Must not break

- Jump select / `aria-pressed` behavior.
- Empty list still renders nothing.
- Operator-visible message strings from the API (no rewrite at the API/catalog source).
- Sibling Issue details wrap/link work.

## Style-guide impact

Norm appended ([Corpus: ui-style]):

> TAC notes list: error rows use destructive text + semibold and a light destructive tint; Note / Warning stay default weight and no tint.

Target section: Tokens / Accessibility

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/app/components/TacLintJumps.test.tsx` |
| Red date | 2026-10-29 |
| Green date | 2026-10-29 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-29 | Intake closed: danger text + semibold + light tint; display styling only. |
| 2026-10-29 | Red Vitest asserted destructive classes; green after `lintJumpButtonClass`. |
| 2026-10-29 | Sibling added display-layer `scrubInternalDocRefs` on jump labels; left in place. Tooltip polish deferred. |

## Fix

- `apps/frontend/src/app/components/TacLintJumps.tsx` — error rows: `text-destructive font-semibold bg-destructive/10` (dark `/20`); notes/warnings keep gray defaults.
- `apps/frontend/src/app/components/TacLintJumps.test.tsx` — severity class assertions.
- `docs/ui-style-guide.md` Changelog of norms row.

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings added by this tweak
- [x] Session closed / HANDOFF written
