# Routing plan — S064 / EV-055

**Status:** approved (`D-S064-route=1`) · **cycle OPEN**  
**Preset:** **Standard** — not Auto-Lean (FE metrics normalize + validate-engine spike/fix + H4–H5)

| Stage | Include? | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | **completed** | `D-S064-route=1` / Phase 0 intake locked |
| 16-evolve | yes | orchestrate | **in_progress** | Phase 0–1 locked; 01 COMPLETE → **02-verify-plan** |
| 01-requirements | yes | delta | **completed** | `D-S064-01-ac=1`; AC1–AC7; TC-EV055; UJ-056 deepen |
| 02-verify-plan | yes | delta | pending | Gate A |
| 03-plan-tooling | no | — | skipped | No new Cursor rule expected |
| 04-tech-plan | yes | delta | pending | Execution plan + Build Plan Card |
| 05-verify-tech | yes | delta | pending | Gate B (engine + metrics paths) |
| 06-tech-tooling | no | — | skipped | No new deps expected (inventory in 04 if native tooling changes) |
| 07-build | yes | delta | pending | Normalize + Schematron/XSD disposition |
| 08-verify-build | yes | delta | pending | Gate C |
| 09-qa | yes | delta | pending | |
| 10-e2e | yes | delta | pending | Quality metrics UJ smoke (extend UJ-056 or child) |
| 11-verify-impl | yes | delta | pending | Per-AC; UI preview AskQuestion |
| 12-verify-deploy | yes | delta | pending | PR → **stage** |
| 13-deploy-smoke | yes | delta | pending | Staging smoke; promote only if asked |

## Recommended ordered stages

`00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13`

## Skip rationale

- **Not Auto-Lean:** #982 changes match_status + diff UX; #980 may change `iwxxm-validate`
  Schematron path; needs 04/07/08/09/10/11 + deploy 12/13.
- **Skip 03/06:** no new Cursor rules expected; new deps only if 04 invents (then amend).
- **Include 05:** engine + quality-metrics generator contracts need Gate B.
- **Include 10 + 12 + 13:** operator UI surface ships to stage.

## Board

- Project [#7](https://github.com/orgs/EMPIRIC2/projects/7) — #982 / #980 / #979 **In progress**
- WIP advisory: 3 tickets > policy ≤2 (`D-S064-board=1` override)

## Locked intake

| ID | Decision |
|----|----------|
| D-S064-intent | **1** — Ship all three when disposition clear |
| D-S064-parked | **1** — Leave EV-043/044 parked |
| D-S064-success | **1** — Quieter diffs + dispositions |
| D-S064-normalize | **1** — Both sides; match_status = normalized equality |
| D-S064-spike-pref | **3** — Prefer Schematron enable; XSD fix optional |
| D-S064-surface | **1** — Quality metrics tab (F7.q) |
| D-S064-engine | **1** — F2/F13 engine-in allowed for spikes |
| D-S064-oos | **1** — OOS list accepted |
| D-S064-route | **1** — Standard; PR → stage |
| D-S064-branch | **1** — From stage@4fd51e39 |
| D-S064-board | **1** — Three issues In progress |
| D-S064-01-manifest | **1** — feature-list + journeys + test-plan + api-contract + decisions |
| D-S064-ui-preview | **2** — Docs/repo only |
| D-S064-uj | **1** — Deepen UJ-056 |
| D-S064-01-ac | **1** — AC1–AC7 |
| D-S064-regen | **1** — Regenerate corpus_metrics |
