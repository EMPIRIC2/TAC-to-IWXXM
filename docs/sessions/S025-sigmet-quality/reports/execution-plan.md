# Execution plan — S025 / EV-019 (F23 + F6.d/F12 deepen)

> **Status**: **approved** (2026-07-29) — E19-19..22 (B / B+A / A / A)  
> **Branch**: `evolve/EV-019-sigmet-quality`  
> **Evolve cycle**: EV-019  
> **Features**: F23 (new); deepen F6.d / F12 (SIGMET + VA SIGMET)  
> **Spec sources**: feature-list §F23; ADR-028; UJ-034; TC-F23-001..006;
> COVERAGE_MATRIX F23 themes G1–G3 / V1–V3 / C1; api-contract S025 review; E19-1..E19-22

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase C — 07-build |
| **Active milestone** | M2 — General SIGMET goldens (F23 theme G3 / F6.d) |
| **Active task** | T2.3 (pending) |
| **Tasks** | 10 / 29 completed |
| **Last updated** | 2026-07-29 |

## Tech Stack Summary

| Area | Choice | Source |
|------|--------|--------|
| Registry | Reuse ADR-028 `packages/tac-validate` registry; add SIGMET (+ VA) rows | E19-3 |
| Public codes | SCREAMING_SNAKE; optional `product`/`tags` (e.g. `sigmet`, `va_sigmet`) | EV-011 pattern |
| Catalog (docs) | Regenerate `ISSUE_CATALOG.md` (+ JSON); drift tests | Existing |
| Catalog (HTTP) | Existing `GET /api/v1/lint-issue-catalog` — **extend FE filters/copy for SIGMET/VA tags** | E19-17=B |
| Research | **Full mining pass** → session `sigmet-research-catalog.md` | E19-16=B |
| Lint fixtures | `packages/tac-validate/tests/fixtures/{accept,negative}/sigmet/` (+ VA as needed) | TC-F23-004 |
| Convert goldens | Extend `tac2iwxxm` annex3 goldens; roots `iwxxm:SIGMET` / `VolcanicAshSIGMET` | TC-F23-002/003 |
| CI | **Dedicated** `.github/workflows/sigmet-quality.yml` + existing `ci-cd.yml` package matrix | E19-19=B |
| New deps | **AskQuestion per new dependency** (default none) | E19-18=B |
| HTTP wire | Unchanged (`product=sigmet`; content-selected VA root) | E19-13 |
| Deploy | API+FE redeploy at M5; H1–H3 if API; **H4–H5 required** (FE catalog) | E19-21=A |
| Kill-switch | HARD themes; mid-build block → AskQuestion (no silent defer) | S1.M1 |
| Mining | Full dig **SIGMET + VA SIGMET**; **light sibling notes** (#738/AIRMET/VAA cite-only) | E19-20=B+A |
| Theme naming | Always “F23 theme G1” vs “gate G1” | S6.M1 |

## Interview locks (Batch 1 + 2)

| ID | Decision |
|----|----------|
| E19-15 | Milestone order **A** — Research → G1–G2 → G3 → V1–V2 → V3 → C1/matrix → smoke |
| E19-16 | Research **B** — full mining + `sigmet-research-catalog.md` |
| E19-17 | FE **B** — extend catalog panel for SIGMET/VA tags (**amends E19-14**) |
| E19-18 | Deps **B** — AskQuestion per new dependency (prefer none) |
| E19-19 | CI **B** — dedicated `sigmet-quality.yml` workflow |
| E19-20 | Mining **B+A** — dig SIGMET+VA; light sibling notes (cite-only) |
| E19-21 | Deploy **A** — redeploy; H1–H3 if API; H4–H5 required |
| E19-22 | Plan **A** — approve M0–M5; skip 05/06; B→C → 07 @ T0.1 |

## Milestones & Tasks (TDD order)

`evolve_cycle_id: EV-019` · `feature_ids: [F23, F6, F12]`

### M0 — Research mining catalog (F23)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T0.1 | Docs | Mine WMO guidance + EUR Doc 014 + Annex/codes cites for SIGMET+VA; write `reports/sigmet-research-catalog.md` mapping → F23 themes G1–G3 / V1–V3 / C1; **light sibling notes** (#738 TC / AIRMET / VAA — cite-only) | E19-16; E19-20; #733/#739 | — | completed |
| T0.2 | Docs | Link catalog from COVERAGE_MATRIX F23 section; cite-only paywall | F23 acc5 | T0.1 | completed |
| T0.3 | Config | Add dedicated `.github/workflows/sigmet-quality.yml` (path-filtered SIGMET/VA pytest packs for tac-validate + tac2iwxxm); document in Makefile if needed | E19-19=B | T0.2 | completed |

### M1 — General SIGMET lint (F23 themes G1–G2 / F12)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T1.1 | Test | Accept/negative fixtures F23 theme G1 (CNL, point→circle, single alt, STNR, polygon/line CRS) | TC-F23-004; matrix G1 | T0.2 | completed |
| T1.2 | Code | Registry rows + SIGMET rules for G1 | F23; ADR-028 | T1.1 | completed |
| T1.3 | Test | Fixtures F23 theme G2 (sequence / validity / FIR·CTA / phenomenon / movement·intensity) | matrix G2 | T1.2 | completed |
| T1.4 | Code | Encode G2 checklist rules | F23 | T1.3 | completed |

### M2 — General SIGMET goldens (F23 theme G3 / F6.d)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T2.1 | Test | Expand annex3 general SIGMET golden manifests (`sigmet-A6-1a-TS`, CNL, …); M-xsd/M-sch stubs; root `iwxxm:SIGMET` | TC-F23-002 | T1.4 | completed |
| T2.2 | Code | Convert fidelity fixes for general SIGMET exceptional rules | F6.d; #733 | T2.1 | completed |
| T2.3 | Docs | Mark F23 themes G1–G3 closed or AskQuestion-deferred | S1.M1 | T2.2 | pending |

### M3 — VA SIGMET lint + adjacency (F23 themes V1–V2)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T3.1 | Test | VA accept/negative fixtures (volcano identity, ash geometry/forecast, `NO VA EXP`, CNL FIR-moved) | TC-F23-004; #739; V1 | T2.3 | pending |
| T3.2 | Code | VA SIGMET registry rules + encode path toward `VolcanicAshSIGMET` | F12; F23 | T3.1 | pending |
| T3.3 | Test | Adjacency guards: VA↔general SIGMET↔VAA (never silent root/product swap) | TC-F23-006; V2 | T3.2 | pending |
| T3.4 | Code | Content-selected root under `product=sigmet`; product-hint / Auto-detect fixes if any fail | E19-13; F23 | T3.3 | pending |

### M4 — VA goldens + C1 / matrix close (F23 themes V3 / C1)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T4.1 | Test | Expand VA SIGMET goldens (`sigmet-VA-EGGX`, …); root `iwxxm:VolcanicAshSIGMET`; M-xsd/M-sch | TC-F23-003; V3 | T3.4 | pending |
| T4.2 | Code | Convert fidelity for VA goldens | F6.d; #739 | T4.1 | pending |
| T4.3 | Test | Common-rule fixtures (reportStatus/nilReasons/CRS/one-report/`translationFailedTAC`) where lint applies | matrix C1 | T4.2 | pending |
| T4.4 | Code | Encode/defer C1 with rationale (F20 C1 pattern) | F23; guidance | T4.3 | pending |
| T4.5 | Docs | COVERAGE_MATRIX F23 acc checklist; ISSUE_CATALOG regen; mark V1–V3/C1 closed or deferred | F23 acc5; S1.M1 | T4.4 | pending |
| T4.6 | Test | TC-F23-001 registry completeness green | TC-F23-001 | T4.5 | pending |

### M5 — FE catalog SIGMET/VA tags + smoke + verify (F23)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T5.1 | Test | Vitest: catalog panel filters/copy for SIGMET (+ VA) tags | E19-17; TC-F23-005 | T4.6 | pending |
| T5.2 | Code | FE: extend catalog panel filters/copy for SIGMET/VA (additive) | E19-17; UJ-034 | T5.1 | pending |
| T5.3 | Test | API/workbench smoke `product=sigmet` lint+convert (general + VA fixtures) + catalog GET | TC-F23-005 | T5.2 | pending |
| T5.4 | Config | 08-verify-build — lint/typecheck/format/full suites | 08 | M0–M4, T5.2 | pending |
| T5.5 | Test | 10-e2e — UJ-034 / TC-F23-001..006 (09 skipped Lean+build) | 10 | T5.4 | pending |
| T5.6 | Test | 13-deploy-smoke — redeploy if API/FE changed; H1–H3 if API; **H4–H5 required** (T5.2) | 13; E19-7 | T5.5 | pending |

## Data Dependencies

| Asset | Needed by | Notes |
|-------|-----------|-------|
| Vendor `TAC-to-XML-Guidance.txt` + 2025-2 XSD/SCH | M0–M4 | Read-only vendor |
| #733/#739 exceptional-rule tables | M1–M4 | Issue bodies |
| Existing SIGMET/VA goldens (`sigmet-A6-*`, `sigmet-VA-EGGX`) | M2 / M4 | Extend |
| EUR Doc 014 mining notes | M0 | Public TAC shape |
| Mining sources (Annex/FM 205/codes — cite-only) | M0 | Full dig per E19-16; siblings light notes E19-20 |
| F15/F20 adjacency patterns | M3 V2 | TC-F15-005 / TC-F20-006 peers |

## Git Strategy

- Branch: `evolve/EV-019-sigmet-quality`
- Atomic commits per task: `[T1.1] test: …`
- Evolve PR to `main` after M5 / Phase D
- After push: `bash scripts/ci/watch_github_ci.sh`
- **HARD themes (S1.M1)**: if blocked mid-build → AskQuestion; do **not** silently defer
- Theme ids: always “F23 theme Gn” vs “gate Gn” (S6.M1)
- Dedicated workflow: `sigmet-quality.yml` (E19-19) — still run full `ci-cd.yml` on PRs

## Connectivity (H0c / H4–H5)

- No new CORS / `VITE_*` knobs expected
- FE catalog filter work → **H4–H5 required** after FE deploy (E19-17 / E19-21)
- Re-run H0c if API image changes
- Staging secrets matrix: reuse existing rows

## Phase Gate Check (B→C)

- [x] Execution plan approved by user (E19-22=A)
- [x] 05-verify-tech — **skipped** (S9.M1); 04-exit consistency PASS (below)
- [x] 06-tech-tooling — **skipped** (Lean+build; no new hooks in plan)

## 04-exit consistency (S9.M1 substitute for 05)

| Check | Result |
|-------|--------|
| F23 ↔ milestones M0–M5 | **PASS** |
| UJ-034 ↔ TC-F23 ↔ tasks | **PASS** |
| F23 themes G/V/C ↔ M1–M4 | **PASS** |
| FE catalog filters ↔ T5.1–T5.2 + H4–H5 | **PASS** (E19-17 / E19-21) |
| Dedicated GHA ↔ T0.3 | **PASS** (E19-19) |
| Sibling light notes ↔ T0.1 | **PASS** (E19-20 B+A) |
| No new routes vs api-contract | **PASS** |
| Deps policy AskQuestion-gated | **PASS** |
| 05/06 skip documented | **PASS** |
| E19-14 amend noted (E19-17) | **PASS** |

## Phase Gate Log

| Gate | Date | Result | Notes |
|------|------|--------|-------|
| A→B | 2026-07-29 | passed | D-S025-02-phase-a-A |
| B plan | 2026-07-29 | approved | E19-19..22; D-S025-04-plan-approve-A |
| B tech audit | 2026-07-29 | waived | 05 skipped; 04-exit consistency PASS |
| B→C | 2026-07-29 | passed | D-S025-04-plan-approve-A → 07 @ T0.1 |
