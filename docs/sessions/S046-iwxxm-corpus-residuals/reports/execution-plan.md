# Execution plan — S046 / EV-038 (#846 residuals #849–#861)

> **Status**: **draft** — awaiting `D-S046-04-plan` approval → Gate B / 05  
> **Branch**: `evolve/EV-038-iwxxm-corpus-residuals`  
> **Evolve cycle**: EV-038  
> **Features**: deepen **F2 / F4 / F6 / F7 / F32** (no new Fn)  
> **Spec sources**: feature-list §EV-038; UJ-050; TC-EV038-001..014; AC1–AC14;
> `D-S046-mplan`; `D-S046-sot`; S02.M1–M5; #846 / #849–#861

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase B — technical (A→B PASS) |
| **Active milestone** | — (plan approval) |
| **Active task** | — |
| **Tasks** | 0 / ~28 pending |
| **Last updated** | 2026-08-05 |

## Tech Stack Summary

| Area | Choice | Source |
|------|--------|--------|
| Template | `static+api+worker` | template |
| #851 SoT | Python `iwxxm_versions.py` → **generated committed JSON** → FE + OpenAPI/CI | `D-S046-sot`=1 |
| #854 labels | Roles `latest` / `previous` from generated JSON (replace hardcoded strings) | UJ-050; AC7 |
| #852 tip-diff | Script/job vs previous vendor pin; no hand-edit vendor | AC5 |
| #853 US gate | Checklist + optional CI smoke; lag decision documented | AC6 |
| Encode M4 | Fixtures + SCH; cite-only deferral OK when no WMO peer | AC11–AC13; S02.M4 |
| New deps | **None** expected | — |
| Deploy | Standard 12/13; **waive for docs-only M1** ship if alone; required for M2+ runtime | S02.M5 |
| Local UI | Non-deployed preview at M2/#854 | `D-S046-mplan` Q2=1 |

### Generated JSON shape (locked)

```json
{
  "default": "2025-2",
  "versions": [
    {"id": "2025-2", "role": "latest"},
    {"id": "2023-1", "role": "previous"}
  ]
}
```

Path TBD in T2.1 (prefer `packages/shared` or `apps/frontend/src/generated/`).

## Interview locks

| ID | Decision |
|----|----------|
| D-S046-mplan | M1→M2→M3→M4; UI yes@M2 |
| D-S046-ac | AC1–AC14 approved |
| D-S046-02-gate-a | PASS after SoT |
| D-S046-sot | Python → generated JSON → FE + OpenAPI/CI |
| D-S046-04-plan | pending |

## Milestones & Tasks (TDD order)

`evolve_cycle_id: EV-038` · `deepen_feature_ids: [F2, F4, F6, F7, F32]`

**Work order:** M1 docs → M2 release-line → M3 soft → M4 encode → closeout.

### M1 — Docs / process (#858, #861, #855)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T1.1 | Docs | COVERAGE_MATRIX + epic note: WAFS/QVACI/SIGWX XML-only OOS (G5) | AC1; TC-EV038-001; #858 | — | pending |
| T1.2 | Docs | iwxxm-modelling delta-watch checklist step on sync PRs (G8) | AC2; TC-EV038-002; #861 | T1.1 | pending |
| T1.3 | Docs | Deprecation-calendar GitHub issue template + dry-run note | AC3; TC-EV038-003; #855 | T1.2 | pending |
| T1.4 | Docs | Close #858/#861/#855; link #846 | AC14 | T1.3 | pending |

### M2 — Release-line automation + UX (#851–#854)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T2.1 | Test | Red: CI/drift test fails when FE/OpenAPI diverge from Python SoT | AC4; TC-EV038-004; `D-S046-sot` | T1.4 | pending |
| T2.2 | Code | Export script: Python → committed JSON (+ roles); wire Makefile/`make` target | AC4; `D-S046-sot` | T2.1 | pending |
| T2.3 | Code | FE import JSON for picker options + Latest/Previous labels; drop hardcodes | AC7; UJ-050; TC-EV038-007; #854 | T2.2 | pending |
| T2.4 | Code | OpenAPI / schema enum docs align with export; CI assert | AC4; TC-EV038-004 | T2.2 | pending |
| T2.5 | Test | Green drift CI + FE Vitest for labels | TC-EV038-004/007 | T2.3, T2.4 | pending |
| T2.6 | Code | Sync-PR tip-diff script (XSD/SCH/example stems); link adopt checklist | AC5; TC-EV038-005; #852 | T2.5 | pending |
| T2.7 | Docs | iwxxm-us compatibility checklist + optional CI smoke; lag decision | AC6; TC-EV038-006; #853 | T2.6 | pending |
| T2.8 | Docs | Close #851–#854; local UI preview note | AC14; UJ-050 | T2.7 | pending |

### M3 — Corpus soft / gates (#859, #860, #857)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T3.1 | Docs/Config | codes.wmo.int vs vendor codelist drift check cadence (+ optional CI) | AC8; TC-EV038-008; #859 | T2.8 | pending |
| T3.2 | Docs | Inventory `*-translation-failed*` vs soft path; fixtures or deferral | AC9; TC-EV038-009; #860 | T3.1 | pending |
| T3.3 | Docs | SWXA A7-4/A7-5 disposition; catalog only with vendor peers | AC10; TC-EV038-010; #857 | T3.2 | pending |
| T3.4 | Docs | Close/defer #859/#860/#857 | AC14 | T3.3 | pending |

### M4 — Encode deepen (#849, #850, #856)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T4.1 | Test | Red: VONA vertical-extent fixtures (HGT SOURCE / MOV) when TAC supplies | AC11; TC-EV038-011; #849 | T3.4 | pending |
| T4.2 | Code | Encode `VolcanicAshCloudVerticalExtent` path (no invented packing) | AC11; F32 | T4.1 | pending |
| T4.3 | Test | Green SCH + matrix residual row for G-VONA-1 | TC-EV038-011 | T4.2 | pending |
| T4.4 | Test/Docs | RESUSPENDED_VOLCANIC_ASH — fixtures **or** cite-only deferral + matrix | AC12; TC-EV038-012; #850 | T4.3 | pending |
| T4.5 | Test | Red: ADR-032 equality vs `sigmet-VA-EGGX` (or irreducible-diff doc) | AC13; TC-EV038-013; #856 | T4.4 | pending |
| T4.6 | Code | Encode/canonicalize deltas → equality green when feasible | AC13; ADR-032 | T4.5 | pending |
| T4.7 | Code | Catalog promote → `wmoPass` **or** document residual; FIXTURE_GAPS | AC13; TC-EV038-013 | T4.6 | pending |
| T4.8 | Docs | Close/defer #849/#850/#856; COVERAGE_MATRIX | AC14 | T4.7 | pending |

### M5 — Verify / deploy closeout

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T5.1 | Config | 08-verify-build — lint/typecheck/format/suites | 08 | T4.8 | pending |
| T5.2 | Test | 09-qa + 10-e2e (UJ-050); H4–H5 prep | 09; 10 | T5.1 | pending |
| T5.3 | Docs | 11-verify-impl AC roll-up; epic #846 update | AC14; TC-EV038-014; 11 | T5.2 | pending |
| T5.4 | Deploy | 12 + 13 (or waive if final ship docs-only — unlikely after M2+) | 12; 13; S02.M5 | T5.3 | pending |

## PR / Git Strategy

| Item | Value |
|------|-------|
| Branch | `evolve/EV-038-iwxxm-corpus-residuals` → `main` |
| Commits | Atomic per task / logical group; `[EV-038]` / `[T*]` prefix |
| PR title | `[EV-038] Epic #846 corpus residuals #849–#861` |
| Merge | Explicit user approval |

## Phase Gate Check (B→C)

- [ ] Execution plan approved (`D-S046-04-plan`)
- [ ] 05-verify-tech PASS
- [ ] No new deps without inventory back-add
- [ ] SoT path + OpenAPI drift tasks present (T2.1–T2.5)
