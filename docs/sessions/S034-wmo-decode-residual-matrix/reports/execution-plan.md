# Execution plan — S034 / EV-027 (#815)

**Branch**: `evolve/EV-027-wmo-decode-residual-matrix`  
**Preset**: Lean+build · **Features**: F25 / F9 / F7.g deepen  
**Status**: draft (pending Gate B)

## Policies (locked)

| ID | Policy |
|----|--------|
| S02.M1 | Residual allowlist = package test artifact; FIXTURE_GAPS = catalog/load only |
| S02.M2 | All seven target `residuals == []`; allowlist only with standing-doc intent (F9 G4 / ADR-025) + child issue |
| S02.L1 | Inventory = pytest-discovered vendor/mirrored TAC peers |
| E27-4 | Fix decode when cheap; else allowlist + child (no silent leftovers) |

## Milestones

### M0 — Inventory dig

| Task | Spec Source | Depends On | Description |
|------|-------------|------------|-------------|
| T0.1 | #815 §1; TC-EV027-001; S02.L1 | — | Discover official WMO TAC peers (vendor pin + mirrored annex3); dump stem list |
| T0.2 | TC-EV027-002; UJ-039 | T0.1 | Diff inventory vs `examplesCatalog.ts` ∪ `FIXTURE_GAPS.md`; note silent omissions |
| T0.3 | TC-EV027-003; E27-4 | T0.1 | Run `decode_tac` over registered peers; dump residual text per stem |

### M1 — CI matrix (red → green)

| Task | Spec Source | Depends On | Description |
|------|-------------|------------|-------------|
| T1.1 | TC-EV027-001..002 | T0.2 | Parametrized inventory/catalog∪gaps tests (red if omissions) |
| T1.2 | TC-EV027-003; S02.M1 | T0.3 | Residual matrix pytest + empty allowlist scaffold (red on unexpected) |
| T1.3 | E27-4; S02.M2 | T1.2 | Fix cheap decode residuals (METAR/SPECI/TAF first; SIGMET/AIRMET next) |
| T1.4 | S02.M2; F9 G4 | T1.3 | Allowlist only doc-intentional residuals (G4/ADR-025) + file child issues |
| T1.5 | TC-EV027-001..003 | T1.3, T1.4 | Matrix green (empty or allowlisted) |

### M2 — Load path / catalog

| Task | Spec Source | Depends On | Description |
|------|-------------|------------|-------------|
| T2.1 | TC-EV027-004; UJ-039 | T0.2 | Register missing in-scope stems **or** gap rows + child issues |
| T2.2 | TC-EV027-004 | T2.1 | Load-path Vitest/unit smoke for registered stems |
| T2.3 | UJ-039 deepen | T2.1 | Catalog Vitest: no silent omissions; US/quarantine out of WMO list |

### M3 — Verify / close

| Task | Spec Source | Depends On | Description |
|------|-------------|------------|-------------|
| T3.1 | 08-verify-build | T1.5, T2.3 | Full suite + lint/typecheck green |
| T3.2 | 10-e2e | T3.1 | Catalog Vitest + residual matrix smoke report |
| T3.3 | #815 AC | T3.2 | PR + close #815 (or link deferral children); Gate C |
| T3.4 | TC-EV027-005 | T3.3 | 13-deploy-smoke when FE ships (else waive) |

## Gate C (close)

1. TC-EV027-001..004 green  
2. Residual matrix: empty or allowlisted with doc intent + child issues  
3. No silent catalog omissions  
4. #815 closed or deferrals filed  

## Out of scope (do not schedule)

Encode equality promotion · IWXXM-US in WMO menu · inventing TAC · new products beyond F6 seven
