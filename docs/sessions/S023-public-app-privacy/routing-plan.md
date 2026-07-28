# Routing plan — S023-public-app-privacy

**Preset:** Standard (E17-3, 2026-07-27)  
**Orchestrator:** 16-evolve · **Cycle:** EV-017  
**Issue:** [#783](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/783)

| Stage | Required | Mode | Status | Skip rationale |
|-------|----------|------|--------|----------------|
| 00-context | yes | scoped | completed | Session open + `docs/context/public-app-privacy.md` |
| 16-evolve | yes | orchestrator | in_progress | EV-017 — next 11-verify-impl |
| 01-requirements | yes | delta | completed | F21/F22 + F5/F7/M4 deltas — `reports/01-requirements.md` |
| 02-verify-plan | yes | delta | completed | Gate A 2026-07-27; D-S023-02-C-EV017-A; Phase A passed |
| 03-plan-tooling | **no** | — | skipped | No new Cursor rules/hooks expected at open; add if ADR needs guardrails |
| 04-tech-plan | yes | delta | completed | ADR-031 + execution plan (D-S023-04-plan-approve-A) |
| 05-verify-tech | **no** | — | skipped | Standard skip unless 04 adds deps/ADR conflict |
| 06-tech-tooling | **no** | — | skipped | No new tooling expected |
| 07-build | yes | full | completed | M1–M7 28/28 |
| 08-verify-build | yes | full | completed | PASS 2026-07-28 — `reports/verification-report.md`; pyasn1 0.6.4 @ `836c1a4` |
| 09-qa | yes | full | completed | pass_with_advisories — `reports/qa-report.md` |
| 10-e2e | yes | full | completed | T0 PASS (8 Playwright + Vitest + F21) — `reports/e2e-report.md` |
| 11-verify-impl | yes | full | pending | Next — per-Fn AC + UI preview (pending handoff) |
| 12-verify-deploy | yes | full | pending | Env matrix / secret cleanup checklist |
| 13-deploy-smoke | yes | full | pending | Live public convert + privacy settings |

## Skip rationale

- **03 / 06**: Defer unless auth/privacy guardrails need new hooks (re-open via AskQuestion).
- **05**: Re-run only if 04 introduces new dependencies or contradicts template/ADR.
- **Standard (not Lean)**: Breaking auth/API/session model + multi-corpus updates need 04/07/08/09/11/12.
- **12 required**: Env/`DISABLE_AUTH`/Supabase Auth secret cleanup is in #783 AC.

## Approval

| Gate | Decision | Date |
|------|----------|------|
| Session open | S023 / EV-017 | 2026-07-27 (E17-1 = A) |
| Architecture | Baseline **with tweaks** | 2026-07-27 (E17-2 = B) |
| Routing | **Standard** | 2026-07-27 (E17-3 = A) |
| Scope lock | **Approved** — E17-4A…E17-11 | 2026-07-27 |
| 01-requirements | Spec deltas written | 2026-07-27 |
| 02-verify-plan / Phase A | D-S023-02-phase-a-A | 2026-07-27 |
| 04-tech-plan / Phase B | D-S023-04-plan-approve-A | 2026-07-28 |
| 08-verify-build | PASS (D-S023-08-pyasn1-A) | 2026-07-28 |
| Phase C (C→D) | **Passed** — D-S023-phase-c-A (user 2 then 1) | 2026-07-28 |
| 09-qa / 10-e2e | COMPLETE — next 11 | 2026-07-28 |
