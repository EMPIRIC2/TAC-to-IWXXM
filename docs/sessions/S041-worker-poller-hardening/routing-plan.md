# Routing plan — S041-worker-poller-hardening

**Preset:** Standard — approved via `D-S041-open` = proceed_1-5_plus_code  
**Orchestrator:** 16-evolve · **Cycle:** EV-033  
**Path:** `00→16→01→02→04→07→08` (+ 09–13 **waived** lean-close)  
**Skip:** `03, 05, 06` (original); `09–13` waived `D-S041-1+3`  
**Deepen:** F8 (`INGEST_POLLER_URL` cutover hardening)  
**Branch:** `main` @ `5245f8de` (includes #865/#845/#866; feature tip `753bc94d`)  
**Status:** **completed** 2026-08-05 (lean-close)  
**Prior:** S040/EV-032 **suspended** — `resume_after` updated to S042 (not auto-resume)

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | scoped | **completed** | Suspend S040; open S041; D-S041-open |
| 16-evolve | yes | orchestrator | **completed** | Lean-close D-S041-1+3; EV-033 closed |
| 01-requirements | yes | delta | **completed** | Prevention 1–5 + code guard |
| 02-verify-plan | yes | delta | **completed** | Gate A |
| 03-plan-tooling | no | — | skipped | Re-add if new rules/hooks |
| 04-tech-plan | yes | delta | **completed** | Gate B |
| 05-verify-tech | no | — | skipped | Re-add if new deps |
| 06-tech-tooling | no | — | skipped | — |
| 07-build | yes | full | **completed** | PR #865 MERGED @ 963a2777 |
| 08-verify-build | yes | delta | **completed** | PASS @ tip `5245f8de`; C→D passed |
| 09-qa | yes | delta | **waived** | D-S041-1+3 lean close |
| 10-e2e | yes | smoke | **waived** | D-S041-1+3 lean close |
| 11-verify-impl | yes | delta | **waived** | D-S041-1+3 lean close |
| 12-verify-deploy | yes | delta | **waived** | D-S041-1+3 lean close |
| 13-deploy-smoke | yes | full | **waived** | Formal waived; deploy **passed_via_ops** via DOKS `20260805003332-5245f8d` |

## Skip / waive rationale

Existing app; F8 deepen on config/CI/docs/code guards. Standard matched prior ops-hardening
evolve cycles. No new deployable. Skip 03/05/06 unless 04 required them.

**Lean-close (`D-S041-1+3`):** Waive 09–13 — live worker/API verified via one-shot DOKS
rollout; remaining AC depth deferred. CD automation continues in S042/EV-034.

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Session open / Phase 0 | `D-S041-open` = **proceed_1-5_plus_code** | 2026-08-04 |
| Session priority | `D-S041-cd-defer` = **finish_S041_first** (option 2) | 2026-08-04 |
| Lean close + DOKS | `D-S041-1+3` = **lean_close_and_doks_oneshot** — waive 09–13; DOKS one-shot; open S042 | 2026-08-05 |

**Note:** AskQuestion tool unavailable for open; decisions recorded from chat approval.
