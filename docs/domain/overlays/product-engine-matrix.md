# Product × engine honesty matrix

**Ticket:** [#1226](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1226) (program) · baseline [#1224](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1224)  
**Session:** `EV-yaml-full-configurability`  
**Status:** M3 in progress (#1229) — METAR/SPECI **emit** YAML-routed (ADR-047 Accepted); other products still plugin-only  
**TC lock:** TC-EVYEC-001 (presence) · TC-EVYFC-001 (all-full gate at M5) · TC-EVYFC-005 (M2 METAR/SPECI row lock) · TC-EVYFC-002 (emit parity)

[Corpus: product §F2/F6/F9/F12/F15] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046] [Corpus: adr/ADR-047] [Corpus: tests]

Cells today (honesty): **full** | **partial** | **stub** | **N/A**  
Program success: every in-scope cell becomes **full** with evidence (M2–M5).

| Product | Decode pack | TAC quality policy | TAC detector YAML | IWXXM output policy | Convert pack-IR | Convert emit |
|---------|-------------|--------------------|-------------------|---------------------|-----------------|--------------|
| METAR | full | full | full | full | full | full |
| SPECI | full | full | full | full | full | full |
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

- Mined catalogs under `tac2iwxxm/data/*.yaml` are **projections**, not executors — convert emit uses `data/emit_maps/` (ADR-047).
- IWXXM **XSD/Schematron** remain vendor SoT; output policy only selects/ignores assert ids. Pin↔SCH must match (TC-EVYFC-004).
- Airport name enrichment on decode is a **Python** resolver hook (`set_location_name_resolver`), not pack YAML. **M2 decision:** enrichment does **not** block decode `full` when the token-stream pack is YAML SoT (D-YFC / Build scope 2a).
- TAC detector **python residuals** (same class as decode enrichment): R1 field-order (`hatch_r1_order`), R3 WMO 4678 weather grammar + span edge cases (`hatch_r3`), R4 register membership (`hatch_r4_membership`), R5 multi-token PK WND + `iwxxm_us` profile extension (`hatch_r5_pk_and_extension`). **M2 decision:** these do **not** block detectors `full` when R1 identity / R2 / R4 shape / R5 SLP·P·T / R8 packs are YAML DSL SoT and residuals are named python hatches only.
- Convert emit **python builders** remain the XML constructors referenced by emit-map `plugin:` entrypoints. **M3 decision:** YAML emit maps are the SoT for METAR/SPECI routing (`TAC2IWXXM_EMIT_MAP_DIR` overlays); builders do **not** block emit `full` when the map is package YAML (ADR-047 Accepted / TC-EVYFC-002).

## Evidence (M2 / #1228 · M3 / #1229)

| Engine | METAR/SPECI evidence |
|--------|----------------------|
| Decode pack | `packages/tac-decoding/src/tac_decoding/data/packs/{metar,speci}.yaml` + starters/overlays; enrichment hook documented above |
| TAC quality | `packages/tac-validate/src/tac_validate/data/policies/annex3-metar-quality.yaml` (`product: metar` covers SPECI tags) + `detectors:` pack id list |
| TAC detectors | `packages/tac-validate/src/tac_validate/data/detectors/metar-speci-r{1,2,3,4,5,8}-*.yaml` + declarative DSL; residuals listed above → **full** |
| IWXXM output policy | `packages/iwxxm-validate/src/iwxxm_validate/data/policies/annex3-iwxxm-output.yaml` + starters |
| Convert pack-IR | `TAC2IWXXM_CONVERT_IR_SOURCE` auto → `pack` for METAR/SPECI (`tac2iwxxm.ir_source`) |
| Convert emit | `packages/tac2iwxxm/src/tac2iwxxm/data/emit_maps/*-metar-speci.yaml` + `emit_map.emit_with_map`; overlays via `TAC2IWXXM_EMIT_MAP_DIR` |

DX smoke: `make overlay-preflight` · package CLIs `--check-overlay` · TC-EVYFC-003 · TC-EVYFC-005 · TC-EVYFC-002.

## Program follow-ups (#1226)

1. M1: templates + evidence upgrade where cheap — **done** (#1227 / #1234).
2. M2: METAR+SPECI → full (except emit) — **done** (#1228).
3. M3: emit YAML pilot METAR→SPECI — **in progress** (#1229).
4. M4: remaining products → full (parallel).
5. M5: all-full CI + pin↔SCH.
