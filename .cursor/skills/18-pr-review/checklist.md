# 18-pr-review — Merged checklist

Sources (verbatim intent preserved where noted):

- [Katy Huff PR review checklist](https://gist.github.com/katyhuff/845e06656f18784210190e4f46a4aa95)
- [stevemao/github-issue-templates](https://github.com/stevemao/github-issue-templates) — `checklist/` + `checklist2/` PR templates
- deployed service project rules — `.cursor/rules/`, [09-qa](../09-qa/SKILL.md), [ci-after-push](../../rules/ci-after-push.mdc)

Severity key:

| Severity | Meaning | Verdict impact |
|----------|---------|----------------|
| 🔴 **Blocking** | Must fix before merge | Contributes to **Request changes** |
| 🟡 **Advisory** | Should improve; not merge-blocking alone | **Comment** if no blockers |
| 🟢 **Praise** | Specific positive observation | Required in review body opener |

---

## A — PR intake (author + reviewer)

| # | Item | Severity if fail |
|---|------|------------------|
| A1 | Read the PR description | — |
| A2 | PR body explains **what** changed and **why** (stevemao core-features) | 🟡 |
| A3 | No duplicate open PRs for the same change (stevemao all-submissions) | 🔴 |
| A4 | Change type identified: bug fix / feature / breaking / docs-only (stevemao checklist2) | 🟡 |
| A5 | Linked issue(s) present when applicable; `Closes #N` accurate (Katy Huff) | 🟡 |
| A6 | Documentation updated when behavior or APIs changed (stevemao checklist2) | 🔴 if user-facing API changed without docs |

---

## B — Code quality (Katy Huff + stevemao)

| # | Item | Severity if fail |
|---|------|------------------|
| B1 | **Start with praise** — at least one specific 🟢 in review body | Required (process) |
| B2 | Variable names brief but descriptive | 🟡 |
| B3 | New/changed functions no longer than a paragraph | 🟡 |
| B4 | Function parameters have defaults where appropriate | 🟡 |
| B5 | Code clear and clean (Clean Code readability) | 🟡 |
| B6 | Enough documentation for non-obvious logic | 🟡 |
| B7 | Style matches repo (Python: ruff; TS: ESLint strict) | 🔴 on CI lint failure |
| B8 | Code follows project typing policy — no explicit `Any` / `any` | 🔴 |

---

## C — Tests

| # | Item | Severity if fail |
|---|------|------------------|
| C1 | New feature or bug fix includes tests (Katy Huff + stevemao) | 🔴 |
| C2 | Tests exercise the changed functionality — not tautological | 🔴 |
| C3 | Edge cases covered where risk warrants | 🟡 |
| C4 | Corner cases covered where risk warrants | 🟡 |
| C5 | All new and existing tests pass (stevemao checklist2) | 🔴 |

---

## D — CI and local verification

| # | Item | Severity if fail |
|---|------|------------------|
| D1 | Remote `ci.yml` green on PR HEAD (`python` + `frontend` jobs) | 🔴 |
| D2 | If target/base is `main`: `deploy-preflight.yml` considered when relevant | 🔴 on main-bound PR |
| D3 | If remote CI missing/red: checkout PR branch and run [09-qa Phase 1](../09-qa/SKILL.md) parity locally | 🔴 if local fails |
| D4 | No secrets, operator spec exports, or `.env` artifacts in diff | 🔴 |
| D5 | `bash scripts/check_no_operator_specs_tracked.sh` would pass | 🔴 |

---

## E — Repository hygiene

| # | Item | Severity if fail |
|---|------|------------------|
| E1 | No random cruft (build artifacts, `.swp`, editor junk) | 🔴 |
| E2 | All files belong in the repository | 🔴 |
| E3 | File deletions justified | 🟡 if unexplained |
| E4 | New files/data compatible with repository license | 🔴 |
| E5 | Scope matches approved plan when execution-plan task IDs cited | 🟡 |

---

## F — deployed service deploy / connectivity (when applicable)

Run rows that apply to touched paths.

| # | Item | Severity if fail |
|---|------|------------------|
| F1 | Frontend changes: `VITE_*` wiring + bundle grep (H5) | 🔴 |
| F2 | API/CORS changes: connectivity tests or H4 preflight | 🔴 |
| F3 | OpenAPI / contract changes: `bash scripts/check_openapi_specs.sh` | 🔴 |
| F4 | Modal / deploy changes: `bash scripts/check_modal_no_database_url.sh` | 🔴 |
| F5 | Migrations included when schema changes | 🔴 |
| F6 | PR `stage`→`main`: release prep noted (semver for changed publishable pkgs + CHANGELOG); post-merge deploy/PyPI tags planned ([Corpus: deploy] §Promote) | 🟡 |

---

## G — Automated deep review (subagents)

| # | Item | Severity if fail |
|---|------|------------------|
| G1 | Bugbot subagent run; findings triaged into 🔴/🟡/🟢 | 🔴 for confirmed bugs |
| G2 | Security-review subagent run; findings triaged | 🔴 for confirmed vulnerabilities |

---

## H — Review delivery (required)

| # | Item | Notes |
|---|------|-------|
| H1 | Inline comments on specific lines for 🔴 and substantive 🟡 | `gh api` pull comment |
| H2 | Review body: praise → checklist table → findings summary → test plan echo | `gh pr review` |
| H3 | Verdict: **Approve** if no 🔴; **Request changes** if any 🔴; **Comment** if 🟡 only | Never merge |
| H4 | Thank the author in review body closing (Katy Huff) | Required |
| H5 | Record cycle in `pr_review_cycles[]` via workflow-state-manager | Required |

---

## Verdict matrix

| 🔴 blockers | 🟡 advisories | `gh pr review` event |
|-------------|---------------|----------------------|
| 0 | any | `--approve` |
| ≥1 | any | `--request-changes` |
| 0 | ≥1 (no approve-worthy cleanliness) | `--comment` |

When 🔴 = 0 and change is trivial/docs-only, prefer `--approve` even with minor 🟡 noted inline.
