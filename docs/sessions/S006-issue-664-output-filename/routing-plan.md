# Routing Plan — S006-issue-664-output-filename

Small frontend-only UX enhancement to F1 (custom output filename for manual input). Routed through
**16-evolve** as a feature delta — no requirements/tech-plan stages needed (stack and contract unchanged).

| Stage | Required | Status | Notes |
|-------|----------|--------|-------|
| 00-context (scoped) | yes | completed | `docs/context/issue-664-output-filename.md` |
| 16-evolve | yes | pending | Confirm scope, R4 multi-line scheme; allocate to F1; spec/journey deltas |
| 07-build | yes | pending | Filename input + sanitizer + manual-result naming + downloads (TDD) |
| 08-verify-build | yes | pending | ESLint + Prettier + tsc + Vitest |
| 09-qa | yes | pending | Lint/format/typecheck/security gates |
| 10-e2e | yes | pending | Playwright: custom-name manual download assertion |
| 11-verify-impl | yes | pending | UJ-001 sign-off on custom filename |
| 18-pr-review | optional | pending | Per atomic-commit/PR workflow |
| 12-verify-deploy | optional | pending | Frontend static deploy if user requests |
| 13-deploy-smoke | optional | pending | Only if deploying |

**Skipped**

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

**Active/related sessions**

| Session | Status | Note |
|---------|--------|------|
| S005-issue-671-docker-db | closed | PR #692 merged to main 2026-06-25 |
