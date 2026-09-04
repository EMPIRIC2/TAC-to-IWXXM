# UK_METOFFICE — UK Met Office / CAA thin overlay (P2)

> **Profile id**: `UK_METOFFICE` · **Kind**: semantic · **Priority**: P2 · **Status**: implemented (EV-094 deepen / [#1098](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1098); prior EV-089 / #920 closed)  
> **Catalog row**: [`catalog.yaml`](../catalog.yaml) · **Path**: thin · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

UK national semantic overlay extending `ICAO_2025`: CAP 746 aerodrome MET conventions for
METAR/SPECI/TAF. Core IWXXM only — no published UK extension XSD.

## Owns (target)

| Area | Scope |
|------|-------|
| TAC parse / normalize | ICAO baseline; CAP 746 deltas via fixtures (± empty override list) |
| IWXXM encode | **Core WMO only** |
| Products | METAR, SPECI, TAF |
| Overrides | **Empty** (civil ICAO; military colour OOS — D-EV094-uk-mil) |

## Standards hierarchy (L0–L6)

| Level | Source | Status |
|-------|--------|--------|
| L0 | CAP 746 | mined (kickoff + EV-094) |
| L1 | WMO-No. 306 | via ICAO_2025 |
| L2–L3 | IWXXM core pin | via ICAO_2025 |
| L4–L5 | National XSD / vocab | **N/A — do not invent** |
| L6 | Ops corpus (AWC / Met Office) | METAR + TAF attributed (M1); SPECI gap |

## Code list policy

| Code / list | Global SoT | National override | Notes |
|-------------|------------|-------------------|-------|
| Standard METAR/TAF tokens | ICAO / WMO | none | ATIS specials → fixtures |

## Fixtures

`packages/tac2iwxxm/tests/fixtures/profiles/UK_METOFFICE/` — EV-094 M1 attributed EGLL METAR/TAF;
SPECI remains labeled `synthetic_ev089` until a real corpus is harvested.

## Gaps

- [x] Registry + convert allowlist (EV-089)
- [x] ≥1 attributed METAR + TAF (EV-094 M1)
- [ ] Attributed real SPECI corpus
- [x] Catalog `status: implemented` (EV-094 M7 / #1098)
- [ ] Promote durable CAP 746 URLs into RULE_SOURCE_URLS when rules land

## References

- Mining: [`uk-metoffice-tac-mining-notes.md`](../../mining/uk-metoffice-tac-mining-notes.md)
- Tracking: [#1098](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1098) (do not reopen [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920))
