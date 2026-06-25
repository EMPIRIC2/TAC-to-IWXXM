# Routing Plan — S005-issue-671-docker-db (hotfix)

| Stage | Required | Status | Notes |
|-------|----------|--------|-------|
| 00-context (scoped) | yes | completed | `issue-671-docker-db.md` |
| 14-hotfix | yes | pending | Orchestrator for the fix |
| bug-investigation | yes | pending | BUG report + failing repro test, then green |
| 08-verify-build | yes | pending | Lint + typecheck + full suite after fix |
| 10-e2e | optional | pending | Integration `docker compose` smoke (backend↔db, /health 200) |
| 18-pr-review | yes | pending | PR for the compose/db change |
| 13-deploy-smoke | no | n/a | Local-dev change only; prod uses Supabase |

**Skipped**

| Stage | Rationale |
|-------|-----------|
| 01–07 product stages | Hotfix — no new requirements/features (REQ-016) |
| 03/06 tooling | No new guardrails or dev tooling |
| 16-evolve | Not a feature cycle |

**Paused / superseded session**

| Session | Status | Note |
|---------|--------|------|
| S004-issue-555-feedback | completed (merged) | PR #687 merged to `main`; closed at S005 open |
