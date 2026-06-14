# 18-pr-review — Reference

## GitHub CLI prerequisites

```bash
gh auth status
gh repo view --json nameWithOwner
```

If auth fails, stop and AskQuestion — user must authenticate before posting.

---

## Resolve PR target (Phase 0)

```bash
# By number
gh pr view 123 --json number,title,url,headRefName,baseRefName,body,commits,files,statusCheckRollup

# By URL
gh pr view https://github.com/org/repo/pull/123 --json ...

# List open PRs (when user picks from list)
gh pr list --state open --json number,title,headRefName,author

# Current branch
gh pr view --json number,title,url 2>/dev/null || echo "no PR for current branch"
```

Checkout when remote CI red/missing (user confirmed or policy triggers local run):

```bash
gh pr checkout <number>
```

---

## Diff and files

```bash
gh pr diff <number>
gh pr view <number> --json files --jq '.files[].path'
gh pr checks <number>
```

Watch CI on PR branch:

```bash
BRANCH=$(gh pr view <number> --json headRefName --jq .headRefName)
bash scripts/ci/watch_github_ci.sh "$BRANCH"
```

---

## Subagents

**Bugbot** — Cursor `review-bugbot` skill:

```text
Full Repository Path: <repo-root>
Diff: branch changes
Base Branch: <pr-base>   # only when PR base ≠ default
```

Checkout PR head before launch when reviewing remote PR:

```bash
gh pr checkout <number>
```

**Security review** — Cursor `review-security` skill: same prompt shape, `subagent_type: security-review`.

Do not fix findings unless user asks after review posts.

---

## Post inline review comments

Get latest commit SHA on PR head:

```bash
SHA=$(gh pr view <number> --json headRefOid --jq .headRefOid)
```

Post one inline comment (repeat per finding):

```bash
gh api \
  --method POST \
  /repos/{owner}/{repo}/pulls/<number>/comments \
  -f body='🔴 Blocking: …' \
  -f commit_id="$SHA" \
  -f path='apps/example.py' \
  -F line=42
```

For multi-line diffs, prefer commenting on the **new file line** in the PR diff view. If line lookup fails, use a single PR-level comment referencing `path:line` in the review body instead.

---

## Submit review summary

```bash
# Request changes (any 🔴)
gh pr review <number> --request-changes --body "$(cat <<'EOF'
## PR review (18-pr-review)

### Praise
🟢 …

### Checklist
| Section | Result |
|---------|--------|
| A Intake | pass |
| … | … |

### Findings
- 🔴 …
- 🟡 …

### CI
- ci.yml: success on <sha>

### Subagents
- Bugbot: N findings (…)
- Security: N findings (…)

Thank you for the contribution — please address the blocking items above.

EOF
)"

# Approve (no 🔴)
gh pr review <number> --approve --body '…'

# Comment only (🟡 advisories, no blockers)
gh pr review <number> --comment --body '…'
```

**Never** `gh pr merge` in this skill.

---

## workflow-state.yaml schema

Append via [workflow-state-manager](../../agents/workflow-state-manager.md):

```yaml
stages:
  18-pr-review:
    status: in_progress
    started: "2026-06-12"
    completed: null
    last_cycle: PRR-001

pr_review_cycles:
  - id: PRR-001
    pr_number: 123
    pr_url: https://github.com/org/repo/pull/123
    title: "[M1] Example milestone"
    status: completed
    started: "2026-06-12"
    completed: "2026-06-12"
    head_ref: feat/example
    base_ref: main
    verdict: REQUEST_CHANGES   # APPROVE | REQUEST_CHANGES | COMMENT
    blockers: 2
    advisories: 3
    praise: 1
    ci_status: success
    subagents:
      bugbot: completed
      security_review: completed
    artifacts:
      - path: .cursor/skills/18-pr-review/checklist.md
        note: checklist source
    gh_review_url: null        # fill if returned by API
```

Mirror confirmed process gaps to top-level `issue_log` when review reveals systemic gaps.
