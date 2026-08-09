# Execution plan — S057 / EV-048 (#951 strip internal doc refs)

> **Generated**: 2026-08-08  
> **Skill**: 04-tech-plan (delta)  
> **Branch**: `evolve/EV-048-strip-internal-doc-refs`  
> **Issues**: [#951](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/951)  
> **Build Plan Card**: `docs/sessions/S057-strip-internal-doc-refs/build-plan-card.md`

**Corpus**: [Corpus: product §F7] [Corpus: product §F21] [Corpus: api]
[Corpus: tests] [Corpus: journeys] [Corpus: decisions]

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase 1: Copy hygiene |
| **Active milestone** | M3 complete — awaiting 08-verify-build |
| **Active task** | — |
| **Tasks completed** | 7 / 8 (T3.3 skipped — no UI hits) |
| **Stage** | 07-build |
| **Last updated** | 2026-08-08 |

## Tech decisions (**locked** `D-S057-04-plan=1`, `D-S057-04-guard-ext=1`)

| ID | Choice |
|----|--------|
| D-S057-04-openapi | Scan via FastAPI `app.openapi()`; walk all string values in export |
| D-S057-04-guard | Shared pattern set (BE pytest + FE Vitest): `\[Corpus:`, `docs/sessions/`, `docs/feature-list`, `\bADR-\d+\b`, `\bEV-\d+\b`, `\bS0\d+\b` |
| D-S057-04-guard-ext | **Locked**: also fail (and strip in M2) `\bTC-[A-Z0-9-]+\b`, `\bE\d{2}-\d+\b`, `\b#\d{3,}\b` |
| D-S057-04-fe-catalogs | Scan exported operator string modules: SoftPreviewControl, operatorHelp, guestLossNotice, privacy preference copy, examplesCatalog `label`s, FileConverter user-visible literals via catalog helper if needed |
| D-S057-04-t3 | Playwright UJ-055 only if FE audit finds visible hits; else T0/T2 unit guards |
| D-S057-04-allowlist | Empty initially; document in test module if a domain false positive appears |

## Audit snapshot (pre-build, 2026-08-08)

### OpenAPI (`app.openapi()`) — 16 hits (locked patterns + planning extras)

| Surface | Leak |
|---------|------|
| convert `preview` / `include_nil_reasons` Form | ADR-022, ADR-024 |
| ConversionResponse `ok` / `failed_spans` | ADR-022 |
| FailedSpan schema description | ADR-022 / F7 |
| DecodeTacResponse `summary` | F9 / ADR-025 |
| DecodeSegmentModel description | S011 / #702 |
| lint-issue-catalog / LintIssueCatalogEntryModel | E11-31 / EV-040 |
| decode-tac route docstring | S011 / #702 / TC-F7-002 |
| convert-bulletin route docstring | TC-F6-030 |
| ingest-collect route docstring | ADR-024 |
| validate + ICAO translation stats docstrings | F21 / ADR-031 |
| (comments-only) | out of scope |

### Frontend

Operator-visible string literals appear **clean** so far (SoftPreview already plain language). ADRs/EV/S0 appear in **comments** and **tests** (keep). Guard still required for regression.

### Client errors

No common `HTTPException(detail=…ADR…)` found; `NotImplementedError` ADR-033 is developer-path — confirm not returned as public `detail`.

## Tech Stack Summary

| Category | Choice | Source |
|----------|--------|--------|
| OpenAPI | FastAPI export | TC-EV048-002 |
| BE test | pytest unit | TC-EV048-002/004/005 |
| FE test | Vitest | TC-EV048-003/005 |
| Connectivity | 10-e2e if UI hits; 12/13 waived | routing |

## Data Dependencies

None.

## Implementation Phases

### Phase 1: Copy hygiene

**Entry**: `D-S057-04-plan=1` approved.  
**Exit**: AC1–AC6 green; tip tests green; PR lists audit findings.

#### M1: Red guards + audit report — P0

**Goal**: Failing tests encode guard; PR audit list drafted.  
**Acceptance**: TC-EV048-001/005 red then green after M2/M3.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T1.1 | Backend unit: walk `app.openapi()` strings; assert no guard patterns; include synthetic inject regression | Test | completed | TC-EV048-002/005 | — | — |
| T1.2 | Frontend Vitest: scan agreed string catalogs; synthetic inject regression | Test | completed | TC-EV048-003/005 | — | — |
| T1.3 | Write audit findings markdown for PR (`reports/audit-internal-doc-refs.md`) | Docs | completed | TC-EV048-001 | — | — |

#### M2: Strip OpenAPI + client-facing copy — P0

**Goal**: OpenAPI export clean; operator-friendly replacements.  
**Acceptance**: TC-EV048-002/004 green.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T2.1 | Rewrite Field/`Form` descriptions in `schemas/conversion.py`, `schemas/validation.py`, `api.py` Form params | Code | completed | AC2/AC6; #951 examples | T1.1 | — |
| T2.2 | Rewrite route docstrings that feed OpenAPI (`api.py`, `icao_opmet.py`, related) — keep Auth note without ADR/F21 planning IDs | Code | completed | AC2 | T1.1 | — |
| T2.3 | Spot-check client `detail` paths; fix any leaks; keep comments citing corpus | Code | completed | AC4 | T1.1 | — |

#### M3: FE catalog guard + any UI fixes — P0

**Goal**: FE guard green; fix any visible hits if audit finds them.  
**Acceptance**: TC-EV048-003 green; T3 only if needed.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T3.1 | Implement FE string catalog scanner module + Vitest | Code | completed | TC-EV048-003/005 | T1.2 | — |
| T3.2 | Fix any operator-visible FE leaks found; else document clean | Code | completed | AC3 | T1.2, T1.3 | — |
| T3.3 | Optional Playwright UJ-055 if T3.2 found visible hits | Test | skipped | UJ-055; D-S057-04-t3 — no FE hits | T3.2 | — |

## PR Plan

| PR | Base | When |
|----|------|------|
| EV-048 strip internal doc refs | `stage` | After 08–11 |

## Replacement examples (locked intent)

| Bad | Good |
|-----|------|
| Soft-preview mode (ADR-022): … | Soft-preview: best-effort IWXXM with failure spans on partial convert |
| F9 / ADR-025 | Deterministic plain-language paragraph of the report |
| Public (no JWT) — F21 / ADR-031 | Public (no login required) |
