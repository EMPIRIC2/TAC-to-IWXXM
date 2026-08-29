# KR_KMA — Korea KMA compat overlay (P2)

> **Profile id**: `KR_KMA` · **Kind**: semantic · **Priority**: P2 · **Status**: in_progress (EV-089 / [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920))  
> **Path**: compat · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

Compat pack: Korean AIP-aligned METAR/TAF/SIGMET/AIRMET corpora under `ICAO_2025` emit.
Automated national TAC→IWXXM (reported since ~2017) → assume Annex compliance until fixtures
prove otherwise; **no** invented KR XSD.

## Owns (target)

| Area | Scope |
|------|-------|
| Products | METAR, TAF, SIGMET, AIRMET |
| IWXXM | Core only |
| Overrides | Expected empty |

## Gaps

- [ ] AIP GEN 3.5 durable URL
- [ ] Fixtures (e.g. RKSI) + registry

## References

- Mining: [`kr-kma-tac-mining-notes.md`](../../mining/kr-kma-tac-mining-notes.md)
