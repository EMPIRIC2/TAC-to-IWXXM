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
- A separate worker or database. Rejected: the existing API and database stay the home unless the tech plan shows the cap cannot be met there.
