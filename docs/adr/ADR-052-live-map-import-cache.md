# ADR-052: Multi-feed live map cache with import-time translation

> **Status**: Accepted
> **Date**: 2026-10-03
> **Deciders**: User (EV-globe-live-map)

[Corpus: product §F37] [Corpus: system-spec] [Corpus: api] [Corpus: adr]

## Context

Decode visuals already has a Leaflet map and a cache read on `feat/live-tac-map`. That cache stores feed text and translates a report when someone opens it. The map asks for the current view and starts on METAR and SPECI.

The operator asked for every current alert on a world view, more than one public feed, and translation stored at import. Production is one API process. Translating the world on the request path would delay Convert and validate.

## Decision

1. Keep Leaflet and the existing tile source. The lowest zoom is the flat world. Every cached point and shape in that view is drawn. There is no clustering and no globe library.
2. The browser calls `GET /api/v1/live-map` only. The route reads the cache. It does not call a vendor.
3. Feeds this cycle are public Aviation Weather Center products: METAR, TAF, AIRMET, international SIGMET, and G-AIRMET. The NWS active-alert feed stays off this map. A separate ICAO live feed is not available. A feed that needs credentials or a license is out.
4. About every 5 minutes the API process stores every fetched location and text. It translates and lints at most 40 reports (`LIVE_MAP_IMPORT_LIMIT`). A point or shape is drawn before IWXXM is stored. A tick already running is skipped.
5. Each place keeps the newest report and two earlier ones. The newest is first.
6. Space weather is stored for the list beside the map and is never a map place.
7. Convert and validate response bodies stay as they are. The F8 worker stays at 0 replicas for this map. No new database.

## Consequences

- Opening a report reads stored IWXXM when that tick has translated it. Until then the click says translation is pending.
- A tick can leave IWXXM empty for reports it already drew.
- NWS active alerts from the 2026-10-03 check were marine and flood warnings, so they are not map places.
- The live METAR bbox order is latitude, longitude, latitude, longitude. The current client sends the other order and gets an empty body.

## Alternatives considered

- Translate only the report someone opens. Rejected: the operator asked for translation at import.
- Cluster pins at world zoom. Rejected: the operator asked for every pinpoint.
- A separate worker or database. Rejected for the 2026-10-03 cycle: the existing API and database stay the home unless the cap cannot be met there. Amended below.

## Amend — EV-map-worker-cluster (2026-10-04)

The operator accepted a review of translation pace and clustering. The 40-report cap does not finish a refresh area: the next tick moves to another area and later translates the same first 40 rows again. A worker that only has its own memory cannot update the map.

1. Leaflet stays. There is no globe and no pin-clustering library. World zoom draws one marker per continent that has reports. The next zoom draws sub-region markers. A closer zoom draws each station, polygon, line, and circle. A continent or sub-region click only zooms.
2. Hover, and a tap on a phone, opens a scrolling popup on the station. The panel under the map is removed. The popup keeps the place name, wind line, report times, TAC, and either the stored IWXXM, the issues, or “Translation is pending.”
3. The page and the popup say: “These reports are not validated for operational use. They come from the Aviation Weather Center.”
4. A new Deployment on the existing DigitalOcean Kubernetes cluster translates. It is not a public service. It has CPU and memory requests and a memory limit. Staging starts at one replica. It finishes one of the five refresh areas before it starts the next. The ingest poller stays at 0 replicas.
5. The API stops running the translation timer once that Deployment owns it. The API and the translator use the same `LIVE_MAP_CACHE_URL`. That is the existing cache database, not a new database server. Convert and validate response bodies stay as they are. Staging only. Do not promote to production.

## Amend — EV-map-product-layers (2026-10-06)

The operator asked for one layer and one color per TAC product, a hover card, and a click that loads the converter. [Corpus: product §F37]

1. Leaflet and the current tiles stay. Continent markers, then sub-region markers, stay. Per-product colors and shapes appear at the closer zoom. There is still no globe library and no pin-clustering package.
2. Each product is its own layer: `metar` `#1d4ed8`, `speci` `#0369a1`, `taf` `#0f766e`, `airmet` `#c2410c`, `gairmet` `#a16207`, `sigmet` `#b91c1c`, `vaa` `#6d28d9`, `tca` `#be185d`, `vona` `#4338ca`. Colors are fixed. Fills and outlines differ. The newest report is solid. Two earlier reports are faded. Hover highlights the shape. Co-located airport reports are offset and each has a type chip.
3. Rows from the G-AIRMET feed are stored as `gairmet`. A domestic row whose text is a SIGMET stays `sigmet`. `GET /api/v1/live-map` already filters by product id. This amend adds `gairmet` to the allowed set and the default. Family names are not a query parameter. The browser list stays `observed_at` and `tac`.
4. The hover card shows the product, the issue time, and the station, or Area when there is no airport. Scrollable TAC sits to the right on a wide screen and below the metadata on a narrow screen. The card opens on the newest report. A control selects an earlier copy. Clicking the shape or the card loads that copy into the converter at the top of the page.
5. Space weather stays off the map. The list uses `#0e7490` when it has rows. This amend does not add a space-weather feed.
6. Convert and validate response bodies stay as they are. Guest access stays. Staging is the ship target. Do not promote to production.
