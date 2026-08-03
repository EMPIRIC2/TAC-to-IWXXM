# Execution plan — S037 / EV-030 (#831 / #829 / #820)

> **Status**: **approved** (2026-08-03) — `D-S037-04-plan` = 1; Gate B PASS → 07 @ T0.1  
> **Branch**: `evolve/EV-030-quality-residuals-831`  
> **Evolve cycle**: EV-030  
> **Features**: **F29** (new); deepen F23 / F12 / F2 / F13 / F9 / F26 / F27  
> **Spec sources**: feature-list §F29 + EV-030 deepen; spec §S037/EV-030; UJ-044;
> TC-EV030-001..006; TC-F29-001..007; api-contract S037; E30-*; S02.M1–L1;
> #831 / #829 / #820; ADR-028 / ADR-032

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase C — build |
| **Active milestone** | M1 — F29 harness |
| **Active task** | T1.4 — METAR/SPECI pilot — convert engine |
| **Tasks** | 7 / 27 completed |
| **Last updated** | 2026-08-03 |

## Tech Stack Summary

| Area | Choice | Source |
|------|--------|--------|
| Template | `static+api+worker` | template |
| Case storage | YAML/JSON under `tests/quality_matrices/testdata/` + pytest load | E30-T2=1 |
| Inventory SoT | Unified index: registry / Schematron assert / encode row → matrix slots | E30-T3=1 |
| Runners home | `tests/quality_matrices/` shared loaders (no new package) | E30-T8=1 |
| Harness doc | Session design note (not full ADR) unless spike forces ADR | S02.L1; E30-T8=1 |
| Registry | ADR-028 reuse (TC SIGMET lint codes for #829) | F12/F23 |
| Catalog | Unlock `sigmet-A6-2-TC` when quality path green (`wmoPass`/`wmoReference`) | E30-T4=1; ADR-032 |
| Runtime SoT | Vendor IWXXM **2025-2** | context |
| API | No new product enum; lint catalog additive; decode deepen (#820) | api-contract |
| YAML dep | **Reuse** existing `pyyaml` via `tac2iwxxm` stack — **no new dep** | E30-T5=2 |
| CI | PR smoke subset (pilot) + optional full-matrix marker/job | E30-T7=1 |
| Deploy | API redeploy if behavior ships; **H1–H3**; **H4–H5 required** for FE catalog unlock | E30-T6=1 |
| Pilot | METAR/SPECI lint+encode+validate first | S02.M1 |
| Kill / residual | STNR may OOS with cite (S02.M2); #820 may child residual (S02.M3) | Batch F |

## Interview locks

| ID | Decision |
|----|----------|
| E30-T1 | **1** — M0–M4 as proposed |
| E30-T2 | **1** — YAML/JSON testdata + pytest load |
| E30-T3 | **1** — unified rule inventory index |
| E30-T4 | **1** — unlock A6-2-TC when quality path green |
| E30-T5 | **2** — allow PyYAML if needed → **already present** (`tac2iwxxm`); no new dep |
| E30-T6 | **1** — redeploy + H1–H3; H4–H5 for catalog unlock |
| E30-T7 | **1** — PR smoke + optional full matrix |
| E30-T8 | **1** — session design note + `tests/quality_matrices/` |

## Milestones & Tasks (TDD order)

`evolve_cycle_id: EV-030` · `feature_ids: [F29, F23, F12, F2, F13, F9, F26, F27]`

**Work order:** #831 (M0–M1) → #829 (M2) → #820 (M3) → smoke (M4).

### M0 — #831 design / spike

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T0.1 | Docs | Design note: answer #831 eval Qs (storage, inventory SoT, runners, skip/`needs-fixture`, CI) under `reports/` | TC-F29-001; TC-EV030-001; E30-T2/T3/T8 | — | **completed** |
| T0.2 | Docs | Unified inventory sketch — map METAR/SPECI pilot rules (registry + SCH + encode) → 20 slots | TC-F29-004; E30-T3 | T0.1 | **completed** |
| T0.3 | Test | Spike: YAML RuleCase load + node-id shape (`rule/bucket/case`) — red then minimal green scaffold | TC-F29-005; E30-T2 | T0.1 | **completed** |
| T0.4 | Docs | M0 exit checklist — proceed M1 only when design note + spike API agreed | E30-T1 | T0.2, T0.3 | **completed** |

### M1 — F29 harness (runners + METAR/SPECI pilot)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T1.1 | Test | Shared YAML/JSON loader + case schema tests under `tests/quality_matrices/` | TC-F29-002; E30-T8 | T0.4 | **completed** |
| T1.2 | Code | Lint / convert / validate runners + `needs-fixture` skip/xfail policy | TC-F29-002; TC-EV030-002 | T1.1 | **completed** |
| T1.3 | Test | METAR/SPECI pilot matrices (fill or explicit `needs-fixture`) — lint engine | TC-F29-003; S02.M1 | T1.2 | **completed** |
| T1.4 | Test | METAR/SPECI pilot — convert engine | TC-F29-003 | T1.2 | pending |
| T1.5 | Test | METAR/SPECI pilot — validate engine | TC-F29-003 | T1.2 | pending |
| T1.6 | Code | Inventory gate: in-scope pilot rules have 20 slots or tracked TODO | TC-F29-004; TC-EV030-003 | T1.3–T1.5 | pending |
| T1.7 | Config | PR smoke subset + optional full-matrix marker/`make` target (E30-T7) | TC-F29-006 | T1.6 | pending |
| T1.8 | Docs | Authoring guide: add case when adding/changing a rule | TC-F29-007 | T1.7 | pending |

### M2 — #829 TC SIGMET deepen + catalog unlock

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T2.1 | Test | Dedicated `tac-validate` TC SIGMET accept/negative pack (peer VA) | TC-EV030-004; #829 | T1.8 | pending |
| T2.2 | Code | Registry + fixtures for TC lint codes (ADR-028) | F12/F23; #829 | T2.1 | pending |
| T2.3 | Test | STNR / exceptional geometry negatives — or **OOS with cite** (S02.M2) | TC-EV030-004; S02.M2 | T2.2 | pending |
| T2.4 | Code | Unlock `sigmet-A6-2-TC` catalog tier (`wmoPass`/`wmoReference` per ADR-032) when M7 quality path still green | TC-EV030-005; E30-T4 | T2.2 | pending |
| T2.5 | Test | FE catalog / Examples Vitest + path smoke for unlocked stem | TC-EV030-005; UJ-039 | T2.4 | pending |
| T2.6 | Docs | #829 closeout or child-split; COVERAGE_MATRIX / mining notes | #829 | T2.3, T2.5 | pending |

### M3 — #820 VAA/TCA decode deepen

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T3.1 | Test | Baseline residual matrix / allowlist for `vaa_a7_2` / `tca_a2_2` | TC-EV030-006; #820 | T2.6 | pending |
| T3.2 | Code | Structured decode for major VAA/TCA field labels + forecast hours | F9/F26/F27; #820 | T3.1 | pending |
| T3.3 | Test | Shrink residuals toward `[]` or update allowlist + **child residual** (S02.M3) | TC-EV030-006; S02.M3 | T3.2 | pending |
| T3.4 | Docs | #820 closeout or child-issue link | #820 | T3.3 | pending |

### M4 — Smoke / verify / deploy

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T4.1 | Config | 08-verify-build — lint / typecheck / format / suites | 08 | T3.4 | pending |
| T4.2 | Test | 09-qa delta + 10-e2e smoke (UJ-044; H4–H5 for catalog unlock) | 09; 10; E30-T6 | T4.1 | pending |
| T4.3 | Docs | 11-verify-impl per–AC (F29 + deepen); 12-verify-deploy | 11; 12 | T4.2 | pending |
| T4.4 | Test | 13-deploy-smoke — API redeploy if needed; **H1–H3**; **H4–H5 required** (FE unlock) | 13; E30-T6; TC-EV030-005 | T4.3 | pending |
| T4.5 | Docs | Close #831/#829/#820 (or children); evolve summary; F29 → Done | #831/#829/#820 | T4.4 | pending |

## Data Dependencies

| Asset | Needed by | Notes |
|-------|-----------|-------|
| Vendor IWXXM 2025-2 + Guidance | M0–M3 | Read-only `vendor/` |
| `tac-validate` issue registry | M0–M2 | Unified inventory source |
| Schematron assert ids | M0–M1 | Validate matrix slots |
| Annex3 / WMO goldens (`sigmet-A6-2-TC`, VAA/TCA peers) | M2–M3 | Catalog unlock + decode |
| Existing family packs (`test_tc_f15_*`, `tc-sigmet-quality`) | M1–M2 | Peer patterns; do not replace |
| No external weights/datasets | — | DMP N/A |

## Git Strategy

| Item | Value |
|------|-------|
| Branch | `evolve/EV-030-quality-residuals-831` |
| Commits | Atomic per task `[T{m}.{n}] …` / `[EV-030] …` |
| PR | One evolve PR to `main` after M4 (or mid-cycle if preferred) |
| Checklist | Lint · typecheck · tests · no secrets · TC mapping · no new deps without AskQuestion |

## Phase Gate Log

| Gate | Criteria | Status |
|------|----------|--------|
| A→B | Specs + 02 PASS | **passed** (`D-S037-02-phase-a`) |
| B→C | Plan approved; 05/06 skipped (no new deps/tooling) | **passed** (`D-S037-04-plan` = 1) |
| C→D | All Fn tasks done; 08 pass | pending |
| Deploy | 09+10; 11+12; 13 H1–H5 | pending |

## Out of scope (do not schedule)

- New deployables / #830 Supabase strip / #806 WIS2 / SIGWX/VONA/QVACI  
- Claiming 100% Annex-3 rule coverage in first PR  
- New public HTTP routes for F29 v1  
- Non-deployed UI preview (declined)  
- New PyYAML (or other) dependency without AskQuestion — stack already has `pyyaml` via `tac2iwxxm`
