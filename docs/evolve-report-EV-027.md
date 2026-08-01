# Evolve report — EV-027

| Field | Value |
|-------|-------|
| Cycle | EV-027 |
| Session | S034-wmo-decode-residual-matrix |
| Status | **completed** |
| Started | 2026-07-31 |
| Completed | 2026-07-31 |
| Issues | #815 **closed**; child [#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820) **open** (VAA/TCA G4) |
| PR | [#821](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/821) → `ad36aa0` |
| Closeout | [#822](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/822) → `9ff0157` |
| Deploy smoke | **waived** — `D-S034-gate-c` / TC-EV027-005 (no FE deploy this cycle) |
| Close decision | `D-S034-EV027-phase4-close` option **1** |

## Scope

Official WMO decode residual matrix: inventory vendor/mirrored TAC peers; lock catalog ∪
`FIXTURE_GAPS` completeness; parametrized CI that happy-path official TAC →
`residuals == []` (or allowlisted with standing-doc intent + child issue).

## Routing

Lean+build: `00→16→01→02→04→07→08→10` (+13 when ships). Skipped 03/05/06/09/11/12.
13 waived at Gate C (`D-S034-gate-c`).

## Results

| Gate | Result |
|------|--------|
| A→B | passed (Batch F 1,2,1) |
| B→C | passed (execution plan M0–M3) |
| C→D | passed (PR #821; matrix + catalog green) |
| Deploy | waived (no FE ship) |

## Feature deltas

Deepened F25 / F9 / F7.g (no new Fn). Decode fixes for cheap residuals (RVR/CNL/VA
SIGMET geometry); VAA/TCA G4 allowlisted with child #820. Catalog Vitest + residual
matrix pytest green; #815 closed on merge.

## Follow-ups

- [#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820) — deepen VAA/TCA residual
  coverage beyond F9 G4 best-effort
