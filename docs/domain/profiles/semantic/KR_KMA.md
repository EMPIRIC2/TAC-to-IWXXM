# KR_KMA — Korea KMA compat overlay (P2)

> **Profile id**: `KR_KMA` · **Kind**: semantic · **Priority**: P2 · **Status**: in_progress (EV-094 deepen / [#1098](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1098); kickoff EV-089 / [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920))  
> **Path**: compat · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

Compat pack: Korean AIP-aligned METAR/SPECI/TAF/SIGMET/AIRMET under `ICAO_2025` emit.
Research (EV-094): KMA states no significant Annex 3 differences — empty overrides expected.
**SPECI** on convert allowlist (EV-094 M3 / D-EV094-speci-expand). No invented KR XSD.

## Owns (target)

| Area | Scope |
|------|-------|
| Products | METAR, SPECI, TAF, SIGMET, AIRMET |
| IWXXM | Core only |
| Overrides | Expected empty |

## Gaps

- [x] SPECI fixture + allowlist wire (Build M3)
- [x] Attributed real METAR/TAF corpora (AWC RKSI) — EV-094 / #1098
- [ ] Attributed real SPECI / FIR SIGMET / AIRMET corpora (synthetic_ev089 gaps)
- [ ] AIP GEN 3.5 durable URL

## References

- Mining: [`kr-kma-tac-mining-notes.md`](../../mining/kr-kma-tac-mining-notes.md)
