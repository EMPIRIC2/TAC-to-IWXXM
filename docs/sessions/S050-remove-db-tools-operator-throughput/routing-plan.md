# Routing plan — S050 / EV-042

**Preset:** Standard (**approved** Q8)  
**Route:** `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13`  
**Skip:** `03-plan-tooling`, `06-tech-tooling` (unless new Cursor rules / publish deps appear)  
**Branch:** `evolve/EV-042-remove-db-tools-operator-throughput`  
**Features:** deepen **F7 / F16**; propose **F33** secure mass ingest (Phase 1 confirm)  
**Issues:** [#897](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/897) epic; [#898](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/898) follow-up  
**Status:** completed — `D-S050-13=1`; #899 merged; live smoke PASS; S050/EV-042 closed  
**Prior:** S049 / EV-041 completed (PR #895 merged)  
**Approved routing:** 2026-08-07 (user Q8=1)

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | scoped | **completed** | S050 open |
| 16-evolve | yes | orchestrator | **in_progress** | Phase B |
| 01-requirements | yes | delta | **completed** | AC1–AC7 locked |
| 02-verify-plan | yes | delta | **completed** | Gate A PASS; C1 dedicated mass limit |
| 03-plan-tooling | no | — | skipped | |
| 04-tech-plan | yes | delta | **completed** | execution-plan + build-plan-card |
| 05-verify-tech | yes | delta | **completed** | Gate B PASS |
| 06-tech-tooling | no | — | skipped* | |
| 07-build | yes | full | **completed** | M1–M4 T4.1–T4.2 |
| 08-verify-build | yes | delta | **completed** | M4 PASS @ 6bc756ef |
| 09-qa | yes | delta | **completed** | pass_with_advisories; qa-report.md |
| 10-e2e | yes | full | **completed** | local UJ-051..053 6/6; live H4–H5 → 13 |
| 11-verify-impl | yes | delta | **completed** | features+UJ approved; T3→13; fix adad127c |
| 12-verify-deploy | yes | delta | **completed** | D-S050-12=1; tip CI green @ 18d028ed; Sync DB mig OOS |
| 13-deploy-smoke | yes | delta | **completed** | D-S050-13=1; CD green; H4–H5+UJ 6/6; S050/EV-042 closed |

## Skip rationale

| Skipped | Why |
|---------|-----|
| 03 | No new plan-adherence rules expected; optional if upload security rule needed |
| 06 | Prefer existing stack; escalate if new publish/runtime deps |

## Why Standard (not Lean)

UI + API surface changes (drawer, mass ingest, workflow), H4–H5 connectivity, and
deploy smoke required — Lean would skip 04/07/09/11/12.
