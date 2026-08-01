# Execution plan — S034 / EV-027 (#815)

**Branch**: `evolve/EV-027-wmo-decode-residual-matrix`  
**Preset**: Lean+build · **Features**: F25 / F9 / F7.g deepen  
**Status**: **approved** — Gate B (`D-S034-04-plan-approve`) · Batch T **2,1,2,1,1**

## Policies (locked)

| ID | Policy |
|----|--------|
| S02.M1 | Residual allowlist = package test artifact; FIXTURE_GAPS = catalog/load only |
| S02.M2 | All seven target `residuals == []`; allowlist only with standing-doc intent (F9 G4 / ADR-025) + child issue |
| S02.L1 | Inventory = pytest-discovered vendor/mirrored TAC peers |
| E27-4 | Fix decode when cheap; else allowlist + child (no silent leftovers) |
| E27-T1 | **2** — Catalog completeness **first**, then residual matrix |
| E27-T2 | **1** — One commit per product family (or shared theme) when fixing residuals |
| E27-T3 | **2** — AskQuestion per new dep (prefer none) |
| E27-T4 | **1** — Gate C: matrix green + catalog∪gaps + #815 closed/deferred children (no soft escape) |

## Milestones (catalog-first)

### M0 — Inventory dig

| Task | Status | Spec Source | Depends On | Description |
|------|--------|-------------|------------|-------------|
| T0.1 | **completed** | #815 §1; TC-EV027-001; S02.L1 | — | Discover official WMO TAC peers (vendor pin + mirrored annex3); dump stem list |
| T0.2 | **completed** | TC-EV027-002; UJ-039 | T0.1 | Diff inventory vs `examplesCatalog.ts` ∪ `FIXTURE_GAPS.md`; note silent omissions |
| T0.3 | **completed** | TC-EV027-003; E27-4 | T0.1 | Run `decode_tac` over registered peers; dump residual text per stem (informational until M2) |

### M1 — Catalog / load path (first)

| Task | Status | Spec Source | Depends On | Description |
|------|--------|-------------|------------|-------------|
| T1.1 | **completed** | TC-EV027-001..002; TC-EV027-004 | T0.2 | No silent omissions — inventory locks registered ∪ deferred |
| T1.2 | **completed** | TC-EV027-004 | T1.1 | Existing load-path / catalog Vitest covers registered stems |
| T1.3 | **completed** | UJ-039 deepen | T1.1 | Catalog Vitest: inventory ↔ catalog ∪ FIXTURE_GAPS; US/quarantine out |

### M2 — CI residual matrix (after catalog)

| Task | Status | Spec Source | Depends On | Description |
|------|--------|-------------|------------|-------------|
| T2.1 | **completed** | TC-EV027-003; S02.M1 | T0.3, T1.3 | Residual matrix pytest + allowlist scaffold |
| T2.2 | **completed** | E27-4; S02.M2; E27-T2 | T2.1 | Decode fixes — RVR/CNL/VA SIGMET geometry |
| T2.3 | **completed** | S02.M2; F9 G4 | T2.2 | Allowlist VAA/TCA G4 + child #820 |
| T2.4 | **completed** | TC-EV027-003 | T2.2, T2.3 | Matrix green (empty or allowlisted) |

### M3 — Verify / close

| Task | Status | Spec Source | Depends On | Description |
|------|--------|-------------|------------|-------------|
| T3.1 | pending | 08-verify-build | T2.4, T1.3 | Full suite + lint/typecheck green |
| T3.2 | pending | 10-e2e | T3.1 | Catalog Vitest + residual matrix smoke report |
| T3.3 | pending | #815 AC; E27-T4 | T3.2 | PR + close #815 (or link deferral children); Gate C |
| T3.4 | pending | TC-EV027-005 | T3.3 | 13-deploy-smoke when FE ships (else waive) |

## Gate C (close)

1. TC-EV027-001..004 green  
2. Residual matrix: empty or allowlisted with doc intent + child issues  
3. No silent catalog omissions  
4. #815 closed or deferrals filed  

## Out of scope (do not schedule)

Encode equality promotion · IWXXM-US in WMO menu · inventing TAC · new products beyond F6 seven
