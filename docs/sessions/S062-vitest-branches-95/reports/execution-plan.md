# Execution plan — S062 / EV-053 (Vitest branches ≥95 / #968)

> **Generated**: 2026-08-10  
> **Skill**: 04-tech-plan (delta)  
> **Branch**: `evolve/EV-053-vitest-branches-95`  
> **Issues**: [#968](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/968)  
> **Build Plan Card**: `docs/sessions/S062-vitest-branches-95/build-plan-card.md`

**Corpus**: [Corpus: product §F29] [Corpus: product §M5] [Corpus: tests]
[Corpus: adr/ADR-007] [Corpus: decisions §EV-052] [Corpus: decisions §EV-053]

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase 1: Vitest branches / FileConverter |
| **Active milestone** | — (await `D-S062-04-plan`) |
| **Active task** | — |
| **Tasks completed** | 0 / 9 |
| **Stage** | 04-tech-plan |
| **Last updated** | 2026-08-10 |
| **Plan approval** | pending `D-S062-04-plan` |

## Tech decisions (proposed — await `D-S062-04-plan`)

| ID | Choice |
|----|--------|
| D-S062-ac5-proof | **1** — AC5 proven from Vitest coverage JSON + session 08/09/11 reports (`D-S062-m1=1`); **no** new CI fail plugin unless fill reveals need |
| D-S062-cov-exclude | Remove `src/app/components/FileConverter.tsx` from Vitest `coverage.exclude` |
| D-S062-cov-thresh | Set Vitest `branches: 95` (keep lines/statements/functions ≥95) |
| D-S062-test-home | Prefer extending `FileConverter.test.tsx` (+ work-session suite only if needed); no product UX change |
| D-S062-inventory | Update S061 `coverage-surface-inventory.yaml` in-place: resolve `branch_waiver`; drop FileConverter from intentional_excludes |
| D-S062-m-order | M1 config+baseline → M2 FileConverter branch fill → M3 inventory/docs/CI closeout |
| D-S062-05 | Keep **05 skipped** (no new deps/arch) |

### Locked (prior)

| ID | Choice |
|----|--------|
| D-S062-route | Standard; skip 03/05/06/10/12/13 |
| D-S062-fc-strategy | Re-include FileConverter |
| D-S062-01-ac | AC1–AC5 |
| D-S062-gateA / M1 | PASS; AC5 verify-report proof |

## Tech Stack Summary

| Category | Choice | Source |
|----------|--------|--------|
| FE tests | Vitest + Testing Library (existing) | apps/frontend |
| Coverage | Vitest v8 provider; thresholds in `vitest.config.ts` | ADR-007 / #968 |
| CI | `.github/workflows/ci-cd.yml` frontend matrix `test:coverage` | TC-EV053-002 |
| Connectivity H4–H5 | N/A | routing |

## Data Dependencies

None.

## Implementation Phases

### Phase 1: Close branches waiver

**Entry**: `D-S062-04-plan=1` approved.  
**Exit**: AC1–AC5 met; tip CI green; inventory waiver resolved; ready for 08→09→11.

#### M1: Config + baseline — P0

**Goal**: Re-include FileConverter; raise `branches` to 95; capture red baseline.  
**Acceptance**: AC1 partial (config); baseline numbers for M2.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T1.1 | Remove FileConverter from `vitest.config.ts` coverage exclude; set `branches: 95`; scrub waiver comments | Config | pending | TC-EV053-001; AC1; D-S062-cov-* | — | — |
| T1.2 | Run FE coverage once; record aggregate + FileConverter per-file % in session baseline note | Test/Docs | pending | AC5 baseline; D-S062-ac5-proof | T1.1 | — |
| T1.3 | Contract assert (unit or doc test): thresholds ≥95 and FileConverter not in exclude list | Test | pending | TC-EV053-001; AC1 | T1.1 | — |

#### M2: FileConverter branch fill — P0

**Goal**: FileConverter branches ≥95% and aggregate gates green.  
**Acceptance**: AC2, AC5; TC-EV053-002, TC-EV053-005.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T2.1 | Triage uncovered FileConverter branches from coverage JSON (group by handler/UI path) | Test | pending | AC5; #968 | T1.2 | — |
| T2.2 | Add/extend Vitest cases for highest-miss branch clusters (iterate until FileConverter branches ≥95) | Test | pending | AC5; TC-EV053-005 | T2.1 | — |
| T2.3 | Ensure aggregate lines/stmts/funcs/branches all ≥95 with FileConverter included | Test | pending | AC2; TC-EV053-002 | T2.2 | — |

#### M3: Inventory + docs + tip CI — P0

**Goal**: Resolve waiver docs; tip CI green; handoff verify.  
**Acceptance**: AC3, AC4; TC-EV053-003..004.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T3.1 | Resolve `branch_waiver` in coverage inventory; remove FileConverter intentional exclude | Docs | pending | AC3; TC-EV053-003 | T2.3 | — |
| T3.2 | Record FileConverter branch % in session verify artifact (AC5 proof); update evolve-decisions closeout notes as needed | Docs | pending | AC5; D-S062-ac5-proof | T2.3 | — |
| T3.3 | Push tip; confirm frontend coverage CI green; prepare PR → `stage` after 08/09/11 | CI | pending | AC4; TC-EV053-004 | T3.1, T3.2 | — |

## Git Strategy

- Branch: `evolve/EV-053-vitest-branches-95` (base `stage`)
- PR target: `stage` (not `main`)
- One logical commit per task when practical; M2 may batch related tests

## Out of scope

- New deps / ADR-007 rewrite / operator UI redesign
- Per-file CI fail plugin (unless M2 proves verify-only insufficient — AskQuestion)
- 12/13 deploy stages
