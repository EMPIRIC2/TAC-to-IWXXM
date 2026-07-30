# Execution plan — S030 / EV-023 (#800 APAC/codes encode–validate deepen)

> **Status**: **approved** (2026-07-30) — E23-T1..T6 (1 / 1 / 2 / 2 / 1 / 1)  
> **Branch**: `evolve/EV-023-apac-encode-validate`  
> **Evolve cycle**: EV-023  
> **Features**: deepen F6 / F2 / F12 / F13 (no new Fn)  
> **Spec sources**: feature-list §EV-023 deepen; spec §S030; TC-EV023-001..009;
> config-spec translationCentre; api-contract S030; E23-*; S02.M1/M2/L1; #800;
> COVERAGE_MATRIX APAC/codes rows (cite)

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase C — Build |
| **Active milestone** | M1 — P0 NSC exclusivity |
| **Active task** | T1.2 |
| **Tasks** | 4 / 24 |
| **Last updated** | 2026-07-30 |

## Tech Stack Summary

| Area | Choice | Source |
|------|--------|--------|
| Runtime SoT | Vendor pin IWXXM **v2025-2** | #800; E23 |
| Registry | Reuse ADR-028; tighten NSC codes if needed | F12 |
| Nils / colour | Offline vendor RDF/CSV | P1 |
| Informative suite | Marker in **main CI as soft/xfail** | E23-T4=2 |
| translationCentre | Default omit; Form `emit_translation_centre` + optional designator/name | E23-T2=1 |
| COLLECT P2 | F16–F19 / bulletin hooks only | S02.M2 |
| FIR / S OF | Helpers; full TC SIGMET stays #738 | P2 |
| New deps | AskQuestion per new dep (prefer none) | E23-T3=2 |
| Deploy | 13 when convert/validate ships | E23-4 |

## Interview locks

| ID | Decision |
|----|----------|
| E23-T1 | Order **1** — M0→P0→P1→P2→smoke |
| E23-T2 | Wire **1** — `emit_translation_centre` + optional designator/name |
| E23-T3 | Deps **2** — AskQuestion per new dep |
| E23-T4 | CI **2** — soft/xfail in main CI |
| E23-T5 | Kill-switch **1** — AskQuestion; no silent defer HARD P0 |
| E23-T6 | Plan **1** — approve; B→C → 07 @ T0.1 |

## Milestones & Tasks (TDD order)

`evolve_cycle_id: EV-023` · `feature_ids: [F6, F2, F12, F13]`

### M0 — Theme map + CI marker scaffold

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T0.1 | Docs | Map TC-EV023-001..009 → fixtures/vendor/guidance; `reports/apac-encode-theme-fixture-map.md` | #800 | — | **completed** |
| T0.2 | Docs | Link map from COVERAGE_MATRIX #800 / APAC rows | matrix | T0.1 | **completed** |
| T0.3 | Config | `pytest.mark.iwxxm_translation_informative`; main CI soft/xfail | E23-T4=2 | T0.2 | **completed** |

### M1 — P0 NSC exclusivity

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T1.1 | Test | NSC → no layered cloud; SCH/XSD negative | TC-EV023-001 | T0.1 | **completed** |
| T1.2 | Code | Convert omit layered cloud on NSC | F6 | T1.1 | pending |
| T1.3 | Code | Lint tighten beyond `NSC_PRESENT` if needed | F12 | T1.2 | pending |

### M2 — P0 missing WX / Guidance nils

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T2.1 | Test | `common/nil` vs `iwxxm/nil` fixtures | TC-EV023-002 | T1.3 | pending |
| T2.2 | Code | Align missing WX with Guidance | F6 | T2.1 | pending |

### M3 — P0 translationFailedTAC

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T3.1 | Test | Official `*-translation-failed.xml` attr matrix | TC-EV023-003 | T2.2 | pending |
| T3.2 | Code | Quarantine emits original TAC | F6 | T3.1 | pending |

### M4 — P1 dual-register + translationCentre

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T4.1 | Test | Offline dual-register colour + dual nil | TC-EV023-004 | T3.2 | pending |
| T4.2 | Code | Encode href policy from vendor RDF/CSV | F6/F13 | T4.1 | pending |
| T4.3 | Test | Default omit centre*; emit when flag on | TC-EV023-006 | T4.2 | pending |
| T4.4 | Code | Convert + Form `emit_translation_centre` (+ optional fields) | E23-T2 | T4.3 | pending |

### M5 — P1 informative translation suite

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T5.1 | Test | Amd79 TAC → 2025-2 → XSD+SCH under marker | TC-EV023-005 | T0.3; T4.4 | pending |
| T5.2 | Config | Soft/xfail in main CI (no hard-fail on 2023-1 bytes) | E23-T4=2 | T5.1 | pending |

### M6 — P2 geometry / COLLECT / QA / matrix

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T6.1 | Test | FIR / “S OF” polygon helper tests | TC-EV023-007 | T5.2 | pending |
| T6.2 | Code | Helper impl (coord #738) | F6 | T6.1 | pending |
| T6.3 | Test/Docs | COLLECT multi-version hooks F16–F19 | TC-EV023-008 | T6.2 | pending |
| T6.4 | Test/Docs | Optional #798 QA + matrix confirm | TC-EV023-009 | T6.3 | pending |

### M7 — Smoke / verify / deploy

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T7.1 | Test | API convert/validate smoke | TC-EV023 | T6.4 | pending |
| T7.2 | Config | 08-verify-build | 08 | M0–M6 | pending |
| T7.3 | Test | 10-e2e smoke | 10 | T7.2 | pending |
| T7.4 | Test | 13-deploy-smoke when behavior ships | 13; E23-4 | T7.3 | pending |

## Data Dependencies

| Asset | Needed by | Notes |
|-------|-----------|-------|
| Vendor 2025-2 XSD/SCH/examples + Guidance | M1–M5 | Read-only |
| Official `*-translation-failed.xml` | M3 | Attr matrix |
| Vendor RDF/CSV colour + nil | M4 | Offline SoT |
| iwxxm-translation Amd79-80-2023 TAC | M5 | Soft/xfail CI |
| Mining notes | M0, M6 | Cite only |

## Git Strategy

- Branch: `evolve/EV-023-apac-encode-validate`
- Atomic commits: `[T0.1] docs: …`
- Kill-switch E23-T5; new deps AskQuestion E23-T3

## Connectivity

- Form flag on `/convert` → H0c + API smoke; H4–H5 only if FE wires later
- 13 when API ships (E23-4)

## Phase Gate Check (B→C)

- [x] Plan approved (E23-T6=1)
- [x] 05/06 skipped (Lean+build)
