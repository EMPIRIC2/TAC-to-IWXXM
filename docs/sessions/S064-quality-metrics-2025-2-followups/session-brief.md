---
session_id: S064-quality-metrics-2025-2-followups
type: feature
status: completed
branch: evolve/EV-055-quality-metrics-2025-2-followups
orchestrator: 16-evolve
evolve_cycle_id: EV-055
github_issues: [982, 980, 979]
opened: 2026-08-11
closed: 2026-08-11
---

# Session brief — S064-quality-metrics-2025-2-followups

> **Cycle**: EV-055 · **Type**: feature · **Opened**: 2026-08-11  
> **Branch**: `evolve/EV-055-quality-metrics-2025-2-followups` (base `stage@4fd51e39`)  
> **Orchestrator**: **16-evolve**  
> **Corpus**: [Corpus: product §F7] [Corpus: product §F2] [Corpus: product §F13]
> [Corpus: product §F4] [Corpus: api] [Corpus: tests] [Corpus: system-spec]
> [Corpus: decisions §EV-055]

## Goal

Ship quieter Quality-metrics XML diffs via **W3C C14N** (#982), with normalized XML
panes (override to raw), and **hard-fix** IWXXM 2025-2 `SCHEMATRON_SKIPPED` (#980) and
`SCHEMA_IMPORT_WARNING` (#979) in `iwxxm-validate`.

## Intent (locked — Phase 0 intake)

Follow-ups from EV-054 / S063 / [#836](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/836)
(PR [#977](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/977) → `stage`). One cycle for
all three tickets when disposition is clear.

| Decision | Choice |
|----------|--------|
| D-S064-intent | **1** — Investigate and fix/ship all three when disposition is clear |
| D-S064-parked | **1** — Leave EV-043 / EV-044 parked; open S064 / EV-055 |
| D-S064-success | **1** — Quieter diffs + clear disposition for both 2025-2 validate warnings |
| D-S064-normalize | **1** — Normalize **both** official and converted XML; `match_status` = normalized equality |
| D-S064-spike-pref | **3** — Prefer enable Schematron for 2025-2 if native can do xslt2; XSD fix optional |
| D-S064-surface | **1** — Operator surface = Quality metrics tab (F7.q); engine-in allowed (see D-S064-engine) |
| D-S064-engine | **1** — Allow F2/F13 (`iwxxm-validate`) changes for #980/#979; Quality metrics is consumer |
| D-S064-oos | **1** — Accept out-of-scope list below |
| D-S064-route | **1** — Standard preset; PR → `stage` |
| D-S064-branch | **1** — Open from `stage`; leave `docs/EV-054-closeout` alone |
| D-S064-board | **1** — #982 / #980 / #979 → In progress (WIP advisory: 3 > policy ≤2; user override) |

## Out of scope

- Hand-editing `vendor/schemas/*` (sync/pin PRs only)
- Reopening closed #836 / redoing the Quality metrics tab shell
- DOKS / F30 (EV-043 / EV-044 remain parked)
- New product families / encode parity work
- `stage`→`main` promote unless explicitly approved later

## Features

- Deepen **F7.q** — whitespace-normalized Quality metrics diffs + validate chip/copy
  ([Corpus: product §F7])
- Deepen **F2** / **F13** as needed for Schematron/XSD disposition on 2025-2
  ([Corpus: product §F2] [Corpus: product §F13])
- Touch **F4** only if version-line messaging / skip labeling requires it
  ([Corpus: product §F4])

## Acceptance (draft for 01)

### #982 — Whitespace-normalize diffs

1. Whitespace-only differences no longer dominate unified diff for representative stems
2. Semantic XML differences still appear
3. `match_status` uses equality of **normalized** forms (both sides)
4. Vendor schemas remain read-only; any fixture rewrite is documented
5. Tests for normalize helper + at least one golden stem

### #980 — SCHEMATRON_SKIPPED 2025-2

1. Root cause + engine matrix (lxml vs native) documented
2. Disposition decided; prefer **enable** via native if feasible
3. Tests or metrics labeling updated to match disposition
4. Outcome linked from #836 / Quality metrics

### #979 — SCHEMA_IMPORT_WARNING 2025-2

1. Root cause written (file + import URI)
2. Disposition decided (fix / document / defer); fix optional this cycle
3. If fix: regression test; if document: operator-facing message + test-plan note
4. Outcome linked from #836 / F2 / F7.q

## Related issues

- [#982](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/982) — whitespace-normalize (primary ship)
- [#980](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/980) — Schematron xslt2 skip (spike → enable preferred)
- [#979](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/979) — Schema import warning (spike → fix optional)
- Parent: [#836](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/836) (closed); EV-054 / S063

## Board

- Project [#7 TAC-to-IWXXM](https://github.com/orgs/EMPIRIC2/projects/7)
- #982 / #980 / #979 → **In progress** (`D-S064-board=1`)
- Note: board WIP policy ≤2; three tickets pulled by explicit intake override

## UI preview

Deferred at open — re-offer after Phase C / at **11-verify-impl** (Quality metrics UI in scope).

## Notes

- Parked EV-043 / EV-044 (DOKS / F30) unchanged
- Local dirt on prior `docs/EV-054-closeout` not carried into this branch
- Evidence for spikes: stage CI run from EV-054 closeout (see issue bodies)
