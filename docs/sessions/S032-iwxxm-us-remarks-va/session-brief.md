---
session_id: S032-iwxxm-us-remarks-va
type: feature
status: completed
completed_at: 2026-07-31
branch: evolve/EV-025-iwxxm-us-remarks-va
started_at: 2026-07-31
intent: "Dual-lane: encode all ❌ iwxxm-us REMARKS types from #773 dig (#810+#811+#812 + adjacent) plus #809 WMO sigmet-multi-location-VA annex3 golden"
orchestrator: 16-evolve
evolve_cycle_id: EV-025
github_issues:
  - 810
  - 811
  - 812
  - 809
context_briefs:
  - docs/context/iwxxm-us-remarks-va.md
standing_docs_touched:
  - docs/feature-list.md
  - docs/test-plan.md
  - docs/decisions/evolve-decisions.md
  - docs/decisions/requirements-decisions.md
  - docs/domain/IWXXM_CONVERSION.md
  - docs/domain/TAC_VALIDATION.md
  - docs/domain/IWXXM_VALIDATION.md
  - docs/domain/rules/COVERAGE_MATRIX.md
feature_ids: [F6, F12, F2, F13, F23]
feature_note: "Deepen F6.b (full US dig ❌ encode) + F12 lint + F2/F13 extension validate; deepen F23 for #809 VA multi-location golden — no new Fn"
---

# Session S032 — iwxxm-us-remarks-va

## Intent

Implement **engine + goldens** for US METAR/SPECI REMARKS → `iwxxm-us` extensions mined in
S031 / EV-024 (#773), plus the deferred WMO VA multi-location convert golden (#809).

Runtime SoT: `vendor/manifest.json` → IWXXM **v2025-2** + `iwxxm-us` **3.0**. No hand-edits
to `vendor/schemas/*`. Do **not** add US examples to the WMO sample menu (UJ-039).

## Prior session

| Item | Disposition |
|------|-------------|
| S031 / EV-024 | **Completed** — domain mine; children #809–#812 filed; PR #813 |
| Dig notes | [iwxxm-us-metar-speci-pdf-mining-notes.md](../../domain/mining/iwxxm-us-metar-speci-pdf-mining-notes.md) |
| Gap list | [guidance-sch-assert-gap-list.md](../S031-iwxxm-domain-mine/reports/guidance-sch-assert-gap-list.md) |

## Scope (locked — E25-1..E25-4 + E25-4b/c)

### Lane A — iwxxm-us REMARKS (F6.b / F12 / F2·F13)

**Named tickets (full AC):**

| Issue | Focus |
|-------|--------|
| [#810](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/810) | Variable RVR / meanRVR withheld |
| [#811](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/811) | Lightning / VisuallyObservablePhenomena |
| [#812](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/812) | SnowIncrease + Failed/Inoperative/MeteorologicalSensors |

**Adjacent ❌ (and still-⚠) US types from dig checklist — all in scope (E25-4c=3):**

- Addendum residuals (beyond existing AO2/SLP/PK WND themes)
- AerodromeWindShift (WSHFT / FROPA)
- CharacterOfTheSky / CloudTypes
- ConvectiveCloudLocation / ConvectiveCloudTypes
- HailstoneSize
- MaxMinTemperatures
- Obscurations
- ObservedAtSecondLocation / SensorLocation / TowerVisibility
- RecentWeather (US extension path where distinct from WMO)
- Sector / SectorVisibility
- ProcessedProperty + statistical codelists
- VariableCeilingHeight / VariableSkyCondition / VariableVisibility
- Codelist href fidelity (`codes.nws.noaa.gov` where PDF requires)

Each type: tac-validate recognition as needed + tac2iwxxm encode to pin XSD + annex3/`iwxxm_us`
golden + combined-catalog validate smoke.

### Lane B — WMO VA multi-location (#809 / F23)

- Package annex3 golden (or soft-compare gate) for `sigmet-multi-location-VA`
- Root `iwxxm:VolcanicAshSIGMET`; multi-location geometry / forecast collections per Guidance
- Promote catalog tier to `wmoPass` only when ADR-032 equality holds under defaults

### Out

- USWX (non–Annex 3)
- Hand-edit `vendor/schemas/*`; commit PDF / full upstream clones
- Mixing US examples into WMO sample menu
- [#808](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/808) release-line maintainability dig
- TC SIGMET A6-2 (#738); SWX/VONA/WAFS/QVACI roadmap

## Routing

See [routing-plan.md](./routing-plan.md). **Approved** Lean+build (E25-3=1).

## UI preview

**N/A** (E25-ui=1) — package/engine cycle; no browser surface.

## Current stage

**00-context** complete → handoff **01-requirements** (delta).

## Links

- Issues: #810 · #811 · #812 · #809
- Parent dig: #773 (closed) · S031
- Context: [docs/context/iwxxm-us-remarks-va.md](../../context/iwxxm-us-remarks-va.md)
