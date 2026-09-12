---
session_id: S008-general-tac-iwxxm-converter
type: feature
status: in_progress
branch: evolve/S008-general-tac-iwxxm-converter
started_at: 2026-07-12
intent: "General TAC→IWXXM converter (F6/tac2iwxxm) plus data-entry and near-realtime ingest conversion with Schematron gate on IWXXM output"
orchestrator: 16-evolve
evolve_cycle_id: null
amended_at: 2026-07-12
amend_decision: D-S008-realtime-amend-q1q2q3
context_briefs:
  - docs/context/general-tac-iwxxm-converter.md
  - docs/context/realtime-tac-ingest.md
standing_docs_touched:
  - docs/adr/ADR-013-tac2iwxxm-package-architecture.md
  - docs/adr/ADR-014-general-tac-iwxxm-f6.md
  - docs/context/general-tac-iwxxm-converter.md
  - docs/context/realtime-tac-ingest.md
---

# Session S008 — general TAC→IWXXM converter (amended)

## Intent

**Amended 2026-07-12** (`D-S008-realtime-amend-q1q2q3`): keep the F6/tac2iwxxm converter design track, and expand scope to:

1. **General TAC data entry** — operator/UI paths for entering TAC (METAR/SPECI and broader products per F6)
2. **Near-realtime ingest pipeline** — continuous feed → near-RT convert + Schematron (not a one-shot batch job)
3. **Schematron gate on IWXXM only** — extend F2; TAC uses separate syntax/business checks (not Schematron)

Original design-partner intent (still in force for the converter package):

- Converts TAC (METAR/SPECI first; expandable to TAF, AIRMET, SIGMET, …) → IWXXM XML
- Supports [WMO IWXXM](https://github.com/wmo-im/iwxxm) Schematron/XSD **and** [NOAA MDL IWXXM-US](https://vlab.noaa.gov/web/mdl/data-modeling) national extensions
- Uses a Python public API with optional C/Cython (or Rust/PyO3 per ADR-014 amendments) hotspots
- Measures conversion accuracy and covers edge cases
- Remains extensible for new formats without rewriting the core

## Scope

**In**

- Architecture brief + package boundary decisions (existing `general-tac-iwxxm-converter` brief)
- **Scoped refresh** brief: `docs/context/realtime-tac-ingest.md` (active) for ingest + data-entry delta
- Product/tech delta via reopened **00-context (scoped)** → **01-requirements (delta)** → 04-tech-plan
- Mapping of IWXXM-US METAR/SPECI + TAF extension types to a remark/extension pipeline
- Near-RT ingest path: continuous feed → convert → IWXXM Schematron gate (extend F2)

**Out (this session until evolve build)**

- Implementing Cython/Rust modules or shipping a new package (build phase)
- Rewriting `packages/gifts` in-place outside approved ADR cutover
- Deploy / Render changes until wired in evolve plan

## Routing status (amend)

| Stage | Status |
|-------|--------|
| 00-context (scoped `realtime-tac-ingest`) | **completed** (2026-07-12) |
| 01-requirements (delta `S008-realtime-ingest`) | **in_progress** |
| 04-tech-plan | pending (after 01) |

See [routing-plan.md](./routing-plan.md).

**Note (2026-07-12):** Scoped 00-context brief written (`docs/context/realtime-tac-ingest.md`, status active). Next: 01-requirements delta manifest for S008-realtime-ingest.

## Links

- Scoped brief (converter): [general-tac-iwxxm-converter.md](../../context/general-tac-iwxxm-converter.md)
- Scoped brief (ingest amend, active): [realtime-tac-ingest.md](../../context/realtime-tac-ingest.md)
- Standing: [feature-list.md](../../feature-list.md), [spec.md](../../spec.md), [CORPUS.md](../../CORPUS.md)
- Prior gifts: [packages/gifts](../../../packages/gifts)
- Vendor WMO: [vendor/schemas/iwxxm](../../../vendor/schemas/iwxxm)
- Upstream: [wmo-im/iwxxm](https://github.com/wmo-im/iwxxm), [MDL Data Modeling](https://vlab.noaa.gov/web/mdl/data-modeling)
