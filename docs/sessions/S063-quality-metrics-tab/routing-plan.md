# Routing plan — S063 / EV-054

**Status:** approved (`D-S063-route=1`)  
**Preset:** **Standard** — not Auto-Lean (new operator UI tab + fixture metrics + H4–H5)

| Stage | Include? | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | **completed** | `D-S063-route=1` / `D-S063-ui-preview=2` |
| 16-evolve | yes | orchestrate | **in_progress** | Phase 0–1 Plan orchestrator |
| 01-requirements | yes | delta | **completed** | `D-S063-01-ac=1`; UJ-056; TC-EV054; shell-tab + unified diff |
| 02-verify-plan | yes | delta | **completed** | Gate A PASS `D-S063-gateA=2`; api-contract + 05 |
| 03-plan-tooling | no | — | skipped | No new Cursor rule expected |
| 04-tech-plan | yes | delta | **completed** | `D-S063-04-plan=1` — M1→M5 / 15 tasks |
| 05-verify-tech | yes | delta | **completed** | `D-S063-05=1` Gate B PASS |
| 06-tech-tooling | no | — | skipped | No new deps expected |
| 07-build | yes | delta | **in_progress** | M1 generator + artifact |
| 08-verify-build | yes | delta | pending | Local + tip CI |
| 09-qa | yes | delta | pending | AC map |
| 10-e2e | yes | delta | pending | Playwright / H4–H5 smoke per #836 AC |
| 11-verify-impl | yes | delta | pending | AC sign-off; close #836 |
| 12-verify-deploy | yes | delta | pending | Staging path when UI ships |
| 13-deploy-smoke | yes | delta | pending | Staging smoke; promote later |

## Recommended ordered stages

`00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13`

## Skip rationale

- **Not Auto-Lean:** new UI surface + corpus metrics model + connectivity smoke — needs
  04/07/08/09/10/11 (+ deploy 12/13), not Lean’s thin verify path alone.
- **Skip 03/06:** no new Cursor rules expected; new FE diff dep (if any) inventoried in 04/05.
- **Include 05:** Gate A option 2 requires public metrics HTTP API — tech verify after 04.
- **Include 10 + 12 + 13:** #836 AC requires H4–H5 or Playwright; UI ships to stage.

## Board

- Project [#7](https://github.com/orgs/EMPIRIC2/projects/7) — #836 **In progress**; #959 **Done**
- Ready queue = 2 (`#948`, `#958`) — below 3–5; refill later

## Locked intake

| ID | Decision |
|----|----------|
| D-S063-route | **1** — Standard as drafted; branch from `stage@f2926ac8` |
| D-S063-ui-preview | **2** — No local UI preview |
| D-S063-gateA | **2** — PASS; public `GET /api/v1/quality-metrics*` required; 05 re-enabled |
| D-S063-04-plan | **1** — Approve execution plan as drafted; no npm `diff`; single corpus blob |
