# Product × engine honesty matrix

**Ticket:** [#1226](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1226) (program) · baseline [#1224](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1224)  
**Session:** `EV-yaml-full-configurability`  
**Status:** M4 in progress (#1230) — TAF → **full**; SIGMET/AIRMET/VAA/TCA remain  
**TC lock:** TC-EVYEC-001 · TC-EVYFC-001 (M5) · TC-EVYFC-005 (METAR/SPECI) · TC-EVYFC-002 (emit) · TC-EVYFC-006 (TAF row)

[Corpus: product §F2/F6/F9/F12/F15] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046] [Corpus: adr/ADR-047] [Corpus: tests]

Cells today (honesty): **full** | **partial** | **stub** | **N/A**  
Program success: every in-scope cell becomes **full** with evidence (M2–M5).

| Product | Decode pack | TAC quality policy | TAC detector YAML | IWXXM output policy | Convert pack-IR | Convert emit |
|---------|-------------|--------------------|-------------------|---------------------|-----------------|--------------|
| METAR | full | full | full | full | full | full |
| SPECI | full | full | full | full | full | full |
| TAF | full | full | full | full | full | full |
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
- TAC detector **python residuals** (same class as decode enrichment): R1 field-order (`hatch_r1_order`), R3 WMO 4678 weather grammar + span edge cases (`hatch_r3`), R4 register membership (`hatch_r4_membership`), R5 multi-token PK WND + `iwxxm_us` profile extension (`hatch_r5_pk_and_extension`), TAF A5-1 checklist (`hatch_taf`). **M2/M4 decision:** these do **not** block detectors `full` when packs are YAML DSL SoT and residuals are named python hatches only.
- Convert emit **python builders** remain the XML constructors referenced by emit-map `plugin:` entrypoints. **M3/M4 decision:** YAML emit maps are the SoT for METAR/SPECI/TAF routing (`TAC2IWXXM_EMIT_MAP_DIR`); builders do **not** block emit `full` (ADR-047 / TC-EVYFC-002).
- TAF decode residual: catch-all `token` rule remains for free groups after named A5-1 patterns — does **not** block decode `full`.

## Evidence (M2–M4)

| Engine | METAR/SPECI SoT | TAF SoT |
|--------|-----------------|---------|
| Decode pack | `tac_decoding/data/packs/{metar,speci}.yaml` | `tac_decoding/data/packs/taf.yaml` |
| TAC quality | `annex3-metar-quality.yaml` + detectors list | `annex3-taf-quality.yaml` + `taf-core` |
| TAC detectors | `metar-speci-r{1,2,3,4,5,8}-*.yaml` | `taf-core.yaml` (`hatch_taf`) |
| IWXXM output policy | `annex3-iwxxm-output.yaml` | same pin-scoped policy |
| Convert pack-IR | `TAC2IWXXM_CONVERT_IR_SOURCE` auto → pack | same (TAF in `_PACK_DEFAULT_PRODUCTS`) |
| Convert emit | `emit_maps/*-metar-speci.yaml` | `emit_maps/*-taf.yaml` (`pass_product: false`) |

DX smoke: `make overlay-preflight` · package CLIs `--check-overlay` · TC-EVYFC-002/003/005/006.

## Program follow-ups (#1226)

1. M1: templates + evidence — **done** (#1227 / #1234).
2. M2: METAR+SPECI full (minus emit) — **done** (#1228).
3. M3: emit YAML pilot METAR→SPECI — **done** (#1229).
4. M4: remaining products → full — **in progress** (TAF this PR; SIGMET/AIRMET/VAA/TCA next).
5. M5: all-full CI + pin↔SCH.
