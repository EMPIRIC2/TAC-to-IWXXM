# Product × engine honesty matrix

**Ticket:** [#1226](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1226) (program) · baseline [#1224](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1224)  
**Session:** `EV-yaml-full-configurability`  
**Status:** M4 complete for matrix products (#1230) — METAR…TCA → **full**  
**TC lock:** TC-EVYEC-001 · TC-EVYFC-001 (M5) · TC-EVYFC-005 · TC-EVYFC-002 · TC-EVYFC-006 · TC-EVYFC-007 · TC-EVYFC-008

[Corpus: product §F2/F6/F9/F12/F15] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046] [Corpus: adr/ADR-047] [Corpus: tests]

Cells today (honesty): **full** | **partial** | **stub** | **N/A**  
Program success: every in-scope cell becomes **full** with evidence (M2–M5).

| Product | Decode pack | TAC quality policy | TAC detector YAML | IWXXM output policy | Convert pack-IR | Convert emit |
|---------|-------------|--------------------|-------------------|---------------------|-----------------|--------------|
| METAR | full | full | full | full | full | full |
| SPECI | full | full | full | full | full | full |
| TAF | full | full | full | full | full | full |
| SIGMET | full | full | full | full | full | full |
| AIRMET | full | full | full | full | full | full |
| VAA | full | full | full | full | full | full |
| TCA | full | full | full | full | full | full |

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
- TAC detector **python residuals** (same class as decode enrichment): R1 field-order (`hatch_r1_order`), R3 WMO 4678 weather grammar (`hatch_r3`), R4 register membership (`hatch_r4_membership`), R5 multi-token PK WND (`hatch_r5_pk_and_extension`), plus `hatch_taf` / `hatch_sigmet` (`sigmet-core`) / `hatch_airmet` / `hatch_vaa` / `hatch_tca`. **M2/M4 decision:** these do **not** block detectors `full` when packs are YAML DSL SoT and residuals are named python hatches only.
- Convert emit **python builders** remain the XML constructors referenced by emit-map `plugin:` entrypoints. **M3/M4 decision:** YAML emit maps are the SoT for METAR/SPECI/TAF/SIGMET/AIRMET/VAA/TCA routing (`TAC2IWXXM_EMIT_MAP_DIR`); builders do **not** block emit `full` (ADR-047 / TC-EVYFC-002).
- Decode residuals: catch-all `token` on token-stream packs under `data/packs/`; VAA/TCA label packs keep free-text in label values — does **not** block decode `full`. Policies live under `tac_validate/data/policies/`.

## Evidence (M2–M4)

| Engine | Core-obs SoT | Forecast SoT | Hazard SoT | Advisory SoT |
|--------|--------------|--------------|------------|--------------|
| Decode pack | `{metar,speci}.yaml` | `taf.yaml` | `{sigmet,va_sigmet,tc_sigmet,airmet}.yaml` | `{vaa,tca}.yaml` labels |
| TAC quality | `annex3-metar-quality` | `annex3-taf-quality` | `annex3-{sigmet,airmet}-quality` | `annex3-{vaa,tca}-quality` |
| TAC detectors | `metar-speci-r*.yaml` | `taf-core` | `{sigmet,airmet}-core` | `{vaa,tca}-core` |
| IWXXM output policy | `annex3-iwxxm-output.yaml` (pin-scoped) | same | same | same |
| Convert pack-IR | `_PACK_DEFAULT_PRODUCTS` | same | same | same |
| Convert emit | `*-metar-speci.yaml` | `*-taf.yaml` | `*-{sigmet,airmet}.yaml` | `*-{vaa,tca}.yaml` |

DX smoke: `make overlay-preflight` · package CLIs `--check-overlay` · TC-EVYFC-002/003/005/006/007/008.

## Program follow-ups (#1226)

1. M1: templates + evidence — **done** (#1227 / #1234).
2. M2: METAR+SPECI full (minus emit) — **done** (#1228).
3. M3: emit YAML pilot METAR→SPECI — **done** (#1229).
4. M4: remaining products → full — **done** (TAF #1239 · SIGMET #1240 · AIRMET/VAA/TCA this PR).
5. M5: all-full CI + pin↔SCH (#1231).
