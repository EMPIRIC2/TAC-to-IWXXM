---
name: github-projects
description: Configure GitHub Projects v2 boards via gh CLI — labels, Status options, views, README. Use when setting up or updating project boards, kanban columns, views, or when gh project commands fail with missing scopes.
---

# GitHub Projects v2

Board policy: [`docs/project-board.md`](../../../docs/project-board.md)  
Bootstrap: `bash scripts/ci/setup_github_project.sh`

**Defaults:** org `Math-Data-Justice-Collaborative`, project **#3**, repo `Math-Data-Justice-Collaborative/deployed-service`.

## Auth

Requires `project` + `read:project` scopes (not just `repo`):

```bash
gh auth refresh -h github.com -s read:project,project
```

Device login is interactive — **AskQuestion**, wait for user, then retry.

## Bootstrap

```bash
bash scripts/ci/setup_github_project.sh
```

Labels → link repo → Status options → README → views (skips existing view names).

**Manual UI after:** delete stale/duplicate tabs; on **Board** set **Group by → Status**.

## API limits (github.com)

| Works | Doesn't (use UI) |
|-------|------------------|
| GraphQL: Status options (`updateProjectV2Field`), README, list views | Update/delete views (REST 404) |
| REST POST: create views | View group-by on create (422) |
| `gh label create`, `gh project link` | `createProjectV2View` GraphQL |

Status mutation **replaces all options** — see [reference.md](reference.md).  
View filters and labels: defined in `docs/project-board.md` and the setup script.

## Filters (pitfalls)

- OR same field: comma — `status:"Ready","In review"`
- OR across fields: **not supported** — use separate views
- Spaces: quote — `status:"In progress"`

## Updates

1. Edit `docs/project-board.md`
2. Re-run setup script (or snippets in [reference.md](reference.md))
