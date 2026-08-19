# Execution plan — S071 / EV-061 (epic #1009)

> **Generated**: 2026-08-18  
> **Skill**: 04-tech-plan (delta)  
> **Branch**: `evolve/EV-061-pre-promote-ux-catalog`  
> **Issues**: [#1009](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1009)–[#1015](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1015)  
> **Build Plan Card**: `docs/sessions/S071-pre-promote-ux-catalog/build-plan-card.md`  
> **Plan approval**: pending `D-S071-04-plan`

**Corpus**: [Corpus: product §F2] [Corpus: product §F6] [Corpus: product §F7] [Corpus: product §F9]
[Corpus: product §F10] [Corpus: product §F15] [Corpus: product §F34] [Corpus: api]
[Corpus: journeys] [Corpus: tests] [Corpus: deploy] [Corpus: decisions §EV-061]

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Spec-development (04-tech-plan) |
| **Active milestone** | (Build) M1 #1011 — after Spec→Build opens |
| **Tasks completed** | 0 / 24 |
| **Stage** | 04-tech-plan |
| **Plan approval** | pending |
| **Spec→Build gate** | **closed** |
| **GitHub milestone** | **M0** (roadmap) — not the same as plan M1–M6 |

## Tech decisions (intake A — 2026-08-18)

| ID | Choice |
|----|--------|
| D-S071-m-order | **M1 #1011 → M2 #1012 → M3 #1010 → M4 #1013 → M5 #1014 → M6 #1015** |
| D-S071-deps | **No new** npm/PyPI deps |
| D-S071-adr | **No new ADR** — catalog 3-tier stays in evolve-decisions + mining note |
| D-S071-api | Additive: `INVALID_AHL`; optional validate `segments`/`summary`; extend `GET /lint-issue-catalog` (IWXXM rows + source fields). **No** new catalog endpoint |
| D-S071-cors | No new origins; reuse H0c; H4–H5 in 12/13 |
| D-S071-ci | On `stage`→`main`: required checks = full unit (`Test (*)`), **lint**, **typecheck**, **full E2E** (not smoke-only), plus existing Staging gate. Restore lint/typecheck as CI jobs (today they are local pre-commit only — EV-036). Branch protection may need maintainer admin (no app secrets) |
| D-S071-catalog-fe | Top-level nav tab/page; FE consumes `GET /lint-issue-catalog` (+ additive fields). Operator hrefs = verified landings; semantic IDs not required as href |
| D-S071-validate-ux | Item-by-item F9 row panel on Validate IWXXM when decode exists; F7.s / F7.t remain |
| D-S071-ahl | Golden `SAUS31 KZNY` multi-METAR: decode per report + convert-bulletin; malformed → `INVALID_AHL` / `empty_bulletin` |
| D-S071-skip | Skip 03/05/06 still (no new rules/deps) |

## Implementation Phases

### Phase 1: EV-061 pre-promote pack (after Spec→Build open)

**Entry**: Spec→Build **open**; this plan approved.  
**Exit**: AC for #1010–#1015 on `stage`; promote held until #1015 gate is configured.

#### M1: Live bulletin multipart `files` (#1011) — P0 chore

| ID | Type | Task | Status | Depends On | Spec Source | Tests |
|----|------|------|--------|------------|-------------|-------|
| T1.1 | Test | Assert live harness posts multipart `files` | pending | — | [Corpus: api] [Corpus: tests §TC-LIVE-F6-030] | TC-LIVE-F6-030 |
| T1.2 | Code | `tests/live/test_tc_live_f6_030_bulletin.py`: `file` → `files` | pending | T1.1 | #1011 | T1.1 |

#### M2: AHL decode + convert-bulletin (#1012) — P0

| ID | Type | Task | Status | Depends On | Spec Source | Tests |
|----|------|------|--------|------------|-------------|-------|
| T2.1 | Test | Red golden multi-METAR decode + convert; malformed `INVALID_AHL` | pending | — | [Corpus: product §F6] UJ-065 | TC-EV061-1012-001..004 |
| T2.2 | Code | AHL split/decode: per-report F9 rows + convert-bulletin success | pending | T2.1 | feature-list F6 EV-061 | T2.1 |
| T2.3 | Code | Malformed AHL → clear `INVALID_AHL` / `empty_bulletin` (no silent 200) | pending | T2.1 | [Corpus: api] | TC-EV061-1012-004 |
| T2.4 | Docs | OpenAPI / operator copy for AHL errors (no internal doc refs) | pending | T2.3 | [Corpus: api] EV-048 | — |

#### M3: Validate IWXXM readable decode (#1010) — P0

| ID | Type | Task | Status | Depends On | Spec Source | Tests |
|----|------|------|--------|------------|-------------|-------|
| T3.1 | Test | Red: validate IWXXM shows item-by-item rows not raw dump | pending | — | UJ-064 F9/F2 | TC-EV061-1010-001..003 |
| T3.2 | Code | Additive optional `segments`/`summary` on `/validate` (F9 shape) **or** FE maps existing decode | pending | T3.1 | [Corpus: api] D-S071-api | T3.1 |
| T3.3 | Code | FE decode panel parity; keep F7.s / F7.t | pending | T3.2 | [Corpus: product §F7] | TC-EV061-1010-003 |

#### M4: Product/Profile + param bars (#1013) — P0

| ID | Type | Task | Status | Depends On | Spec Source | Tests |
|----|------|------|--------|------------|-------------|-------|
| T4.1 | Test | Red: no-wrap ≥1024px; stack below; a11y labels | pending | — | UJ-066/067 F7.u | TC-EV061-1013-001..003 |
| T4.2 | Code | Product Type + Profile one bar; mode selects one row; params one row | pending | T4.1 | feature-list F7.u | T4.1 |

#### M5: Lint & validation catalog tab (#1014) — P0

| ID | Type | Task | Status | Depends On | Spec Source | Tests |
|----|------|------|--------|------------|-------------|-------|
| T5.1 | Test | Red: tab/page lists code, description, level, working source hrefs | pending | — | UJ-068 F7.v/F15 | TC-EV061-1014-001..004 |
| T5.2 | Code | Additive catalog fields + IWXXM validation rows on `GET /lint-issue-catalog` | pending | T5.1 | [Corpus: api] D-S071-api | TC-EV061-1014-002 |
| T5.3 | Code | Top-level nav tab/page; operator hrefs = verified landings (`D-S071-links-resolve`) | pending | T5.2 | mining note | TC-EV061-1014-003 |
| T5.4 | Docs | OpenAPI aliases for additive catalog fields; no planning ids in attribution | pending | T5.2 | EV-048 | TC-EV061-1014-004 |

#### M6: Stricter stage→main gate (#1015) — P0

| ID | Type | Task | Status | Depends On | Spec Source | Tests |
|----|------|------|--------|------------|-------------|-------|
| T6.1 | Test/Docs | Inventory current required checks vs target set | pending | — | UJ-DEV-009 deploy.md | TC-EV061-1015-001 |
| T6.2 | Config | CI jobs: lint + typecheck + full Playwright E2E on promote PRs | pending | T6.1 | [Corpus: tech-spec] D-S071-ci | TC-EV061-1015-002 |
| T6.3 | Docs | deploy.md + promote PR template; branch-protection runbook (admin) | pending | T6.2 | [Corpus: deploy] | T6.1 |

## Connectivity

No new CORS origins. Keep `test_cors_policy.py` green in 07. **H4–H5** in 12/13 for
UJ-064, UJ-065, UJ-066, UJ-067, UJ-068. UJ-DEV-009 is CI. H7 TC-LIVE-F6-030 after M1.

## Data / deps

No ML weights. No new packages. Reuse `metar_multi_ahl` / `SAUS31 KZNY` fixture.
Catalog sources: mining note + `catalog_attribution.json` (already retargeted in 01).

## Git

Branch `evolve/EV-061-pre-promote-ux-catalog` → PRs to **`stage`**. Prefer one PR per
milestone (or stacked). Promote held until #1015 required checks exist.

## Skip

03 / 05 / 06 — no new Cursor rules or dependencies.

## Dual Spec (after this plan is approved)

- `verify-qa` Spec — TC matrix coverage for TC-EV061-*
- `uat` Spec — catalog + AHL + validate UX + bars checklists

Then **Spec→Build AskQuestion** (still closed until that gate).
