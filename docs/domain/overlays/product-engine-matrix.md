# Product × engine honesty matrix (draft)

**Ticket:** [#1224](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1224)  
**Session:** EV-yaml-engine-configurability  
**Status:** draft (Spec band) — Build locks cells with TC-EVYEC-001

[Corpus: product §F2/F6/F9/F12/F15] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046] [Corpus: tests]

Cells: **full** | **partial** | **stub** | **N/A**

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

- Mined catalogs under `tac2iwxxm/data/*.yaml` are **projections**, not executors — not a “full” convert column.
- IWXXM **XSD/Schematron** remain vendor SoT; output policy only selects/ignores assert ids.
- Airport name enrichment on decode is a **Python** resolver hook, not YAML.

## Build follow-ups

1. Replace draft cells with evidence-backed ratings in tech-plan / Build.
2. CI presence/schema lock (TC-EVYEC-001).
