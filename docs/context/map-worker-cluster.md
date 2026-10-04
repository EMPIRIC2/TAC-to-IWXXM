# Faster map translation and a clearer plot

Session: EV-map-worker-cluster. Scale: standard. Gate: open.

[Corpus: product §F37] [Corpus: product §F8] [Corpus: adr/ADR-052] [Corpus: product §F21]

UI reference: **non-deployed** local Vite at `http://127.0.0.1:5173/` on 2026-10-04. The local API was already listening on port 18001. Not staging or production.

## Goal

Move live-map IWXXM translation onto a DigitalOcean worker so one refresh region finishes before the next starts, without slowing Convert. Keep the five refresh boxes. At world zoom, draw one cluster per continent, then sub-region clusters, then stations. Hover or tap opens the station on the pin. Say the reports are not validated for operational use and cite Aviation Weather Center.

## What the local screen does today

Decode visuals, signed out, Search left as `KJFK`:

- The map is a flat Leaflet view zoomed to the New York area. A handful of blue dots are visible. There is no cluster control and no popup on a dot.
- Product checkboxes for METAR, SPECI, TAF, AIRMET, SIGMET, VAA, TCA, and VONA start on. Copy says space weather has no map location.
- Under the map, the selected station shows the airport name, a wind line, report times, the TAC text, and “Translation is pending.”
- There is no standing notice that the feed is unvalidated or that it comes from Aviation Weather Center.

## Locked decisions

| Topic | Decision |
|-------|----------|
| Feature | Deepen F37. No new feature id |
| Translation | A region’s stored reports finish before the next region starts. Convert and validate responses stay as they are |
| Where it runs | A separate DigitalOcean Kubernetes Deployment translates. It has resource requests and a memory limit and is not a public service. Staging starts at one replica. The ingest poller stays off |
| Refresh | Keep the five current boxes |
| Plot | World zoom clusters by continent. The next zoom clusters by sub-region. Closer zoom shows stations. The five refresh boxes stay |
| Detail | Hover, and tap on a phone, opens a popup on the pin. Remove the panel under the map |
| Notice | Standing notice on the map, repeated in the popup, naming Aviation Weather Center |
| Ship | Staging only. Do not promote to production |

## Locked after review

Sub-regions, in that order so smaller boxes win: Central America, Caribbean, North America, South America, Europe, Middle East, South Asia, Southeast Asia, North Asia, Africa, and Oceania (including the Pacific side of the date line). A coordinate outside those boxes still joins the nearest continent. Cluster click only zooms. Station zoom shows pins and shapes. The API and the translator share `LIVE_MAP_CACHE_URL`. The ingest poller stays off.
