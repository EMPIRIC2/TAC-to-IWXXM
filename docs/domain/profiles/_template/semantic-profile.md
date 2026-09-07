# PLACEHOLDER_ID — semantic profile stub

> **Profile id**: `PLACEHOLDER_ID` · **Kind**: semantic · **Priority**: P2 · **Status**: planned  
> **Catalog row**: [`catalog.yaml`](../catalog.yaml) · **Playbook**: [NATIONAL_PROFILE_PLAYBOOK.md](../NATIONAL_PROFILE_PLAYBOOK.md)  
> **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

One-paragraph purpose: issuing body, products, thin vs full path.

## Owns (target)

| Area | Scope |
|------|-------|
| TAC parse / normalize | … |
| IWXXM extensions | none (thin) \| list XSDs (full) |
| Products | METAR, SPECI, TAF, … |

## Standards hierarchy (L0–L6)

| Level | Source | Status |
|-------|--------|--------|
| L0 | | gap / mined |
| L1 | WMO-No. 306 | |
| L2 | IWXXM model pin | |
| L3 | XSD + Schematron pin | |
| L4 | National XSD | N/A or pin |
| L5 | Code lists | |
| L6 | Ops corpus | |

## Code list policy

| Code / list | Global SoT | National override | Notes |
|-------------|------------|-------------------|-------|
| | | none \| describe | |

## Fixtures

`packages/tac2iwxxm/tests/fixtures/profiles/PLACEHOLDER_ID/` — see playbook §4.

## Gaps

- [ ] …

## References

- Mining notes: `docs/domain/mining/…`
- Issues: …
