# Per-product layers on the live map

Session: EV-map-product-layers. Scale: standard. Gate: closed.

[Corpus: product §F37] [Corpus: system-spec] [Corpus: api] [Corpus: adr/ADR-052] [Corpus: tests]

UI reference: **non-deployed** local Vite at `http://127.0.0.1:5173/` on 2026-10-06. Not staging or production. The Weather map section was already on the Convert page, under the converter output.

## Goal

A guest can turn each TAC product on or off, see that product in its own color, read a short hover card (product, issue time, station, scrollable TAC), and click the card to load that report into the converter at the top of the page.

## What the local screen does today

Observed signed out, with the map able to draw:

- Filters are four groups with a checkbox per product already inside them: Observations (METAR, SPECI), Forecasts (TAF), Hazards (AIRMET, SIGMET), Advisories (volcanic ash, tropical cyclone, volcano notice).
- G-AIRMET is not its own checkbox. The cache maps both the AIRMET feed and the G-AIRMET feed to `airmet`, except when the text is a SIGMET.
- Space weather is the sentence “Space weather has no map location.” It is not a colored list.
- Pin color is by family: METAR and SPECI share blue, TAF is teal, AIRMET and SIGMET share orange, advisories share purple. On the local map the polygons and dots still read as one blue-green mass at a glance.
- Copy says to open a point or outlined area to load it above. The newest observation time in the view is shown above the map.
- Continent and sub-region markers from the prior cycle stay in the product row. This pass did not re-test world zoom.

Prior briefs: [globe-live-map.md](globe-live-map.md), [map-worker-cluster.md](map-worker-cluster.md). This cycle does not reopen clustering, the translator Deployment, or the tile source.

## Locked decisions

| Id | Topic | Decision |
|----|--------|----------|
| R1 | Feature | Deepen F37. No new feature id |
| R2 | Who | Guest on Decode visuals. Sign-in is not required |
| R3 | Zoom | Keep continent markers, then sub-region markers. Per-product colors and shapes appear at the closer zoom |
| R4 | Layers | One layer and one color per product: METAR, SPECI, TAF, SIGMET, AIRMET, G-AIRMET, volcanic ash, tropical cyclone, volcano notice |
| R5 | Space weather | Stays off the map. The side list gets its own color |
| R6 | Hover | Card shows product, issue time, and station, plus scrollable TAC. Click loads that report into the converter at the top |
| R7 | Visuals | Legend tied to the toggles; distinct fill and outline; latest report solid and older ones faded; hover highlights the shape; co-located airport reports offset or stacked with a type chip |
| R8 | API | Compatible add: product id on each item, and per-product filters. Existing family filters keep working. Convert and validate bodies stay as they are |
| R9 | Code later | Frontend map, live-map API, and `packages/live-map-geometry` if colors or offsets need a shared helper. Not in this spec pass |
| R10 | Privacy | No new personal data or retention |
| R11 | Ship checks | H4–H5 when the screen ships to staging. CORS stays. Production promotion is out |
| R12 | Docs | Delta F37, system spec, API contract, test plan, and the live-map journey. Amend ADR-052 because per-product layers and the hover card change the accepted map decision |
| R13 | Preview | Operator asked to see the non-deployed local UI. That view is reference only |

## Memory

Session-open and historical retrieve returned no Decision, Feature, or FailureMode for this map. Disposition: **skip**. SDD suggestions had no actionable next step. Nothing from memory is applied. [Corpus: skill-integration]

## Out of scope

Replacing Leaflet or the current tiles. Drawing space weather as pins. A globe library, a pin-clustering package, or a new map vendor. Browser calls to vendor feeds. Sign-in required to view. Changes to Convert or validate response bodies. Production promotion.

## Build intent (not started)

`apps/frontend` map, `apps/backend` live-map filter and product id, `packages/live-map-geometry` only if a shared color or offset helper is needed. Staging smoke later. E2E is in the build band and stays blocked until the spec gate opens.
