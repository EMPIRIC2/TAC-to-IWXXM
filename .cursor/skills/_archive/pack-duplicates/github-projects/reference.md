# GitHub Projects — API snippets

Constants: `OWNER=Math-Data-Justice-Collaborative`, `PROJECT_NUMBER=3`, `REPO=${OWNER}/deployed-service`

## Status options (GraphQL — replaces full list)

```bash
FIELD_ID=$(gh project field-list "$PROJECT_NUMBER" --owner "$OWNER" \
  --jq '.fields[] | select(.name == "Status") | .id')
# Full jq mutation body: scripts/ci/setup_github_project.sh → update_status_options()
```

## README sync

```bash
PROJECT_ID=$(gh project view "$PROJECT_NUMBER" --owner "$OWNER" --format json --jq .id)
jq -n --arg projectId "$PROJECT_ID" --rawfile readme docs/project-board.md '{
  query: "mutation($projectId: ID!, $readme: String!) { updateProjectV2(input: { projectId: $projectId, readme: $readme }) { projectV2 { id } } }",
  variables: { projectId: $projectId, readme: $readme }
}' | gh api graphql --input -
```

Prefer GraphQL + `--rawfile` over `gh project edit --readme` for long markdown.

## Create view (REST POST only)

```bash
jq -n --arg name "Bugs" --arg layout "table" --arg filter "label:bug,hotfix" \
  '{name:$name,layout:$layout,filter:$filter}' \
  | gh api -X POST -H "X-GitHub-Api-Version:2022-11-28" \
      "/orgs/${OWNER}/projectsV2/${PROJECT_NUMBER}/views" --input -
```

Layouts: `table`, `board`, `roadmap`. List views: GraphQL `projectV2.views`.
