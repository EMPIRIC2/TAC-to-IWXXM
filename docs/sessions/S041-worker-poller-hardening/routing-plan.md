# Routing plan — S041-worker-poller-hardening

**Preset:** Standard — approved via `D-S041-open` = proceed_1-5_plus_code  
**Orchestrator:** 16-evolve · **Cycle:** EV-033  
**Path:** `00→16→01→02→04→07→08→09→10→11→12→13`  
**Skip:** `03, 05, 06` (re-add if 04 introduces new deps/ADR tooling/guardrails)  
**Deepen:** F8 (`INGEST_POLLER_URL` cutover hardening)  
**Branch:** `evolve/EV-033-worker-poller-hardening` (pending create)  
**Prior:** S040/EV-032 **suspended** (not completed/cancelled)

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | scoped | **completed** | Suspend S040; open S041; D-S041-open |
| 16-evolve | yes | orchestrator | **in_progress** | Phase 0 locked; next 01 |
| 01-requirements | yes | delta | pending | Prevention 1–5 + code guard |
| 02-verify-plan | yes | delta | pending | Gate A |
| 03-plan-tooling | no | — | skipped | Re-add if new rules/hooks |
| 04-tech-plan | yes | delta | pending | Gate B |
| 05-verify-tech | no | — | skipped | Re-add if new deps |
| 06-tech-tooling | no | — | skipped | — |
| 07-build | yes | full | pending | — |
| 08-verify-build | yes | delta | pending | — |
| 09-qa | yes | delta | pending | — |
| 10-e2e | yes | smoke | pending | Worker-focused as needed |
| 11-verify-impl | yes | delta | pending | F8 deepen ACs |
| 12-verify-deploy | yes | delta | pending | — |
| 13-deploy-smoke | yes | full | pending | Worker / poller live checks |

## Skip rationale

Existing app; F8 deepen on config/CI/docs/code guards. Standard matches prior ops-hardening
evolve cycles. No new deployable. Skip 03/05/06 unless 04 requires them.

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Session open / Phase 0 | `D-S041-open` = **proceed_1-5_plus_code** — new session + Standard + items 1–5 + code; S040 suspended | 2026-08-04 |

**Note:** AskQuestion tool unavailable; decision recorded from chat approval to proceed via `/16-evolve`.
