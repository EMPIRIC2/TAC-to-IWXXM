# UX-2026-11-02-cite-live-map-provider

| Field | Value |
|-------|--------|
| Id | `UX-2026-11-02-cite-live-map-provider` |
| Session | `UX-cite-live-map-provider` (local session store) |
| Surface | Results → Map / live world map chrome |
| Journeys touched | Live map (tests/docs only — not UI copy) |
| Status | fixed |

## Desired change

Show who supplies the live-map reports in Results. The string already names the
Aviation Weather Center, but it was screen-reader-only. Put a muted visible line
near the newest-observation status so operators see the source without hunting.

## Acceptance

- [x] Results map chrome shows the Aviation Weather Center notice in plain sight (not `sr-only`).
- [x] Copy stays the existing `LIVE_MAP_NOTICE` wording; no planning ids.
- [x] Vitest asserts the notice text is present and visible.
- [x] Filter chips, product toggles, and map load stay as they are.

## Must not break

- Product layer chips and phenomenon filters
- Map canvas load / pan / zoom
- OSM tile corner attribution (separate from report provider)

## Style-guide impact

Norm to append ([Corpus: ui-style] Copy / tone):

> Live map Results chrome must show the report provider in a muted visible line near the newest-observation status (Aviation Weather Center via `LIVE_MAP_NOTICE`); do not leave that credit screen-reader-only.

Target section: Copy / tone

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/app/components/LiveWorldMap.test.tsx` |
| Red date | 2026-11-02 |
| Green date | 2026-11-02 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-11-02 | Provider name from `LIVE_MAP_NOTICE` in `apps/frontend/src/utils/liveMap.ts`: “Aviation Weather Center”. Same phrase in product F37 / ADR-052 live-map copy. Not a guess. |
| 2026-11-02 | `LiveWorldMap.tsx` had the notice as `sr-only` above the filter chips; newest-observation status was visible; OSM tile credit is a separate Leaflet corner string. |

## Fix

- `apps/frontend/src/app/components/LiveWorldMap.tsx` — move `LIVE_MAP_NOTICE` under the newest-observation status as muted visible text; keep `id` for `aria-describedby`
- `apps/frontend/src/app/components/LiveWorldMap.test.tsx` — assert Aviation Weather Center text, visible, not `sr-only`
- `docs/ui-style-guide.md` — Copy / tone bullet + Changelog of norms row

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [ ] Session closed / HANDOFF written
