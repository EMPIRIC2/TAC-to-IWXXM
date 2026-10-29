# UX-2026-10-29-footer-links-horizontal

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-29-footer-links-horizontal` |
| Session | `UX-footer-links-horizontal` (local session store) |
| Surface | Public convert footer (`OperatorFooter`) — Privacy / Feedback / Terms |
| Journeys touched | Public app chrome (F21/F22; tests/docs only — not UI copy) |
| Status | closed |

## Desired change

Footer chrome links (Privacy settings, Feedback + Beta, Terms of service) sit in
one horizontal row instead of a vertical stack, with calm spacing or separators.
Beta badge stays next to Feedback. Destinations and copy stay as they are.

## Acceptance

- [x] Privacy settings, Feedback (+ Beta), and Terms of service share one horizontal
      flex row (`flex-row` + wrap on narrow viewports).
- [x] Beta badge remains adjacent to Feedback.
- [x] Vitest asserts the link group uses a horizontal layout class / role grouping.
- [x] Link labels, aria labels, and click handlers unchanged.

## Must not break

- Privacy settings / Terms dialog openers.
- Feedback dialog + Beta badge behavior.
- Footer blurb above the links; brand bar below stays untouched.
- No planning ids in operator-facing strings.

## Style-guide impact

Norm to append ([Corpus: ui-style]):

> Public footer chrome links sit in one horizontal row (wrap allowed); keep the Beta badge with Feedback.

Target section: Layout / density

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/app/components/OperatorFooter.test.tsx` |
| Red date | 2026-10-29 |
| Green date | 2026-10-29 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-29 | Screenshot: three footer links stacked in separate `<p className="mt-2">` blocks. |
| 2026-10-29 | Red Vitest: missing `role="group"` Site links with `flex-row`. |
| 2026-10-29 | Fix: single flex-row wrap group, middot separators, Feedback+Beta in one inline cluster. |
| 2026-10-29 | Scoped eslint/prettier PASS on footer files. Full `make lint`/FE `tsc` red from ambient sibling (`groupDecodeSegments.ts`) — out of scope. |

## Fix

- `OperatorFooter.tsx`: replace stacked `<p>` link blocks with
  `role="group"` `flex flex-row flex-wrap` row; middot separators (`aria-hidden`);
  Feedback + `BetaBadge` wrapped in `inline-flex` so the badge stays with Feedback.
- `OperatorFooter.test.tsx`: layout suite for horizontal group + Beta adjacency.
- `docs/ui-style-guide.md`: Changelog of norms row.

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [x] Session closed / HANDOFF written
