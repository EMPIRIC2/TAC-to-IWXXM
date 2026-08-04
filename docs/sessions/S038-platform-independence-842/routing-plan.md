# Routing plan — S038-platform-independence-842

**Preset:** Standard — intake `D-S038-open` Q3=1  
**Orchestrator:** 16-evolve · **Cycle:** EV-031  
**Path:** `00→16→01→02→04→07→08→09→10→11→12→13`  
**Skip:** `03, 05, 06` (re-add if 04 introduces new deps/ADR tooling/guardrails)  
**Work order:** #830 → #712 (prefer auth/data topology settled before K8s secrets redesign)

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | scoped | **completed** | Phase 0 + Fn lock; open `d286bfb` |
| 16-evolve | yes | orchestrator | **in_progress** | Gate B PASS → 07 @ T0.1 |
| 01-requirements | yes | delta | **completed** | Gate A lean docs `fc3bbe5`; gaps→04 |
| 02-verify-plan | yes | delta | **completed** | C1–C5 fixed; `D-S038-02-batch-c`/`phase-a`; Gate A PASS |
| 03-plan-tooling | no | — | skipped | Re-add if new rules/hooks needed |
| 04-tech-plan | yes | delta | **completed** | Gate B PASS; ADR-033 Accepted; 38 tasks M0–M7 |
| 05-verify-tech | no | — | skipped | Re-add if new deps |
| 06-tech-tooling | no | — | skipped | — |
| 07-build | yes | full | **completed** | M0–M7 done; T6.5 under `D-S038-t65-waive` |
| 08-verify-build | yes | delta | **completed** | C→D PASS — `verification-report.md` |
| 09-qa | yes | delta | pending | Phase D |
| 10-e2e | yes | smoke | pending | T0 local + provisional DOKS evidence from T7 |
| 11-verify-impl | yes | delta | pending | Per-Fn acceptance |
| 12-verify-deploy | yes | delta | pending | DOKS cutover per `D-S038-doks-depth=3` |
| 13-deploy-smoke | yes | full | pending | Smoke Auth+DO; DOKS primary after cutover |

## Skip rationale

Standard on an existing app with architectural + deploy-path change. No new product engines.
UI preview accepted (local only). Connectivity H4–H5 when frontend Auth restore ships.
DOKS live cutover locked by `D-S038-doks-depth=3`.

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Session open / Phase 0 batch | `D-S038-open` = **3,1,1,1** — full epic + IaC; general; Standard; local UI yes | 2026-08-03 |
| DOKS depth | `D-S038-doks-depth` = **3** — full prod cutover + Render decommission after soak | 2026-08-03 |
| F8 + data plane | `D-S038-f8` = **1** + amend: F8 on DO Postgres; Supabase Auth-only | 2026-08-03 |
| Routing confirm | `D-S038-route` = **1** — Standard approved | 2026-08-03 |
| Auth model | `D-S038-auth-model` = **1** — reintroduce Supabase Auth for **long-term storage** (amend F21) | 2026-08-03 |
| Session store | `D-S038-session-store` = **1** — DO Postgres when logged in; guest local + loss notice + F22 privacy | 2026-08-03 |
| #830 amend | `D-S038-830-amend` = **1** — rewrite ticket: Auth-kept / data-plane strip | 2026-08-03 |
| Fn allocation | `D-S038-fn` = **1,1,1** — F30+F31; start 01; commit open `d286bfb` | 2026-08-03 |
| Document Manifest | `D-S038-E31-M` = **1,1** — full 1–10; Feature List first | 2026-08-03 |
| Test Plan + lean docs | `D-S038-tp` = **1,1,1**; `D-S038-01-gate-a` = **1** | 2026-08-03 |
| 02 Gate A | `D-S038-02-batch-c` / `D-S038-02-phase-a` = **1,1,1** — C1–C5 fixed; ADR-033 Proposed; → 04 | 2026-08-03 |
| 04 Batches 1–2 | `D-S038-04-b1`/`b2` = **1,2,1,1** + **1,1,1(+CI),1** | 2026-08-03 |
| 04 Gate B | `D-S038-04-plan` = **1** — plan approved; ADR-033 Accepted → 07 @ T0.1 | 2026-08-03 |
