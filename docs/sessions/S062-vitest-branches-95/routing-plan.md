# Routing plan — S062 / EV-053

**Status:** approved (`D-S062-route=1`)  
**Preset:** **Standard** — not Auto-Lean (FileConverter branch campaign needs build + verify)

| Stage | Include? | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | **completed** | Opened S062; `D-S062-route=1` |
| 16-evolve | yes | orchestrate | **in_progress** | Phase 0–1 lock + child stages |
| 01-requirements | yes | delta | pending | AC from #968; FileConverter include vs exclude strategy |
| 02-verify-plan | yes | delta | pending | Gate A |
| 03-plan-tooling | no | — | skipped | No new Cursor rule expected |
| 04-tech-plan | yes | delta | pending | Thin execution plan (test milestones) |
| 05-verify-tech | no | — | skipped | Skip unless 04 adds deps/arch |
| 06-tech-tooling | no | — | skipped | No new deps |
| 07-build | yes | delta | pending | Raise branches gate + fill FileConverter-heavy tests |
| 08-verify-build | yes | delta | pending | Local + tip CI |
| 09-qa | yes | delta | pending | Coverage thresholds / inventory |
| 10-e2e | no | — | skipped | No journey delta; Vitest + existing Playwright coverage |
| 11-verify-impl | yes | delta | pending | AC sign-off; close #968 |
| 12-verify-deploy | no | — | skipped | CI-only; no deploy surface |
| 13-deploy-smoke | no | — | skipped | CI-only |

## Recommended ordered stages

`00 → 16 → 01 → 02 → 04 → 07 → 08 → 09 → 11`

## Skip rationale

- **Not Auto-Lean:** issue text calls out a large FileConverter branch campaign; needs
  04/07/08/09/11, not Lean’s 10/13-only verify path.
- **Skip 03/05/06:** no new rules/deps/arch beyond vitest config + tests + inventory/docs.
- **Skip 10/12/13:** no operator journey or deploy change; H4–H5 N/A for this CI gate.
- Re-enable 05 if 04 invents non-trivial structure; re-enable 10 if FileConverter product
  behavior changes (should not).

## Board

- Issue [#968](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/968) already **In progress**
  on project TAC-to-IWXXM — keep through implement; move **In review** when PR opens.

## Locked intake

| ID | Decision |
|----|----------|
| D-S062-route | **1** — Standard as drafted |
| D-S062-ui-preview | **2** — No local UI preview |
| D-S062-dirty | **2** — S061 closeout already on stage (#972); proceed clean |
