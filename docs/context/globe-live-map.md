# Globe of current aviation weather

Session: EV-globe-live-map. Scale: full. Gate: closed.

[Corpus: product §F37] [Corpus: product §F7] [Corpus: product §F9] [Corpus: product §F21] [Corpus: product §F3]

UI reference: **non-deployed** local Vite at `http://127.0.0.1:5173/` on 2026-10-03. Not staging or production.

## Goal

A guest opens Decode visuals and sees current aviation weather on a map they can zoom from the world to a station. Every geographically located report is its own point or polygon. Opening one shows its text and any lint or validation issues. Station identifiers are reviewed across search, decode, and this map. Products with no surface location stay in a list.

## What the local screen does today

Branch `feat/live-tac-map` already has a Leaflet map on Decode visuals. The product row still says that map is not built. This brief treats the code as the current screen.

Observed on the local page, signed out:

- Station field accepted `KJFK` and showed John F. Kennedy International Airport, with no wind group in that decode.
- Views are Observations, Forecasts, Hazards, and Advisories. Observations starts with METAR and SPECI on.
- Copy says space weather has no map location.
- The map tiles drew. The place request to `http://localhost:18001/api/v1/live-map` failed, the page said the live map could not be loaded, and no markers were drawn.
- Zoom controls are Leaflet plus and minus. There is no globe projection and no clustering control.

The station-identifier review is still open. This pass did not show the station field rejecting `KJFK`.

## Locked decisions

| Topic | Decision |
|-------|----------|
| Feature | Deepen F37. No new feature id |
| Who | Guests and signed-in operators. Sign-in is not required |
| Screen | Decode visuals. The map replaces the one-station minimap only |
| Must not break | Convert, validate, guest access, and station search |
| Contract | Add map endpoints and cache tables. Convert and validate responses stay as they are |
| Feeds | AWC METAR, TAF, AIRMET, international SIGMET, and G-AIRMET. NWS active alerts are out |
| First paint | One map of everything current. The existing views become filters |
| Density | Every individual pinpoint at world zoom. No clustering |
| Geometry | Points for point reports. Polygons, lines, and circles when the report has that shape |
| Non-geo | Space weather stays in a list beside the map |
| Import | Store every fetched location on the tick. Translate and lint at most 40. Draw the shape before IWXXM exists. Refresh about every 5 minutes |
| Privacy | Public weather only. The map does not store operator names, sessions, or sign-in details |
| Ship | Spec now. After the gate opens, build toward staging, not production |
| Browser | Talks only to this app |

## Out of scope

Browser calls to vendor feeds. Sign-in required to view. Pins for space weather. Clustering. Translating only when a report is opened. Credentialed feeds. A new database or map vendor. Saving map history into work sessions. Changing Convert or validate response bodies.

## Build intent (not started)

Likely touch `apps/frontend` and `apps/backend`, plus the existing database. The ingest worker stays at 0 replicas unless the tech plan shows the import cap cannot be met on the API timer. Browser checks are in the build band. Gate stays closed.

## Requirements locked so far

| Topic | Decision |
|-------|----------|
| History | Latest report plus two earlier ones. The current report opens first |
| Click | Shape or station graphic, TAC, stored IWXXM, and any lint or validation issues |
| Refresh | About every 5 minutes, still capped so Convert and validate stay responsive |
| Beta | Decode visuals carries a Beta label and a feedback link until sign-off |

| Base map | Leaflet. Flat world. No globe library |

## Docs updated

Feature list F37, system spec, UJ-087, TC-F37-001..006, API contract, config and env names, deploy note, ADR-052 (proposed), `docs/decisions/ev-globe-live-map.md`.

## Feasibility outcome

AWC METAR, TAF, AIRMET, international SIGMET, and G-AIRMET are the map feeds. NWS active alerts are out. Import limit is 40 translations per tick. Locations are stored and drawn before translation finishes.
