---
name: 19-address-pr-review
description: >
  Works through pull request review findings one-by-one or in batches: triages GitHub review
  comments (including 18-pr-review output), confirms fix approach with the user, applies TDD
  for blockers, commits atomically, replies and resolves threads, pushes, watches CI, and
  offers 18-pr-review re-run. Never merges. Use when the user asks to address PR review
  feedback, fix review comments, or remediate findings after 18-pr-review.
disable-model-invocation: true
---

# 19 — Address PR Review

On-demand **Phase G follow-up** to [18-pr-review](../18-pr-review/SKILL.md): turn posted review
findings into scoped fixes on the PR branch.

**GitHub commands:** [reference.md](reference.md)  
**Preamble:** [pipeline-preamble.md](../pipeline-preamble.md)  
**Cross-cutting:** [considerations.md](../considerations.md), [ci-after-push](../../rules/ci-after-push.mdc), [bug-investigation](../bug-investigation/SKILL.md) (🔴 TDD)  
**State agent:** [workflow-state-manager](../../agents/workflow-state-manager.md) — mandatory read/update

**Never merge.** User merges manually after re-review passes.

## When to use

| Situation | Use |
|-----------|-----|
| Fix findings after **18-pr-review** posted | **19-address-pr-review** |
| Triage and fix open PR review / inline comments | **19-address-pr-review** |
| Post structured review to GitHub | [18-pr-review](../18-pr-review/SKILL.md) |
| Production bug without open PR | [14-hotfix](../14-hotfix/SKILL.md) |
| Keep PR merge-ready (conflicts + CI loop, less interview) | Cursor built-in `babysit` skill |

## Prerequisites

1. **`gh` CLI** authenticated (`gh auth status`).
2. **PR exists** with review comments or a prior **18-pr-review** cycle.
3. **Checkout access** — agent can `gh pr checkout` and commit on the PR head branch.
4. **`workflow-state.yaml`** exists — warn and proceed without state writes if missing (user may waive).

## Interactive questions (required)

**Every user-facing gate must use AskQuestion.** Do not expect inline chat replies for gates.

| Phase | AskQuestion |
|-------|-------------|
| **0 — Target** | PR URL · PR number · current branch · list open PRs · Let me explain |
| **0 — Resume** | New remediation session · Resume in-progress `pr_remediation_cycles[]` · Let me explain |
| **1 — Scope** | Blockers only (🔴) · Blockers then advisories (🟡) · Pick specific items · Let me explain |
| **2 — Per finding** | Confirm fix approach · Won't fix (reply on thread) · Defer · Let me explain |
| **2 — Post-fix** | Confirm resolution before GitHub reply / thread resolve | 
| **3 — Push** | Push commits now? (yes / no / wait for more fixes) |
| **4 — Re-review** | Run **18-pr-review** on this PR now? (yes / no / later) |

First option = recommendation; last = `Let me explain / provide more context`.

## State management

1. Invoke **workflow-state-manager** `read_context` + `skill_id: 19-address-pr-review`.
2. After Phase 0, agent `update` → new `pr_remediation_cycles[]` entry `status: in_progress`.
3. Link `linked_review_cycle_id` when a matching `pr_review_cycles[]` entry exists (same PR number).
4. After each finding: append to cycle `findings[]` with status (`fixed` | `deferred` | `wont_fix`).
5. On completion, agent `update` → `status: completed`, counts, head SHA after push.

Schema: [reference.md](reference.md) §workflow-state.yaml schema.

## Workflow

### Phase 0 — Intake

1. **AskQuestion:** How to identify the PR?
2. Resolve metadata: `gh pr view` — number, URL, head, base, checks.
3. `gh pr checkout <number>` (unless already on PR head).
4. **Fetch findings** — all unresolved review input ([reference.md](reference.md) §Fetch findings):
   - Inline review comments on open threads
   - Review bodies with 🔴 / 🟡 markers (including **18-pr-review** posts)
   - Classify each item: **blocker** (🔴, `REQUEST_CHANGES`, or labeled blocking) vs **advisory** (🟡)
5. **AskQuestion:** Resume prior cycle or start new?
6. Present numbered backlog; note already-resolved threads (skip).

### Phase 1 — Session scope

1. **AskQuestion:** Blockers only · blockers then advisories · pick specific IDs.
2. Default order: **all blockers first**, then batch advisories by **file or theme** (max ~5 per batch).

### Phase 2 — Remediate (per item or batch)

**Blockers (one at a time):**

1. Show finding: path, line, comment body, reviewer.
2. **AskQuestion:** Proposed fix approach · won't fix · defer.
3. If **won't fix** or **defer** → draft GitHub reply; resolve thread only when user confirms on close-out for won't-fix with rationale.
4. If **fix**:
   - **TDD when finding is a defect** (logic bug, regression, security issue): follow [bug-investigation](../bug-investigation/SKILL.md) — repro test in `tests/bugs/`, red → green, one bug per test module.
   - Non-defect blockers (spec/checklist/hygiene): fix in place; add/adjust tests only when behavior changed.
5. Local checks on touched paths ([reference.md](reference.md) §Local verification).
6. **Atomic commit** — one finding per commit unless user approved a batch in Phase 1.
7. **AskQuestion:** Confirm resolution matches intent?
8. **GitHub:** reply on thread citing commit SHA; **resolve thread** when fix is complete ([reference.md](reference.md) §Resolve threads).

**Advisories (batched):**

1. Present batch (same file or theme).
2. **AskQuestion:** Fix batch · skip batch · pick subset.
3. Fix without mandatory repro tests unless behavior change warrants tests.
4. One commit per approved batch; reply per thread or one summary reply if threads are linked.

Do **not** push until Phase 3 unless user explicitly requests push after a single finding.

### Phase 3 — Push and CI

1. **AskQuestion:** Push now?
2. `git push` to PR head remote.
3. Watch CI: `bash scripts/ci/watch_github_ci.sh <head-ref>` ([ci-after-push](../../rules/ci-after-push.mdc)).
4. If CI fails on changes in scope → fix in loop (AskQuestion before out-of-scope CI/workflow edits).
5. Record `ci_status` on cycle.

### Phase 4 — Close out

1. workflow-state-manager `update` — complete `pr_remediation_cycles[]`.
2. Chat summary: PR URL, fixed / deferred / won't-fix counts, commit SHAs, CI status.
3. **AskQuestion:** Run [18-pr-review](../18-pr-review/SKILL.md) now?
4. Do **not** merge.

## Severity and scope rules

| Source | In scope | Default handling |
|--------|----------|------------------|
| 🔴 / blocking inline | Yes | Phase 2 one-by-one; TDD if defect |
| 🟡 / advisory inline | Yes | After blockers; batched |
| **18-pr-review** review body | Yes | Parse Findings section |
| Human / Bugbot / other bots | Yes | Same triage; validate before acting |
| Praise (🟢) | No | Acknowledge only — do not "fix" |
| Merge conflicts | Out of scope | Suggest `babysit` or manual merge |
| Unrelated CI on base branch | Out of scope | Report; suggest merge base or babysit |

When disagreeing with a comment: **won't fix** path — AskQuestion, then reply with evidence; do not resolve thread unless user treats comment as satisfied.

## Output rules

| Artifact | Location |
|----------|----------|
| Code fixes | PR head branch commits |
| GitHub replies | PR review threads |
| State | `workflow-state.yaml` → `pr_remediation_cycles[]` |
| Bug repro (🔴 defects) | `docs/bug-reports/BUG-*.md` + `tests/bugs/test_bug_*.py` |

## Anti-patterns

- Merging the PR
- Fixing without Phase 2 AskQuestion on approach
- One giant commit for unrelated findings
- Skipping CI watch after push
- Changing CI workflows to greenwash unrelated failures
- Auto-starting after **18-pr-review** without user invoking **19-address-pr-review**
- Resolving GitHub threads before user confirms resolution
