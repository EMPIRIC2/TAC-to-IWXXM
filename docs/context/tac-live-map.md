# Live TAC map

Session: EV-tac-map. Scale: full. Gate: closed.

[Corpus: product §F37] [Corpus: product §F7] [Corpus: product §F9] [Corpus: product §F21]

UI reference: design canvas only. No local preview in this pass.

## Goal

Guests see a world map on Decode visuals. Airport reports come from the NOAA Aviation Weather Center feed. Polygons appear only when that feed includes a region. Each place keeps three reports. The browser never calls the feed.

## Locked decisions

| Topic | Decision |
|-------|----------|
| Build timing | Design now. Build only after the documenting-to-implementing gate opens |
| Who | Guests and signed-in operators. Sign-in is not required |
| Screen | Decode visuals replaces the one-station minimap |
| Feed | NOAA Aviation Weather Center Data API, via this app’s API |
| Airports | Every station the feed returns in the current map view |
| History | Latest report plus two earlier ones |
| Polygons | Drawn only when the feed includes geometry. The map says when a family has none in view |
| Space weather | List beside the map |
| Backend | Timer inside the existing API. Existing database. Ingest worker stays at 0 replicas. The tick stores feed text and does not convert the world; one opened report converts on demand |
| Views | Observations (METAR + SPECI on), Forecasts, Hazards, Advisories. Space weather is a list |

## Out of scope

Browser calls to the feed. Worker polling for this map. OpenAIP as the live source. Feed XML as goldens. A separate Map tab. Saving map history into work sessions. A continuous three-hour film.
