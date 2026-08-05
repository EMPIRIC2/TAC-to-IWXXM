# Execution plan — S043 / EV-035

> **Status**: **approved** (2026-08-05) — `D-S043-04-plan` = 1; Gate B PASS → 07  
> **Branch**: `evolve/EV-035-rule-source-traceability`  
> **Evolve cycle**: EV-035  
> **Features**: deepen **F6 / F12 / F15 / F2** (no new Fn — G1=2)  
> **Spec sources**: feature-list deepen EV-035; test-plan TC-EV035-001..006;
> evolve-decisions §EV-035; S02.M1–M3/L1; provenance-gaps.md; #869–#872 / #846  
> **Corpus**: `[Corpus: product|tests]` · `[docs/domain/rules/…]` · G3 path-cite waiver

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase C — build |
| **Active milestone** | M3 — matrix + dense + closeout |
| **Active task** | T3.6 (handoff 08) |
| **Tasks** | 15 / 16 completed (T3.6 = 08 handoff) |
| **Last updated** | 2026-08-05 |

## Tech Stack Summary

| Area | Choice | Source |
|------|--------|--------|
| Template | `static+api+worker` | template |
| Deliverable | `PROVENANCE_MAP.md` + JSON twin under `docs/domain/rules/` | E35-T2 |
| Catalog scope | **All** ISSUE_CATALOG codes → status ∈ {ok, gap, paywall, N/A} | E35-T3 |
| VONA | ⚠ Guidance; ✅ AHL/FM205/XSD/peer cites | S02.M1; #869 |
| US validate | Keep ⚠; document N/A SCH in pin | #870 |
| Bulletin AHL | Matrix refresh vs fixtures | S02.M3; #872 |
| New deps | **None** | E35-T4 |
| UI / H4–H5 | **N/A** | 10 skipped |
| Deploy | Docs/tests-only — **expect waive** 12/13 | S02.L1; E35-T5 |
| Local CI | Path-filtered canary; `make test-provenance-quality` | E35-T4 |
| Dense asserts | ≥3 sites per revisited executable rule | TC-EV035-005 |

## Interview locks

| ID | Decision |
|----|----------|
| E35-T1 | **1** — M0–M3 |
| E35-T2 | **1** — MD + JSON twin |
| E35-T3 | **1** — all catalog codes + gap rows |
| E35-T4 | **1** — no new deps; tiered CI |
| E35-T5 | **1** — plan deploy waive at 12/13 |
| E35-T6 | **1** — Gate B → 07 @ T0.1 |

## Milestones & Tasks (TDD order)

`evolve_cycle_id: EV-035` · `deepen_feature_ids: [F6, F12, F15, F2]`

### M0 — Provenance scaffold

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T0.1 | Docs | Scaffold `PROVENANCE_MAP.md` + JSON twin | TC-EV035-*; E35-T2 | — | **completed** |
| T0.2 | Docs | Index map from rules README; link mining README | TC-EV035-001 | T0.1 | **completed** |
| T0.3 | Config | `make test-provenance-quality` + path-filtered canary | E35-T4 | T0.2 | **completed** |

### M1 — Dig inventory (TC-EV035-001)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T1.1 | Test | Red→green parametric dig inventory | TC-EV035-001 | T0.3 | **completed** |
| T1.2 | Docs | Index all digs (incl. vona remine) | TC-EV035-001 | T1.1 | **completed** |
| T1.3 | Test | Green dig inventory asserts | TC-EV035-001 | T1.2 | **completed** |

### M2 — ISSUE_CATALOG ↔ sources (TC-EV035-002 / #871)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T2.1 | Test | Parametric over all ISSUE_CATALOG codes | TC-EV035-002; #871 | T1.3 | **completed** |
| T2.2 | Docs | Fill PROVENANCE_MAP catalog rows | F15/F12; #871 | T2.1 | **completed** |
| T2.3 | Test | Green TC-EV035-002 (100/100); #871 closeable | TC-EV035-002; S02.M2 | T2.2 | **completed** |

### M3 — Matrix + full-stack cites + dense + gap gate

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T3.1 | Docs | COVERAGE_MATRIX refresh VONA/#870/#872 | TC-EV035-003; #869–#872 | T2.3 | **completed** |
| T3.2 | Test | TC-EV035-003/004 green | TC-EV035-003/004 | T3.1 | **completed** |
| T3.3 | Test | TC-EV035-005 dense asserts | TC-EV035-005 | T3.2 | **completed** |
| T3.4 | Test | TC-EV035-006 gap-raise gate | TC-EV035-006 | T3.3 | **completed** |
| T3.5 | Docs | Ticket/session gap closeout notes | S02.*; #846 | T3.4 | **completed** |
| T3.6 | Config | 08-verify-build handoff | 08 | T3.5 | **in_progress** |

## Git Strategy

- Branch: `evolve/EV-035-rule-source-traceability`
- PR title: `[EV-035] Rule-source provenance map (deepen F6/F12/F15/F2)`
- Checklist: lint · typecheck · `make test-provenance-quality` · no secrets · TC-EV035-001..006 · no F33 · path-cites only · #869–#872 linked

## Phase gates

| Gate | Criteria | Status |
|------|----------|--------|
| B→C | Execution plan approved; no new deps | **passed** |
| C→D | All M0–M3 tasks completed; 08 pass | pending |
| Deploy | AskQuestion — waive 12/13 if no runtime (S02.L1) | pending |

## Out of scope

New Fn; UI provenance UX; vendor hand-edits; IWXXM re-pin; inventing sources for gap rows;
full F29 matrix fill for every catalog code (only revisited executable rules in TC-EV035-005).
