# Product × engine honesty matrix

**Ticket:** [#1226](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1226) (program) · baseline [#1224](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1224)  
**Session:** `EV-yaml-full-configurability`  
**Status:** baseline snapshot after #1225 — **end-state target = all cells full** (ADR-047)  
**TC lock:** TC-EVYEC-001 (presence) · TC-EVYFC-001 (all-full gate at M5)

[Corpus: product §F2/F6/F9/F12/F15] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046] [Corpus: adr/ADR-047] [Corpus: tests]

Cells today (honesty): **full** | **partial** | **stub** | **N/A**  
Program success: every in-scope cell becomes **full** with evidence (M2–M5).

| Product | Decode pack | TAC quality policy | TAC detector YAML | IWXXM output policy | Convert pack-IR | Convert emit |
|---------|-------------|--------------------|-------------------|---------------------|-----------------|--------------|
| METAR | partial | partial | partial | partial | partial | partial (Python plugins) |
| SPECI | partial | partial | partial | partial | partial | partial (Python plugins) |
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
- Airport name enrichment on decode is a **Python** resolver hook, not YAML (may remain partial even when pack rules are full — Spec must call out if enrichment blocks `full`).

## Program follow-ups (#1226)

1. M1: templates + evidence upgrade where cheap.
2. M2: METAR+SPECI → full (except emit).
3. M3: emit YAML pilot METAR→SPECI.
4. M4: remaining products → full (parallel).
5. M5: all-full CI + pin↔SCH.
