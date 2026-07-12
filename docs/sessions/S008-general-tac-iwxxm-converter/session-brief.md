---
session_id: S008-general-tac-iwxxm-converter
type: feature
status: in_progress
branch: evolve/S008-general-tac-iwxxm-converter
started_at: 2026-07-12
intent: "Design a generalizable, high-performance TAC→IWXXM converter library (C/Cython-capable) covering WMO IWXXM + NOAA IWXXM-US extensions, with accuracy metrics and format extensibility"
orchestrator: 16-evolve
evolve_cycle_id: null
context_briefs:
  - docs/context/general-tac-iwxxm-converter.md
standing_docs_touched:
  - docs/adr/ADR-013-tac2iwxxm-package-architecture.md
  - docs/context/general-tac-iwxxm-converter.md
---

# Session S008 — general TAC→IWXXM converter

## Intent

Act as research/design partner for a general converter package (gifts-like layout under `packages/`) that:

- Converts TAC (METAR/SPECI first; expandable to TAF, AIRMET, SIGMET, …) → IWXXM XML
- Supports [WMO IWXXM](https://github.com/wmo-im/iwxxm) Schematron/XSD **and** [NOAA MDL IWXXM-US](https://vlab.noaa.gov/web/mdl/data-modeling) national extensions
- Uses a Python public API with optional C/Cython hotspots (NumPy-style)
- Measures conversion accuracy and covers edge cases
- Remains extensible for new formats without rewriting the core

## Scope

**In**

- Architecture brief + package boundary decisions
- Product/tech delta for a new Fn (or evolve F1) via 01/04/16-evolve
- Mapping of IWXXM-US METAR/SPECI + TAF extension types to a remark/extension pipeline

**Out (this session until evolve build)**

- Implementing Cython modules or shipping a new package
- Rewriting `packages/gifts` in-place (conflicts with REQ-014 / REQ-016 unless explicitly approved)
- Deploy / Render changes

## Routing plan

See [routing-plan.md](./routing-plan.md).

## Links

- Scoped brief: [general-tac-iwxxm-converter.md](../../context/general-tac-iwxxm-converter.md)
- Standing: [feature-list.md](../../feature-list.md), [spec.md](../../spec.md), [CORPUS.md](../../CORPUS.md)
- Prior gifts: [packages/gifts](../../../packages/gifts)
- Vendor WMO: [vendor/schemas/iwxxm](../../../vendor/schemas/iwxxm)
- Upstream: [wmo-im/iwxxm](https://github.com/wmo-im/iwxxm), [MDL Data Modeling](https://vlab.noaa.gov/web/mdl/data-modeling)
