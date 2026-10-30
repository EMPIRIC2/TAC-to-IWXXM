# GitHub Project board (EMPIRIC2 #7)

[Corpus: project-board]

Org project: [EMPIRIC2 Project #7](https://github.com/orgs/EMPIRIC2/projects/7)
(TAC-to-IWXXM board — Status / Size / Iteration / velocity).

## Auto-import of issues

Two complementary paths:

1. **Native Project workflow (preferred when available)**  
   Project → Workflows → Auto-add to project (filter `is:issue`).

2. **Repo Actions workflow** [`.github/workflows/project-auto-add.yml`](../.github/workflows/project-auto-add.yml)  
   Runs on `issues: [opened, reopened, transferred]`.

### `PROJECT_TOKEN` secret

`actions/add-to-project` needs a token that can write org Projects. The default
`GITHUB_TOKEN` is not enough for org Project #7.

| Item | Value |
|------|--------|
| Secret name | `PROJECT_TOKEN` (repository Actions secret) |
| Token type | Fine-grained PAT on a dedicated bot user |
| Scopes | Organization **Projects** (read & write); this repo **Issues** (read) |
| Do not use | Classic PAT with blanket `repo` scope |

If `PROJECT_TOKEN` is unset, the workflow **warns and skips** (job stays green)
so missing secret does not fail every new issue. Restore auto-add by setting the
secret or relying on the native Project workflow above.

## Related

- Workflow regression: `tests/bugs/test_bug_2026_10_30_project_auto_add_missing_token.py`
