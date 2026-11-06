# UX-2026-10-29-center-more-actions-buttons

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-29-center-more-actions-buttons` |
| Session | `UX-center-more-actions-buttons` (local session store) |
| Surface | Convert Settings → More actions (Convert&Send, Disseminate, Download ZIP, Clear) |
| Journeys touched | Convert secondary actions (tests only — not UI copy) |
| Status | closed |

## Desired change

Label + Beta badge (or count) sit as a centered cluster inside each More actions outline/ghost button — not left-packed against the leading edge.

## Acceptance

- [x] More actions buttons use horizontal flex center (`justify-center`), not `justify-start`.
- [x] Vertical centering stays with shared `Button` ([UX-2026-10-29-center-button-text](UX-2026-10-29-center-button-text.md)); this tweak does not touch `py-2` / size tokens.

## Must not break

- Shared `Button` default size fix (`h-9`, no `py-2`, base `justify-center`).
- Convert&Send / Disseminate / Download ZIP / Clear labels, `data-testid`s, and outline/ghost variants.
- Primary Convert toolbar centering from the sibling UX log.

## Style-guide impact

Norm to append ([Corpus: ui-style]):

> More actions (and other full-width Convert secondary buttons): keep shared `Button` flex center; do not override with `justify-start`.

Target section: Layout / density

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/app/components/FileConverter.test.tsx` |
| Red date | 2026-10-29 |
| Green date | 2026-10-29 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-29 | Intake: screenshot shows left-aligned More actions labels. |
| 2026-10-29 | Sibling [UX-2026-10-29-center-button-text](UX-2026-10-29-center-button-text.md) already dropped `py-2` on shared Button — vertical OK; do not reapply. |
| 2026-10-29 | Root cause: More actions `className`s pass `justify-start`, which drops base `justify-center` via `twMerge`. |
| 2026-10-29 | Fix: swap `justify-start` → `justify-center` on the four More actions buttons only. |

## Fix

- `apps/frontend/src/app/components/FileConverter.tsx` — More actions buttons: `justify-center` instead of `justify-start`.
- `apps/frontend/src/app/components/FileConverter.test.tsx` — assert panel buttons keep `justify-center` and omit `justify-start`.
- `docs/ui-style-guide.md` — changelog row for this UX id.

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [x] Session closed / HANDOFF written
