# UK_METOFFICE — UK Met Office / CAA thin overlay (P2)

> **Profile id**: `UK_METOFFICE` · **Kind**: semantic · **Priority**: P2 · **Status**: in_progress (EV-089 / [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920))  
> **Catalog row**: [`catalog.yaml`](../catalog.yaml) · **Path**: thin · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

UK national semantic overlay extending `ICAO_2025`: CAP 746 aerodrome MET conventions for
METAR/SPECI/TAF. Core IWXXM only — no published UK extension XSD.

## Owns (target)

| Area | Scope |
|------|-------|
| TAC parse / normalize | ICAO baseline; CAP 746 deltas via fixtures (± empty override list) |
| IWXXM encode | **Core WMO only** |
| Products | METAR, SPECI, TAF |
| Overrides | Expected empty / pure ICAO unless Build mining finds durable rules |

## Standards hierarchy (L0–L6)

| Level | Source | Status |
|-------|--------|--------|
| L0 | CAP 746 | mined (kickoff) |
| L1 | WMO-No. 306 | via ICAO_2025 |
| L2–L3 | IWXXM core pin | via ICAO_2025 |
| L4–L5 | National XSD / vocab | **N/A — do not invent** |
| L6 | Ops corpus (OGIMET / Met Office) | Build fixtures |

## Code list policy

| Code / list | Global SoT | National override | Notes |
|-------------|------------|-------------------|-------|
| Standard METAR/TAF tokens | ICAO / WMO | none expected | ATIS specials → fixtures |

## Fixtures

`packages/tac2iwxxm/tests/fixtures/profiles/UK_METOFFICE/` — Build (first #920 PR).

## Gaps

- [ ] Registry + convert allowlist
- [ ] ≥1 valid TAC fixture per v1 product
- [ ] Promote durable CAP 746 URLs into RULE_SOURCE_URLS when rules land

## References

- Mining: [`uk-metoffice-tac-mining-notes.md`](../../mining/uk-metoffice-tac-mining-notes.md)
- Issue: [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920)
