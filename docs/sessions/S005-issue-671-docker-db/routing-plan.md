# Routing Plan — S005-issue-671-docker-db (hotfix)

| Stage | Required | Status | Notes |
|-------|----------|--------|-------|
| 00-context (scoped) | yes | completed | `issue-671-docker-db.md` |
| 14-hotfix | yes | completed | Bundled Postgres + env hardening; commit b16530e |
| bug-investigation | yes | completed | BUG-2026-06-25-docker-db-connect; repro red→green |
| 08-verify-build | yes | completed | ruff/prettier/yamllint/gitleaks/basedpyright + 1154 unit @ 98.04% |
| 10-e2e | optional | completed | `docker compose up -d db` healthy; DDL round-trip on `db:5432` |
| 18-pr-review | yes | in_progress | PR [#692](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/692) open; CI running |
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
