# HK_HKO — Hong Kong Observatory compat overlay (P2)

> **Profile id**: `HK_HKO` · **Kind**: semantic · **Priority**: P2 · **Status**: implemented (EV-094 deepen / [#1098](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1098); kickoff EV-089 / [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920))  
> **Path**: compat · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

APAC interoperability fixture pack: METAR/SPECI/TAF/SIGMET/VAA under `ICAO_2025`.
Overrides expected **empty**; HKO TAFs include TX/TN (Annex-conformant). Chinese-language
bulletin variants not required for v1.

## Owns (target)

| Area | Scope |
|------|-------|
| Products | METAR, SPECI, TAF, SIGMET, VAA |
| IWXXM | Core only |
| Overrides | none (empty) |

## Gaps

- [x] Attributed VHHH METAR/TAF (AWC; EV-094 M6 / #1098) — SPECI/SIGMET/VAA still synthetic
- [x] Registry allowlist (EV-089; SIGMET+VAA retained per D-EV094-products)
- [x] Catalog `status: implemented` (EV-094 M7 / #1098)
- [ ] Attributed SPECI / Hong Kong FIR SIGMET / VAA corpora
- [ ] AIP GEN 3.5 durable URL when public pin found

## References

- Mining: [`hk-hko-tac-mining-notes.md`](../../mining/hk-hko-tac-mining-notes.md)
- Research: EV-094 `evidence/deep-research-report-deepen.md`
