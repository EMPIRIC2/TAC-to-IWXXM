---
session_id: S034-wmo-decode-residual-matrix
type: feature
status: completed
branch: main
started_at: 2026-07-31
completed_at: 2026-07-31
intent: "#815 — official WMO IWXXM TAC peers load cleanly with no unexpected decode residuals; inventory ∪ FIXTURE_GAPS + CI residual matrix gate"
orchestrator: 16-evolve
evolve_cycle_id: EV-027
pr: 821
merge_sha: ad36aa0
closeout_pr: 822
closeout_merge_sha: 9ff0157
close_decision_id: D-S034-EV027-phase4-close
github_issues:
  - 815
  - 820
context_briefs:
  - docs/context/wmo-decode-residual-matrix.md
standing_docs_touched:
  - docs/feature-list.md
  - docs/test-plan.md
  - docs/user-journeys.md
  - docs/decisions/evolve-decisions.md
  - docs/decisions/requirements-decisions.md
e27_manifest: "E27-M/UJ/TC = 1,1,1 — lean + UJ-042 + TC-EV027-001..005"
feature_ids: [F25, F9, F7]
feature_note: "Deepen F25 (WMO parity beyond catalog) + F9 (decode residuals) + F7.g (sample menu inventory) — no new Fn (D-S034-open)"
ui_preview: deferred_after_build
phase0_lock: "D-S034-open = 1,1,2,1"
---

# Session S034 — wmo-decode-residual-matrix

## Intent

Deliver [#815](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/815): every in-scope official
WMO IWXXM TAC peer from the vendor pin is **loadable** from the workbench sample menu (or
explicitly deferred in `FIXTURE_GAPS`) and **decode leaves no residuals unless expected**.

This deepens **F25 / F9 / UJ-039** beyond “listed in catalog” — operators and CI should see
full token coverage on official textbook TAC, with unexpected leftovers treated as defects.

## Prior art

| Item | Disposition |
|------|-------------|
| S031 / EV-024 | **Completed** — UJ-039 sample menu; official stems loadable (#813) |
| S026 / EV-020 | **Completed** — F25 encode parity METAR/SPECI/TAF (#793) |
| S029 / EV-022 | **Cancelled** (`D-S029-park`) — narrow SIGMET A6-1a residuals; **superseded/broadened** by #815 matrix |
| BUG-2026-07-30 / #805 | Merged — SPECI A3-2 decode residuals (piecemeal) |
| S033 / EV-026 | **Completed** — #809 VA encode equality (orthogonal; just closed) |

## Scope (locked — D-S034-open = 1,1,2,1)

| Q | Choice | Decision |
|---|--------|----------|
| 1 Session + scope | **1** | Lock #815 as drafted — inventory + residual matrix + CI; F25/F9/F7.g deepen |
| 2 Routing | **1** | Lean+build; 13 when FE/decode chrome ships |
| 3 UI preview | **2** | No now — docs/repo only; re-offer after build |
| 4 Residual triage | **1** | Fix decode in-cycle when cheap; else allowlist + child issue (no silent leftovers) |

### In

1. **Inventory (SoT)** — official WMO stems with TAC peers under current `vendor/schemas` pin;
   cross-check `examplesCatalog.ts` ∪ `FIXTURE_GAPS.md` ∪ package fixtures
2. **Load path** — registered stems load correct TAC/product/provenance (ADR-032
   `wmoPass` vs `wmoReference`); US/quarantine stay out of WMO happy-path list
3. **Decode residual matrix** — happy-path official TAC → `residuals == []`; expected
   residuals on documented allowlist; unexpected → defect or child issue
4. **CI** — parametrized package/API tests + catalog Vitest; optional H4–H5 smoke when FE ships

### Out (issue non-goals)

- Inventing TAC not in vendor pin / mirrored fixtures
- Promoting `wmoReference` → `wmoPass` encode equality (ADR-032 / encode children)
- Expanding IWXXM-US REMARKS into WMO sample menu (#810–#812 closed)
- New products beyond F6 seven; deferred SWX/VONA/WAFS/QVACI / TC-SIGMET A6-2 unless already catalogued

## Success (from #815 AC)

1. Inventory checked in (docs or generated list) matches catalog ∪ `FIXTURE_GAPS`
2. Every in-scope peer loads from sample menu **or** has gap row + linked child issue
3. Residual matrix: empty for happy-path peers except documented allowlist
4. Unexpected residuals fail CI
5. Child issues filed for stems that cannot close in-cycle

## Routing (locked)

**Lean+build**: `00→16→01→02→04→07→08→10` (+ `13` when UI/behavior ships)  
**Skip:** `03, 05, 06, 09, 11, 12`
