# UX-2026-10-30-map-data-attribution

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-30-map-data-attribution` |
| Session | `UX-map-data-attribution` (local session store) |
| Surface | Results → Map / live world map + station minimap tile chrome |
| Journeys touched | Live map (tests/docs only — not UI copy) |
| Status | closed |

## Desired change

On the Map surface, make it clear where map tiles / geographic data come from (API/service name) and under what license that data is provided. Micro polish: Leaflet-style corner credit, not a redesign.

## Acceptance

- [x] Operator can see the map data source (OpenStreetMap) without leaving the Map tab.
- [x] Operator can see the license (Open Database License / ODbL), with a link to the official copyright page.
- [x] Copy is plain language; no planning ids (`EV-` / `UJ-` / `ADR-` / `docs/…`).
- [x] Same attribution string is used for live world map and station minimap tile layers.

## Must not break

- Map rendering, pan/zoom, overlays
- Other Results tabs
- Convert primary path

## Style-guide impact

Norm to append ([Corpus: ui-style] Copy / tone):

> Live map and station minimap Leaflet corner attribution must name OpenStreetMap contributors and the Open Database License (ODbL), with a link to the OSM copyright page, not a bare "© OpenStreetMap".

Target section: Copy / tone

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/utils/mapTileAttribution.test.ts` |
| Red date | 2026-10-30 |
| Green date | 2026-10-30 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-30 | Code uses Leaflet `L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap' })` in `LiveWorldMap.tsx` and `stationMap.ts`. |
| 2026-10-30 | Provider terms (https://www.openstreetmap.org/copyright): OSM data under ODbL; require credit to OpenStreetMap contributors and make ODbL clear (linking copyright page is accepted). Current string is incomplete. |

## Fix

- `apps/frontend/src/utils/mapTileAttribution.ts` — shared `OSM_TILE_URL` + `OSM_TILE_ATTRIBUTION`
- `apps/frontend/src/utils/stationMap.ts` — use shared constants
- `apps/frontend/src/app/components/LiveWorldMap.tsx` — use shared constants
- Operator-visible credit: `© OpenStreetMap contributors · Open Database License (ODbL)` with link to `https://www.openstreetmap.org/copyright`

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [x] Session closed / HANDOFF written
