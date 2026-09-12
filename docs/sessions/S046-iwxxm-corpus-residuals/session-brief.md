---
session_id: S046-iwxxm-corpus-residuals
type: feature
status: in_progress
branch: evolve/EV-038-iwxxm-corpus-residuals
started_at: 2026-08-05
completed_at: null
intent: "Close epic #846 residual children #849–#861 (VONA deepen, release-line automation, corpus G3–G8) under Standard evolve"
orchestrator: 16-evolve
evolve_cycle_id: EV-038
prior_session: S045-matrix-disposition-residuals
prior_evolve_cycle_id: EV-037
github_issues:
  - 849
  - 850
  - 851
  - 852
  - 853
  - 854
  - 855
  - 856
  - 857
  - 858
  - 859
  - 860
  - 861
parent_epic: 846
context_briefs:
  - docs/context/iwxxm-corpus-residuals-846.md
standing_docs_touched:
  - docs/feature-list.md
  - docs/test-plan.md
  - docs/decisions/evolve-decisions.md
  - docs/domain/rules/COVERAGE_MATRIX.md
  - docs/domain/iwxxm/RELEASE_LINE_ADOPTABILITY.md
feature_ids: []
deepen_feature_ids:
  - F2
  - F4
  - F6
  - F7
  - F32
feature_note: "Deepen F2/F4/F6/F7/F32 — no new Fn expected unless encode unlock requires; #854 UI"
route_status: in_progress
current_stage: 04-tech-plan
ui_preview: yes_at_m2_854
decisions:
  D-S046-open: "Q1=1 Q2=5 Q3=2"
  D-S046-mplan: "Q1=1 Q2=1 Q3=1"
  D-S046-ac: "1"
  D-S046-02-gate-a: "2"
  D-S046-sot: "1"
---

# Session S046 — iwxxm-corpus-residuals

## Intent

Ship the remaining open children of epic
[#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846) — **#849–#861** — in one
Standard evolve cycle (**EV-038**), split across milestones.

## Phase 0 (locked)

| ID | Decision |
|----|----------|
| Q1 | Open **S046** → **EV-038** |
| Q2 | **Whole residual set** #849–#861 (split milestones) |
| Q3 | **Standard** — `00→16→01→02→04→05→07→08→09→10→11→12→13` (skip 03, 06; +05 for B→C) |

## Scope

### In

| Slice | Issues | Themes |
|-------|--------|--------|
| VONA deepen | #849, #850 | F32 residual encode paths (G-VONA-1 / G-VONA-5) |
| Release-line | #851–#855 | SoT versions, sync-PR tip-diff, iwxxm-us gate, picker Latest/Previous, deprecation template |
| Corpus G3–G8 | #856–#861 | VA-EGGX `wmoPass`, SWXA unlock, WAFS/QVACI/SIGWX OOS, codes drift, translation-failed, modelling watch |

### Out

- Implementing scope in the epic issue body itself
- Metrics UI (#836) / workbench epic (#840) unless a tiny catalog-tier change is required
- Hand-editing `vendor/schemas/*` outside normal sync PRs
- Re-pinning a new IWXXM release line as the primary goal (adopt checklists / automation only)

## Milestone plan (locked — D-S046-mplan)

| Milestone | Issues | Theme |
|-----------|--------|-------|
| **M1** | #858, #861, #855 | Docs / process |
| **M2** | #851, #852, #853, #854 | Release-line automation + UX (local UI preview at #854) |
| **M3** | #859, #860, #857 | Corpus soft / gates |
| **M4** | #849, #850, #856 | Encode deepen |

| ID | Decision |
|----|----------|
| D-S046-mplan Q1 | M1 → M2 → M3 → M4 |
| D-S046-mplan Q2 | **Yes** — local UI when M2/#854 |
| D-S046-mplan Q3 | Commit session-open → **01-requirements** |

## Routing plan

See [routing-plan.md](./routing-plan.md).

## Links

- Epic: [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846)
- Prior: [S040](../S040-iwxxm-corpus-quality/) / EV-032; [S045](../S045-matrix-disposition-residuals/) / EV-037
- Gap index: [t0.2-gap-index.md](../S040-iwxxm-corpus-quality/reports/t0.2-gap-index.md)
- Corpus: `[Corpus: product]` · `[Corpus: tests]` · `[Corpus: decisions]` · `[Corpus: tech-spec]` · `[docs/domain/iwxxm/RELEASE_LINE_ADOPTABILITY.md]` · `[docs/domain/rules/COVERAGE_MATRIX.md]`
