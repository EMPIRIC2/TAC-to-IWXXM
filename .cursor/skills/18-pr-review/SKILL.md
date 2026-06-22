---
name: 18-pr-review
description: >
  Reviews GitHub pull requests using the Katy Huff PR checklist, stevemao PR template
  checklists, deployed service CI and project rules, and Bugbot + Security Review subagents.
  Posts inline comments and a summary review body to the PR via gh CLI; records cycles in
  workflow-state.yaml. Never merges. Use when the user asks to review a PR, post a PR review,
  or check merge readiness for a pull request.
---

# 18 — PR Review

On-demand **Phase G** skill: structured pull-request review with findings posted to GitHub.

**Checklist:** [checklist.md](checklist.md) — Katy Huff + stevemao + deployed service overlay.  
**GitHub commands:** [reference.md](reference.md).  
**Preamble:** [pipeline-preamble.md](../pipeline-preamble.md).  
**Sessions:** [sessions-reference.md](../sessions-reference.md) — requires `active_session` unless waived; reports under `docs/sessions/{id}/reports/`.
**Cross-cutting:** [considerations.md](../considerations.md), [09-qa](../09-qa/SKILL.md), [ci-after-push](../../rules/ci-after-push.mdc).  
**State agent:** [workflow-state-manager](../../agents/workflow-state-manager.md) — mandatory read/update.

**Subagents (orchestrated):** Cursor built-in `review-bugbot` and `review-security` skills — launch Bugbot and Security Review subagents per their skill instructions.

**Never merge.** Recommend verdict only; user merges manually.

## When to use

| Situation | Use |
|-----------|-----|
| Review open PR before merge | **18-pr-review** |
| Milestone or phase PR ready for human/agent review | **18-pr-review** |
| Post structured feedback to GitHub | **18-pr-review** |
| Fix review findings on the PR branch | [19-address-pr-review](../19-address-pr-review/SKILL.md) |
| Production bug patch | [14-hotfix](../14-hotfix/SKILL.md) first, then **18-pr-review** on the fix PR |
| Process retrospective | [17-retrospective](../17-retrospective/SKILL.md) |

## Prerequisites

1. **`gh` CLI** authenticated (`gh auth status`).
2. **PR exists** on GitHub (or user will create one first).
3. **`workflow-state.yaml`** exists (greenfield pipeline started) — if missing, warn and proceed without state writes unless user waives.

## Interactive questions (required)

**Every user-facing question must use AskQuestion.** Do not expect inline chat replies for gates.

| Phase | AskQuestion |
|-------|-------------|
| **0 — Target** | PR URL · PR number · current branch · list open PRs · Let me explain |
| **0 — Scope** | Full checklist · Fast (skip local checkout unless CI red) · Include/exclude connectivity rows |
| **Before checkout** | CI red/missing — checkout locally and run 09-qa parity? (yes / no / waive) |
| **Before post** | If verdict surprising — confirm post Request changes / Approve? (default: follow verdict matrix) |

First option = recommendation; last = `Let me explain / provide more context`.


## Session management

Per [sessions-reference.md](../sessions-reference.md) §10 and [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).

1. Agent `read_context` must return `active_session` (or blocking deviation).
2. Current stage must appear in `active_session.routing_plan` unless user amends plan.
3. Write stage reports to `active_session.artifacts_dir/reports/` when this stage produces a report.
4. On completion: update routing-plan entry status; mirror `project.stages.{key}` via agent `update`.
5. **00-context** exempt from active_session requirement (session opener).
Report: `reports/pr-review.md`.

## State management

1. Invoke **workflow-state-manager** `read_context` + `skill_id: 18-pr-review`.
2. After Phase 0, agent `update` → new `pr_review_cycles[]` entry `status: in_progress`.
3. On completion, agent `update` → `status: completed`, verdict, counts, PR URL.

Schema: [reference.md](reference.md) §workflow-state.yaml schema.

## Workflow

### Phase 0 — Intake

1. **AskQuestion:** How to identify the PR? (URL / number / current branch / list open / explain)
2. Resolve metadata: `gh pr view` — title, body, base, head, files, checks.
3. **AskQuestion:** Review depth (full / fast / custom sections).
4. Read PR description (checklist A1). Note linked issues and change type (A4–A5).

### Phase 1 — Gather evidence

1. `gh pr diff` — read all changes; note files touched for deployed service overlay (§F).
2. **CI (remote first):** `gh pr checks` + latest `ci.yml` on PR head.
   - Green → record pass (D1).
   - Red/missing → **AskQuestion** then optionally `gh pr checkout` + [09-qa Phase 1](../09-qa/SKILL.md) parity (D3).
3. Hygiene scan on diff: cruft, secrets, operator specs (D4–D5, E1–E4).
4. Map findings to checklist rows; draft 🟢 praise (required, B1).

### Phase 2 — Subagents

Run **in sequence** (same PR head checked out locally):

1. **Bugbot** — readonly; fold findings into G1.
2. **Security review** — readonly; fold findings into G2.

Triage each subagent finding as 🔴 / 🟡 / 🟢. Do not auto-elevate to 🔴 without evidence in diff or subagent detail.

### Phase 3 — Checklist pass

Walk [checklist.md](checklist.md) sections **A → H**. For each failed row:

- Assign severity per checklist table.
- Draft inline comment text (path + line from diff).
- Track blocker/advisory/praise counts.

**Verdict matrix** (checklist §Verdict matrix):

- Any 🔴 → `--request-changes`
- No 🔴, only 🟡 → `--comment` (or `--approve` if trivial with noted advisories)
- No 🔴, clean → `--approve`

### Phase 4 — Post to GitHub

Order:

1. Post **inline comments** for 🔴 and substantive 🟡 (`gh api` — [reference.md](reference.md)).
2. Post **review body** with:
   - **Praise** (🟢) — first section, specific
   - **Checklist results** — section pass/fail table
   - **Findings** — 🔴 / 🟡 summary
   - **CI + subagents** — status lines
   - **Thank the author** — closing line (Katy Huff)
3. `gh pr review` with correct event — **never merge**.

If `gh` post fails, report error verbatim; retry once; then AskQuestion.

### Phase 5 — Close out

1. workflow-state-manager `update` — complete `pr_review_cycles[]`.
2. Chat summary: PR URL, verdict, blocker count, link to posted review.
3. Do **not** fix code or push unless user explicitly asks in a follow-up — use
   [19-address-pr-review](../19-address-pr-review/SKILL.md) for structured remediation.

## Output rules

| Artifact | Location |
|----------|----------|
| Posted review | GitHub PR (inline + review body) |
| State | `workflow-state.yaml` → `pr_review_cycles[]` |
| Checklist source | [checklist.md](checklist.md) (stable; do not fork per PR) |

## Relationship to repo PR template

Authors should fill [.github/pull_request_template.md](../../.github/pull_request_template.md) before review. Reviewer validates A2, A4–A6 against that template.

## Anti-patterns

- Merging or approving without reading the diff
- Skipping praise in the review body
- Posting review without inline comments when 🔴 line-specific issues exist
- Running Bugbot/Security only in chat — must orchestrate subagents
- Fixing findings in the same invocation without user request
