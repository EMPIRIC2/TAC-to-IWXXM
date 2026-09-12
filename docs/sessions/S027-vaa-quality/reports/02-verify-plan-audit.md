# 02-verify-plan audit — S027 / EV-021

**Date**: 2026-07-29  
**Mode**: evolve delta  
**Status**: **PASS** (Batch F all Approve = 1,1,1)

## Inventory

| # | Document | Delta focus | Status |
|---|----------|-------------|--------|
| 1 | feature-list.md | F26/F27 + F6.f/F12/F7.g deepen | audited |
| 2 | spec.md | F24/F25 → Done; F26/F27 Planned (**fixed**) | audited |
| 3 | user-journeys.md | UJ-037/038 | audited |
| 4 | test-plan.md | TC-F26/F27; scope F1–F27 | audited |
| 5 | acceptance-criteria (session) | 11 sign-off | audited |
| 6 | COVERAGE_MATRIX.md | F26 V1–V3/C1; F27 T1–T3/C1 | audited |
| 7 | api-contract.md | S027 review | audited |
| 8 | config-spec.md | §F26/F27 no new env | audited |
| 9 | ADR-028 / ADR-032 | Related + golden extends to VAA/TCA | audited |
| 10 | evolve-decisions §EV-021 | intake + Batch D lock | audited |
| 11 | wmo-vaa-tca-examples-inventory.md | E21-3 dig | audited |

## Consistency checklist

| Check | Result |
|-------|--------|
| Feature ↔ Spec | **FIXED** — added F26/F27; marked F24/F25 Done (were stale Planned) |
| Feature ↔ Journey | **PASS** — UJ-037 (F26), UJ-038 (F27) |
| Journey ↔ Test | **PASS** — TC-F26 / TC-F27 mapped; H4–H5 when FE |
| Feature ↔ Test | **PASS** |
| Spec ↔ Config | **PASS** — no new env; ADR-032 defaults |
| Test ↔ Acceptance | **PASS** — session AC mirrors TC ids |
| Cross-doc naming | **PASS** — F26 themes V1–V3 vs F23 VA-SIGMET V1–V3; mandatory “F26/F27 theme” prefix (**S02.M1=1**) |
| Scope boundaries | **PASS** — F23 historical OOS of VAA/TCA OK; F26/F27 own #736/#737 |
| Connectivity | **PASS** — H4–H5 when FE touched (UJ-037/038) |
| Template | **PASS** — no new deployable; static+api+worker unchanged |

## Auto-approved (high confidence)

Derived from E21-1..4 / D1..D4 / E1:

- Scope: VAA #736 **and** TCA #737 (F26 + F27)
- Golden: `canonicalize_xml` under **defaults** only (`va-advisory-A7-2`, `tc-advisory-A2-2`)
- Catalog: passers only; mine WMO + translation TAC themes
- Routing: Lean+build+11
- Manifest: all recommended docs
- Journeys: UJ-037 + UJ-038; TC-F26/F27 packs
- Themes: F26 V1–V3+C1; F27 T1–T3+C1
- Translation fixtures: TAC themes only; no Amd79 XML byte-match under 2025-2
- API: no new routes; `product=vaa`/`tca` already exist
- ADR-028 reuse (codes only); ADR-032 applies to F26/F27

**Count**: 12 high-confidence auto-approved (delta set).

## Medium / low — Batch F (2026-07-29)

| ID | Conf | Statement | Verdict |
|----|------|-----------|---------|
| S02.M1 | Medium | Keep theme ids **F26 V1–V3** / **F27 T1–T3** (despite F23 V1–V3 for VA SIGMET) with mandatory “F26/F27 theme” prefix in plans/PRs | **Approve** (1) — `D-S027-EV021-s02m1-1` |
| S02.M2 | Medium | Catalog unlock **incremental per product** — VAA when F26 golden greens; TCA when F27 greens (peer E20-F4) | **Approve** (1) — `D-S027-EV021-s02m2-1` |
| S02.L1 | Low | Extend combined `wmo-quality.yml` (or current pack) with VAA+TCA; finalize in 04 | **Approve** (1) — `D-S027-EV021-s02l1-1` |

## Results

| Metric | Count |
|--------|-------|
| Documents audited | 11 |
| Auto-approved (high) | 12 |
| User-approved (medium/low) | 3 |
| Denied / Modified / Skipped | 0 |
| Consistency issues | 1 fixed (spec F24/F25/F26/F27); 0 open |

## Gate A → B

- [x] F26/F27 in feature-list + spec
- [x] Delta specs + ADR-028/032 notes
- [x] 02-verify-plan **PASS**
- [x] 03-plan-tooling **skipped** (Lean+build+11)

**Next**: `04-tech-plan` (Lean — routine Phase A AskQuestion skipped; `D-S027-02-phase-a`).
