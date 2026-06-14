---
name: gather-context
description: >
  Runs paper-analyst and repo-researcher agents in parallel, cross-references their findings,
  surfaces contradictions / ambiguities / decisions / bloat / uncertainty to the user via
  AskQuestion, and produces a Research Brief that downstream skills (doc-planner, etc.) consume.
  Use when starting work on a codebase that has an associated research paper and you need a
  vetted, cross-referenced understanding of both before planning or building.
---

# Gather Context

Research a codebase and its associated paper, cross-reference findings, resolve conflicts with
the user, and produce a structured Research Brief for downstream skills.

**Cross-cutting:** [considerations.md](../considerations.md) — spec-error loops, changelogs,
perf validation handoff, root-cause typing.

## When to use

- **Before doc-planner**: This skill must run first. Doc-planner expects the Research Brief as
  input and will invoke this skill if it hasn't been run yet.
- **Standalone**: Can also be invoked on its own when you need a deep, cross-referenced
  understanding of a paper + repo pair without planning documents.

## Uncertainty Resolution Protocol

**Core rule**: Never silently resolve a decision, ambiguity, contradiction, bloat concern, or
source of uncertainty. Every one must be surfaced to the user as a structured question using
the AskQuestion tool before proceeding.

### What to surface

Scan for these categories at every phase of the workflow:

| Category | Trigger | Example |
|---|---|---|
| **Decision** | Multiple valid approaches exist and the choice affects downstream output | Which model architecture variant should downstream docs describe — the paper's baseline or its ablation winner? |
| **Ambiguity** | A requirement, term, metric, or scope boundary is under-defined | The paper says "standard preprocessing" without specifying steps; the repo has two different normalizers. Which is canonical? |
| **Contradiction** | Paper and repo disagree, or a single source contradicts itself | Paper reports 95% accuracy on dataset X, but the repo's eval script targets dataset Y with a different threshold. |
| **Bloat** | A piece of information or scope item adds noise without clear value | The repo bundles a visualization notebook unrelated to the core pipeline. Should downstream docs cover it? |
| **Uncertainty** | Low confidence in a fact, metric, or design detail — not enough evidence to commit | The repo imports `scikit-learn` but never appears to call it in the pipeline. Is it a vestigial dependency or used in a path we haven't traced? |

### How to surface

For each issue found, use the **AskQuestion** tool with this structure:

1. **Prompt**: State the issue concisely. Lead with the category label in brackets, e.g.
   `[Contradiction]`, `[Decision]`, `[Ambiguity]`, `[Bloat]`, `[Uncertainty]`.
2. **Findings**: Include the evidence that triggered the issue — cite the paper section
   (`[Paper §X]`), the repo path (`[Repo: path/to/file:L10-20]`), or both. If other repos or
   external references provide clarifying context, include those too.
3. **Recommendation**: Always provide a recommended option as the first choice, with a short
   rationale derived from the evidence.
4. **Options**: Provide 2–4 concrete options. The first option should be the recommendation.
   Always include a "Let me explain / provide more context" escape hatch as the last option.

**Shape**: `prompt` leads with `[Category]`, then evidence; `options` mirror the template above.

### Batching

When multiple issues are found at the same phase, batch them into a single AskQuestion call
with multiple questions rather than interrupting the user repeatedly. Group by category.

### Blocking behavior

- **Decisions, Contradictions, Ambiguities**: These are **blocking** — do not proceed past the
  current phase until the user responds. The answer directly affects downstream output.
- **Bloat, Uncertainty**: These are **advisory** — present them, but if the user does not
  respond, proceed with the recommended option and note the assumption in the Research Brief
  with a `⚠️ Assumed:` prefix.

## State management

**Canonical:** repo-root [`workflow-state.yaml`](../../workflow-state.yaml) §`stages.gather-context`.
Rules: [workflow-state-reference.md](../workflow-state-reference.md).

Legacy `docs/gather-context-state.md` is **deprecated** — mirror phase progress into YAML only.

### On invocation — check state

Before doing any work:

1. Read `workflow-state.yaml` §`stages.gather-context` (create key `pending` if missing).
2. Determine status from YAML (not from a separate state file):
   - **`complete`**: The skill has already finished. Ask the user via AskQuestion:
     - "Reuse the existing Research Brief as-is"
     - "Update — re-run only incomplete phases and merge"
     - "Regenerate — start over from scratch"
   - **`in_progress`**: The skill was interrupted mid-run. Report what completed and what
     remains. Ask the user:
     - "Resume from where we left off"
     - "Restart from the beginning"
   - **`failed`**: A phase failed. Report which phase and why. Ask the user:
     - "Retry the failed phase"
     - "Restart from the beginning"
     - "Abort — I'll fix the issue first"
3. **If `pending`**: Start fresh. Set `in_progress` + `started_at` at Phase 1.

### YAML substeps (§`stages.gather-context`)

```yaml
status: pending | in_progress | completed | failed
started_at: YYYY-MM-DD
completed_at: YYYY-MM-DD
phases:
  phase1_agents: { status: pending }
  phase2_cross_reference: { status: pending }
  phase3_surface_issues: { status: pending }
  phase4_research_brief: { status: pending }
agents:
  paper_analyst: { status: pending }
  repo_researcher: { status: pending }
report: docs/research-brief.md
```

Also update top-level `workflow-state.yaml` §`agents` when subagents finish.

## Issue Tracking

| Metric | Value |
|--------|-------|
| Issues detected | 0 |
| Issues surfaced | 0 |
| Blocking resolved | 0 |
| Blocking pending | 0 |
| Advisory resolved | 0 |
| Advisory assumed | 0 |

## Current Position

- **Active phase**: [1–5 or complete]
- **Waiting on**: [nothing / user response / agent completion]
- **Blocker**: [none / description]
```

### Updating state

After each phase completes (or fails), immediately update `workflow-state.yaml` §`stages.gather-context`:
- Set the phase status to `completed` (or `failed` with notes)
- Update the Agent Status table after Phase 1
- Update Issue Tracking after Phases 2 and 3
- Set overall status to `complete` after Phase 5

State writes are **immediate** — never buffer. If the session ends mid-skill, all progress
up to the last completed phase is preserved.

## Inputs

Collect these from the user (check README.md, conversation context, or ask):

1. **Repository URL** — GitHub URL of the target codebase (or local path if already cloned)
2. **Paper path** — local path to the research paper (JATS XML, PDF, or markdown)
3. **Output directory** — where to write the Research Brief (default: `docs/` in the repo root)

## Workflow

### Phase 1 — Run Analysis Agents

**State**: Ensure `workflow-state.yaml` §`stages.gather-context` exists. Set status to
`in_progress`. Set Phase 1 status to `in_progress` with the current timestamp.

Launch both agents in parallel using the Task tool:

1. **paper-analyst** — invoke with the paper path. Prompt it to extract build, run, test, and
   config insights from the research paper. Use `claude-4.6-opus-max-thinking` model as
   specified in the agent's metadata (`.cursor/agents/paper-analyst.md`).

2. **repo-researcher** — invoke with the repository URL. Prompt it to produce a comprehensive
   implementation guide covering build, run, test, and configure. Use
   `claude-4.6-opus-max-thinking` model as specified in the agent's metadata
   (`.cursor/agents/repo-researcher.md`).

Wait for both to complete. Store their full outputs as working context.

**State**: Update Agent Status for both agents (status, output size). Set Phase 1 to
`completed`. Set Phase 2 to `in_progress`. If either agent failed, set Phase 1 to `failed`
with notes, set overall status to `failed`, and stop.

### Phase 2 — Cross-Reference & Detect Issues

Systematically compare the two agent reports to detect issues across five scans:

1. **Contradiction scan**: Align claims from the paper-analyst against the repo-researcher on
   shared topics (datasets, metrics, parameters, architecture, dependencies). Log every
   mismatch — even minor ones like version differences.

2. **Ambiguity scan**: Identify terms, metrics, or procedures that one source defines vaguely
   or differently than the other. Flag cases where the paper uses a term the repo never
   mentions, or vice versa. Pay special attention to:
   - Parameter names that differ between paper and code
   - Pipeline stages described in the paper but absent from the repo
   - Features present in the repo but not mentioned in the paper

3. **Decision scan**: Find points where the paper describes multiple approaches (ablations,
   alternative models, optional steps) and the repo implements only one — or implements
   something the paper doesn't describe. Each of these is a fork that downstream consumers
   need to know about.

4. **Bloat scan**: Identify content in either report that is tangential to the core pipeline —
   e.g., visualization utilities, legacy scripts, deprecated features. Flag anything that
   would add noise to downstream documentation without clear engineering value.

5. **Uncertainty scan**: Note any facts cited by only one source with no corroboration, or
   where an agent report itself flagged low confidence (`⚠️ Inferred:`, `⚠️ Not found`, etc.).
   Also flag:
   - Dependencies listed in the repo but never mentioned in the paper
   - Paper-described features with no corresponding code path found
   - Metrics or thresholds stated without context on how they were derived

6. **Data & model weight scan**: Identify all external data assets the project requires to
   run — corpus fixtures, pretrained checkpoints, datasets, tokenizer files, embedding matrices,
   etc. For each asset found, collect:
   - **Name and type** (corpus fixtures, dataset, checkpoint, tokenizer, embeddings)
   - **Source** (HuggingFace Hub, Zenodo, S3, direct URL, Git LFS, generated)
   - **Size** (approximate, from paper or repo docs)
   - **Where the code loads it** (file path patterns from repo analysis)
   - **Where the paper references it** (section, table, or supplementary)
   - **Authentication required** (gated model, API key, license acceptance)
   - **Mutability** (static release vs. frequently updated)
   Cross-reference paper and repo to detect:
   - Assets the paper mentions but the repo doesn't download or document
   - Assets the repo loads but the paper doesn't describe (undocumented dependencies)
   - Conflicting paths or versions between paper and repo
   - Missing checksums, sizes, or download instructions
   Flag each finding per the categories above (Contradiction, Ambiguity, etc.).

**State**: Update Issue Tracking with the count of issues detected. Set Phase 2 to
`completed`. Set Phase 3 to `in_progress`.

### Phase 3 — Surface Issues to User

Collect all issues from Phase 2. If any exist:

1. Batch them into AskQuestion calls grouped by category (see Uncertainty Resolution Protocol).
2. Wait for responses to all **blocking** issues before continuing.
3. For **advisory** issues the user does not respond to, adopt the recommended option.

Record all resolutions in a **Resolution Log**:

```
Resolution Log:
  R1: [Contradiction] Dataset split — User chose: paper's spec (SAbDab 90/10)
  R2: [Bloat] Visualization notebook — User chose: Exclude from scope
  R3: [Uncertainty] scikit-learn dep — Assumed: vestigial (user did not respond, advisory)
  R4: [Ambiguity] "standard preprocessing" — User chose: repo's normalize_v2.py is canonical
  R5: [Decision] Model variant — User chose: describe the ablation winner, not baseline
```

**State**: Update Issue Tracking with surfaced/resolved/assumed counts. Set Phase 3 to
`completed`. Set Phase 4 to `in_progress`. If blocking issues remain unresolved, set
Waiting on to `user response` and Current Position to Phase 3 until resolved.

### Phase 4 — Produce the Research Brief

Write a structured Research Brief to `{output_directory}/research-brief.md`. This file is the
primary handoff artifact to downstream skills.

#### Research Brief structure

Read the full template from [research-brief-template.md](research-brief-template.md).

Key sections: Executive Summary, Resolution Log, Paper Analysis Summary (parameters,
experiments, hardware), Repository Analysis Summary (build, pipeline stages, config surface),
Data & Model Weight Requirements (asset inventory with source/size/auth/status), Cross-Reference
Matrix, Unresolved Gaps, and Full Agent Reports (collapsible).

**State**: Set Phase 4 to `completed`. Set Phase 5 to `in_progress`.

### Phase 5 — Summary

Report completion to the user:

```
Gather Context Complete.

Research Brief written to: docs/research-brief.md

Sources analyzed:
  Paper: [title] — [N] build, [N] run, [N] test, [N] config insights extracted
  Repo:  [URL]   — [N] files scanned, [N] config surfaces documented

Issues surfaced: [N] total
  Blocking — [N] raised, [N] resolved by user
  Advisory — [N] raised, [N] assumed

Unresolved gaps: [N] (marked in Research Brief for downstream handling)

Ready for: doc-planner, or any skill that consumes the Research Brief.
```

**State**: Set Phase 5 to `completed`. Set overall status to `complete`. Set Active phase
to `complete`. Set Waiting on to `nothing`.

## Output Rules

1. **Evidence-based**: Every claim must trace to paper-analyst or repo-researcher output.
   Never fabricate details.
2. **Citation format**: Paper references use `[Paper §X]` or `[Paper Table N]`. Repo references
   use `[Repo: path/to/file:L10-20]`.
3. **Full reports preserved**: The complete agent outputs are included in the Research Brief
   under collapsible sections so downstream skills have access to raw detail.
4. **Resolution traceability**: Every resolution is numbered (R1, R2, ...) and referenced in
   the Cross-Reference Matrix and Resolution Log. Downstream skills cite these IDs.
5. **No silent resolution**: Per the Uncertainty Resolution Protocol — never pick an answer
   to a blocking issue without the user's input. Advisory issues may be assumed, but must be
   marked with `⚠️ Assumed:`.
6. **State-managed**: All progress is tracked in `workflow-state.yaml` §`stages.gather-context`. State writes
   happen immediately after each phase. On re-invocation, the state file determines whether
   to resume, update, or regenerate — see State Management section above.
