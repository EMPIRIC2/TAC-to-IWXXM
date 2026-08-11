# Execution plan — S064 / EV-055 (Quality metrics C14N + 2025-2 validate)

> **Generated**: 2026-08-11  
> **Skill**: 04-tech-plan (delta)  
> **Branch**: `evolve/EV-055-quality-metrics-2025-2-followups`  
> **Issues**: [#982](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/982),
> [#980](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/980),
> [#979](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/979)  
> **Build Plan Card**: `docs/sessions/S064-quality-metrics-2025-2-followups/build-plan-card.md`

**Corpus**: [Corpus: product §F7] [Corpus: product §F2] [Corpus: product §F13]
[Corpus: journeys §UJ-056] [Corpus: tests] [Corpus: api] [Corpus: decisions §EV-055]

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase 1: EV-055 follow-ups |
| **Active milestone** | M1 — Engine hard fixes (#980 / #979) (**complete**) |
| **Active task** | — (M1 complete; next M2) |
| **Tasks completed** | 4 / 17 |
| **Stage** | 07-build (M1 complete → M2) |
| **Last updated** | 2026-08-11 |
| **Plan approval** | **approved** `D-S064-04-plan=1`; Gate B `D-S064-05=1` |
| **PR** | — |

## Tech decisions (locked `D-S064-04-plan=1`)

| ID | Choice |
|----|--------|
| D-S064-c14n-impl | **W3C C14N 1.0** via existing **lxml** in **`packages/iwxxm-validate`** (new helper; do **not** put lxml in `packages/shared`; do **not** overload ADR-032 `canonicalize_xml`). FE: small **TypeScript exclusive-C14N** helper (no new npm). Generator imports validate-package helper; FE uses TS peer (`D-S064-gateA-M1=1`; Gate B `D-S064-c14n-host=1`). |
| D-S064-c14n-host | **1** — Python C14N lives in `packages/iwxxm-validate` (lxml already declared); shared stays dep-free. |
| D-S064-adr-c14n | Short ADR: Quality-metrics equality/diff uses W3C C14N; ADR-032 canonicalize remains for other comparative/CI paths until callers migrate. |
| D-S064-engine-path | #980: enable Schematron for 2025-2 on **native (F13)** path so evaluation occurs; document lxml vs native matrix. #979: fix XSD import resolution in `packages/iwxxm-validate` (+ backend parity utilities if they still soft-skip). |
| D-S064-pane-ux | Detail panes default to **C14N XML**; control toggles to **raw** (`D-S064-gateA-M2=override`). Diff always on C14N peers. |
| D-S064-regen-task | After generator switches to C14N and engine fixes land, run `make generate-quality-metrics` and commit artifact (`D-S064-regen=1`). |
| D-S064-m-order | **M1 engine → M2 C14N helpers → M3 generator+regen → M4 FE panes → M5 E2E/docs** (risk-first for hard #980/#979). |
| D-S064-deps | **No new runtime deps** expected (lxml already inventoried). If native Schematron tooling forces a dep, amend 06 + inventory before merge. |
| D-S064-connectivity | Existing CORS / H0c; no new `configure_cors` tasks. H4–H5 via stages 12/13 (UJ-056 deepen). |

### Locked (prior / Gate A)

| ID | Choice |
|----|--------|
| D-S064-c14n | Always W3C C14N |
| D-S064-sch-hard | #980 Schematron enable **required** |
| D-S064-xsd-hard | #979 SCHEMA_IMPORT **fix required** |
| D-S064-gateA-M1 | Shared generator + FE normalize semantics |
| D-S064-gateA-M2 | Panes normalized by default; override → raw |
| D-S064-normalize | Both sides; `match_status` = normalized equality |
| D-S064-regen | Regenerate `corpus_metrics` |
| D-S064-engine | F2/F13 engine-in allowed |
| D-S064-route | Standard; PR → `stage`; skip 03/06 |

## Tech Stack Summary

| Category | Choice | Source |
|----------|--------|--------|
| C14N (Python) | lxml C14N helper in `packages/iwxxm-validate` | `D-S064-c14n-host=1`; inventory lxml |
| C14N (FE) | Local TS helper; no new npm | `D-S064-gateA-M1` |
| Match / artifact | `scripts/ci/generate_quality_metrics.py` → `corpus_metrics.json` | EV-054 path; switch to C14N |
| Validate engine | `packages/iwxxm-validate` (+ backend utilities parity) | F2/F13; #980/#979 |
| FE surface | `QualityMetricsDetail` panes + diff | F7.q; UJ-056 |
| E2E | Playwright UJ-056 deepen | TC-EV055-007; H4–H5 @ 12/13 |
| Connectivity | Existing CORS | H0c / H4–H5 |

## Data Dependencies

| Asset | Status | Notes |
|-------|--------|-------|
| Vendor IWXXM 2025-2 pin | staged in-repo | Read-only; no hand-edits |
| `corpus_metrics.json` | **regen in M3** | After C14N + engine fixes |
| Native iwxxm-validate build | CI/local | Required for #980 enable path |

## Implementation Phases

### Phase 1: EV-055 follow-ups (F7.q + F2/F13)

**Entry**: Gate A PASS (`D-S064-gateA=1`); `D-S064-04-plan` approved.  
**Exit**: AC1–AC7 met; tip CI green; UJ-056 deepen; ready for 05→07…→13.

#### M1: Engine hard fixes (#980 / #979) — P0

**Goal**: 2025-2 Schematron **evaluated**; SCHEMA_IMPORT_WARNING **gone** on representative path.  
**Acceptance**: TC-EV055-004, TC-EV055-005; AC4–AC5.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T1.1 | Red tests: 2025-2 must not close with `SCHEMATRON_SKIPPED`; matrix stub (lxml vs native) | Test | completed | TC-EV055-004; AC4; `D-S064-sch-hard=1` | — | vendor 2025-2 |
| T1.2 | Enable Schematron for 2025-2 (native path); stop soft-skip as success; document matrix | Impl | completed | AC4; F13; #980 | T1.1 | native build |
| T1.3 | Red tests: SCHEMA_IMPORT_WARNING absent / XSD compiles for resolved 2025-2 import | Test | completed | TC-EV055-005; AC5; `D-S064-xsd-hard=1` | — | vendor 2025-2 |
| T1.4 | Fix XSD import resolution (file + URI); backend utility parity if still soft-skipping | Impl | completed | AC5; F2; #979 | T1.3 | — |

#### M2: W3C C14N helpers (shared) — P0

**Goal**: Python + FE C14N helpers with golden coverage; ADR note vs ADR-032.  
**Acceptance**: TC-EV055-003; AC3.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T2.1 | Unit tests + ≥1 golden for Python W3C C14N helper (whitespace-equal peers) | Test | pending | TC-EV055-003; AC3 | — | — |
| T2.2 | Implement `c14n_xml` (name TBD) in `packages/iwxxm-validate`; keep ADR-032 `canonicalize_xml` intact; no lxml on `packages/shared` | Impl | pending | AC3; `D-S064-c14n=1`; `D-S064-c14n-host=1` | T2.1 | lxml (validate pkg) |
| T2.3 | FE TS C14N helper tests + implement; Vitest parity with Python golden | Test/Impl | pending | TC-EV055-003; `D-S064-gateA-M1=1` | T2.1 | — |
| T2.4 | ADR: Quality metrics C14N vs ADR-032 canonicalize | Docs | pending | `D-S064-adr-c14n` | T2.2 | — |

#### M3: Generator match_status + corpus_metrics regen — P0

**Goal**: Precomputed `match_status` = C14N equality; artifact regenerated.  
**Acceptance**: TC-EV055-002, TC-EV055-006; AC2/AC7.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T3.1 | Generator tests: formatting-only pair → `match_status=equal` under C14N | Test | pending | TC-EV055-002; AC2 | T2.2 | — |
| T3.2 | Switch `generate_quality_metrics.py` from ADR-032 canonicalize to C14N for match | Impl | pending | AC2; [Corpus: api] | T3.1, T1.2, T1.4 | — |
| T3.3 | `make generate-quality-metrics`; commit `corpus_metrics.json`; loader/summary smoke | Data/Test | pending | TC-EV055-006; AC7; `D-S064-regen=1` | T3.2 | artifact |

#### M4: FE panes + C14N diff + validate chips — P0

**Goal**: Normalized panes by default; override → raw; quieter diff; validate disposition UX.  
**Acceptance**: TC-EV055-001; AC1/AC6; partial TC-EV055-007.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T4.1 | Vitest: default panes show C14N; toggle shows raw; diff empty/semantic-only for formatting stem | Test | pending | TC-EV055-001; AC1; `D-S064-gateA-M2=override` | T2.3 | — |
| T4.2 | Wire `QualityMetricsDetail`: default C14N panes, override control, `unifiedLineDiff` on C14N peers | Impl | pending | AC1/AC6; UJ-056 | T4.1, T3.3 | — |
| T4.3 | Validate chip/copy reflects enabled/fixed disposition (no skip-as-OK); EV-048 operator copy clean | Impl/Test | pending | AC6; TC-EV055-004..005 | T1.2, T1.4, T4.2 | — |

#### M5: E2E / CI / docs closeout — P0

**Goal**: UJ-056 deepen Playwright; tip CI; docs parity; handoff 05/08 chain.  
**Acceptance**: TC-EV055-007; AC7; tip ready for verify/deploy.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T5.1 | Playwright UJ-056 deepen: C14N panes + override + validate chips | Test | pending | TC-EV055-007; UJ-056; H4–H5 @ 12/13 | T4.3 | — |
| T5.2 | Docs touch-up if wire/ADR drifted; evolve-decisions 04 log; tip push + CI | Docs/CI | pending | AC6/AC7 | T5.1 | — |
| T5.3 | Board: keep #982/#980/#979 In progress until PR; then In review | Config | pending | `D-S064-board=1` | T5.2 | — |

**M5 exit / connectivity**: T5.1 covers local Playwright. Live **H4–H5** staging smoke → stages **12-verify-deploy** + **13-deploy-smoke**.

## Task Tracking

| Task | Milestone | Status | Blocked by |
|------|-----------|--------|------------|
| T1.1 | M1 | completed | — |
| T1.2 | M1 | completed | T1.1 |
| T1.3 | M1 | completed | — |
| T1.4 | M1 | completed | T1.3 |
| T2.1 | M2 | pending | — |
| T2.2 | M2 | pending | T2.1 |
| T2.3 | M2 | pending | T2.1 |
| T2.4 | M2 | pending | T2.2 |
| T3.1 | M3 | pending | T2.2 |
| T3.2 | M3 | pending | T3.1, T1.2, T1.4 |
| T3.3 | M3 | pending | T3.2 |
| T4.1 | M4 | pending | T2.3 |
| T4.2 | M4 | pending | T4.1, T3.3 |
| T4.3 | M4 | pending | T1.2, T1.4, T4.2 |
| T5.1 | M5 | pending | T4.3 |
| T5.2 | M5 | pending | T5.1 |
| T5.3 | M5 | pending | T5.2 |

## Git Strategy

- Branch: `evolve/EV-055-quality-metrics-2025-2-followups` (base `stage@4fd51e39`)
- PR → `stage` after 08/09/10/11 (and 12/13 per routing)
- Prefer one logical commit per task / small groups per milestone
- Board: #982 / #980 / #979 → **In review** when PR opens

## Out of scope

- Hand-editing `vendor/schemas/*`
- Replacing ADR-032 canonicalize for all non–quality-metrics callers this cycle
- Redoing Quality metrics tab shell (#836)
- DOKS / F30 (EV-043 / EV-044)
- New npm XML-diff / C14N package (v1 = local helpers)
- `stage`→`main` unless explicitly approved

## Phase Gate Log

| Gate | Result | Notes |
|------|--------|-------|
| A (02) | PASS | `D-S064-gateA=1` |
| B (05) | — | After 04 approval |
| C (08) | — | After 07 |
