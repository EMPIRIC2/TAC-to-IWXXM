# Execution plan — S048 / EV-040

**Preset:** Standard  
**Branch:** `evolve/EV-040-workbench-lint-ux`  
**Features:** deepen F7 / F10 / F15  
**Corpus:** [Corpus: product §F7/F10/F15], [Corpus: api], [Corpus: tests], [Corpus: adr/ADR-028]

## Milestone M1 — Workbench UX + lint FPs

| Task | Spec Source | Depends On | Status |
|------|-------------|------------|--------|
| T1.1 | Fix `_RVR_OK` tendency + AHL YYGGgg FP; tests | product_rules + EV-040 ACs | — | completed |
| T1.2 | Lint console one line per issue | useLiveWorkbenchAssist | T1.1 | completed |
| T1.3 | Preserve manual input on convert; New TAC; action strip placement | FileConverter | — | completed |
| T1.4 | Slim UserPreferences to name + extension | UserPreferencesDialog | — | completed |
| T1.5 | Official AHL + IWXXM Collect examples | examplesCatalog | T1.1 | completed |

## Milestone M2 — Catalog source attribution

| Task | Spec Source | Depends On | Status |
|------|-------------|------------|--------|
| T2.1 | catalog-regen + packaged attribution JSON | PROVENANCE_MAP / ISSUE_CATALOG | — | completed |
| T2.2 | API + FE catalog source fields | api-contract EV-040 | T2.1 | completed |

## Gate notes

- A→B / B→C: plan-approved ACs (D-S048-ac)
- C→D: quality gates + targeted Vitest/pytest
