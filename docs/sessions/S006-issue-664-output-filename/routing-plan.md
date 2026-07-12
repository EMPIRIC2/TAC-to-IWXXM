# Routing Plan — S006-issue-664-output-filename

Small frontend-only UX enhancement to F1 (custom output filename for manual input). Routed through
**16-evolve** as a feature delta — no requirements/tech-plan stages needed (stack and contract unchanged).

**Session status:** completed (closed 2026-07-12). PR [#695](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/695) merged 2026-06-25.

| Stage | Required | Status | Notes |
|-------|----------|--------|-------|
| 00-context (scoped) | yes | completed | `docs/context/issue-664-output-filename.md` |
| 16-evolve | yes | completed | Scope R1–R8; F1+F5; spec/journey/test deltas |
| 07-build | yes | completed | Sanitizer + FileConverter + Vitest/e2e commits; PR #695 |
| 08-verify-build | yes | completed | PASS — `reports/verification-report.md` |
| 09-qa | yes | completed | PASS — `reports/qa-report.md` |
| 10-e2e | yes | completed | PASS — `reports/e2e-report.md` |
| 11-verify-impl | yes | skipped | User waived at close (S006-R5); 07–10 PASS |
| 18-pr-review | optional | skipped | No formal PRR cycle for #695 |
| 12-verify-deploy | optional | skipped | Deploy not requested |
| 13-deploy-smoke | optional | skipped | Deploy not requested |

**Skipped (plan baseline)**

| Stage | Rationale |
|-------|-----------|
| 01-requirements / 02-verify-plan | No new product requirement; extends existing F1 behavior |
| 03-plan-tooling / 06-tech-tooling | No new guardrails or stack changes |
| 04-tech-plan / 05-verify-tech | No architecture/API/deployment change (frontend-only) |
| 14-hotfix | Enhancement, not a regression/bug |
| bug-investigation | Not a failure |

**Features in scope**

| ID | Scope |
|----|-------|
| F1 | Manual-input custom output filename (download single + ZIP entry + result label); default `manual_input` |
| F5 | Persist custom name via existing `conversion_params` JSONB (no migration) |

**Close**

| Field | Value |
|-------|-------|
| Completed | 2026-07-12 |
| PR | #695 merged 2026-06-25 |
| Evolve | EV-005 completed |
| Follow-on | Docs reorg unblocked via **00-context** (S006-R5) |
