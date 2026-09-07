# JP_JMA — Japan JMA / Tokyo VAAC compat overlay (P2)

> **Profile id**: `JP_JMA` · **Kind**: semantic · **Priority**: P2 · **Status**: implemented (EV-094 deepen / [#1098](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1098); kickoff EV-089 / [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920))  
> **Path**: compat · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

Compat pack for JMA METAR/SPECI/TAF/SIGMET plus Tokyo VAAC **VAA**. AIRMET **excluded**
(D-EV089-jp-va). **SPECI** on convert allowlist (EV-094 M4 / D-EV094-speci-expand).
Core IWXXM only — no national VA schema fork.

## Owns (target)

| Area | Scope |
|------|-------|
| Products | METAR, SPECI, TAF, SIGMET, VAA |
| AIRMET | Out of v1 |
| IWXXM | Core / existing VAA paths |

## Gaps

- [x] SPECI fixture + allowlist wire (Build M4)
- [x] Attributed real METAR/TAF corpora (AWC RJTT) — EV-094 / #1098
- [x] Catalog `status: implemented` (EV-094 M7 / #1098)
- [ ] Attributed real SPECI / FIR SIGMET / Tokyo VAA corpora (synthetic_ev089 gaps)

## References

- Mining: [`jp-jma-tac-mining-notes.md`](../../mining/jp-jma-tac-mining-notes.md)
