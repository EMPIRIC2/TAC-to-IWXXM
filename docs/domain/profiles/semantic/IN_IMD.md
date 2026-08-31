# IN_IMD — India IMD compat overlay (P2)

> **Profile id**: `IN_IMD` · **Kind**: semantic · **Priority**: P2 · **Status**: implemented (EV-094 deepen / [#1098](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1098); kickoff EV-089 / [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920))  
> **Path**: compat · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

Compat pack for IMD METAR/SPECI/TAF/SIGMET. Indian TAFs commonly omit TX/TN temperature
extremes. EV-094 adds a **lint profile overlay** (`in_imd` / `IN_IMD`) that emits a
registered **info** awareness code (`IN_TAF_TX_TN_OMITTED`) when TX/TN are absent —
convert remains core IWXXM (no unpublished IMDIMET XSD). No AIRMET/GAMET in v1.

## Owns (target)

| Area | Scope |
|------|-------|
| Products | METAR, SPECI, TAF, SIGMET |
| Lint | `in_imd` — TAF TX/TN omission awareness (D-EV094-in-taf) |
| IWXXM | Core only |

## Gaps

- [x] Attributed VIDP METAR/TAF (AWC; EV-094 M5 / #1098) — SPECI/SIGMET still synthetic
- [x] Wire `in_imd` in `tac-validate` + `IN_TAF_TX_TN_OMITTED` + TC-EV094-004
- [x] Catalog `status: implemented` (EV-094 M7 / #1098)
- [ ] AIP GEN 3.5 durable URL when public pin found
- [ ] Attributed SPECI / FIR SIGMET corpora

## References

- Mining: [`in-imd-tac-mining-notes.md`](../../mining/in-imd-tac-mining-notes.md)
- Research: EV-094 `evidence/deep-research-report-deepen.md`
