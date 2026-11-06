# UX-2026-10-29-drop-mass-ingest

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-29-drop-mass-ingest` |
| Session | `UX-drop-mass-ingest` (local session store) |
| Surface | Convert / workbench drop-zone chrome (Select files row) |
| Journeys touched | Mass folder/zip ingest chrome removed from Convert; API route kept (docs/tests only) |
| Status | closed |

## Desired change

Drop the Mass Ingest control (lock + label / Folder / Zip group) from the Convert toolbar next to Select files. Operators should not see that chrome on the primary convert path.

## Acceptance

- [x] Convert drop-zone actions show Select files and do not show Mass ingest / mass-ingest test ids
- [x] Vitest asserts Mass Ingest chrome is absent on the Convert surface
- [x] Tests that required the button present are updated
- [x] Style-guide Changelog of norms row added
- [x] `POST /api/v1/ingest/mass` client helper and backend route remain

## Must not break

- Select files / drag-drop queue
- Auth, Convert, Validate IWXXM chrome
- Sibling polish on the same day
- Backend mass-ingest API (not FE-only route delete)

## Style-guide impact

Norm to append:

> Convert drop-zone chrome keeps Select files; do not show Mass Ingest beside it.

Target section in `[Corpus: ui-style]`: Layout / density

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/app/components/FileConverter.test.tsx` (Workbench layout) |
| Red date | 2026-10-29 (asserted absence while chrome still rendered) |
| Green date | 2026-10-29 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-29 | Mass ingest group lived in `FileConverter` compact drop zone beside Select files (`mass-ingest-actions`). |
| 2026-10-29 | Intake default: hide/remove Convert chrome; keep `massIngestFiles` / API. |
| 2026-10-29 | Removed Convert chrome + local handlers/refs; kept `apps/frontend/src/utils/api.ts` `massIngestFiles` and backend route. Updated Vitest + Playwright that required the button. |

## Fix

- `FileConverter.tsx`: drop Mass Ingest group, folder/zip inputs, and unused handlers/state/imports
- `FileConverter.test.tsx`: absence AC on Workbench layout; remove chrome-interaction cases
- `apps/e2e/uj051-053-ev042-mass-queue.e2e.spec.ts`: assert chrome absent; keep unauthenticated API deny + queue via Select files
- `docs/ui-style-guide.md`: layout bullet + Changelog of norms row

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [x] Session closed / HANDOFF written
