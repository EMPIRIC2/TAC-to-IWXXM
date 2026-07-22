# Routing plan — S020-aerodrome-quality

**Preset:** Lean+build (`D-S020-EV015-route-1`, 2026-07-22)  
**Orchestrator:** 16-evolve · **Cycle:** EV-015

| Stage | Required | Mode | Skip rationale |
|-------|----------|------|----------------|
| 00-context | yes | scoped | Session open + `docs/context/aerodrome-quality.md` |
| 16-evolve | yes | orchestrator | EV-015 |
| 01-requirements | yes | delta | F20 + F6/F12 deepen; #735/#734 → corpus |
| 02-verify-plan | yes | delta | Consistency across product / domain / test-plan |
| 03-plan-tooling | **no** | — | ADR-028 registry guardrails already exist; revisit if new conventions appear |
| 04-tech-plan | yes | delta | Execution plan: TAF/SPECI rules → goldens → coverage matrix |
| 05-verify-tech | **no** | — | Lean+build; re-run if 04 introduces deps/ADR conflict |
| 06-tech-tooling | **no** | — | Reuse F15 CI/registry hooks unless new tooling needed |
| 07-build | yes | full | Package + API smoke paths |
| 08-verify-build | yes | full | — |
| 09-qa | yes | full | — |
| 10-e2e | yes | full | `product=taf` + `product=speci` + workbench smoke |
| 11-verify-impl | yes | full | Per-Fn (F20 + F6/F12 deepen) sign-off |
| 12-verify-deploy | **no** | — | Lean+build; run only if API/FE contract changes force checklist |
| 13-deploy-smoke | yes | full | H1–H5 when deployables change; waive only if build-only |

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Fn allocation | F20 + deepen F6.b/F6.c/F12 | 2026-07-22 (E15-3) |
| Scope products | Full #735 TAF + full #734 SPECI | 2026-07-22 (E15-2) |
| Routing | **Lean+build** (E15-route-amend=A) | 2026-07-22 (`D-S020-EV015-route-1`) |
| AskQuestion | Written interview waive | 2026-07-22 |
