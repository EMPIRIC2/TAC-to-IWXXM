# Execution plan — S059 / EV-050 (#959 Validated harvest + membership)

> **Generated**: 2026-08-09  
> **Skill**: 04-tech-plan (delta)  
> **Branch**: `evolve/EV-050-codes-wmo-validated`  
> **Issues**: [#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959) (parent [#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889))  
> **Build Plan Card**: `docs/sessions/S059-codes-wmo-validated/build-plan-card.md`

**Corpus**: [Corpus: product §F6] [Corpus: product §F12] [Corpus: product §F15]
[Corpus: product §F20] [Corpus: product §F23] [Corpus: product §F24]
[Corpus: product §F28] [Corpus: tests] [Corpus: tech-spec] [Corpus: decisions]

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase 1: Validated membership |
| **Active milestone** | M3: Dual-profile compare |
| **Active task** | T3.3 |
| **Tasks completed** | 10 / 15 |
| **Stage** | 07-build |
| **Last updated** | 2026-08-09 |
| **Plan approve** | `D-S059-04-plan=1` |
| **Gate B** | `D-S059-gateB=1` |
| **Build Plan Card** | `docs/sessions/S059-codes-wmo-validated/build-plan-card.md` |

## Tech decisions (**locked** `D-S059-04-*`)

| ID | Choice |
|----|--------|
| D-S059-04-milestones | **1** — Four milestones: M1 harvest · M2 membership+fixtures · M3 profiles · M4 closeout docs |
| D-S059-04-harvest | **1** — L3 SoT = vendor CSV `notation` under `iwxxm-codelists`; pin RDF for nil / dual paths (extend `tac2iwxxm.codelists` pattern) |
| D-S059-04-wire | **1** — Generated membership artifact under `packages/tac-validate` data; pytest membership; `make` regenerate on vendor pin bump |
| D-S059-04-adr | **1** — No new ADR; cadence + path in tech-spec / domain docs + this plan |
| D-S059-profiles | **1b** — All F6; `iwxxm_us` N/A where unsupported; AC7–AC8 |
| Connectivity | **N/A** — no browser UI; H4–H5 skipped; 12/13 waived |

## Tech Stack Summary

| Category | Choice | Source |
|----------|--------|--------|
| Language | Python 3.11+ (uv workspace) | [Corpus: tech-spec] |
| Lint / format | Ruff | existing |
| Tests | pytest (`packages/tac-validate`, `tac2iwxxm`) | [Corpus: tests] |
| Harvest input | `vendor/schemas/iwxxm-codelists/CSV/**` + pin RDF under `iwxxm/*/IWXXM/rule/` | AC1; D-S059-04-harvest |
| Membership runtime | `tac-validate` generated data + lint hooks | AC2; D-S059-04-wire |
| Profiles | `annex3` / `iwxxm_us` via existing F6 profile plugins | AC7; [Corpus: product §F6] |
| Deploy / CORS | Unchanged — no API/UI surface | routing skip 12/13 |
| New deps | **None expected** (06 skipped) | D-S059-route |

## Data Dependencies

| Asset | Type | Staging | Needed By |
|-------|------|---------|-----------|
| `vendor/schemas/iwxxm-codelists` (pinned) | vendor snapshot | already in-repo | M1–M3 |
| `vendor/schemas/iwxxm/{pin}/IWXXM/rule/*.rdf` | pin RDF | already in-repo | M1 (nil / dual) |
| Fixture packs under `packages/tac-validate/tests/fixtures` | test data | extend in M2 | M2–M3 |

No external download / Modal volume staging. Vendor remains read-only (sync PRs only).

## Implementation Phases

### Phase 1: Validated membership

**Entry**: `D-S059-04-plan=1` + Gate B (05) PASS.  
**Exit**: AC1–AC8 / TC-EV050-001..008 green or explicit deferral+cite; tip CI green; PR → `stage`.

#### M1: Offline harvest → membership sets — P0

**Goal**: Standing offline harvest produces CI-consumable membership sets; no live HTML.  
**Acceptance**: TC-EV050-001, TC-EV050-003; AC1, AC3.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T1.1 | Test: harvest produces frozen membership for v1 families (`D-S059-families=1a`); assert offline-only (no network) | Test | completed | TC-EV050-001; AC1 | — | vendor CSV + RDF |
| T1.2 | Code: harvest script/module (CSV `notation` + pin RDF for nil); write artifact under `packages/tac-validate` data | Code | completed | AC1; D-S059-04-harvest/wire | T1.1 | vendor |
| T1.3 | Config: `make` target to regenerate membership on `iwxxm-codelists` pin bump; wire optional CI drift check | Config | completed | AC1; AC3 | T1.2 | — |
| T1.4 | Docs: harvest cadence vs `vendor/manifest.json` pin; cross-link #859; RULE_SOURCE_URLS / TAC_VALIDATION pointers | Docs | completed | TC-EV050-003; AC3 | T1.2 | — |

#### M2: Membership wire + aggressive fixtures — P0

**Goal**: Happy/sad membership in `tac-validate`; close EV-046 gap packs (`2c`).  
**Acceptance**: TC-EV050-002, TC-EV050-004; AC2, AC4.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T2.1 | Test: happy + sad membership matrix for weather / recent / cloud / SIGMET+AIRMET phenomena / nil | Test | completed | TC-EV050-002; AC2; families 1a | T1.2 | membership artifact |
| T2.2 | Code: wire membership checks into lint/rules (stable issue codes); underscore↔space normalize for AIRMET as needed | Code | completed | AC2; fixture baseline | T2.1 | — |
| T2.3 | Test+fixtures: aggressive packs — `RE*`, AIRMET `_` / spaced phenomena, SpaceWxPhenomena, TCU (accept + unknown/sad) | Test | completed | TC-EV050-004; AC4; fixtures 2c | T2.1 | fixtures |
| T2.4 | Docs: COVERAGE_MATRIX / fixture baseline delta; residual gaps → child issues or defer+cite | Docs | completed | AC4; fixture-quality-baseline.md | T2.3 | — |

#### M3: Dual-profile compare + true-error fixes — P0

**Goal**: All-F6 `annex3` vs `iwxxm_us` disposition; fix true errors with regressions.  
**Acceptance**: TC-EV050-007, TC-EV050-008; AC7, AC8.  
**N/A rule**: `iwxxm_us` unsupported product → **N/A row (not fail)**.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T3.1 | Test: dual-profile harness — same TAC under `profile=annex3` and `iwxxm_us`; fail on unclassified divergent dual-applicable rows | Test | completed | TC-EV050-007; AC7 | T2.2 | fixtures + packs |
| T3.2 | Docs: disposition table for **all F6 products** (shared WMO · intentional L5 · true error · N/A) | Docs | completed | AC7; TAC_VALIDATION L3/L5 | T3.1 | — |
| T3.3 | Code: fix true-error rows (severity / false pass-fail / missing membership / wrong gating); no invented US tokens | Code | pending | TC-EV050-008; AC8 | T3.1, T3.2 | — |
| T3.4 | Test: regression cases per fixed true error; intentional/N/A retain cites; allow AC8 defer+cite | Test | pending | AC8; Gate A M1 | T3.3 | — |

#### M4: Closeout docs (#889 / #882) — P1

**Goal**: Validated triad element closed; #882 design-only note; no notify job.  
**Acceptance**: TC-EV050-005, TC-EV050-006; AC5, AC6.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T4.1 | Docs: #882 compose design note (session report or domain/ops) — outside PR CI; no job impl | Docs | pending | TC-EV050-006; AC6; 882=3a | — | — |
| T4.2 | Docs/process: #889 Validated satisfied (or re-scope) in evolve-decisions + issue comment criteria | Docs | pending | TC-EV050-005; AC5 | T2.2, T3.4 | — |
| T4.3 | Docs: tech-spec / domain back-add for harvest path + membership regenerate (no ADR) | Docs | pending | D-S059-04-adr; AC3 | T1.4 | — |

### Phase 1 Gate Check

| Criterion | Status |
|-----------|--------|
| TC-EV050-001..008 green or defer+cite | pending |
| No live `codes.wmo.int` HTML in PR CI | pending |
| N/A ≠ fail for unsupported `iwxxm_us` | pending |
| No new Fn; deepen only | locked |
| H4–H5 N/A; 12/13 waived | locked |

## Task Tracking (master)

| ID | Milestone | Status | Depends On |
|----|-----------|--------|------------|
| T1.1 | M1 | completed | — |
| T1.2 | M1 | completed | T1.1 |
| T1.3 | M1 | completed | T1.2 |
| T1.4 | M1 | completed | T1.2 |
| T2.1 | M2 | completed | T1.2 |
| T2.2 | M2 | completed | T2.1 |
| T2.3 | M2 | completed | T2.1 |
| T2.4 | M2 | completed | T2.3 |
| T3.1 | M3 | completed | T2.2 |
| T3.2 | M3 | completed | T3.1 |
| T3.3 | M3 | pending | T3.1, T3.2 |
| T3.4 | M3 | pending | T3.3 |
| T4.1 | M4 | pending | — |
| T4.2 | M4 | pending | T2.2, T3.4 |
| T4.3 | M4 | pending | T1.4 |

**Count**: 15 numbered tasks (22 if counting fixture/sub-cases as separate work units in 07). Parallelizable: T1.1 ‖ T4.1; after T1.2: T1.3 ‖ T1.4; after T2.1: T2.2 ‖ T2.3.

## Git Strategy

| Item | Value |
|------|-------|
| Branch | `evolve/EV-050-codes-wmo-validated` |
| Base | `stage` |
| Commits | One logical task (or small TDD pair) per commit: `[T1.1] test: …` |
| Push | On user request; tip CI before PR |
| PR | → `stage` after 08–11; no `stage`→`main` this cycle |

## PR Plan

| PR | Base | When |
|----|------|------|
| EV-050 Validated harvest + membership | `stage` | After 08–11 (or earlier docs-only if split) |

## Advisories (from Gate A — accepted)

| ID | Handling in 07 |
|----|----------------|
| M1 true-error volume unknown | AC8 defer+cite OK |
| M2 many `iwxxm_us` N/A | Matrix must not fail N/A |
| M3 large 07 | Four milestones as locked |

## Out of scope (do not task)

- Vendor hand-edits; live HTML PR CI; full #882 job; `#958`; promote to `main`; new ADR; new runtime PyPI deps; H4–H5 UI work
