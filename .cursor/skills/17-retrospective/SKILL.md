---
name: 17-retrospective
description: >
  Reviews Cursor agent conversation logs and pipeline skills 00-19 against project
  artifacts, then interviews the user with batched AskQuestion prompts to capture what
  went well, what to improve, and brainstorm process fixes. Ends with an interactive
  skill-update workshop (proposed patches per SKILL.md, user approves via AskQuestion).
  Produces a retrospective report and prioritized action backlog. Use after milestones,
  phase completions, hotfix cycles, evolve cycles, or when the user asks for a
  retrospective, lessons learned, or pipeline improvement — not for bug fixes (14-hotfix)
  or feature work (16-evolve).
---

# 17 — Retrospective

Meta-improvement stage: mine **conversation evidence**, compare it to **skills 00–19** and
**workflow artifacts**, then run a structured **user interview** to learn and plan better
process — without re-running the pipeline.

**Preamble:** [pipeline-preamble.md](../pipeline-preamble.md) — shared conventions for stages 00–19.
**Cross-cutting:** [considerations.md](../considerations.md), [connectivity-gates.md](../connectivity-gates.md).
**State agent:** [workflow-state-manager](../../agents/workflow-state-manager.md) — mandatory read/update.

When reviewing pipeline gaps, ask whether **connectivity tiers** (H0c/H0i/H4/H5) were skipped or
misunderstood in the session under review.

**User is the source of truth.** Agent-inferred themes are hypotheses until the user
confirms via **AskQuestion**. Do not edit skills, rules, or product code until **Phase 6 —
Skill update workshop**: each target file gets a concrete proposed patch and its own
AskQuestion approval (or defer/waive). Backlog-only items never auto-edit.

## When to use

| Situation | Use |
|-----------|-----|
| Phase or milestone just finished | **17-retrospective** |
| Several hotfixes or evolve cycles completed | **17-retrospective** |
| Pipeline felt slow, confusing, or repetitive | **17-retrospective** |
| Before changing skills 00–16 org-wide | **17-retrospective** (evidence first) |
| Production bug or patch | [14-hotfix](../14-hotfix/SKILL.md) |
| New product feature | [16-evolve](../16-evolve/SKILL.md) |
| Scope/API change (no new Fn) | [16-evolve](../16-evolve/SKILL.md) |
| Modal health investigation only | [15-service-health](../15-service-health/SKILL.md) |

## Prerequisites

1. **`workflow-state.yaml` exists** (any stage progress is fine).
2. **At least one** of: agent transcripts for this repo, or user can paste/export session links.
3. User agrees to **scope** (time window, stages, depth) in Phase 0.

If transcripts are unavailable, proceed on `workflow-state.yaml`, `docs/`, git history, and
user memory — record the gap in the report.

## Interactive questions (required)

**Every user-facing question must use the AskQuestion tool.** Do not post interview prompts
as markdown lists expecting inline replies.

Reference: [considerations.md](../considerations.md) §7.

| Situation | Pattern |
|-----------|---------|
| Intake / scope | 2–4 `questions` per batch |
| Per-stage rating | One AskQuestion per stage (or batch 2 stages if user chose "fast") |
| Themes / brainstorm | One AskQuestion per theme; options include concrete skill patches |
| Action routing | One AskQuestion: implement now / backlog / ADR / waive |
| Skill update workshop | One AskQuestion **per skill file** (or batched pair): apply patch / modify / defer / waive |
| Skill workshop opener | One AskQuestion: which RA items enter the workshop this session |
| Single gate | First option = recommendation; last = `Let me explain / provide more context` |

## Privacy and evidence hygiene

Before mining transcripts:

1. **AskQuestion**: Include transcripts in scope? (full / date range / exclude current session / none)
2. Do **not** paste secrets, tokens, or full API keys into reports — redact if seen.
3. Prefer **summaries** (counts, dates, skill names, failure classes) over long verbatim quotes.
4. Cite sessions as `[short title](uuid)` per user rules — never cite subagent transcript IDs.

Transcript paths and parsing: [reference.md](reference.md) §Conversation logs.

## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).
**Stage key:** `stages.17-retrospective`.

Invoke **workflow-state-manager** `read_context` before any other action; `update` after each
substep. **Do not** edit `workflow-state.yaml` directly.

`retrospective_cycles[]`. Rules: [workflow-state-reference.md](../workflow-state-reference.md).

### Retrospective cycles

Each invocation starts or resumes a **retrospective cycle** — schema in
[reference.md](reference.md) §YAML schema.

On invocation:

1. Read `workflow-state.yaml`.
2. If a cycle is `in_progress`, report position and **AskQuestion**: resume / abandon / start new.
3. If none in progress, start **Phase 0 — Intake**.

After every substep: update the active cycle immediately.

### Commit-as-you-go

Commit artifacts to an appropriate branch before transitioning to the next stage or
asking the user a blocking question. Branch type per
[workflow-state-reference.md](../workflow-state-reference.md) §Git history.
Record every commit in `workflow-state.yaml` §`git_history.commits` with
`stage: "17-retrospective"`.

### Artifacts

| Artifact | Path |
|----------|------|
| Session report | `docs/retrospectives/YYYY-MM-DD-{slug}.md` |
| Rolling backlog | `docs/retrospective-actions.md` (append; create if missing) |
| Skill patch proposals | Section in report + optional PR checklist (no auto-edit) |

## Delta / feature-addition mode

If retrospective follows a feature cycle, mine `evolve_cycles[]` and feature IDs for evidence.
Does not implement features — process improvement only.
## Workflow overview

```
Phase 0 — Intake (scope, depth, transcript consent)
       │
       ▼
Phase 1 — Evidence digest (transcripts + state + docs + git)
       │
       ▼
Phase 2 — Skill rubric pass (00–16 vs evidence, hypotheses only)
       │
       ▼
Phase 3 — User interview (went well / improve / friction)
       │
       ▼
Phase 4 — Brainstorm solutions (AskQuestion-driven)
       │
       ▼
Phase 5 — Action routing (backlog, ADR, skill edit, 16-evolve, waive)
       │
       ▼
Phase 6 — Skill update workshop (propose patches, AskQuestion per file, apply if approved)
       │
       ▼
Phase 7 — Report + state complete
```

---

## Phase 0 — Intake

**AskQuestion** (one call, 2–4 questions):

1. **Scope**: Full pipeline 00–13 · Maintenance 14–15 only · Evolve/hotfix only · Custom stage list
2. **Time window**: All time · Since last retro · Since date · This session only
3. **Depth**: Deep (per-stage interview) · Standard · Light (themes only)
4. **Transcript consent**: Full · Range · Exclude current · None (artifacts only)

Record answers on the new `retrospective_cycles[]` entry (`scope`, `time_window`, `depth`).

---

## Phase 1 — Evidence digest

Build an internal **Evidence digest** (not shown verbatim to user until validated in Phase 3).

### Sources (read in parallel where possible)

| Source | Extract |
|--------|---------|
| `workflow-state.yaml` | Stage statuses, dates, `issue_log`, `decisions_log`, evolve cycles |
| `workflow-state.yaml + execution plan artifact` | Task churn, blocked tasks, gate log |
| `docs/hotfix-log.md`, `docs/incidents/` | Post-deploy pain |
| `docs/deploy-report.md`, service-health reports | Ops friction |
| `docs/*-decisions.md`, `docs/adr/` | Decision volume and rework |
| Agent transcripts | User goals, skill invocations, loops, AskQuestion density — [reference.md](reference.md) |
| `git log --oneline` (scoped) | Commit cadence, fix churn |

### Transcript mining (when consented)

1. List transcript folders under the project `agent-transcripts/` directory (newest first).
2. Filter by `time_window` (folder `LastWriteTime` or first user message date).
3. For each session, extract per [reference.md](reference.md) §Mining checklist.
4. Map sessions → **likely stages** (keyword/skill path heuristics; mark confidence low/medium/high).

### Digest output shape

```markdown
## Evidence digest (internal)
- Sessions reviewed: N
- Stages touched (inferred): ...
- Recurring patterns: ...
- issue_log / hotfix themes: ...
- Spec vs code vs tooling (considerations §1): counts by class
- Open questions for user: ...
```

Update cycle: `evidence_digest_path` or inline `evidence_summary` in YAML.

---

## Phase 2 — Skill rubric pass (00–16)

For each stage **in scope**, read `.cursor/skills/{NN}-*/SKILL.md` (and `pipeline/SKILL.md`
for orchestration). Score against evidence using the rubric in
[reference.md](reference.md) §Per-stage rubric.

Produce **hypotheses** only — table format:

| Stage | Skill worked? | Evidence | Hypothesis | Confidence |
|-------|---------------|----------|------------|------------|
| 07-build | Partially | 3 resume loops | State pointer unclear | medium |

Do **not** ask the user yet; Phase 3 validates hypotheses.

---

## Phase 3 — User interview (went well / improve)

Interview order follows [reference.md](reference.md) §Interview order.

### Depth: Deep

For **each stage in scope**, one **AskQuestion** with 2–3 questions:

1. What **went well** for this stage? (options from digest + "Something else")
2. What **should improve**? (options = top hypotheses + "None — stage was fine")
3. **Friction rating**: Smooth · Some friction · Major pain

### Depth: Standard

Batch **2 stages per AskQuestion** (same three question types per stage in prompt text).

### Depth: Light

Skip per-stage loop; go to Phase 4 cross-cutting themes only.

### Cross-cutting batch (all depths)

After per-stage (or instead, for Light), one **AskQuestion**:

- Overall pipeline **went well** (pick up to 3 themes)
- Overall **improve** (pick up to 3 themes)
- Biggest **surprise** (unexpected rework, cost, or confusion)

Record verbatim user choices in `docs/retrospectives/...md` §Interview responses.

---

## Phase 4 — Brainstorm solutions

For each **improve** theme the user confirmed (not merely hypothesized):

1. Propose **2–4 concrete options** (skill text change, new hook, ADR, execution-plan task,
   run 16-evolve, run 14-hotfix pattern, doc-only).
2. **AskQuestion**: Which option(s) to pursue? Multi-select if `allow_multiple: true`.
3. Optional second batch: "Combine into one change set?" for related themes.

Brainstorm rules:

- Prefer **small, testable** process changes over rewriting entire skills.
- Reference **exact skill file** and section when proposing edits.
- If the fix is product/code, route to **16-evolve** or **14-hotfix** — do not smuggle code changes into retro.

---

## Phase 5 — Action routing

Consolidate approved ideas into a prioritized table:

| ID | Action | Owner | Target | Priority |
|----|--------|-------|--------|----------|
| RA-001 | Clarify 07-build resume pointer in SKILL.md | agent+user | `.cursor/skills/07-build/SKILL.md` | P1 |

**AskQuestion** (routing gate — not the skill-edit gate; that is Phase 6):

1. Route skill/rule targets to **Phase 6 workshop** this session? (All P1+P2 / P1 only / Backlog only)
2. Create **ADR(s)** for process decisions? (Yes / No / Later)
3. Schedule **follow-up retro**? (After next milestone / After next hotfix / No)

Apply user choices:

- **Backlog only**: Append to `docs/retrospective-actions.md` with status `open`; skip Phase 6
  unless user later opts in via workshop opener.
- **ADR**: Create `docs/adr/ADR-{NNN}.md` per considerations §8.
- **Workshop this session**: Mark skill-target RA rows for Phase 6; do **not** edit files here.
- **16-evolve / 14-hotfix**: Add pointer row in backlog — do not invoke without user ask.

Log actions on the cycle entry (`actions[]`).

---

## Phase 6 — Skill update workshop (required closing step)

Turn approved brainstorm items into **concrete, reviewable skill patches** and walk the
user through them with **AskQuestion** — this is the mandatory end-of-review step before
the report is finalized.

### 6.1 Build the workshop queue

From Phase 5 `actions[]`, collect every row whose `target` is under `.cursor/skills/`
(including `reference.md` companions). If the queue is empty:

**AskQuestion** (single gate):

1. Any skills 00–16 (or `pipeline`) to improve from this retro anyway?
   - Yes — I'll name them · No — skip workshop, proceed to report
   - Let me explain / provide more context

If **No**, record `skill_workshop: skipped` on the cycle and go to Phase 7.

### 6.2 Workshop opener

**AskQuestion** (one call, 2–3 questions):

1. **Which items enter the workshop now?** Multi-select from RA rows that touch skills
   (default: all P1 skill targets pre-selected in options).
2. **Edit scope**: Project skills only (`.cursor/skills/` in this repo) · Also org-wide
   template skills (if applicable) · Defer all to backlog
3. **Batching**: One question per skill file · Batch up to 2 related skills per question
   (e.g. 09-qa + 11-verify-impl)

### 6.3 Propose and confirm each patch

For **each skill file** in the workshop queue (respect batching choice):

1. **Read** the current `SKILL.md` (and `reference.md` if the patch belongs there).
2. **Draft** a minimal patch: exact section heading, 2–5 bullet summary of change, and a
   short before/after excerpt (not the full file) in the report draft.
3. **AskQuestion** — one call per file (or per batch of 2):

   | Question | Options (customize per patch) |
   |----------|-------------------------------|
   | Apply this patch to `{path}`? | **Apply as proposed** (recommended) · Apply with my edits (→ follow-up) · Defer to backlog only · Waive — no change needed |
   | If companion `reference.md` also changes | Same four options, or "N/A — SKILL only" |

   Rules:

   - First option = the agent's recommended patch.
   - Last option = `Let me explain / provide more context`.
   - If user picks **Apply with my edits**, ask one follow-up AskQuestion (or accept their
     free-text in "explain") then revise the patch and re-ask **Apply revised patch?**
   - **Defer** / **Waive**: update the RA row status; do not edit the file.

4. **Apply** only after explicit **Apply** (or **Apply revised patch**) for that file.
   Edit the minimum text needed; prefer additive checklists and AskQuestion reminders over
   rewrites. Update matching `reference.md` sections when the SKILL points there.

5. Record on the cycle: `skill_patches[]` with `path`, `status` (`applied` | `deferred` |
   `waived`), and one-line summary.

### 6.4 Cross-cutting skill themes

After per-file questions, if multiple patches hit the same theme (e.g. "resume pointer",
"AskQuestion batching"), one **AskQuestion**:

- Fold into a shared **pipeline/SKILL.md** or **considerations.md** edit?
  - Yes — add to pipeline · Yes — add to considerations §… · No — keep per-skill only
  - Let me explain / provide more context

Apply only if user selects a **Yes** option.

### 6.5 Workshop close gate

**AskQuestion**:

1. Commit skill edits now? (Yes — one commit if user requests · No · Already committed)
2. Open a PR for skill-only changes? (Yes / No / N/A)
3. Anything else to patch before the report? (List files / No / Explain)

Do **not** invoke 16-evolve or change product code in this phase.

---

## Phase 7 — Report and close

Write `docs/retrospectives/YYYY-MM-DD-{slug}.md` using the template in
[reference.md](reference.md) §Report template (include §Skill updates).

Update `workflow-state.yaml`:

- `stages.17-retrospective` status / timestamps / `last_report`
- Active `retrospective_cycles[]`: `status: completed`, `completed` date, artifact paths,
  `skill_patches[]`

Present a short summary to the user: top wins, top improvements, **skills updated**
(applied / deferred / waived counts), open actions count, report path.

---

## Relationship to pipeline skills

| Skill | Retrospective focus |
|-------|---------------------|
| 00–03 | Planning clarity, interview length, verify-plan signal-to-noise |
| 04–06 | Tech plan ↔ product plan, tooling ROI |
| 07–08 | Build throughput, TDD, execution-plan sync, PR cadence |
| 09–11 | QA/e2e/impl verification fit |
| 12–13 | Deploy gates, smoke value |
| 14–15 | Incident response, Modal ops loops |
| 16 | Evolve cycle overhead vs value |
| pipeline | Orchestration, gates, state file ergonomics |

Legacy skills (`doc-planner`, `build-executor`, etc.) are out of scope unless transcripts show they ran.

---

## Exit criteria

- [ ] User completed intake and (per depth) interview batches
- [ ] **Phase 6 skill workshop** completed (patches applied, or user explicitly skipped)
- [ ] Report written under `docs/retrospectives/` (includes skill update outcomes)
- [ ] Actions recorded (backlog and/or ADR and/or applied skill edits)
- [ ] `workflow-state.yaml` cycle marked `completed`

## Additional resources

- [reference.md](reference.md) — YAML schema, transcript mining, rubric, question banks, report template
