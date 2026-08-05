# Routing plan — S044-local-precommit-long-jobs

**Preset:** Lean — **approved** (G1=1)  
**Orchestrator:** 16-evolve · **Cycle:** EV-036  
**Path:** `00→16→01→02→07→08→09→11`  
**Skip:** `03, 04, 05, 06, 10, 12, 13`  
**Branch:** `evolve/EV-036-local-precommit-long-jobs`  
**Features:** deepen **M5** only (no new Fn)  
**Status:** 02 COMPLETE → **07-build**

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | scoped | **completed** | S044 open; Batch B locked |
| 16-evolve | yes | orchestrator | in_progress | Phase 0→1 |
| 01-requirements | yes | delta | **completed** | R1=local Compose; AC=1 |
| 02-verify-plan | yes | delta | **completed** | Gate A PASS; S02.M2 modified (keep units+coverage) |
| 03-plan-tooling | no | — | skipped | existing hooks; no new Cursor rules expected |
| 04-tech-plan | no | — | skipped | Lean — execution tasks in 01/07 |
| 05-verify-tech | no | — | skipped | — |
| 06-tech-tooling | no | — | skipped | — |
| 07-build | yes | full | **in_progress** | T1–T5 impl done pending commit → 08; hooks/ci-cd/TC-EV036/DEVELOPMENT |
| 08-verify-build | yes | delta | pending | |
| 09-qa | yes | delta | pending | local hook smoke |
| 10-e2e | no | — | skipped | no UI |
| 11-verify-impl | yes | delta | pending | |
| 12-verify-deploy | no | — | skipped | no runtime; confirm waive at gate |
| 13-deploy-smoke | no | — | skipped | with 12 |

## Skip rationale

Tooling/hooks/CI policy only. Lean: no new deps (05/06), no formal 04 plan (tasks fit
01→07), no browser UJ (10), no deploy surface (12/13).

## Locked resource model (Gate A amend)

| Tier | Hook | Jobs |
|------|------|------|
| Fast + medium | pre-commit | existing fast + `validate-ci-medium` (de-duped) |
| Long local | pre-push | `make ci` = `ci-prepush` + Compose integration |
| Remote | ci-cd.yml | no validate / no Compose; **keep units + coverage + PR comment**; native/e2e/alembic/deploy |

## Approval

| Gate | Decision | Date |
|------|----------|------|
| Phase 0 Batch A | Q1=1, Q2=4+1, Q3=N/A | 2026-08-05 |
| Phase 0 Batch B | B1=3, B2=1→**amended**, B3=1, B4=1 | 2026-08-05 |
| Proceed / routing | G1=1, G2=1 Lean → 01 | 2026-08-05 |
| 01 R1 + ACs | R1=local Compose; AC=1 | 2026-08-05 |
| Gate A / 02 | `1,1,1,1` + contradiction `1,1,1,1` — S02.M2 modified | 2026-08-05 |
