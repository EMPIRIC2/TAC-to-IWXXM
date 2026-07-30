# Execution plan — S027 / EV-021 (F26 / F27 + F6.f·F12·F7.g deepen)

> **Status**: **approved** (2026-07-29) — E21-T1..T6 (1 / 1 / 1 / 1 / 1 / 1)  
> **Branch**: `evolve/EV-021-vaa-quality`  
> **Evolve cycle**: EV-021  
> **Features**: F26 (new); F27 (new); deepen F6.f / F12 / F7.g  
> **Spec sources**: feature-list §F26/F27; ADR-028; ADR-032; UJ-037/038; TC-F26/TC-F27;
> COVERAGE_MATRIX F26 V1–V3/C1 / F27 T1–T3/C1; api-contract S027; config-spec;
> E21-*; S02.M1/M2/L1; inventory `reports/wmo-vaa-tca-examples-inventory.md`

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase D — Complete |
| **Active milestone** | M6 — Smoke / verify / AC / deploy |
| **Active task** | — (all done) |
| **Tasks** | 26 / 26 completed |
| **Last updated** | 2026-07-30 |

## Tech Stack Summary

| Area | Choice | Source |
|------|--------|--------|
| Registry | Reuse ADR-028 `tac-validate`; add VAA + TCA rows | F26/F27 |
| Golden compare | `canonicalize_xml` under default convert settings | ADR-032; E21-2 |
| Products | VAA (`va-advisory-A7-2`) + TCA (`tc-advisory-A2-2`) | E21-1; E21-2 |
| Themes | **F26 themes** V1–V3/C1; **F27 themes** T1–T3/C1 (prefix mandatory) | E21-D3; S02.M1 |
| Catalog (FE) | Incremental unlock — VAA when F26 greens; TCA when F27 greens | S02.M2; E21-3 |
| Research | Close inventory — theme→fixture map; light guidance dig | E21-T2=1 |
| CI | Extend combined **`wmo-quality.yml`** with VAA+TCA packs | S02.L1; E21-T1 |
| New deps | **None** | E21-T3=1 |
| HTTP wire | Unchanged; `product=vaa` / `product=tca` already exist | api-contract |
| Deploy | API+FE redeploy if changed; H1–H3 if API; **H4–H5 when FE** | E21-T4=1 |
| Kill-switch | Mid-build theme explosion → AskQuestion (no silent defer) | E21-T5=1 |

## Interview locks

| ID | Decision |
|----|----------|
| E21-T1 | Milestone order **1** — M0→VAA lint→VAA golden→TCA lint→TCA golden→catalog→smoke |
| E21-T2 | Research **1** — close inventory; light dig |
| E21-T3 | Deps **1** — none |
| E21-T4 | Deploy **1** — redeploy; H1–H3 if API; H4–H5 when FE |
| E21-T5 | Kill-switch **1** — AskQuestion; no silent defer |
| E21-T6 | Plan **1** — approve M0–M6; skip 05/06; B→C → 07 @ T0.1 |
| S02.M1 | Keep F26 V1–V3 / F27 T1–T3 + Fn-theme prefix |
| S02.M2 | Incremental catalog unlock per product |
| S02.L1 | Extend `wmo-quality.yml` |

## Milestones & Tasks (TDD order)

`evolve_cycle_id: EV-021` · `feature_ids: [F26, F27, F6, F12, F7]`

### M0 — Research close + extend WMO quality CI

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T0.1 | Docs | Close inventory: map **F26 themes V1–V3/C1** + **F27 themes T1–T3/C1** → vendor goldens + translation TAC fixtures + guidance rows; write `reports/vaa-tca-theme-fixture-map.md`; cite keep-green F23–F25 | E21-T2; #736/#737 | — | **completed** |
| T0.2 | Docs | Link map from COVERAGE_MATRIX F26/F27 sections; cite-only paywall | F26/F27 acc | T0.1 | **completed** |
| T0.3 | Config | Extend `.github/workflows/wmo-quality.yml` + `scripts/ci/run_wmo_quality.sh` (+ Makefile if needed) with VAA+TCA keyword filters; add S027 path triggers; keep F23–F25 green | S02.L1; E21-T1 | T0.2 | **completed** |

### M1 — F26 VAA lint (themes V1–V2)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T1.1 | Test | Accept/negative fixtures **F26 theme V1** (UNKNOWN/UNNAMED, nilReasons, OBS/FCST status, remarks NIL, `NO FURTHER ADVISORIES`, …) | TC-F26-001/004; V1 | T0.2 | **completed** |
| T1.2 | Code | Registry rows + VAA rules for V1 | F26; ADR-028; F12 | T1.1 | **completed** |
| T1.3 | Test | Fixtures **F26 theme V2** (VAA ↔ VA SIGMET adjacency) | TC-F26-006; V2 | T1.2 | **completed** |
| T1.4 | Code | Product/root guards — never emit `VolcanicAshSIGMET` under `product=vaa` | F26; #736/#739 | T1.3 | **completed** |

### M2 — F26 VAA golden (theme V3) + C1

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T2.1 | Test | Golden `va-advisory-A7-2`; M-xsd/M-sch stubs; root `iwxxm:VolcanicAshAdvisory` | TC-F26-002/003; V3 | T1.4 | **completed** |
| T2.2 | Code | Convert fidelity toward vendor shape (defaults only) | F6.f; #736 | T2.1 | **completed** |
| T2.3 | Docs | Mark F26 themes V1–V3 closed or AskQuestion-deferred (E21-T5) | E21-T5 | T2.2 | **completed** |
| T2.4 | Test | **F26 theme C1** + translation-failed not happy-path | TC-F26-004; C1 | T2.3 | **completed** |

### M3 — F27 TCA lint (themes T1–T2)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T3.1 | Test | Accept/negative fixtures **F27 theme T1** (UNNAMED, CB NIL, remarks NIL, `NO MSG EXP`, wind &lt;34 kt, no-longer-TC, …) | TC-F27-001/004; T1 | T2.4 | **completed** |
| T3.2 | Code | Registry rows + TCA rules for T1 | F27; ADR-028; F12 | T3.1 | **completed** |
| T3.3 | Test | Fixtures **F27 theme T2** (TCA ↔ TC SIGMET adjacency) | TC-F27-006; T2 | T3.2 | **completed** |
| T3.4 | Code | Product/root guards — never emit `TropicalCycloneSIGMET` under `product=tca` | F27; #737/#738 | T3.3 | **completed** |

### M4 — F27 TCA golden (theme T3) + C1

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T4.1 | Test | Golden `tc-advisory-A2-2`; M-xsd/M-sch; root `iwxxm:TropicalCycloneAdvisory` | TC-F27-002/003; T3 | T3.4 | **completed** |
| T4.2 | Code | Convert fidelity toward vendor shape (defaults only; RMK NIL → remarks inapplicable) | F6.f; #737 | T4.1 | **completed** |
| T4.3 | Docs | Mark F27 themes T1–T3 closed or AskQuestion-deferred | E21-T5 | T4.2 | **completed** |
| T4.4 | Test | **F27 theme C1** + translation-failed adjacency | TC-F27-004; C1 | T4.3 | **completed** |

### M5 — F7.g catalog unlock (incremental) + keepers

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T5.1 | Test | Vitest: VAA Examples unlock only when F26 golden greens; TCA independently (S02.M2); hide `vaa_basic`/`tca_basic` until replaced | TC-F26-005; TC-F27-005; TC-F7-008 | T4.4 | **completed** |
| T5.2 | Code | FE catalog gate + provenance; unlock VAA/TCA as respective goldens green | F7.g; UJ-037/038; S02.M2 | T5.1 | **completed** |
| T5.3 | Test | Keep F23–F25 WMO packs green (regression) | F23–F25 | T5.2 | **completed** |

### M6 — Smoke / verify / AC / deploy

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T6.1 | Test | API/workbench smoke VAA + TCA (lint/convert) | TC-F26-005; TC-F27-005 | T5.3 | **completed** |
| T6.2 | Config | 08-verify-build — lint/typecheck/format/full suites | 08 | M0–M5 | **completed** |
| T6.3 | Test | 10-e2e — UJ-037 / UJ-038 (+ UJ-032 deepen) | 10 | T6.2 | **completed** |
| T6.4 | Docs | 11-verify-impl — per-Fn AC sign-off F26/F27 + deepen | 11 | T6.3 | **completed** (D-S027-11-approve) |
| T6.5 | Test | 13-deploy-smoke — redeploy if API/FE; H1–H3 if API; **H4–H5 when FE** | 13; E21-T4 | T6.4 | **completed** (D-S027-E21-13-merge) |

## Data Dependencies

| Asset | Needed by | Notes |
|-------|-----------|-------|
| Vendor `TAC-to-XML-Guidance.txt` + 2025-2 examples/XSD/SCH | M0–M4 | Read-only vendor |
| #736 VAA / #737 TCA exceptional rules | M1–M4 | Issue bodies |
| `va-advisory-A7-2`, `tc-advisory-A2-2` | M2, M4 | Vendor goldens |
| iwxxm-translation Amd79-80-2023 advisory TAC cases | M1, M3 | TAC themes only (E21-D4) |
| F23–F25 goldens (keep green) | M0 CI / M5 | Regression |
| Inventory seed | M0 | `reports/wmo-vaa-tca-examples-inventory.md` |

## Git Strategy

- Branch: `evolve/EV-021-vaa-quality`
- Atomic commits per task: `[T1.1] test: …`
- Evolve PR to `main` after M6 / Phase D
- After push: `bash scripts/ci/watch_github_ci.sh`
- **HARD themes (E21-T5)**: if blocked mid-build → AskQuestion; do **not** silently defer
- Theme ids: always “F26 theme Vn” / “F27 theme Tn” vs F23 VA-SIGMET V1–V3 (`D-S027-EV021-s02m1-1`)
- Combined workflow: `wmo-quality.yml` extended (S02.L1) — still run full `ci-cd.yml` on PRs

## Connectivity (H0c / H4–H5)

- No new CORS / `VITE_*` knobs expected
- FE catalog unlock → **H4–H5 when FE** after deploy (E21-T4)
- Re-run H0c if API image changes
- Staging secrets matrix: reuse existing rows

## Phase Gate Check (B→C)

- [x] Execution plan approved by user (E21-T6=1)
- [x] 05-verify-tech — **skipped** (Lean+build+11); 04-exit consistency PASS (below)
- [x] 06-tech-tooling — **skipped** (Lean+build+11; no new hooks in plan)

## 04-exit consistency (05 substitute)

| Check | Result |
|-------|--------|
| F26/F27 ↔ milestones M0–M6 | **PASS** |
| ADR-028/032 ↔ registry + golden tasks | **PASS** |
| UJ-037/038 ↔ T6.1/T6.3 | **PASS** |
| TC-F26/F27 ↔ M1–M5 | **PASS** |
| S02.L1 `wmo-quality.yml` ↔ T0.3 | **PASS** |
| S02.M2 incremental catalog ↔ T5.1/T5.2 | **PASS** |
| S02.M1 theme prefix ↔ Git Strategy + theme tasks | **PASS** |
| E21-T3 no new deps ↔ Tech Stack | **PASS** |
| E21-T4 H4–H5 ↔ T6.5 | **PASS** |
| E21-T5 kill-switch ↔ T2.3/T4.3 | **PASS** |
| Template (static+api+worker) | **PASS** — no new deployable |
| New deps inventory | **PASS** — none |

## PR Plan

| PR | Scope | Status |
|----|-------|--------|
| [#794](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/794) | S027 / EV-021 — F26/F27 VAA + TCA quality | **merged** `df56d1f` |
