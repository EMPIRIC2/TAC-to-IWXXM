# Routing plan — S025-sigmet-quality

**Preset:** Lean+build (E19-4, 2026-07-29)  
**Orchestrator:** 16-evolve · **Cycle:** EV-019

| Stage | Required | Mode | Skip rationale |
|-------|----------|------|----------------|
| 00-context | yes | scoped | Session open + `docs/context/sigmet-quality.md` |
| 16-evolve | yes | orchestrator | EV-019 |
| 01-requirements | yes | delta | F23 + F6.d/F12 deepen; #733/#739 → corpus |
| 02-verify-plan | yes | delta | Consistency across product / domain / test-plan |
| 03-plan-tooling | **no** | — | ADR-028 registry guardrails already exist; revisit if new conventions appear |
| 04-tech-plan | yes | delta | Execution plan: SIGMET/VA rules → goldens → coverage matrix |
| 05-verify-tech | **no** | — | Lean+build; re-run if 04 introduces deps/ADR conflict |
| 06-tech-tooling | **no** | — | Reuse F15/F20 CI/registry hooks unless new tooling needed |
| 07-build | yes | full | Package + API smoke paths |
| 08-verify-build | yes | full | — |
| 09-qa | **no** | — | Lean+build; 08 + 10 cover quality gates |
| 10-e2e | yes | full | `product=sigmet` + VA SIGMET + workbench smoke |
| 11-verify-impl | **no** | — | Lean+build; re-add if multi-Fn sign-off needed |
| 12-verify-deploy | **no** | — | Lean+build; run only if API/FE contract changes force checklist |
| 13-deploy-smoke | yes | full | H1–H5 when deployables change; waive only if build-only |

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Session open | E19-1 = A | 2026-07-29 |
| Product scope | E19-2 = A (#733+#739; #738 OOS) | 2026-07-29 |
| Fn allocation | E19-3 = A (F23 + deepen F6.d/F12) | 2026-07-29 |
| Routing | **Lean+build** E19-4 = A | 2026-07-29 |
| Research depth | E19-5 = A (full AC) | 2026-07-29 |
| Out of scope | E19-6 = A (siblings OOS) | 2026-07-29 |
| Deploy / smoke | E19-7 = A (H1–H5 when changed) | 2026-07-29 |
| Phase 0 close | E19-8 = B (write F23; **pause before 01**) | 2026-07-29 |
| UI preview | E19-ui = B assumed (docs/repo only) | 2026-07-29 |
| AskQuestion | Written interview waive | 2026-07-29 |
