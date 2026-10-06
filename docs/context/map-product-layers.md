# Per-product layers on the live map

Session: EV-map-product-layers. Scale: standard. Gate: closed.

[Corpus: product §F37] [Corpus: system-spec] [Corpus: api] [Corpus: adr/ADR-052] [Corpus: tests]

UI reference: **non-deployed** local Vite at `http://127.0.0.1:5173/` on 2026-10-06. Not staging or production. The Weather map section was already on the Convert page, under the converter output.

## Goal

A guest can turn each TAC product on or off, see that product in its own color, read a short hover card (product, issue time, station, scrollable TAC), and click the card to load that report into the converter at the top of the page.

## Index

The local map does not show this yet. Hover cards, per-product colors, the G-AIRMET layer, and the type chips are specified below and are not on the running page. Build stays blocked until the spec gate opens. [Corpus: product §F37]

| What | Where it is written | Later code |
|------|---------------------|------------|
| Product row, colors, hover, click | [feature-list.md §F37](../feature-list.md) amend EV-map-product-layers | — |
| Hex colors, zoom, card layout | [spec.md §F37](../spec.md) | `apps/frontend/src/utils/liveMap.ts`, `apps/frontend/src/app/components/LiveWorldMap.tsx` |
| Guest steps | [user-journeys.md §UJ-087](../user-journeys.md) | Frontend tests and Playwright when the screen ships |
| Checks TC-F37-007..010 | [test-plan.md §F37](../test-plan.md) | Backend and frontend tests named in those rows |
| `gairmet` on `GET /api/v1/live-map` | [api-contract.md §F37](../api-contract.md) | `apps/backend/src/routers/live_map.py`, `apps/backend/src/services/live_map_refresh.py` |
| Locked architecture | [ADR-052](../adr/ADR-052-live-map-import-cache.md) amend EV-map-product-layers | No new library, tile source, or database |
| Why | [requirements-decisions.md](../decisions/requirements-decisions.md) §EV-map-product-layers | — |

| Task | Delivers | Spec |
|------|----------|------|
| T1 | Tests, then store G-AIRMET rows as `gairmet` and allow that id on the map route | TC-F37-009 |
| T2 | Tests, then one fixed color and checkbox per product, including G-AIRMET under Hazards | TC-F37-007 |
| T3 | Tests, then the hover card and a click that loads the showing copy into the converter | TC-F37-008 |
| T4 | Tests, then faded older copies, hover highlight, offset dots, and a type chip | TC-F37-010 |
| T5 | Tests, then country, region, time presets, and hazard phenomenon on the loaded view | TC-F37-011 |

T5 is specified and not built. It starts only after the filter spec is approved. The live-map request stays the box and the product ids.

Continent zoom, guest access, the current tiles, and convert and validate responses stay as they are. Space weather stays off the map.

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
| R14 | Colors | Fixed palette, one color per product, shown in the legend. Not editable |
| R15 | Hover layout | TAC to the right of the metadata on a wide screen, and below it on a narrow screen |
| R16 | History | Card opens on the newest of the three stored reports. A control switches to an earlier copy. Click loads the copy that is showing |
| R17 | G-AIRMET | Rows from the G-AIRMET feed are product `gairmet`. A domestic row whose text is a SIGMET stays SIGMET |
| R18 | Controls | Keep the group headings. Each product is its own checkbox, color, and map layer. G-AIRMET sits under Hazards |
| R19 | Click | Hover only opens the card. Clicking the shape or the card loads the copy the card is showing into the converter |
| R20 | No station | The station line says Area when the report has no airport, and the airport name when it has one |
| R21 | Overlap | Co-located airport reports are offset slightly and carry a type chip so each product stays clickable |

## Memory

Session-open and historical retrieve returned no Decision, Feature, or FailureMode for this map. Disposition: **skip**. SDD suggestions had no actionable next step. Nothing from memory is applied. [Corpus: skill-integration]

## Out of scope

Replacing Leaflet or the current tiles. Drawing space weather as pins. A globe library, a pin-clustering package, or a new map vendor. Browser calls to vendor feeds. Sign-in required to view. Changes to Convert or validate response bodies. Production promotion.

## Build intent (not started)

`apps/frontend` map, `apps/backend` live-map filter and product id, `packages/live-map-geometry` only if a shared color or offset helper is needed. Staging smoke later. E2E is in the build band and stays blocked until the spec gate opens.
