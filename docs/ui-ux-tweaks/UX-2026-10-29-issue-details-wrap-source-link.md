# UX-2026-10-29-issue-details-wrap-source-link

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-29-issue-details-wrap-source-link` |
| Session | `UX-issue-details-wrap-link` (local session store) |
| Surface | Issue details modal (Workbench console / Error log / Validate report) |
| Journeys touched | Issue detail open from TAC issues list (tests only — not UI copy) |
| Status | closed |

## Desired change

Issue details stays within its max width: long Source text wraps instead of forcing a horizontal scrollbar. When Source includes an `http(s)` URL (with or without a plain label), the URL is a real link that opens in a new tab with safe `rel`.

## Acceptance

- [x] Dialog body does not require horizontal scrolling for long Source URLs (`overflow-x` contained; values wrap / break).
- [x] Source URL renders as an `<a href="…">` with `target="_blank"` and `rel` including `noopener` (and `noreferrer`).
- [x] Plain label text before/around the URL stays plain text (not linked).
- [x] Modal remains usable (scrolls vertically if needed; not crushed by layout).

## Must not break

- Open/close via Close, Escape, and backdrop.
- Other detail fields (Code, Severity, Message, Rule, …).
- TAC issues *list* Error vs Note prevalence work (sibling agent — do not retouch list chrome).

## Style-guide impact

Norm to append ([Corpus: ui-style]):

> Issue details dialog: wrap long field values (no horizontal scroll); Source `http(s)` URLs are links (`target="_blank"`, `rel="noopener noreferrer"`), labels stay plain text.

Target section: Layout / A11y

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/app/components/IssueDetailDialog.test.tsx`; `apps/frontend/src/utils/issueDetailSource.test.ts` |
| Red date | 2026-10-29 |
| Green date | 2026-10-29 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-29 | Root cause: `DetailRow` put unbroken Source URLs in a grid `dd` without `min-w-0` / break; Source was plain text even when attribution embeds a URL. |
| 2026-10-29 | Fix: `overflow-x-hidden` on dialog; `minmax(0,1fr)` + `min-w-0 break-words` on values; `splitSourceSegments` + Source `<a>` with safe `rel`. |

## Fix

- `apps/frontend/src/app/components/IssueDetailDialog.tsx` — wrap layout; Source linkify
- `apps/frontend/src/utils/issueDetailSource.ts` — split label vs URL segments
- `apps/frontend/src/app/components/IssueDetailDialog.test.tsx` — wrap + link AC
- `apps/frontend/src/utils/issueDetailSource.test.ts` — segment unit cases
- `docs/ui-style-guide.md` — Changelog of norms row

## Close checklist

- [x] Regression green (Vitest 6/6)
- [x] Style-guide changelog row added
- [x] No planning ids in operator-facing strings
- [x] Session closed / HANDOFF written (`~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/UX-issue-details-wrap-link`)
- [ ] Commit — deferred (user: no commit)
