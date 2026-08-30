# IN_IMD — India IMD compat overlay (P2)

> **Profile id**: `IN_IMD` · **Kind**: semantic · **Priority**: P2 · **Status**: in_progress (EV-089 / [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920))  
> **Path**: compat · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

Compat pack for IMD METAR/SPECI/TAF/SIGMET. AIP notes TAF may omit forecast visibility /
temperature — document as note / optional override; do **not** invent unpublished IMDIMET XSD.
No AIRMET/GAMET in v1 (not issued per AIP).

## Owns (target)

| Area | Scope |
|------|-------|
| Products | METAR, SPECI, TAF, SIGMET |
| Overrides | TAF vis/temp omission candidate |
| IWXXM | Core only |

## Gaps

- [ ] AIP GEN 3.5 section cite + fixtures
- [ ] Confirm override vs diagnostics-only for TAF omissions

## References

- Mining: [`in-imd-tac-mining-notes.md`](../../mining/in-imd-tac-mining-notes.md)
