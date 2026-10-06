# BUG-2026-10-04 map scrolls up and only shows continent chips

[Corpus: product §F7] [Corpus: product §F37]

## Error description

On the live weather map, opening a report pans the map upward. At the opening
zoom the map draws a continent chip such as North America, and choosing another
region does not open that area. Operators need the points and route polygons in
the converter, each with the TAC, the decode, and the IWXXM.

## Error logs

No server traceback. The map client called `panBy` after a popup opened, and
low zoom replaced individual features with continent and sub-region chips.

## Investigation

The popup timer measured the popup and called `map.panBy` with a negative Y,
which moves the map content up. Cluster drawing replaced points and polygons
until the zoom reached station level, so a region click only changed zoom.
A later layer change opens the card on hover. That still must not call `panBy`.
The converter panes were capped well below one viewport.

## Repro test

`tests/bugs/test_bug_2026_10_04_map_scroll_and_clusters.py`

Frontend coverage: `apps/frontend/src/app/components/LiveWorldMap.test.tsx`
draws a polygon at world zoom, opens its TAC, decode, and IWXXM, and asserts
the map is not panned.
