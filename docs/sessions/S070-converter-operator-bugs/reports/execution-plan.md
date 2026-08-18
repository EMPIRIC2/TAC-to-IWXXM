# Execution plan — S070 / EV-060 (epic #1000)

> **Generated**: 2026-08-17  
> **Skill**: 04-tech-plan (delta)  
> **Branch**: `evolve/EV-060-converter-operator-bugs`  
> **Issues**: [#1000](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1000)–[#1006](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1006)  
> **Build Plan Card**: `docs/sessions/S070-converter-operator-bugs/build-plan-card.md`

**Corpus**: [Corpus: product §F7] [Corpus: product §F6] [Corpus: product §F2]
[Corpus: product §F29] [Corpus: product §F31] [Corpus: api] [Corpus: journeys]
[Corpus: tests] [Corpus: decisions §EV-060]

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Build (gate **open** `D-S070-spec-build=1a`) |
| **Active milestone** | M4 #1006 Auth UAT — T4.1 complete; next T4.2 facilitated UAT |
| **Tasks completed** | 18 / 21 |
| **Stage** | 07-build M4 |
| **Plan approval** | **approved** `D-S070-04-plan=1a` |
| **GitHub milestone** | **M0** (roadmap) — not the same as plan M1–M4 |

## Tech decisions (from intake — confirm with `D-S070-04-plan`)

| ID | Choice |
|----|--------|
| D-S070-m-order | **M1 #1001 → M2 #1003 → M3 #1002+#1004+#1005 → M4 #1006** |
| D-S070-ahl | Split AHL; lint heading as COM; lint contained reports as selected TAC product (`tac-validate` + convert-bulletin) |
| D-S070-iwxxm | Additive `product=iwxxm`; `/convert` no-op + optional F2; `/lint-tac` XML lint; TAC text → not-XML |
| D-S070-f7s | Keep F7.s Validate-only |
| D-S070-profile | Labeled Profile at converter top; same `profile=` multipart; a11y name+label |
| D-S070-log | Wire existing `log_level` to stdlib/package loggers; redact Authorization |
| D-S070-bulletin | Labeled editable Bulletin ID / Issuing Center → existing `bulletin_id` / `issuing_center` |
| D-S070-honor | FileConverter / accumulate / Quality metrics inherit shared product/profile |
| D-S070-deps | **No new** npm/PyPI deps |
| D-S070-adr | **No new ADR** — deepen ADR-023/024 notes in spec (already done in 01) |
| D-S070-cors | No new origins; reuse H0c; H4–H5 in 12/13 |
| D-S070-board | Epic #1000 Backlog; children Ready until 07; WIP≤2 |

## Implementation Phases

### Phase 1: EV-060 converter pack (after Spec→Build open)

**Entry**: Spec→Build **open**; this plan approved.  
**Exit**: AC for #1001–#1006 on `stage`; promote held.

#### M1: AHL bulletin quality (#1001) — P0

| ID | Type | Task | Status | Tests |
|----|------|------|--------|-------|
| T1.1 | Test | Red AHL heading-flood + split fixtures | completed | TC-EV060-1001-001..002 |
| T1.2 | Code | `tac-validate` / splitter: heading COM vs product syntax | completed | T1.1 |
| T1.3 | Code | `/convert-bulletin` + workbench/FileConverter parity | completed | TC-EV060-1001-003 |
| T1.4 | Docs | Fixture notes if needed | completed | reuse `metar_multi_ahl.txt` |

#### M2: IWXXM product pass-through (#1003 / F7.t) — P0

| ID | Type | Task | Status | Tests |
|----|------|------|--------|-------|
| T2.1 | Test | Red product=iwxxm XML vs TAC text | completed | TC-EV060-1003-001..002 |
| T2.2 | Code | Additive enum `iwxxm`; convert no-op; lint XML; OpenAPI | completed | T2.1 |
| T2.3 | Code | FE product select + Convert disabled/no-op copy | completed | TC-EV060-1003-003 |
| T2.4 | Code | FileConverter / accumulate / QM honor | completed | TC-EV060-1003-004 |

#### M3: Profile + bulletin fields + log_level (#1002/#1005/#1004) — P0

| ID | Type | Task | Status | Tests |
|----|------|------|--------|-------|
| T3.1 | Test | Profile a11y + applied `profile=` | completed | TC-EV060-1002-* |
| T3.2 | Code | Profile control at converter top | completed | T3.1 |
| T3.3 | Test | Bulletin ID / Issuing Center round-trip + invalid CCCC | completed | TC-EV060-1005-* |
| T3.4 | Code | Labeled editable fields wired to existing API | completed | T3.3 |
| T3.5 | Test | DEBUG vs ERROR verbosity; no secrets | completed | TC-EV060-1004-* |
| T3.6 | Code | Apply `log_level` to loggers | completed | T3.5 |

#### M4: Auth UAT (#1006) — P0

| ID | Type | Task | Status | Tests |
|----|------|------|--------|-------|
| T4.1 | Test | Playwright register/login/logout/persist | completed | TC-EV060-1006-001..003 |
| T4.2 | UAT | Facilitated uat Build checklist | pending | TC-EV060-1006-004 |
| T4.3 | Verify | Guest convert still works (F21) | completed | UJ-001 |

## Connectivity

Existing CORS. Tasks in 07: keep `test_cors_policy.py` green. H4–H5 in 12/13 for UJ-059..062 and Auth.

## Data / deps

No ML weights. No new packages. IWXXM XML fixtures: reuse F7.s / quality goldens.

## Git

Branch `evolve/EV-060-converter-operator-bugs` → PRs to **`stage`**. Four PRs. Promote held.
