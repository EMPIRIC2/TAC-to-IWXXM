# AU_BOM — Australia BoM semantic overlay (P1)

> **Profile id**: `AU_BOM` · **Kind**: semantic · **Priority**: P1 · **Status**: in_progress (EV-087 / [#917](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/917))  
> **Catalog row**: [`catalog.yaml`](../catalog.yaml) · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

Bureau of Meteorology national semantic overlay: TAF change-group `INTER`, TAF3 service
marker in RMK, forecast T/Q remarks, and AUTO METAR/SPECI tokens (`NCD`, `UP`, solidi).

## Owns (target)

| Area | Scope |
|------|-------|
| TAC parse / normalize | TAF `INTER` vs `TEMPO`; RMK `T`/`Q`/`TAF3`; AUTO METAR tokens |
| IWXXM encode | **Core WMO only** — no published AU extension XSD (EV-087 research) |
| Products | TAF (incl. TAF3-as-flag), METAR, SPECI |
| SIGMET / AIRMET | ICAO base unless later mining shows deltas |

## Key policy (locked)

| Topic | Rule | Decision |
|-------|------|----------|
| `INTER` | Distinct IR change-group; **emit** `TEMPORARY_FLUCTUATIONS` + preserve `INTER` in remarks/diagnostics | D-EV087-inter-emit |
| `TAF3` | RMK marker under `product=TAF` — not a new API product enum | D-EV087-taf3 |
| National XSD | None — do not invent | D-EV087-xsd |

## Authoritative sources

| Source | Access | Proves |
|--------|--------|--------|
| [BoM TAF/METAR reference card](http://www.bom.gov.au/aviation/data/education/taf-metar-speci-reference-card.pdf) | public | INTER/TEMPO durations; T/Q; TAF3; AUTO codes |
| [BoM TAF3 Implementation](https://www.bom.gov.au/aviation/taf3/index.shtml) | public | TAF3 service |
| [BoM International TAF](https://www.bom.gov.au/aviation/forecasts/international-taf/) | public | Examples |
| ICAO APAC Australian TAF WP | public | Regional context |

## Mining notes

- [`au-bom-tac-mining-notes.md`](../../mining/au-bom-tac-mining-notes.md)

## Implementation (Build)

| Component | Location |
|-----------|----------|
| Registry | `packages/tac2iwxxm/src/tac2iwxxm/profile_registry.py` (`au_bom`) |
| Fixtures | `packages/tac2iwxxm/tests/fixtures/profiles/AU_BOM/` |

## Gaps

- Native IWXXM `INTER` changeIndicator does not exist in `taf.xsd` — provenance via remarks.
- Category A/B issuance schedules optional deepen.
