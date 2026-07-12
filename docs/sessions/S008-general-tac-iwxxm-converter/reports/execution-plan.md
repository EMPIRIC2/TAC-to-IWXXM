# Execution Plan — S008 F6 tac2iwxxm + Validate Packages + F8 Worker

> **Project**: METAR to IWXXM Converter  
> **Generated**: 2026-07-12  
> **Skill**: 04-tech-plan (delta)  
> **Session**: S008-general-tac-iwxxm-converter  
> **Branch**: `evolve/S008-general-tac-iwxxm-converter`  
> **Mode**: delta (extends historical monorepo / EV-004 plans; does not reset them)  
> **Specs consumed**: feature-list.md, spec.md, user-journeys.md, test-plan.md, api-contract.md,
> dependency-inventory.md, ADR-013–015, context/general-tac-iwxxm-converter.md,
> context/realtime-tac-ingest.md, decisions D-S008-04-q1q5 … q16q20

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase 1: Package Scaffold (pending approval) |
| **Active milestone** | M1: Workspace members |
| **Active task** | T1.1 |
| **Tasks completed** | 0 / 44 |
| **Last updated** | 2026-07-12 |

## Tech Stack Summary (S008 delta)

| Category | Choice | Source | Spec Reference |
|----------|--------|--------|----------------|
| Template | `static+api` → **`static+api+worker`** | Q15b=B, Q19=A | ADR-018 |
| Language | Python 3.12 + uv workspace | existing | ADR-005 |
| Frontend | Node 22 + pnpm (unchanged this cycle for F7) | existing | — |
| Package layout | `src/` (auth/shared style) | Q1=A | ADR-016 |
| Package IR / issues | **msgspec.Struct** (+ reused Encoder/Decoder) | Q2=B, Q9=C | ADR-016 |
| HTTP schemas | **pydantic** at FastAPI boundary only | Q2=B | ADR-016 |
| Perf gate | Sub-second benches (unit + E2E lib path); soft→hard at cutover | Q11=C | ADR-016 |
| Native | **PyO3 required**; cutover blocked until green | Q12b=A | ADR-017 |
| Validate packages | New `iwxxm-validate` + `tac-validate` (MIT); delete inline F2 at cutover | Q3=B | ADR-015/018 |
| Bulletin API | Partial success + `bulletin_meta` + lint-style issues/fixes | Q6=A, Q7=C | api-contract |
| lint-tac | Multipart only; convert lint flag **default on** | Q8=A, Q14=C | api-contract |
| H7 | `make test-live-bulletin` + pytest; fold into `make test-live` | Q10=A | test-plan |
| Vendor | `iwxxm-us` pin early in Phase 1 | Q13=A | ADR-013 |
| Cutover | Aggressive (ii): gifts delete when METAR/SPECI annex3 + wrappers + bulletin + **PyO3/benches** green | Q5=(ii) | ADR-014/017 |
| F8 worker | `apps/worker/` Render Background Worker | Q15–Q20 | ADR-018 |
| F8 ingest | HTTPS / object-prefix **poller** | Q16=A | ADR-018 |
| F8 store | Supabase on pass; **separate quarantine** store | Q17=A, Q18=B | ADR-018 |
| F8 writers auth | Supabase **service role JWT** | Q20=C | ADR-018 |
| CI | Extend `ci-cd.yml` matrix; coverage ≥95% new packages | Q15=A base + worker | ADR-007 |
| Deploy | Existing API image + **new worker service**; no dedicated converter API | Q15b=B | deploy.md |

## Feature ↔ Milestone Mapping

| Feature | Milestones | Deliverable |
|---------|------------|-------------|
| M1/M5 | M1 | Three uv members + Makefile/CI |
| F2 → package | M2 | `iwxxm-validate` + thin `/validate` |
| F6 lint | M2 | `tac-validate` + `/lint-tac` |
| F6.bulletin + F6.a | M3–M4 | Bulletin split + METAR/SPECI + PyO3 + cutover |
| F6.b–f | M5 | Remaining five products post-cutover |
| H7 | M4 / M7 | Live bulletin gate |
| F8 | M6–M7 | Worker poller + Supabase store/quarantine + deploy |

## Data Dependencies

| Asset | Type | Staging Status | Needed By |
|-------|------|----------------|-----------|
| `vendor/schemas/iwxxm*` | schemas | present | M2–M5 |
| `vendor/schemas/iwxxm-us` | schemas | **pending pin** | M1, M3+ |
| AHL bulletin fixtures | test-data | pending | M3, M4, H7 |
| Gifts annex3 goldens (archive) | goldens | present (pre-delete) | M4 cutover |
| Supabase project | Postgres | present | M6 F8 tables |
| Poller HTTPS fixture URL | staging secret | pending | M6–M7 |

## Implementation Phases

### Phase 1: Package Scaffold & Vendor Pin

**Objective**: Workspace members, msgspec deps, iwxxm-us pin, CI/Makefile hooks.  
**Entry gate**: This plan approved.  
**Exit gate**: Three packages importable; CI matrix rows exist; iwxxm-us in manifest.

#### M1: Workspace + iwxxm-us

| # | Task | Type | Status | Spec Source | Depends On |
|---|------|------|--------|-------------|------------|
| T1.1 | Test: empty package import smoke for three names | Test | pending | TC-F6-M001 | — |
| T1.2 | Config: scaffold `packages/{tac2iwxxm,iwxxm-validate,tac-validate}` (`src/` + pyproject MIT) | Config | pending | ADR-016, Q1 | T1.1 |
| T1.3 | Config: add uv members, Makefile `lint`/`test-unit-*`, `ci-cd.yml` matrix | Config | pending | M5, ADR-007 | T1.2 |
| T1.4 | Config: add `msgspec` to tac2iwxxm + tac-validate; document Encoder reuse | Config | pending | ADR-016, Q2 | T1.2 |
| T1.5 | Config: pin `vendor/schemas/iwxxm-us` + manifest + integrity test | Config | pending | Q13=A, UJ-DEV-003b | — |
| T1.6 | Docs: dependency-inventory IR = msgspec; PyO3 required note | Docs | pending | ADR-016/017 | T1.4 |

**Phase 1 gate**: T1.1–T1.5 green; no gifts deletion yet.

---

### Phase 2: Validate Packages + HTTP Wrappers

**Objective**: New engines from scratch; thin API wrappers; lint-tac multipart.  
**Entry gate**: Phase 1 gate.  
**Exit gate**: `/validate` and `/lint-tac` call packages; TC-F6-031/032/033 green (pre-cutover duplicate F2 OK until M4).

#### M2: iwxxm-validate + tac-validate + routes

| # | Task | Type | Status | Spec Source | Depends On |
|---|------|------|--------|-------------|------------|
| T2.1 | Test: iwxxm-validate XSD+Schematron fixtures (TC-F6-032) | Test | pending | test-plan TC-F6-032 | T1.2 |
| T2.2 | Code: implement `packages/iwxxm-validate` (lxml; vendor read-only) | Code | pending | ADR-015, Q3=B | T2.1 |
| T2.3 | Test: tac-validate msgspec issues + optional fixes (TC-F6-031) | Test | pending | Q9=C | T1.4 |
| T2.4 | Code: implement `packages/tac-validate` rule pack skeleton (7 products) | Code | pending | ADR-015 | T2.3 |
| T2.5 | Test: API `/lint-tac` multipart + `/validate` wrapper contract | Test | pending | api-contract, Q8=A | T2.2, T2.4 |
| T2.6 | Code: thin wrappers; OpenAPI/shared types; `lint` form flag default **true** on convert | Code | pending | Q14=C, Q51–53 | T2.5 |
| T2.7 | Test: sub-second benches soft-fail for lint + validate alone (Q11 A) | Test | pending | ADR-016 Q11=C | T2.2, T2.4 |

**Phase 2 gate**: Wrappers green; old inline F2 still present until M4 delete tasks.

---

### Phase 3: Bulletin + METAR/SPECI + PyO3 (pre-cutover)

**Objective**: F6.bulletin with/before F6.a; PyO3 extension; benches.  
**Entry gate**: Phase 2 gate.  
**Exit gate**: Bulletin + METAR/SPECI annex3 green; PyO3 wheel builds; Q11 benches soft-pass.

#### M3: Bulletin split + convert-bulletin API

| # | Task | Type | Status | Spec Source | Depends On |
|---|------|------|--------|-------------|------------|
| T3.1 | Test: AHL split fixtures → N reports (TC-F6-030 T0) | Test | pending | F6.bulletin, Q4=A | T1.2 |
| T3.2 | Code: bulletin splitter in `tac2iwxxm` | Code | pending | spec.md pipeline | T3.1 |
| T3.3 | Test: `/convert-bulletin` multi-result schema (partial OK + issues/fixes) | Test | pending | Q6=A, Q7=C | T3.2, T2.6 |
| T3.4 | Code: `POST /convert-bulletin` + pydantic response map from msgspec | Code | pending | api-contract | T3.3 |
| T3.5 | Config: commit multi-report AHL fixture for H7 | Config | pending | TC-LIVE-F6-030 | T3.1 |

#### M4: METAR/SPECI + PyO3 + cutover PR

| # | Task | Type | Status | Spec Source | Depends On |
|---|------|------|--------|-------------|------------|
| T4.1 | Test: METAR/SPECI annex3 goldens (TC-F6-020/021) | Test | pending | test-plan | T3.2 |
| T4.2 | Code: METAR/SPECI plugins + XML emit (Python) | Code | pending | F6.a | T4.1 |
| T4.3 | Config: maturin/PyO3 crate scaffold + CI rust job | Config | pending | ADR-017 | T1.2 |
| T4.4 | Test: PyO3 hotspot tests + Q11 E2E lib bench (soft) | Test | pending | Q11=C, Q12b=A | T4.2, T4.3 |
| T4.5 | Code: implement required PyO3 hotspots; hard-pass Q11 benches | Code | pending | ADR-017 | T4.4 |
| T4.6 | Test: cutover gate suite (UJ-001, no gifts imports) | Test | pending | F6 cutover PR gate | T4.5, T3.4, T2.6 |
| T4.7 | Code: wire `/convert` → tac2iwxxm; **delete `packages/gifts`**; delete inline F2 engine | Code | pending | Q5=(ii), Q3=B, ADR-014 | T4.6 |
| T4.8 | Config: CI drop gifts cell; health `tac2iwxxm_available`; archive gifts goldens | Config | pending | TC-F6-022 | T4.7 |
| T4.9 | Config: `make test-live-bulletin` + fold into `make test-live` | Config | pending | Q10=A, H7 | T3.5, T4.7 |

**Phase 3 gate**: Cutover merged; H7 runnable against staging after deploy; gifts gone.

---

### Phase 4: Remaining F6 Products

**Objective**: AIRMET, SIGMET, TAF, VAA, TCA (+ US where applicable) on tac2iwxxm-only tree.  
**Entry gate**: Phase 3 gate.  
**Exit gate**: TC-F6-001/002/003 product matrix green.

#### M5: F6.b–f products

| # | Task | Type | Status | Spec Source | Depends On |
|---|------|------|--------|-------------|------------|
| T5.1 | Test: product matrix fixtures (7 products) | Test | pending | TC-F6-001/002 | T4.7 |
| T5.2 | Code: TAF / SIGMET / AIRMET plugins | Code | pending | F6.b–d | T5.1 |
| T5.3 | Code: VAA / TCA plugins | Code | pending | F6.e–f | T5.1 |
| T5.4 | Test: iwxxm_us profile where published | Test | pending | TC-F6-003 | T1.5, T5.2 |
| T5.5 | Code: US profile extensions | Code | pending | ADR-013 | T5.4 |

**Phase 4 gate**: F6 v1 product QA checklist items for products green.

---

### Phase 5: F8 Worker

**Objective**: `apps/worker` poller → pipeline → Supabase store / quarantine.  
**Entry gate**: Phase 3 gate (packages usable); Phase 4 may run in parallel after T4.7.  
**Exit gate**: Worker processes fixture feed end-to-end locally; migrations applied.

#### M6: Worker + Supabase

| # | Task | Type | Status | Spec Source | Depends On |
|---|------|------|--------|-------------|------------|
| T6.1 | Test: poller fetches HTTPS fixture → N jobs | Test | pending | Q16=A, UJ-014 stub→TC | T4.7 |
| T6.2 | Config: scaffold `apps/worker/` + Render worker blueprint/Dockerfile start | Config | pending | Q19=A, ADR-018 | — |
| T6.3 | Code: pipeline orchestration (lint→convert→iwxxm-validate) | Code | pending | spec unified pipeline | T6.1, T2.2, T2.4, T4.7 |
| T6.4 | Test: Supabase store + quarantine tables (service JWT) | Test | pending | Q17=A, Q18=B, Q20=C | — |
| T6.5 | Code: migrations `iwxxm_ingest_results` + `iwxxm_ingest_quarantine`; worker writers | Code | pending | ADR-018 | T6.4 |
| T6.6 | Config: worker env (`SUPABASE_*` service role, poller URL, interval) | Config | pending | config/deploy | T6.2, T6.5 |
| T6.7 | Docs: template-conformance + deploy.md worker topology | Docs | pending | ADR-018 | T6.2 |

**Phase 5 gate**: Local worker E2E green; secrets matrix updated.

---

### Phase 6: Deploy & Live Gates

**Objective**: Staging API + worker deploy; H4–H7.  
**Entry gate**: Phase 5 gate; Phase 4 ideally complete for full F6 QA.  
**Exit gate**: `make test-live` (incl. H7) green on staging.

#### M7: Staging deploy + H7

| # | Task | Type | Status | Spec Source | Depends On |
|---|------|------|--------|-------------|------------|
| T7.1 | Config: create Render Background Worker service; wire env | Config | pending | ADR-018, deploy.md | T6.6 |
| T7.2 | Test: H3 convert/lint/bulletin smoke on live API | Test | pending | H3 | T4.7 |
| T7.3 | Test: TC-LIVE-F6-030 H7 | Test | pending | H7 | T4.9, T7.1 |
| T7.4 | Test: worker live poll → store/quarantine row | Test | pending | F8 | T7.1 |
| T7.5 | Docs: 04 stage report + CHANGELOG notes for F6/F8 | Docs | pending | — | T7.3 |

**Phase 6 gate**: H4–H5, H3, H6 (existing), H7, F8 live smoke green or waivers recorded.

---

## Git Strategy

- Session branch: `evolve/S008-general-tac-iwxxm-converter`
- Milestone branches: `feat/S008-M{N}-{slug}` → session branch (or phase branches if split)
- Atomic commits per task: `[T{n.m}] type: …`
- **Cutover PR** (M4 T4.6–T4.8): single gated PR deleting gifts + wiring tac2iwxxm
- Minor PRs per milestone; major PR when session routing completes build/verify

### PR Plan

| PR | Type | Milestone | Branch | Target | Status |
|----|------|-----------|--------|--------|--------|
| PR-M1 | Minor | M1 | feat/S008-M1-scaffold | evolve/S008-… | pending |
| PR-M2 | Minor | M2 | feat/S008-M2-validate | evolve/S008-… | pending |
| PR-M3 | Minor | M3 | feat/S008-M3-bulletin | evolve/S008-… | pending |
| PR-M4 | Minor | M4 cutover | feat/S008-M4-cutover | evolve/S008-… | pending |
| PR-M5 | Minor | M5 products | feat/S008-M5-products | evolve/S008-… | pending |
| PR-M6 | Minor | M6 worker | feat/S008-M6-worker | evolve/S008-… | pending |
| PR-M7 | Minor | M7 live | feat/S008-M7-live | evolve/S008-… | pending |

## Task Tracking Summary

| Phase | Milestones | Tasks | Focus |
|-------|------------|-------|-------|
| 1 | M1 | 6 | Scaffold + iwxxm-us |
| 2 | M2 | 7 | Validate packages + HTTP |
| 3 | M3–M4 | 14 | Bulletin, METAR/SPECI, PyO3, cutover, H7 wiring |
| 4 | M5 | 5 | Remaining products |
| 5 | M6 | 7 | F8 worker + Supabase |
| 6 | M7 | 5 | Deploy + live |
| **Total** | **7** | **44** | — |

*(Adjust if tasks split during 05-verify-tech.)*

## Phase Gate Log

| Phase | Result | Date | Notes |
|-------|--------|------|-------|
| — | — | — | Populated during 07-build |

## Connectivity Checklist (04 handoff)

- [x] Bulletin multi-result schema decided (Q6/Q7)
- [x] lint-tac multipart (Q8)
- [x] H7 `make test-live-bulletin` planned (Q10 / T4.9)
- [x] CORS unchanged on existing API; worker is non-browser
- [x] Staging secrets: poller URL + Supabase service role for worker (T6.6)
- [x] F8 worker deployable (ADR-018)

## ADRs Produced This Stage

| ADR | Topic |
|-----|-------|
| ADR-016 | msgspec packages + pydantic HTTP + sub-second benches |
| ADR-017 | PyO3 hard gate (amends ADR-014) |
| ADR-018 | F8 worker + template `static+api+worker` (amends ADR-015) |

## Out of Scope (still deferred)

- F7 multi-product operator UI/sessions (Planned)
- AMHS/SWIM/AFS adapters
- Push sinks (webhook/S3/AMHS) — store + quarantine only
- Dedicated converter microservice (rejected Q15b)
