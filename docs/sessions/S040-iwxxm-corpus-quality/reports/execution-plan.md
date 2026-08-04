# Execution plan — S040 / EV-032 (#846 / #835 / #741 / #808 / #847)

> **Status**: **approved** (2026-08-04) — `D-S040-04-plan` = 1; Gate B PASS → 07 @ T0.1  
> **Branch**: `evolve/EV-032-iwxxm-corpus-quality`  
> **Evolve cycle**: EV-032  
> **Features**: **F32** (new); deepen F23 (#835) / F4 / F6 / F2 / F13 (#808 + corpus)  
> **Spec sources**: feature-list §F32 + EV-032 deepen; spec §S040/EV-032; UJ-045;
> TC-EV032-001..008; TC-F32-001..006; api-contract `product=vona`; E32-*; S02.M1–M3;
> #846 / #835 / #741 / #808 / #847; ADR-028 / ADR-032

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase C — build |
| **Active milestone** | M2 — #741 / F32 VONA |
| **Active task** | T2.6 — pending (next) |
| **Tasks** | 14 / 28 completed |
| **Last updated** | 2026-08-04 |

## Tech Stack Summary

| Area | Choice | Source |
|------|--------|--------|
| Template | `static+api+worker` | template |
| Runtime SoT | Vendor IWXXM **2025-2** (`vona-A7-1`, `sigmet-A6-2-TC`) | context |
| #835 bar | Strict ADR-032 `canonicalize_xml` equality → catalog `wmoPass` | E32-T2=1 |
| F32 encode | Cookbook + fixtures; plugin in `annex3_products` (VAA/SWXA peer); AHL discover in M2 | E32-T3/T4 |
| Examples | Incremental unlock when F32 golden greens | S02.M2 |
| API | Additive runtime `product=vona` (docs already) | api-contract |
| #808 / #847 | Docs + child issues only; durable checklists under `docs/domain/iwxxm/` | S02.M3; E32-T8 |
| New deps | **None** | E32-T5=1 |
| Deploy | API + static redeploy; **H1–H3**; **H4–H5 required** (VONA FE) | E32-T6=1 |
| Local CI | **Tiered** — fast path-filtered **pre-commit** smokes; long packs on **pre-push** / `make` | E32-T7=custom |
| Corpus inventory | Session reports + durable domain docs; children on #846 | E32-T8=1 |

### Local CI packaging (E32-T7 — improvements)

Repo already splits fast vs long:

| Tier | Where | EV-032 content |
|------|-------|----------------|
| **Fast** | `.pre-commit-config.yaml` (path-filtered, not `always_run`) | Catalog tier assert; `product=vona` enum smoke; single A6-2 equality **canary** (or skip until green); registry unknown-code guard |
| **Long** | `.husky/pre-push` → `make validate-ci` + `make ci-prepush`, plus `make test-*-quality` | Full ADR-032 equality suite; full F32 lint/convert/validate pack; corpus inventory pytest if any |

**Improvements (implement in M1/M2 Config tasks):**

1. Prefer `files:` globs over `always_run` for quality hooks (peer `render-deploy-hook-guard`).
2. Add `make test-vona-quality` + thin `scripts/ci/run_vona_quality.sh`; wire TC-SIGMET deepen into existing `test-tc-sigmet-quality` / A6-2 tests — do **not** dump full XSD+SCH packs into default pre-commit.
3. Optional pytest marker `ev032_smoke` for the pre-commit canary subset.
4. Keep default commit path seconds-scale; document in `docs/ops/DEVELOPMENT.md` if hooks grow.

## Interview locks

| ID | Decision |
|----|----------|
| E32-T1 | **1** — M0–M4 |
| E32-T2 | **1** — strict ADR-032 for #835 / `wmoPass` |
| E32-T3 | **1** — cookbook + fixtures; VAA/SWXA-peer plugin |
| E32-T4 | **1** — AHL discover in M2 |
| E32-T5 | **1** — no new deps |
| E32-T6 | **1** — redeploy API+static; H1–H3; H4–H5 required |
| E32-T7 | **custom** — pre-commit fast smokes (path-filtered); long suites pre-push/`make` + improvements above |
| E32-T8 | **1** — M0 session inventory + durable `docs/domain/iwxxm/` for #808/#847 |
| E32-T9 | **1** — Gate B PASS → 07 @ T0.1 |

## Milestones & Tasks (TDD order)

`evolve_cycle_id: EV-032` · `feature_ids: [F32, F23, F4, F6, F2, F13]`

**Work order:** M0 inventory → M1 #835 → M2 F32 → M3 #808+#847 → M4 closeout.

### M0 — Corpus / fixture inventory (#846)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T0.1 | Docs | Session inventory: vendor official peers + WMO-source map (iwxxm / translation / codelists / codes.wmo.int / modelling) under `reports/` | TC-EV032-001/005; E32-T8 | — | **completed** |
| T0.2 | Docs | Gap index → proposed #846 children (encode / golden / catalog / docs) | TC-EV032-005; #846 | T0.1 | **completed** |
| T0.3 | Docs | M0 exit checklist — proceed M1 when inventory + gaps filed or explicitly deferred | E32-T1 | T0.2 | **completed** |

### M1 — #835 A6-2-TC → `wmoPass`

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T1.1 | Test | Red: ADR-032 equality convert(annex3 A6-2-TC) vs vendor `sigmet-A6-2-TC.xml` | TC-EV032-002; E32-T2; #835 | T0.3 | **completed** |
| T1.2 | Code | Encode/canonicalize deltas (coords, airspace type, intensityChange, trailing zeros) | F23; ADR-032; #835 | T1.1 | **completed** |
| T1.3 | Test | Green equality + quality path lint→convert→XSD+SCH still green | TC-EV032-002/003 | T1.2 | **completed** |
| T1.4 | Code | Catalog promote `sigmet_a6_2_tc` → `wmoPass`; Vitest + FIXTURE_GAPS notes | TC-EV032-003; UJ-039 | T1.3 | **completed** |
| T1.5 | Config | Path-filtered pre-commit canary + ensure long pack on `make test-tc-sigmet-quality` / pre-push | E32-T7 | T1.4 | **completed** |
| T1.6 | Docs | #835 closeout | #835 | T1.5 | **completed** |

### M2 — #741 / F32 VONA quality bar

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T2.1 | Docs | VONA cookbook: TAC shapes from `vona-A7-1` + PANS-MET; AHL/T1T2 “when known”; guidance-silent gaps | TC-F32-*; E32-T3/T4; #741 | T1.6 | **completed** |
| T2.2 | Test | Registry + lint accept/negative fixtures (unknown codes fail CI) | TC-F32-001; ADR-028 | T2.1 | **completed** |
| T2.3 | Code | `tac-validate` VONA codes + rules | F12/F32 | T2.2 | **completed** |
| T2.4 | Test | Convert fixtures → `VolcanoObservatoryNoticeForAviation` (+ golden / soft→strict) | TC-F32-002/003 | T2.3 | **completed** |
| T2.5 | Code | Encode plugin in `annex3_products` (+ bulletin/AHL if discovered) | F6; E32-T3 | T2.4 | **completed** |
| T2.6 | Test | XSD+SCH validate path green on official peer | TC-F32-004; F2/F13 | T2.5 | pending |
| T2.7 | Code | Backend runtime enum `product=vona`; FE picker + Examples unlock when golden greens | TC-F32-005/006; S02.M2; UJ-045 | T2.6 | pending |
| T2.8 | Config | `make test-vona-quality` + path-filtered pre-commit smoke; long pack pre-push | E32-T7; TC-EV032-006 | T2.7 | pending |
| T2.9 | Docs | COVERAGE_MATRIX / #741 closeout or children for guidance gaps | #741; TC-F32-005 | T2.8 | pending |

### M3 — #808 + #847 release-line maintainability

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T3.1 | Docs | Engineering blast-radius + adopt/deprecate checklists → `docs/domain/iwxxm/` (align VERSION_SUPPORT_POLICY) | TC-EV032-004; #808; E32-T8 | T2.9 | pending |
| T3.2 | Docs | Non-technical staff review narrative / checklist (#847) — same durable tree or linked section | #847 | T3.1 | pending |
| T3.3 | Docs | Child issues for automation gaps; #808/#847 closeout or remaining AC | S02.M3 | T3.2 | pending |

### M4 — Corpus closeout + verify / deploy

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T4.1 | Docs | File remaining #846 children from M0 gap index; update epic | TC-EV032-005; #846 | T3.3 | pending |
| T4.2 | Config | 08-verify-build — lint/typecheck/format/full suites | 08 | T4.1 | pending |
| T4.3 | Test | 09-qa + 10-e2e (UJ-045); H4–H5 prep | 09; 10; E32-T6 | T4.2 | pending |
| T4.4 | Docs | 11-verify-impl per-AC (F32 + deepen); 12-verify-deploy | 11; 12 | T4.3 | pending |
| T4.5 | Test | 13-deploy-smoke — API+static; H1–H5 | 13; E32-T6; TC-EV032-007/008 | T4.4 | pending |
| T4.6 | Docs | Evolve summary + CHANGELOG notes; close session | 16-evolve | T4.5 | pending |

## Data Dependencies

| Asset | Needed by | Notes |
|-------|-----------|-------|
| `vendor/schemas/iwxxm/2025-2/.../sigmet-A6-2-TC.{tac,xml}` | M1 | Already pinned |
| `vendor/.../vona-A7-1.{tac,xml}` | M2 | Already pinned |
| WMO sibling repos (read-only URL refs) | M0/M3 | No re-pin in #808 |

## Phase gates

| Gate | Criteria | Status |
|------|----------|--------|
| A→B | Specs + 02 PASS | **passed** (`D-S040-02-phase-a`) |
| B→C | This plan approved | **passed** (`D-S040-04-plan`) |
| C→D | All Fn tasks done; 08 PASS | pending |
| Deploy | 09+10; 11+12; smoke | pending |


## Git Strategy

| Field | Value |
|-------|-------|
| Branch | `evolve/EV-032-iwxxm-corpus-quality` |
| Commits | Atomic per task `[T{m}.{n}] …` / `[EV-032] …` |
| PR | Mid-cycle minor PRs per milestone + final evolve PR after M4 |
| Checklist | Lint · typecheck · tests · no secrets · TC mapping · no new deps |

## PR Plan

| PR | Scope | Base ← Head | Status | URL |
|----|-------|-------------|--------|-----|
| PR-M1 | M0–M1 #835 A6-2 `wmoPass` | `main` ← `evolve/EV-032-iwxxm-corpus-quality` | open | https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/848 |
| PR-final | M0–M4 evolve close | `main` ← evolve | pending | — |

## Next

**07-build** in progress — M2 F32 VONA; T2.1–T2.5 **done** → T2.6 XSD+SCH / ADR-032 soft→strict on `vona-A7-1`.
