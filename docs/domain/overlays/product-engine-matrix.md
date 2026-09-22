# Product × engine honesty matrix

**Ticket:** [#1226](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1226) (program) · baseline [#1224](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1224)  
**Session:** `EV-yaml-full-configurability`  
**Status:** M2 in progress (#1228) — METAR/SPECI non-emit engines upgraded where evidence-backed; detectors deepen continues  
**TC lock:** TC-EVYEC-001 (presence) · TC-EVYFC-001 (all-full gate at M5) · TC-EVYFC-005 (M2 METAR/SPECI row lock)

[Corpus: product §F2/F6/F9/F12/F15] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046] [Corpus: adr/ADR-047] [Corpus: tests]

Cells today (honesty): **full** | **partial** | **stub** | **N/A**  
Program success: every in-scope cell becomes **full** with evidence (M2–M5).

| Product | Decode pack | TAC quality policy | TAC detector YAML | IWXXM output policy | Convert pack-IR | Convert emit |
|---------|-------------|--------------------|-------------------|---------------------|-----------------|--------------|
| METAR | full | full | partial | full | full | partial (Python plugins) |
| SPECI | full | full | partial | full | full | partial (Python plugins) |
| TAF | partial | partial | stub | partial | partial | partial (Python plugins) |
| SIGMET | partial | stub | stub | partial | partial | partial (Python plugins) |
| AIRMET | partial | stub | stub | partial | partial | partial (Python plugins) |
| VAA | partial | stub | stub | partial | partial | partial (Python plugins) |
| TCA | partial | stub | stub | partial | partial | partial (Python plugins) |

## Legend

| Cell | Meaning |
|------|---------|
| full | Primary behavior driven by package YAML + documented overlays for this product |
| partial | Mix of YAML and imperative Python; overlays work for the YAML portion |
| stub | Builtin exists but thin / not product-complete |
| N/A | Not applicable for this engine×product |

## Notes

- Mined catalogs under `tac2iwxxm/data/*.yaml` are **projections**, not executors — not a “full” convert column until emit map (ADR-047) ships.
- IWXXM **XSD/Schematron** remain vendor SoT; output policy only selects/ignores assert ids. Pin↔SCH must match (TC-EVYFC-004).
- Airport name enrichment on decode is a **Python** resolver hook (`set_location_name_resolver`), not pack YAML. **M2 decision:** enrichment does **not** block decode `full` when the token-stream pack is YAML SoT (D-YFC / Build scope 2a).
- TAC detectors (M2 deepen): R1 identity + R2 visibility + R4 cloud shape/CB + R5 SLP/P/T malform + R8 modifiers are declarative DSL; residuals (R1 order, R3 weather grammar, R4 membership, R5 PK WND + iwxxm_us extension) stay python → cell stays **partial**.

## Evidence (M2 / #1228)

| Engine | METAR/SPECI evidence |
|--------|----------------------|
| Decode pack | `packages/tac-decoding/src/tac_decoding/data/packs/{metar,speci}.yaml` + starters/overlays; enrichment hook documented above |
| TAC quality | `packages/tac-validate/src/tac_validate/data/policies/annex3-metar-quality.yaml` (`product: metar` covers SPECI tags) + `detectors:` pack id list |
| TAC detectors | `packages/tac-validate/src/tac_validate/data/detectors/metar-speci-r{1,2,3,4,5,8}-*.yaml` — R3 + R1 order + R4 membership + R5 PK/extension still python → **partial** |
| IWXXM output policy | `packages/iwxxm-validate/src/iwxxm_validate/data/policies/annex3-iwxxm-output.yaml` + starters |
| Convert pack-IR | `TAC2IWXXM_CONVERT_IR_SOURCE` auto → `pack` for METAR/SPECI (`tac2iwxxm.ir_source`) |
| Convert emit | Python plugins until ADR-047 emit map (M3+) |

DX smoke: `make overlay-preflight` · package CLIs `--check-overlay` · TC-EVYFC-003 · TC-EVYFC-005.

## Program follow-ups (#1226)

1. M1: templates + evidence upgrade where cheap — **done** (#1227 / #1234).
2. M2: METAR+SPECI → full (except emit) — **in progress** (detectors residual R3 + R1 order + R4 membership + R5 PK/extension).
3. M3: emit YAML pilot METAR→SPECI.
4. M4: remaining products → full (parallel).
5. M5: all-full CI + pin↔SCH.
