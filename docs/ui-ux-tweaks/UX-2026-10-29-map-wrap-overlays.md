# UX-2026-10-29-map-wrap-overlays

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-29-map-wrap-overlays` |
| Session | `UX-session-convert-polish` (local session store) |
| Surface | Live world map (Results → Map / live map route) |
| Journeys touched | Live map hazard overlays (tests only — not UI copy) |
| Status | fixed |

## Desired change

When the live map zooms out and Leaflet shows wrapped world copies, SIGMET/alert polygons and station markers must appear on the looped globe (±360°), not only on the primary copy.

## Acceptance

- [x] Overlays paint at longitude offsets −360, 0, and +360.
- [x] Focus popup opens only on the primary copy (`lngOffset === 0`).
- [x] Vitest asserts circleMarker/polygon calls at wrapped coordinates.

## Must not break

- Primary-copy map interactions, hover/click popups, convert flow.

## Style-guide impact

Norm to append ([Corpus: ui-style]):

> Live map vector overlays that must survive tile wrap are painted on world-copy longitude offsets (−360 / 0 / +360), not only the primary copy.

Target section: Layout

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/utils/liveMap.test.ts`; `apps/frontend/src/app/components/LiveWorldMap.test.tsx` (`draws markers and alert polygons on wrapped world copies`) |
| Red date | 2026-10-29 |
| Green date | 2026-10-29 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-29 | Implemented on `fix/map-wrap-alerts` worktree; copied into main workspace for formalization. Root cause: Path/CircleMarker project once; tiles wrap. |

## Fix

- `apps/frontend/src/utils/liveMap.ts` — `WORLD_COPY_LNG_OFFSETS`, `shiftLatLng`, `shiftPositions`
- `apps/frontend/src/app/components/LiveWorldMap.tsx` — draw loop over world copies
- Matching unit tests

Also present uncommitted on sibling worktree  
`/Users/bigme/Documents/GitHub/TAC-to-IWXXM/TAC-to-IWXXM-HF-map-wrap-alerts` (same patch).

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added
- [x] No planning ids in operator-facing strings
- [x] Session closed / HANDOFF written
