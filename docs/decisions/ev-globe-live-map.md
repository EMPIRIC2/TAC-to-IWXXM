# EV-globe-live-map decisions

[Corpus: product §F37] [Corpus: decisions] [Corpus: adr/ADR-052]

Date: 2026-10-03. Gate closed. No product code in this pass.

| ID | Decision |
|----|----------|
| D-EV-GLOBE-01 | Deepen F37. Review station identifiers in the same cycle. No new feature id |
| D-EV-GLOBE-02 | Map feeds are AWC METAR, TAF, AIRMET, international SIGMET, and G-AIRMET. NWS active alerts and a separate ICAO live feed are out |
| D-EV-GLOBE-03 | One map of everything current. Existing views become filters that start on |
| D-EV-GLOBE-04 | Every individual pinpoint. No clustering. Base map stays Leaflet |
| D-EV-GLOBE-05 | Store every fetched location on the tick. Translate and lint at most 40 reports. Refresh about every 5 minutes. Draw a shape before its IWXXM exists |
| D-EV-GLOBE-06 | Latest report plus two earlier ones. Newest opens first |
| D-EV-GLOBE-07 | A click shows the graphic or shape, TAC, stored IWXXM, and lint or validation issues |
| D-EV-GLOBE-08 | Space weather stays in a list. No pin |
| D-EV-GLOBE-09 | Additive HTTP and cache tables. Convert and validate responses stay as they are |
| D-EV-GLOBE-10 | Must not break Convert, validate, guest access, or station search. The map replaces the one-station minimap only |
| D-EV-GLOBE-11 | Beta label and feedback link on Decode visuals until sign-off |
| D-EV-GLOBE-12 | After the build gate, aim at staging. Not production |
| D-EV-GLOBE-13 | Local non-deployed preview on 2026-10-03: station field accepted KJFK; the live place request to the local API failed and no markers drew |
| D-EV-GLOBE-14 | Confirmed 2026-10-03: NWS alerts stay off the map. Draw stored locations immediately. Translate at most 40 reports per refresh |
