<!--
Shared pipeline ref. Paths like docs/ and workflow-state.yaml are relative to the repo root.
-->
# Cursor Plan mode ↔ Agent loop (04 / 07 / 16)

Use Cursor **Plan mode** to design and refine work, then **Agent mode** to execute.

**Where SwitchMode → Plan is allowed:**

| Skill | Role |
|-------|------|
| **16-evolve** | **Default orchestrator** — Phase 0–1 scope/Fn/routing (+ re-route at checkpoints) |
| **04-tech-plan** | Execution plan structure + Build Plan Card |
| **07-build** | Next milestone batch from Build Plan Card |

Stages **00–03, 05–06, 08–15** (except when invoked under 16’s Plan for routing only) stay in
Agent mode for their own work; they emit artifacts Plan can consume at 04/07/16.

## Modes

| Mode | Use for | Do not use for |
|------|---------|----------------|
| **Plan** | Evolve orchestration (16); tech/execution structure (04); milestone batch (07) | Commits, TDD Task Loop, tooling installs, audits as the primary mode |
| **Agent** | Specs, verify, tooling, tests, code, commits, PRs, child-stage execution | Skipping Plan when 16 is starting a new/re-routed cycle |

**SwitchMode:** from **16**, **04**, or **07** — `target_mode_id: "plan"` or `"agent"` + one-line
`explanation`. User must approve. If unavailable, user switches manually; same handoff content.

## Why this exists

- **16:** Plan designs the cycle (what stages, which Fn); Agent runs children one at a time.
- **04/07:** Full execution plans are rich but slow to re-parse; a short **Build Plan Card**
  lets Plan refine the next milestone; Agent runs the Task Loop.

## Artifact chain

| Stage | Role | Emit / check |
|-------|------|--------------|
| **16** Phase 0–1 | **Plan + Agent** | **Evolve Plan Card** + routing-plan; Plan = orchestrate |
| **00–03** | Producer (Agent) | Goal, non-goals, falsifiable specs |
| **04** | **Plan + Agent** | Execution plan + **Build Plan Card** |
| **05–06** | Gate / tooling (Agent) | Card parity; tooling ready |
| **07** | **Plan + Agent** | Plan = batch; Agent = Task Loop |

### Not Plan-default

| Skill | Plan mode? | Notes |
|-------|------------|-------|
| **01–03, 05–06** | **No** | Agent producers / gates / tooling |
| **08–13** | **No** | Verify / QA / E2E / deploy |
| **14-hotfix** | **No** | Surgical; slows MTTR |
| **15 / 17–19** | **No** | Ops, retro, PR review |
| **pipeline** | N/A | Greenfield orchestrator; still uses 04/07 Plan when those stages run |

## Build Plan Card (required from 04 onward)

Write or update at:

`docs/sessions/{session-id}/build-plan-card.md`

(If no session: `docs/build-plan-card.md` — prefer session path.)

```markdown
# Build Plan Card

> Session: SNNN-slug | Updated: ISO-8601 | Active: Phase N / M{N} / T{id}

## Goal (one sentence)
[What this session/milestone batch delivers]

## Constraints
- [Corpus cites, non-goals, allowlists, template id]
- [Branch base, PR cadence if user constrained]

## In scope (this batch)
- [ ] T{id} — [type] — [one-line] — Spec: [path §]
- [ ] …

## Out of scope (explicit)
- …

## Dependencies / blockers
- Data: [assets or none]
- Prior tasks: [ids]
- Tooling: [06 complete? yes/no]

## Acceptance for this batch
- [ ] Tests / checks named in execution plan
- [ ] Connectivity tiers if UI/API (H0c/H0i/…)

## Next Plan prompt
Paste into Plan mode (see below).
```

Keep the card **≤ ~80 lines**. Full detail stays in the execution plan artifact.

## Plan session prompt (template)

When entering Plan mode (especially before 07 or when refining 04’s execution plan):

```
You are refining the next build batch for this project.

Read:
1. docs/sessions/{id}/build-plan-card.md
2. Execution plan Current State + active milestone tasks only
3. Cited Spec Source rows for those tasks (not the whole docs tree)

Produce:
1. Ordered task list for this batch (respect Depends On)
2. Parallelizable groups
3. Risks / missing spec → AskQuestion categories
4. Updated Build Plan Card body (replace in-scope + acceptance)

Do not implement code. When the user approves, hand off to Agent mode with skill 07-build
and the approved batch task IDs.
```

## Stage obligations

### 00–03 (product) — Agent only

- **Do not** SwitchMode → Plan.
- Frame session goal so a later Build Plan Card can copy it verbatim.
- Prefer decisions that are **falsifiable and task-sized** (good Plan inputs at 04/07).
- At Phase A→B handoff: note “execution plan + Build Plan Card come from 04.”

### 04-tech-plan — Plan + Agent

- After drafting the execution plan, write the **Build Plan Card** for Phase 1 / M1.
- For large or ambiguous tech stacks: **SwitchMode → plan** to refine phases/milestones,
  then return to Agent to write files.
- Exit only when card ↔ Task Tracking for the first milestone match.

### 05-verify-tech — Agent only

- **Do not** SwitchMode → Plan.
- Audit: card tasks ⊆ execution plan; every in-scope task has Spec Source; TDD order holds.
- Fail Plan-readiness if the card is missing or drifts from Task Tracking.

### 06-tech-tooling — Agent only

- **Do not** SwitchMode → Plan.
- Ensure build-execution / TDD rules assume: Plan (batch at 07) → Agent (Task Loop).
- Do not invent a second task tracker; card is a view of the execution plan.

### 07-build — Plan + Agent

**On invocation and at each milestone start:**

1. Read Build Plan Card + execution plan Current State.
2. If the next batch is unclear, multi-milestone, or user asked to replan:
   **SwitchMode → plan** with the Plan session prompt; wait for approval.
3. **SwitchMode → agent** (or continue in Agent if already there).
4. Run the Task Loop **only** for approved batch task IDs.
5. After milestone PR: refresh the card for the next milestone; continue (PRs ≠ session end).

Do **not** re-enter Plan mode between every atomic task — only at batch/milestone
boundaries or when blocked by `[Ambiguity]` / `[Decision]`.

### 16-evolve — Plan orchestrator (default)

**Default:** SwitchMode → **plan** at Phase 0 start / resume / re-route. Produce **Evolve Plan
Card** (`docs/sessions/{id}/evolve-plan-card.md`) + routing. After approval → **agent** to
persist and invoke child stages one at a time.

- Re-enter Plan at phase checkpoints when routing must change.
- Do **not** implement feature code in Plan mode.
- When routing includes **04** / **07**, those skills own their Plan→Agent batch loops;
  16 does not Plan every child task.
- Skip Plan only when the user already approved a complete evolve-plan-card this turn.

See **16-evolve** §Plan mode as orchestrator for the evolve Plan session prompt.

## Anti-patterns

- Pasting the entire CORPUS into Plan mode
- Using Plan mode to write implementation commits
- Dual sources of truth (card tasks that are not in the execution / evolve plan)
- Ending after Plan approval without switching to Agent to persist + run children / 07
- Replacing 04–06 with an ad-hoc Plan chat that never writes the execution plan
- Using 16 Plan mode to micro-manage every atomic 07 task (that’s 07’s batch Plan)

## Quick checklist

- [ ] **16:** Evolve Plan Card + routing approved in Plan; Agent runs children
- [ ] **04/07:** Build Plan Card matches active milestone
- [ ] Plan prompt cites card(s) + Current State / corpus rows only
- [ ] 07 Plan only for batch refine; Agent runs TDD Task Loop
- [ ] Cards refreshed after milestones / re-routes
