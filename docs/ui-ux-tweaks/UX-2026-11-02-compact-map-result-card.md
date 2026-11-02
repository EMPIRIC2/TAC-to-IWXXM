# UX-2026-11-02-compact-map-result-card

| Field            | Value                                                                      |
| ---------------- | -------------------------------------------------------------------------- |
| Id               | `UX-2026-11-02-compact-map-result-card`                                    |
| Session          | `UX-compact-map-result-card` (local session store)                         |
| Surface          | Results → Map live station popup (`StationPopup` in `LiveWorldMap.tsx`)    |
| Journeys touched | Live map → load TAC into Convert workbench (tests/docs only — not UI copy) |
| Status           | fixed                                                                      |

## Desired change

Make live-map station report cards denser:

1. Show **product** (e.g. TAF) and **station** (e.g. EFKS) in a compact header.
2. Replace **Newer copy** / **Earlier copy** pills with a **select** of available observation/issue times.
3. Make **TAC** a **collapsible** section — **collapsed by default** so multiple cards stay short; operators expand when they need the raw text.
4. Add an explicit **Send to converter** button that uses the existing map→workbench handoff (`onLoad` → `placeShowingReport` → `FileConverter` `onOpenPlace` / `setManualInput`). No new convert API.

## Acceptance

- [x] Card shows product label and station id (ICAO / place key) without relying on TAC body alone
- [x] Multi-report places use a select of formatted observation times; changing the select updates shown TAC
- [x] TAC block is collapsible and starts collapsed
- [x] Send to converter control loads the **currently selected** report into the converter via existing `onOpenPlace` path
- [x] Vitest covers select switch, collapse default, and send affordance
- [x] No planning ids in operator-facing strings; Map tab / Hide chrome unchanged

## Must not break

- Loading earlier/newer TAC versions (select replaces pills but must still switch copies)
- Map tab and Results Hide/Show
- Existing click/keyboard load of the showing report into the converter

## Style-guide impact

Norm to append:

> Live map station cards: product + station header, issue-time select (not Newer/Earlier pills), TAC collapsed by default, explicit Send to converter via existing handoff.

Target section in `[Corpus: ui-style]`: Layout / density (+ Changelog of norms)

## Regression test

| Field      | Value                                                    |
| ---------- | -------------------------------------------------------- |
| Kind       | Vitest                                                   |
| Path       | `apps/frontend/src/app/components/LiveWorldMap.test.tsx` |
| Red date   | 2026-11-02                                               |
| Green date | 2026-11-02                                               |

## Change log (investigation)

| When       | Note                                                                                                                                                                                                                                                                            |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-11-02 | Target is `StationPopup` in `LiveWorldMap.tsx`. Handoff already exists: `onLoad(tac)` → `placeShowingReport` → `FileConverter` `onOpenPlace` sets `manualInput`. Screenshot matched EFKS + Newer/Earlier + always-open TAC. Default TAC collapse = densest for map hover cards. |
| 2026-11-02 | Implemented compact header, observation-time `<select>`, Collapsible TAC (default closed), Send to converter button. Removed Newer/Earlier pills.                                                                                                                               |

## Fix

- `apps/frontend/src/app/components/LiveWorldMap.tsx` — `StationPopup` compact layout
- `apps/frontend/src/utils/liveMap.ts` — `LIVE_MAP_SEND_TO_CONVERTER`, `LIVE_MAP_ISSUE_COPY`; drop Newer/Earlier copy constants
- `apps/frontend/src/utils/operatorVisibleCopy.ts` — catalog swap
- Vitest updates in `LiveWorldMap.test.tsx`

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [ ] Session closed / HANDOFF written
