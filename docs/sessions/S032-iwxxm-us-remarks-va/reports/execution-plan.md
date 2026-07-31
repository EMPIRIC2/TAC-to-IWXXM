# Execution plan — S032 / EV-025 (#810–#812 iwxxm-us REMARKS + #809 VA multi-location)

> **Status**: **approved** (2026-07-31) — E25-T1..T6 (1 / 1 / 2 / 1 / 3 / 1); Gate B=`1` (`D-S032-04-plan-approve`)  
> **Branch**: `evolve/EV-025-iwxxm-us-remarks-va`  
> **Evolve cycle**: EV-025  
> **Features**: deepen F6 / F6.b / F12 / F2 / F13 / F23 — no new Fn  
> **Spec sources**: feature-list §S032; spec §S032/EV-025; UJ-040/041; TC-EV025-001..010;
> E25-*; S02.M1/M2/L1; E25-T5 **supersedes** S02.M2 Gate C soft-deferral; #810/#811/#812/#809;
> `docs/domain/mining/iwxxm-us-metar-speci-pdf-mining-notes.md` dig checklist

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase C — Build |
| **Active milestone** | M4 |
| **Active task** | T4.4 (next) |
| **Tasks** | 14 / 28 |
| **Last updated** | 2026-07-31 |

## Tech Stack Summary

| Area | Choice | Source |
|------|--------|--------|
| Runtime SoT | Vendor pin IWXXM **v2025-2** + iwxxm-us **3.0** | E25; dig notes |
| Encode | `packages/tac2iwxxm` `profile=iwxxm_us` | F6.b |
| Lint | `packages/tac-validate` registry (ADR-028) as needed | F12 |
| Validate | `packages/iwxxm-validate` combined catalog / extension smoke | F2/F13 |
| Goldens | Per dig type/row where feasible (encode + lint) | E25-T2=1 |
| #809 | Soft-compare first; `wmoPass` only under ADR-032 equality | S02.M1 |
| Dig ❌ residuals | **Block Gate C** — no child-issue escape for encode gaps | E25-T5=3 |
| SCH smoke | TC-EV025-010 may document SCH deferrals (does not unblock dig ❌) | S02.L1 |
| Lane order | Finish Lane A (US) then Lane B (#809) | E25-T4=1 |
| New deps | AskQuestion per new dep (prefer none) | E25-T3=2 |
| Deploy | 13 when convert/validate ships | E25-3 |
| UI | N/A | E25-ui=1 |

## Interview locks

| ID | Decision |
|----|----------|
| E25-T1 | Order **1** — M0→#810→#811→#812→adjacent→#809 soft→strict→validate→Gate C audit/smoke |
| E25-T2 | Goldens **1** — encode (+lint) per dig type/row where feasible |
| E25-T3 | Deps **2** — AskQuestion per new dep |
| E25-T4 | Lanes **1** — finish Lane A then Lane B |
| E25-T5 | Residuals **3** — any dig ❌ encode residual **blocks Gate C** (supersedes S02.M2 soft deferral) |
| E25-T6 | Draft **1** — plan from T1–T5; Gate B AskQuestion next |

## Milestones & Tasks (TDD order)

`evolve_cycle_id: EV-025` · `feature_ids: [F6, F12, F2, F13, F23]`

### M0 — Theme map + dig audit scaffold

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T0.1 | Docs | Map TC-EV025-001..010 → dig checklist rows / fixture paths; `reports/us-remarks-va-theme-map.md` | TC-EV025 | — | **completed** |
| T0.2 | Docs | Code-audit dig table: ❌/⚠/✅ vs current `tac2iwxxm`/`tac-validate`; list M1–M4 work queue | mining notes | T0.1 | **completed** |

### M1 — #810 Variable RVR / meanRVR withheld

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T1.1 | Test | Red golden(s) for Variable RVR + meanRVR withheld / nilReason | TC-EV025-001 | T0.2 | **completed** |
| T1.2 | Code | Encode `AerodromeVariableRVR` (+ lint registry if needed) | #810; F6.b/F12 | T1.1 | **completed** |
| T1.3 | Test | Green encode/lint; update COVERAGE_MATRIX / IWXXM_CONVERSION rows | TC-EV025-001 | T1.2 | **completed** |

### M2 — #811 Lightning / VisuallyObservablePhenomena

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T2.1 | Test | Red golden(s) for ObservedLightning / Frequency / Type + VOP bundle | TC-EV025-002 | T1.3 | **completed** |
| T2.2 | Code | Encode lightning + VOP (+ related); lint as needed | #811; F6.b/F12 | T2.1 | **completed** |
| T2.3 | Test | Green pack; matrix rows | TC-EV025-002 | T2.2 | **completed** |

### M3 — #812 SnowIncrease + sensor outage

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T3.1 | Test | Red golden(s) for SnowIncrease + Failed/Inoperative/MeteorologicalSensors | TC-EV025-003 | T2.3 | **completed** |
| T3.2 | Code | Encode snow-increase + sensor-outage remarks (+ lint) | #812; F6.b/F12 | T3.1 | **completed** |
| T3.3 | Test | Green pack; matrix rows | TC-EV025-003 | T3.2 | **completed** |

### M4 — Adjacent dig ❌ US type packs (Lane A remainder)

Per-type/row goldens where feasible (E25-T2). Packs may split further in 07 if a type balloons.

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T4.1 | Test+Code | AerodromeWindShift (+ PeakWind deepen if still ❌/⚠) | TC-EV025-004 | T3.3 | **completed** |
| T4.2 | Test+Code | CharacterOfTheSky / CloudTypes / ConvectiveCloud* / HailstoneSize | TC-EV025-004 | T4.1 | **completed** |
| T4.3 | Test+Code | Sector / Obscurations / SecondLocation / TowerVisibility | TC-EV025-004 | T4.2 | **completed** |
| T4.4 | Test+Code | VariableCeilingHeight / VariableSky / VariableVisibility | TC-EV025-004 | T4.3 | pending |
| T4.5 | Test+Code | MaxMinTemperatures + ProcessedProperty / statistical + ObservingSystem codelists | TC-EV025-004 | T4.4 | pending |
| T4.6 | Test+Code | Addendum residuals (AO1/flags/text not yet structured) + RecentWeather deepen if ❌ | TC-EV025-004 | T4.5 | pending |
| T4.7 | Docs | Dig checklist refresh — all Lane A encode rows ✅ (or blocked AskQuestion) | E25-T5=3 | T4.6 | pending |

### M5 — #809 VA multi-location (Lane B)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T5.1 | Test | Soft-compare package golden for `sigmet-multi-location-VA` | TC-EV025-008; S02.M1 | T4.7 | pending |
| T5.2 | Code | Convert fidelity until soft golden stable | #809; F23/F6 | T5.1 | pending |
| T5.3 | Test | Promote `wmoPass` only when ADR-032 equality holds; else reference + FIXTURE_GAPS | TC-EV025-009 | T5.2 | pending |

### M6 — Deepen / validate smoke

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T6.1 | Test | US fixtures never appear in WMO sample menu | TC-EV025-005 | T4.7 | pending |
| T6.2 | Test | Malformed US REMARKS diagnostics | TC-EV025-006 | T4.7 | pending |
| T6.3 | Test | Unparsed REMARKS remain in `humanReadableText` | TC-EV025-007 | T4.7 | pending |
| T6.4 | Test | Combined-catalog validate smoke; SCH deferrals documented OK (S02.L1) — does **not** waive dig ❌ | TC-EV025-010 | T4.7 | pending |

### M7 — Gate C dig close + smoke

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T7.1 | Docs | Final dig ❌→✅ audit; **any remaining encode ❌ blocks Gate C** (E25-T5=3) | E25-4c; E25-T5 | T4.7; T5.3; T6.4 | pending |
| T7.2 | Test | 08-verify-build + 10-e2e smoke (US convert/validate + VA stem) | routing | T7.1 | pending |
| T7.3 | Deploy | 13-deploy-smoke **when** API convert/validate ships | E25-3 | T7.2 | pending |

## Data Dependencies

| Asset | Needed by | Notes |
|-------|-----------|-------|
| `.local/` PDF extract (gitignored) | M1–M4 sample TAC | From S031 extract; re-run extract-pdf-to-repo if missing |
| `vendor/schemas/iwxxm-us/3.0` | All Lane A | Read-only pin |
| Vendor `sigmet-multi-location-VA.{tac,xml}` | M5 | Under IWXXM pin |

## Git Strategy

- Branch: `evolve/EV-025-iwxxm-us-remarks-va`
- One task per atomic commit: `[T{n}.{m}] …`
- PR to main when M0–M7 complete (T7.3 may defer if no API ship)

## PR Plan

| PR | URL | Status |
|----|-----|--------|
| EV-025 / S032 | — | pending |

## PR checklist (draft)

- [ ] #810 / #811 / #812 goldens green
- [ ] Adjacent dig ❌ packs green (TC-EV025-004); dig table all encode ✅
- [ ] US fixtures out of WMO menu
- [ ] #809 soft→strict / promote path under ADR-032
- [ ] TC-EV025-001..010 (SCH deferrals documented only for -010)
- [ ] No new deps without AskQuestion
- [ ] 13 when behavior ships

## Gate B → C

**PASSED** 2026-07-31 — user Gate B=`1` (`D-S032-04-plan-approve`). Lean skip 05 → **07-build** @ T0.1.
