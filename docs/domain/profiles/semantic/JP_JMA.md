# JP_JMA — Japan JMA / Tokyo VAAC compat overlay (P2)

> **Profile id**: `JP_JMA` · **Kind**: semantic · **Priority**: P2 · **Status**: in_progress (EV-089 / [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920))  
> **Path**: compat · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

Compat pack for JMA METAR/TAF/SIGMET plus Tokyo VAAC **VAA**. AIRMET **excluded** from v1
(D-EV089-jp-va). Core IWXXM only — no national VA schema fork.

## Owns (target)

| Area | Scope |
|------|-------|
| Products | METAR, TAF, SIGMET, VAA |
| AIRMET | Out of v1 |
| IWXXM | Core / existing VAA paths |

## Gaps

- [ ] Fixtures from JMA / Tokyo VAAC public bulletins
- [ ] Registry allowlist

## References

- Mining: [`jp-jma-tac-mining-notes.md`](../../mining/jp-jma-tac-mining-notes.md)
