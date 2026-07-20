---
name: audit-docs
description: >
  Audits doc-planner output by breaking each document into provable (falsifiable) statements
  and walking the user through each one for approval, denial, or modification. Produces a
  document audit report, a decision log, and tracks progress with persistent state management.
  Runs after doc-planner and before build-planner. Use when the user wants to verify specs,
  audit documentation claims, validate statements in generated docs, or review doc-planner
  output before implementation.
---

# Audit Docs

Break doc-planner output into provable statements and walk the user through each one,
doc-by-doc and statement-by-statement, to approve, deny, or modify every claim before
implementation begins.

**Cross-cutting:** [considerations.md](../considerations.md).

## Prerequisite — Doc Planner

This skill requires **doc-planner** to have completed. Before starting:

1. Check that doc-planner output exists in `{output_directory}/` (at minimum:
   `research-brief.md`, `deployment-integration.md`, and `data-management-plan.md`).
2. If missing, inform the user and invoke doc-planner first.

## State management

**Canonical:** repo-root [`workflow-state.yaml`](../../workflow-state.yaml) §`stages.audit-docs`.
Rules: [workflow-state-reference.md](../workflow-state-reference.md).

**Detail:** `docs/audit-state.md` may mirror statement counts — do not use it as the only
source of stage completion.

### On invocation

1. Read `workflow-state.yaml` §`stages.audit-docs` (and `docs/audit-state.md` if present).
2. **If `completed`**: Ask reuse / partial re-audit / full restart.
3. **If `in_progress`**: Resume from recorded document/statement counters in YAML.
4. **If `pending`**: Start fresh; set `in_progress` + `started_at`.

Every user decision: update YAML immediately; append resolutions to `decisions_log` when they
affect downstream specs.

## Workflow

### Phase 1 — Inventory Documents

Read all doc-planner output files from the output directory. Build an ordered list of
documents to audit:

| # | Document | Path | Sections | Status |
|---|----------|------|----------|--------|
| 1 | Deployment Integration Plan | docs/deploy.md §Integration | [N] | pending |
| 2 | Data Management Plan | docs/spec.md §Data | [N] | pending |
| 3 | User Journeys | docs/user-journeys.md | [N] | pending |
| 4 | Test Plan | docs/test-plan.md | [N] | pending |
| 5 | Feature List | docs/feature-list.md | [N] | pending |
| ... | ... | ... | ... | ... |

**Ordering**: Audit mandatory documents first (Deployment Integration Plan, Data Management Plan),
then by priority from the doc-planner manifest.

Skip files that are not spec documents (e.g., `research-brief.md` is a reference input,
not a spec to audit).

### Phase 2 — Extract Provable Statements

For each document, read it section-by-section and extract **provable statements** —
claims that are falsifiable (could be proven incorrect). Each statement must be:

- **Specific**: Contains a concrete claim, not vague prose
- **Falsifiable**: Could be contradicted by evidence from the paper, repo, or domain knowledge
- **Atomic**: One claim per statement — do not bundle multiple assertions

#### What counts as a provable statement

| Type | Example | Why it's provable |
|------|---------|-------------------|
| Parameter value | "The default learning rate is 1e-4" | Could be wrong — checkable against code/paper |
| Architecture claim | "The model uses 12 attention heads" | Could mismatch the paper or code |
| Dependency | "Requires PyTorch >= 2.0" | Verifiable against requirements files |
| Pipeline order | "Preprocessing runs before feature extraction" | Could be reversed in the actual code |
| Performance target | "Achieves 95% accuracy on SAbDab" | Could be misquoted from the paper |
| Config mapping | "The `batch_size` field maps to `--bs` CLI flag" | Verifiable in the codebase |
| Scope claim | "The API exposes 3 endpoints" | Could be more or fewer |
| Assumed fact | "⚠️ Assumed: scikit-learn is vestigial" | Explicitly uncertain — needs verification |

#### What is NOT a provable statement

Skip these — they are structural or definitional, not falsifiable:

- Section headers and labels
- Template boilerplate ("Replace [bracketed placeholders]...")
- References and citations themselves (the link, not the claim it supports)
- Purely subjective guidance ("This is a good practice")

#### Statement format

Each extracted statement gets a structured record:

```
S[doc#].[statement#]:
  Document: [doc name]
  Section:  [section path, e.g., "§GPU Strategy > Recommended GPU"]
  Statement: "[the exact claim, quoted from the document]"
  Source: [Paper §X / Repo: file:L# / Assumed / Inferred]
  Confidence: [High / Medium / Low — based on source quality]
```

### Phase 3 — Create Audit Artifacts

Write three files to the output directory. Read
[artifacts-template.md](artifacts-template.md) for the full template of each:

1. **`audit-state.md`** — Progress tracker: documents/statements total, reviewed counts per
   verdict, per-document progress table, current position pointer.
2. **`document-audit.md`** — Full audit report: per-statement records with section, quoted
   claim, source, confidence, verdict, user feedback, and action taken.
3. **`audit-decisions.md`** — Chronological decision log: timestamped table of every verdict.

### Phase 4 — Walk Through Statements

Process documents in order. For each document, process statements in order.

For each statement, present it to the user via **AskQuestion**:

```
prompt: "[Statement S1.1] From Deployment Integration Plan, §GPU Strategy:
  'The recommended GPU for inference is H100 with fallback to A100-80GB.'
  Source: Paper §4.1 (Confidence: Medium)
  
  Progress: Document 1/7, Statement 1/12 (0% complete)"

options:
  1. "Approve — this statement is correct"
  2. "Deny — this statement is incorrect, remove or flag it"
  3. "Modify — I'll provide the correct version"
  4. "Skip for now — come back to this later"
```

#### Processing verdicts

**Approve**: Mark the statement as approved in `document-audit.md`. No changes to the
source document. Log in `audit-decisions.md`.

**Deny**: Mark as denied. In the source document, either:
- Remove the claim if it's entirely wrong
- Replace with `⚠️ Denied in audit (S1.3): [original claim] — User: "[feedback]"`
- Log in `audit-decisions.md` with user's reason

**Modify**: The user provides the corrected version. Update the statement in both
`document-audit.md` and the source document. Log the original and corrected versions
in `audit-decisions.md`.

**Skip**: Mark as `skipped` in audit state. The statement stays pending and will be
revisited in a second pass after all other statements are processed.

#### After each verdict

1. Update `workflow-state.yaml` §`stages.audit-docs` and mirror counts in `audit-state.md`:
   - Increment the reviewed/approved/denied/modified counters
   - Advance the Current Position to the next statement
   - Update the Document Progress row
2. Append to `audit-decisions.md`
3. Update `document-audit.md` with the verdict and feedback
4. If the verdict was **Deny** or **Modify**, update the source spec document

#### Between documents

When all statements in a document are reviewed, before moving to the next:

1. Mark the document as `completed` in §`stages.audit-docs` and `audit-state.md`
2. Report a document summary to the user:

```
Document 1 of 7 complete: Deployment Integration Plan
  Statements: 12 reviewed
  Approved: 9 | Denied: 1 | Modified: 2 | Skipped: 0
  
  Source document updated: 3 changes applied
  
  Moving to Document 2: Test Plan (15 statements)
```

### Phase 5 — Second Pass (Skipped Statements)

After all documents have been processed, check for any `skipped` statements.

If any exist, present them to the user in a batch:

```
prompt: "There are [N] skipped statements across [M] documents. 
  Review them now, or leave as pending?"

options:
  1. "Review them now"
  2. "Leave as pending — I'll come back later"
```

If reviewing, walk through skipped statements the same way as Phase 4.

### Phase 6 — Summary

After all statements are processed (or the user defers remaining skips):

```
Document Audit Complete.

Results:
  Documents audited: [N] / [N]
  Statements reviewed: [N] / [N]

  Approved:  [N] ([%])
  Denied:    [N] ([%])
  Modified:  [N] ([%])
  Skipped:   [N] ([%])

Source documents updated: [N] changes applied across [M] documents

Artifacts:
  docs/audit-state.md     — progress tracker (status: complete)
  docs/document-audit.md  — full audit report
  docs/audit-decisions.md — chronological decision log

Next step: run build-planner to create an execution plan from the audited specs.
```

Set `workflow-state.yaml` §`stages.audit-docs.status: completed` and `audit-state.md` to complete.

## Output Rules

1. **One statement at a time**: Never batch statements into a single question. Each
   statement gets its own AskQuestion call so the user can focus.
2. **Progress visible**: Every question shows the current position (document X/N,
   statement Y/M, overall %).
3. **Immediate persistence**: Write to all three audit files after every single verdict.
   Never buffer decisions. If the session ends mid-audit, all progress is preserved.
4. **Source doc updates are surgical**: When modifying or denying a statement, change only
   the specific claim in the source document. Do not rewrite surrounding content.
5. **Falsifiable only**: Do not extract non-falsifiable content (headers, boilerplate,
   subjective guidance). Every statement must be a concrete claim that could be wrong.
6. **Cite the source**: Every extracted statement must note where it came from (paper
   section, repo file, assumption, inference).
