---
session_id: S045-matrix-disposition-residuals
type: feature
status: in_progress
branch: evolve/EV-037-matrix-disposition-residuals
started_at: 2026-08-05
intent: "Dispose EV-035 residual tickets #869/#870/#872 — VONA SoT wording, IWXXM-US Schematron N/A, Bulletin AHL source vs impl matrix"
orchestrator: 16-evolve
evolve_cycle_id: EV-037
prior_session: S044-local-precommit-long-jobs
prior_evolve_cycle_id: EV-036
github_issues:
  - 869
  - 870
  - 872
parent_epic: 846
context_briefs:
  - docs/context/matrix-disposition-residuals.md
standing_docs_touched:
  - docs/feature-list.md
  - docs/test-plan.md
  - docs/decisions/evolve-decisions.md
  - docs/domain/rules/COVERAGE_MATRIX.md
  - docs/domain/rules/PROVENANCE_MAP.md
  - docs/domain/rules/PROVENANCE_MAP.json
feature_ids: []
deepen_feature_ids:
  - F2
  - F6
  - F32
feature_note: "Deepen F2/F6/F32 matrix+provenance dispositions — no new Fn; no product UI"
route_status: approved_lean_plus_0708
current_stage: 08-verify-build
github_issues_closed:
  - 869
  - 870
  - 872
tip_sha_07: c51e6e9b
ui_preview: n_a
---

# Session S045 — matrix-disposition-residuals

## Intent

Close the three EV-035 remine residual tickets by documenting dispositions in the coverage /
provenance matrices (and related cites), without blocking product encode/validate work.

| Ticket | Disposition (Phase 0 locked) |
|--------|------------------------------|
| [#869](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/869) | Non-blocking upstream Guidance gap; VONA SoT = ICAO + FM205 + AHL + XSD/SCH + code lists; cookbook = derived |
| [#870](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/870) | Official US Schematron = **N/A / not published**; keep WMO XSD/SCH + US XSD + semantic/fixtures columns |
| [#872](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/872) | AHL **source** ✅ for all families; split matrix into source vs parser/BBB/splitter/fixtures/CI; children only for true impl gaps |

## Phase 0 (locked)

| ID | Decision |
|----|----------|
| Q1 | Open **S045** → **EV-037** |
| Q2 | Approve all three dispositions as cycle scope |
| Q3 | **Lean + 07/08** — `00→16→01→02→07→08→11` |
| Q4 | **N/A** — no UI |

## Scope

### In

- Update `COVERAGE_MATRIX` / `PROVENANCE_MAP` (+ JSON) for #869/#870/#872 dispositions
- Feature-list / test-plan deepen notes + TC-EV037-* as needed
- Close or reword GitHub #869/#870/#872 when matrix/docs land; open children only for true impl gaps (#872)
- Optional compat note/test for IWXXM 2025-2 + IWXXM-US 3.0 catalog (docs or canary — not full encode work)

### Out

- New product Fn / browser UI / deploy runtime changes
- Full AHL parser/splitter/fixture implementation beyond matrix column redesign + linking residual children
- Inventing a US Schematron package
- Writing VONA section into upstream `TAC-to-XML-Guidance.txt`

## Routing plan

See [routing-plan.md](./routing-plan.md).

## Phase C (in progress)

| Item | Status |
|------|--------|
| 07-build | **completed** @ `c51e6e9b` — matrix/provenance + AC4 |
| Issues #869 / #870 / #872 | **closed** |
| `gates.b_to_c` | **waived_lean** (04/05 skipped) |
| 08-verify-build | **in_progress** |

## Links

- Epic: [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846)
- Prior gaps: [S043 provenance-gaps](../S043-rule-source-traceability/reports/provenance-gaps.md)
- Standing: [COVERAGE_MATRIX](../../domain/rules/COVERAGE_MATRIX.md) · [PROVENANCE_MAP](../../domain/rules/PROVENANCE_MAP.md)
- Corpus: `[Corpus: product]` · `[Corpus: tests]` · `[Corpus: decisions]` · `[docs/domain/rules/COVERAGE_MATRIX.md]` · `[docs/domain/rules/PROVENANCE_MAP.md]`
