# GitHub Project board (EMPIRIC2 #7)

[Corpus: project-board]

Organization project:
[EMPIRIC2 Project #7](https://github.com/orgs/EMPIRIC2/projects/7)
(TAC-to-IWXXM board — Status / Size / Iteration / velocity).

## Auto-import of issues

Two complementary paths:

1. **Native Project workflow (preferred when available)**  
   Project → Workflows → Auto-add to project (filter `is:issue`).

2. **Repository Actions workflow**
   [`.github/workflows/project-auto-add.yml`](../.github/workflows/project-auto-add.yml)  
   Runs on `issues: [opened, reopened, transferred]`.

### `PROJECT_TOKEN` secret

The `actions/add-to-project` action needs a token that can write organization
Projects. The default `GITHUB_TOKEN` is not enough for organization Project #7.

| Item | Value |
|------|--------|
| Secret name | `PROJECT_TOKEN` (repository Actions secret) |
| Token type | Fine-grained personal access token (PAT) on a dedicated bot user |
| Scopes | Organization **Projects** (read and write); this repository **Issues** (read) |
| Do not use | Classic PAT with blanket `repo` scope |

If `PROJECT_TOKEN` is unset, the workflow **warns and skips** (the job stays
green) so a missing secret does not fail every new issue. Restore auto-add by
setting the secret or by relying on the native Project workflow above.

## Related

- Workflow regression:
  `tests/bugs/quality/test_bug_2026_10_30_project_auto_add_missing_token.py`
