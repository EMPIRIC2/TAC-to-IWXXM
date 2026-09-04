# 19-address-pr-review — Reference

## GitHub CLI prerequisites

```bash
gh auth status
gh repo view --json nameWithOwner
```

---

## Resolve PR and checkout

```bash
gh pr view <number> --json number,title,url,headRefName,baseRefName,headRefOid,statusCheckRollup
gh pr checkout <number>
```

---

## Fetch findings

### Inline review comments (REST)

```bash
OWNER=$(gh repo view --json owner --jq .owner.login)
REPO=$(gh repo view --json name --jq .name)

gh api "/repos/$OWNER/$REPO/pulls/<number>/comments" \
  --paginate \
  --jq '.[] | {id, path, line, body, user: .user.login, in_reply_to_id, commit_id}'
```

Filter: skip bot/human praise-only (🟢 with no action). Prefer comments on **unresolved** threads (see GraphQL below).

### Review summaries (includes 18-pr-review body)

```bash
gh api "/repos/$OWNER/$REPO/pulls/<number>/reviews" \
  --paginate \
  --jq '.[] | {id, state, body, user: .user.login, submitted_at}'
```

Parse `body` for `🔴` / `🟡` bullets when no inline thread exists. Map `state: CHANGES_REQUESTED` to blocker backlog.

### Unresolved review threads (GraphQL)

```bash
gh api graphql -f query='
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
          isOutdated
          comments(first: 50) {
            nodes {
              body
              path
              line
              author { login }
            }
          }
        }
      }
    }
  }
}' -f owner="$OWNER" -f repo="$REPO" -F number=<number>
```

Skip `isResolved: true` or `isOutdated: true` unless user asks to revisit.

### Link to 18-pr-review cycle

From `workflow-state.yaml`, match `pr_review_cycles[]` where `pr_number` equals current PR and `status: completed`. Copy `id` → `linked_review_cycle_id` on remediation cycle.

---

## Reply on a review thread

```bash
# Reply to an existing review comment (creates thread reply)
gh api \
  --method POST \
  "/repos/$OWNER/$REPO/pulls/<number>/comments" \
  -f body='Fixed in abc1234: …' \
  -f commit_id="$(git rev-parse HEAD)" \
  -f path='apps/example.py' \
  -F line=42 \
  -F in_reply_to=<comment_id>
```

---

## Resolve review thread

```bash
gh api graphql -f query='
mutation($threadId: ID!) {
  resolveReviewThread(input: { threadId: $threadId }) {
    thread { isResolved }
  }
}' -f threadId=<ReviewThread.id from GraphQL>
```

Resolve only after Phase 2 post-fix AskQuestion confirms resolution.

---

## Local verification (before each commit)

Minimal parity for touched Python:

```bash
uv run ruff check <paths>
uv run ruff format --check <paths>
uv run basedpyright <paths>
uv run pytest <relevant-tests> -q
```

Frontend paths touched:

```bash
cd apps/frontend && npm run lint && npm test
cd apps/frontend && npm run lint && npm test
```

Full pre-push parity: [ci-after-push.mdc](../../rules/ci-after-push.mdc) §Before the first push.

---

## Push and watch CI

```bash
git push origin HEAD
bash scripts/ci/watch_github_ci.sh "$(gh pr view <number> --json headRefName --jq .headRefName)"
```

---

## Commit message pattern

Per finding (atomic):

```text
fix(review): <short slug for finding>

Addresses PR #<number> review comment on <path>.
<optional: PRR/PRM cycle id>
```

---

## workflow-state.yaml schema

Append via [workflow-state-manager](../../agents/workflow-state-manager.md):

```yaml
stages:
  19-address-pr-review:
    status: in_progress
    started: "2026-06-12"
    completed: null
    last_cycle: PRM-001

pr_remediation_cycles:
  - id: PRM-001
    pr_number: 123
    pr_url: https://github.com/org/repo/pull/123
    linked_review_cycle_id: PRR-001   # optional; from pr_review_cycles[]
    title: "[M1] Example milestone"
    status: completed                 # in_progress | completed | blocked
    started: "2026-06-12"
    completed: "2026-06-12"
    head_ref: feat/example
    base_ref: main
    ci_status: success                # success | failure | pending | not_pushed
    counts:
      fixed: 2
      deferred: 1
      wont_fix: 0
    findings:
      - id: F-001
        source: inline                # inline | review_body | checklist
        severity: blocker             # blocker | advisory
        path: apps/example.py
        line: 42
        thread_id: "PRRT_..."         # GraphQL ReviewThread.id when known
        status: fixed                 # fixed | deferred | wont_fix | pending
        commit: abc1234
        note: null
    artifacts:
      - path: tests/bugs/test_bug_2026_06_12_example.py
        note: blocker TDD repro
    follow_up:
      pr_review_rerun: offered        # offered | completed | declined
```

Mirror systemic gaps to top-level `issue_log` when remediation reveals process gaps.
