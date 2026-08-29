# HK_HKO — Hong Kong Observatory compat overlay (P2)

> **Profile id**: `HK_HKO` · **Kind**: semantic · **Priority**: P2 · **Status**: in_progress (EV-089 / [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920))  
> **Path**: compat · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

APAC interoperability fixture pack: METAR/SPECI/TAF/SIGMET/VAA under `ICAO_2025`.
Overrides expected **empty**; Chinese-language bulletin variants not required for v1.

## Owns (target)

| Area | Scope |
|------|-------|
| Products | METAR, SPECI, TAF, SIGMET, VAA |
| IWXXM | Core only |
| Overrides | none expected |

## Gaps

- [ ] Fixtures (VHHH / HKO public corpus)
- [ ] Registry allowlist

## References

- Mining: [`hk-hko-tac-mining-notes.md`](../../mining/hk-hko-tac-mining-notes.md)
