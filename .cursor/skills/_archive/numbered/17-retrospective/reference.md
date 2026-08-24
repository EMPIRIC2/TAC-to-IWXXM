# 17-retrospective — Reference

Canonical state file: repo-root [`workflow-state.yaml`](../../workflow-state.yaml).
Shared rules: [workflow-state-reference.md](../workflow-state-reference.md).

## YAML schema

Append to `workflow-state.yaml`:

```yaml
stages:
  17-retrospective:
    status: in_progress          # pending | in_progress | completed | skipped
    started: "2026-05-17"
    completed: null
    last_report: docs/retrospectives/2026-05-17-milestone-c.md
    cycles_completed: 1

retrospective_cycles:
  - id: RET-001
    title: "Post Phase D retro"
    status: in_progress          # pending | in_progress | completed | cancelled
    started: "2026-05-17"
    completed: null
    scope:
      mode: full_pipeline        # full_pipeline | maintenance | evolve_hotfix | custom
      stages: []                 # populated when mode: custom
    time_window: since_last_retro  # all | since_last_retro | since_date | session_only
    since_date: null
    depth: standard              # deep | standard | light
    transcript_consent: range    # full | range | exclude_current | none
    current_phase: 1             # 0–7 per SKILL.md
    evidence_summary: |
      ...
    interview:
      stages_completed: []       # e.g. ["07-build", "10-e2e"]
      themes_confirmed: []
    skill_workshop: not_started  # not_started | in_progress | skipped | completed
    actions:
      - id: RA-001
        description: "Add 10-e2e journey checklist to report template"
        target: .cursor/skills/10-e2e/SKILL.md
        priority: P2
        status: open             # open | in_progress | done | deferred | waived
    skill_patches:
      - path: .cursor/skills/10-e2e/SKILL.md
        summary: "Add journey checklist before Modal remote calls"
        status: applied          # applied | deferred | waived
    artifacts:
      - path: docs/retrospectives/2026-05-17-milestone-c.md
        status: in_progress
      - path: docs/retrospective-actions.md
        status: pending
```

Mirror high-impact process issues to top-level `issue_log` with `stage: 17-retrospective`.

---

## Conversation logs

### Location

Cursor stores agent transcripts per workspace:

```
~/.cursor/projects/<workspace-slug>/agent-transcripts/<session-uuid>/<session-uuid>.jsonl
```

For this repo, the slug matches the path under `.cursor/projects/` (e.g.
`c-Users-bigme-OneDrive-Documents-GitHub-CogniChem-tool-rf-antibody`).

### JSONL record shape

Each line is JSON with `role` (`user` | `assistant`) and `message.content[]` blocks:

| Block type | Use for mining |
|------------|----------------|
| `text` | User queries (`<user_query>`), assistant summaries |
| `tool_use` | Skills read, files touched, commands run |

### Mining checklist (per session)

Extract and tally:

- [ ] First user query (intent)
- [ ] Skill paths read (`.cursor/skills/NN-*/SKILL.md`)
- [ ] Stage keywords (`07-build`, `14-hotfix`, `workflow-state`, `execution-plan`)
- [ ] AskQuestion / `[Decision]` / `[Ambiguity]` mentions
- [ ] Failure signals (`FAILED`, `blocked`, `error`, re-run, amend)
- [ ] Loop signals (same file read ≥3 times, repeated pytest)
- [ ] Outcome (deploy, PR, commit, gave up) if stated

### Session → stage mapping (heuristics)

| Signal | Likely stage |
|--------|----------------|
| `01-requirements`, feature-list interview | 01 |
| `02-verify-plan`, document-audit | 02 |
| `04-tech-plan`, execution-plan created | 04 |
| `07-build`, task T*.*, milestone branch | 07 |
| `10-e2e`, user journey, `tests/e2e` | 10 |
| `13-deploy-smoke`, ` platform deploy` | 13 |
| `14-hotfix`, incident | 14 |
| `15-service-health` | 15 |
| `16-evolve`, evolve_cycles | 16 |

Set confidence `low` unless two independent signals agree.

### Search commands (agent may run)

```bash
# List recent sessions (PowerShell)
Get-ChildItem agent-transcripts -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 20 Name, LastWriteTime

# Grep across jsonl (ripgrep)
rg -l "07-build|14-hotfix|16-evolve" agent-transcripts --glob "*.jsonl"
```

Do not load entire multi-MB sessions into context — sample or summarize per session.

---

## Per-stage rubric

Rate each in-scope skill **against evidence** (not ideals):

| Dimension | Question |
|-----------|----------|
| **Clarity** | Could a new session resume without confusion? |
| **Gating** | Right amount of user approval vs auto-progress? |
| **State** | `workflow-state.yaml` / per-skill state accurate and helpful? |
| **Artifacts** | Expected outputs exist and were used downstream? |
| **AskQuestion** | Questions timely, batched, options useful? |
| **Rework** | fix-in-place respected, or unnecessary phase re-runs? |
| **Cost/time** | GPU, deploy, or interview fatigue noted in transcripts? |

Hypothesis confidence: `high` = user + log agree; `medium` = log only; `low` = guess.

---

## Interview order

Default order when `scope.mode: full_pipeline`:

1. **Orchestration**: `pipeline/SKILL.md`
2. **Phase A**: 00 → 01 → 02 → 03
3. **Phase B**: 04 → 05 → 06
4. **Phase C**: 07 → 08
5. **Phase D**: 09 + 10 (pair) → 11 → 12 → 13
6. **Phase E**: 14 → 15
7. **Phase F**: 16
8. **Cross-cutting** themes

For `maintenance`: 14, 15, pipeline (Phase E section only).

For `evolve_hotfix`: 16, 14, pipeline (handoff sections).

---

## Question banks (examples for AskQuestion options)

### Went well (per stage)

- Clear step-by-step workflow
- Good use of AskQuestion / decisions captured
- Artifacts matched what I needed
- Resume from state worked
- Parallel agents saved time
- Nothing notable — stage was fine

### Improve (per stage)

- Too many / too few questions
- Skill too long or too vague
- State file out of sync with reality
- Re-ran work unnecessarily
- Missing checklist or template
- Tooling (hooks/lint) noisy or insufficient
- None — stage was fine

### Brainstorm option types

- Patch `SKILL.md` (specify section)
- Patch `.cursor/rules/*.mdc`
- Add hook in `.cursor/hooks/`
- ADR for process decision
- Append `docs/retrospective-actions.md` only
- Open **16-evolve** change request
- Open **14-hotfix** pattern / incident template tweak

---

## Skill update workshop (Phase 6 question bank)

Use these as **AskQuestion** option seeds; customize labels with the concrete patch summary.

### Workshop opener

| Prompt | Example options |
|--------|-----------------|
| Which RA items enter the workshop? | Multi-select: each `RA-00N` that targets a skill (pre-check P1) |
| Edit scope | Project `.cursor/skills/` only · Org template skills too · Defer all |
| Batching | One question per file · Up to 2 related skills per question |

### Per skill file (required)

| Prompt | Options |
|--------|---------|
| Apply patch to `{path}` §{section}? | **Apply as proposed** · Apply with my edits · Defer to backlog · Waive · Let me explain |
| Also update `{reference.md}`? | Apply companion patch · SKILL only · Defer · Waive · Let me explain |

**Apply with my edits** flow: capture user intent → show revised excerpt → re-ask **Apply revised patch?**

### Cross-cutting fold-in

| Prompt | Options |
|--------|---------|
| Same theme in N skills — centralize? | Add to `pipeline/SKILL.md` · Add to `considerations.md` §N · Keep per-skill only · Let me explain |

### Workshop close gate

| Prompt | Options |
|--------|---------|
| Commit skill edits now? | Yes (user will ask for commit) · No · Already committed |
| PR for skill-only changes? | Yes · No · N/A |
| More patches before report? | No · Yes — list files · Let me explain |

### Patch proposal format (show in prompt text, not markdown lists to user)

```
File: .cursor/skills/07-build/SKILL.md
Section: ## Resume from state
Change: Add explicit pointer to workflow-state.yaml `stages.07-build.current_task`
Before: (1 line excerpt)
After: (1 line excerpt)
```

---

## Report template

```markdown
# Retrospective — {title}

**Cycle:** RET-{NNN}  
**Date:** YYYY-MM-DD  
**Scope:** {scope summary}  
**Depth:** {deep|standard|light}

## Executive summary

{2–4 sentences}

## What went well

- ...

## What to improve

- ...

## Evidence (summary)

| Source | Notes |
|--------|-------|
| workflow-state.yaml | ... |
| Transcripts | N sessions, date range |
| hotfix / deploy | ... |

## Interview responses

{User-confirmed themes only — not unvalidated hypotheses}

## Brainstorm outcomes

| Theme | Chosen direction |
|-------|------------------|
| ... | ... |

## Actions

| ID | Action | Priority | Status |
|----|--------|----------|--------|
| RA-001 | ... | P1 | open |

## Skill updates (Phase 6)

| Path | Summary | Outcome |
|------|---------|---------|
| `.cursor/skills/.../SKILL.md` | ... | applied / deferred / waived |

{If workshop skipped: note reason. If applied, optional commit/PR link.}

## Sessions cited

- [short title](session-uuid)
```

---

## `docs/retrospective-actions.md` backlog row

```markdown
| RA-001 | RET-001 | Patch 10-e2e journey checklist | P2 | open | 2026-05-17 |
```

Columns: ID | Cycle | Description | Priority | Status | Added
