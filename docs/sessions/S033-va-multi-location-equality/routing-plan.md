# Routing plan — S033-va-multi-location-equality

**Preset:** Lean+build + **13 when behavior ships** (**approved** D-S033-open=1)  
**Orchestrator:** 16-evolve · **Cycle:** EV-026  
**Path:** `00→16→01→02→04→07→08→10` (+ `13` if convert/validate ships)  
**Skip:** `03, 05, 06, 09, 11, 12`

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | scoped | **completed** | Session open; Phase 0 locked A–E |
| 16-evolve | yes | orchestrator | **completed** | Phase 4 close `D-S033-EV026-phase4-close` |
| 01-requirements | yes | delta | **completed** | E26-E1 — report 01-requirements.md |
| 02-verify-plan | yes | delta | **completed** | PASS — Batch F 1,1,1; Gate A → 04 |
| 04-tech-plan | yes | delta | **completed** | Batch T 1,1,2,1,1; Gate B → 07 |
| 07-build | yes | full | **completed** | M0–M3 encode/catalog; T3.4 done via 13 |
| 08-verify-build | yes | delta | **completed** | PASS — verification-report.md |
| 09-qa | no | — | skipped | 08+10 cover |
| 10-e2e | yes | smoke | **completed** | 008/009 + catalog Vitest |
| 11-verify-impl | no | — | skipped | Catalog/Vitest only (E26-ui=N/A) |
| 12-verify-deploy | no | — | skipped | — |
| 13-deploy-smoke | when ships | full | **completed** | PASS; pending user approve (`D-S033-13-smoke-pass`) |

## Skip rationale

Encoder-shaped deepen on existing annex3 VA SIGMET path + catalog tier flip. No new
deployable / no new Fn. Soft path already green — do not re-litigate. 13 only when
operator-visible convert/validate behavior ships.

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Session open | S033 / `evolve/EV-026-va-multi-location-equality` | 2026-07-31 |
| Intake A–E | Closeout commit + #809 equality only + Lean+build + UI N/A (`D-S033-open=1`) | 2026-07-31 |
| Routing | Lean+build + 13-when-ships | 2026-07-31 |
| UI preview | N/A — catalog/Vitest only | 2026-07-31 |
| Batch T | E26-T1..T5 = 1,1,2,1,1 | 2026-07-31 |
| Gate B / 04 | `1` — M0–M3 approved → 07 @ T0.1 (`D-S033-04-plan-approve`) | 2026-07-31 |
| Gate C | equality + `wmoPass` + #809 closed | 2026-07-31 |
| 08/10 | PASS smoke | 2026-07-31 |
| PR #817 | Merged to `main` @ `101f555` (`D-S033-817-merge`) | 2026-07-31 |
| 13 start | Choice **1** — run 13 after #817 (`D-S033-13-start`) | 2026-07-31 |
| 13 smoke | PASS H0c–H5 + catalog/convert (`D-S033-13-smoke-pass`); user approve pending | 2026-07-31 |
| Phase 4 close | Choice **1** — approve 13 + close EV-026 (`D-S033-EV026-phase4-close`) | 2026-07-31 |
