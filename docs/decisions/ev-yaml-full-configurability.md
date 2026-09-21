# EV-yaml-full-configurability — decision lock

**Session:** `EV-yaml-full-configurability`  
**Date:** 2026-09-21  
**Epic:** [#1226](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1226)  
**ADR:** [ADR-047](../adr/ADR-047-convert-emit-yaml-full-matrix.md) (Proposed)

[Corpus: product] [Corpus: adr/ADR-047] [Corpus: adr/ADR-044] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046] [Corpus: decisions]

## Locked decisions

| ID | Decision |
|----|----------|
| D-YFC-01 | End-state: every product × every engine cell **full**, including convert emit YAML |
| D-YFC-02 | Multi-milestone on `stage`: M1 DX → M2 METAR/SPECI full (no emit) → M3 emit pilot → M4 remaining parallel → M5 all-full + pin↔SCH |
| D-YFC-03 | ADR-047 declarative emit map; stable `tac2iwxxm.convert`; env overlays only |
| D-YFC-04 | No in-app editor; no HTTP pack/policy YAML; no Schematron-as-YAML; no #1222 unless reopen |
| D-YFC-05 | Schematron vendor SoT; pin must match emit/validate IWXXM version (tests) |
| D-YFC-06 | Detectors in scope until cells full; IWXXM output policy YAML + vendor XSD/SCH |
| D-YFC-07 | H4–H5 N/A unless OpenAPI/UI changes |
| D-YFC-08 | Scale **full**; verification = SoT + overlay behavior + golden + matrix CI |

## Baseline

Honesty + overlays already on `stage` via #1224 / #1225.
