---
name: pipeline
description: >
  End-to-end orchestration skill that takes a project from requirements interview through
  deployment. Combines stages 00-context through 19-address-pr-review into a single resumable
  pipeline with YAML state tracking, phase gates, transition checks, and cross-stage
  consistency verification, and connectivity gates (CORS, VITE_*, integration, H4–H5) across
  stages 00–15. Use when the user wants to build this project end-to-end,
  run the full pipeline, go end-to-end, deploy from scratch, or asks "build this".
  Post-deployment surgical edits use 14-hotfix; production health checks use
  15-service-health without re-running the pipeline. Add features to an existing app
  (including multiple Fn in one cycle) via 16-evolve or any stage 00–18 in delta mode.
  Process improvement uses 17-retrospective (reviews logs and skills 00–17).
  Pull request review uses 18-pr-review (posts to GitHub; never merges). Remediation uses
  19-address-pr-review (fixes findings; never merges).
---

# Pipeline

Build a deployable service from product requirements through deployment, end-to-end.

## Purpose

Take a project from initial concept through deployed, verified service. Every step —
from understanding requirements to deploying code — is structured, audited, and
user-approved. The user is the source of truth at every stage.

**Stage conventions (00–17):** [pipeline-preamble.md](../pipeline-preamble.md).
**State agent:** [workflow-state-manager](../../agents/workflow-state-manager.md) — mandatory read/update.

Shared policy (feedback loops, changelogs, performance testing, spec vs code root cause):
[considerations.md](../considerations.md).

**Connectivity & wiring (all stages 00–15):** [connectivity-gates.md](../connectivity-gates.md) —
CORS, `VITE_*`, integration tests (H0i), and live browser gates (H4–H5). Each stage skill
includes a §Connectivity section; phase gates below enforce the cumulative checklist.

## Pipeline Overview

```
╔═══ PHASE A: PRODUCT PLANNING ════════════════════════════════╗
║  00-context ──► 01-requirements ──► 02-verify-plan ──► 03-   ║
║  (optional)     (interview)         (risk-based)       plan- ║
║                                                        tooling║
╚══════════════════════════════════════════════════════════════╝
          │ Gate A→B
          ▼
╔═══ PHASE B: TECHNICAL PLANNING ══════════════════════════════╗
║  04-tech-plan ──► 05-verify-tech ──► 06-tech-tooling         ║
╚══════════════════════════════════════════════════════════════╝
          │ Gate B→C
          ▼
╔═══ PHASE C: BUILD ═══════════════════════════════════════════╗
║  07-build ◄── 08-verify-build (at milestone boundaries)      ║
╚══════════════════════════════════════════════════════════════╝
          │ Gate C→D
          ▼
╔═══ PHASE D: VERIFICATION & DEPLOY ══════════════════════════╗
║  09-qa ──┐                                                    ║
║          ├──► 11-verify-impl ──► 12-verify-deploy ──► 13-    ║
║  10-e2e ─┘                                             deploy║
║  (parallel)                                            -smoke║
╚══════════════════════════════════════════════════════════════╝
          │ Post-deploy
          ▼
╔═══ PHASE E: MAINTENANCE & OPS ═════════════════════════════╗
║  14-hotfix (on-demand — surgical patches)                   ║
║  15-service-health (on-demand — API + DB + RAG smokes)        ║
╚════════════════════════════════════════════════════════════╝
          │ Structured change / new feature
          ▼
╔═══ PHASE F: EVOLVE & RETROSPECTIVE (on-demand, repeatable) ══╗
║  16-evolve — features (multi-Fn), scope/API/arch, delta 00–15 ║
║  17-retrospective — process improvement from logs + state     ║
╚══════════════════════════════════════════════════════════════╝
          │ PR review (on-demand)
          ▼
╔═══ PHASE G: REVIEW & REMEDIATION (on-demand) ═══════════════╗
║  18-pr-review — structured PR review posted to GitHub         ║
║  19-address-pr-review — fix review findings on PR branch      ║
╚══════════════════════════════════════════════════════════════╝
```

## Quick start

- **Which skill should I use?** → [docs/skill-routing.md](../../docs/skill-routing.md)
- **Post-deploy testing tiers** → [ADR-004](../../docs/adr/ADR-004.md)
- **Add feature(s) to existing app** → [16-evolve](../16-evolve/SKILL.md)
- **Broader scope/API/arch change** → [16-evolve](../16-evolve/SKILL.md)
- **Process retrospective** → [17-retrospective](../17-retrospective/SKILL.md)
- **Review a pull request** → [18-pr-review](../18-pr-review/SKILL.md)
- **Address PR review feedback** → [19-address-pr-review](../19-address-pr-review/SKILL.md)

## Inputs

Collect from the user at start (check conversation context or ask):

| Input | Required | Default | Notes |
|-------|----------|---------|-------|
| **Project name** | Yes | — | Name for the project |
| **Project description** | Yes | — | Brief description |
| **Existing repo** | No | — | URL or local path if code exists |
| **Research paper** | No | — | Path if academic paper exists |
| **Existing docs** | No | — | Paths to prior documentation |
| **Output directory** | No | `docs/` | Where to write artifacts |
| **Deploy target** | No | — | Modal, Render, AWS, etc. |
| **Template** | No | auto-detect | Template from [template-registry.md](../template-registry.md). Auto-detected during 00-context or 01-requirements. User can override. |

## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).

The pipeline orchestrator invokes **workflow-state-manager** at start and after each stage
transition. Child stages also invoke the agent — **only workflow-state-manager writes**
`workflow-state.yaml`.

Schema reference: [workflow-state-reference.md](../workflow-state-reference.md).

### Centralized state

Single source of truth for pipeline position (repo root). The orchestrator passes
`user_intent` (including feature-addition requests) to the agent on every stage handoff.

### On invocation

1. Check if `workflow-state.yaml` exists.
2. **If it exists**: Read it, determine pipeline position, and report:

```
Pipeline State:
  Template: [utility / job / none] — cognichem-[service_name]

  Phase A: Product Planning
    00-context ────────── skipped
    01-requirements ───── completed
    02-verify-plan ────── completed
    03-plan-tooling ───── completed

  Phase B: Technical Planning
    04-tech-plan ──────── completed
    05-verify-tech ────── in_progress (statement 5/12)
    06-tech-tooling ───── pending

  Phase C: Build
    07-build ──────────── pending
    08-verify-build ───── pending

  Phase D: Verification & Deploy
    09-qa ─────────────── pending
    10-e2e ────────────── pending
    11-verify-impl ────── pending
    12-verify-deploy ──── pending
    13-deploy-smoke ───── pending

  Phase E: Maintenance & Ops
    14-hotfix ──────────── [N] applied
    15-service-health ────── [last overall / none]

  Resume from: 05-verify-tech
```

   Ask via AskQuestion:
   - "Resume from 05-verify-tech"
   - "Restart from a specific stage (I'll choose)"
   - "Start over from scratch"
   - "Let me explain / provide more context"

3. **If it does not exist**: Start fresh. Create the state file.

### State updates

After each stage completes (or fails), immediately:

1. **Commit all stage artifacts** to the appropriate branch (see `workflow-state-reference.md`
   §Git history for branch type). Never leave uncommitted work between stages.
2. Update `workflow-state.yaml`:
   - Set stage status
   - Update timestamps
   - Record artifacts produced
   - Log any issues in the issue_log
   - Append commit(s) to `git_history.commits` with stage attribution
   - Update `git_history.current_branch`
3. Commit the workflow-state update itself (can be the same commit as artifacts).

**Commit-as-you-go is mandatory.** If a session ends unexpectedly, all progress since the
last commit is lost. Commit early and often — at least once per substep completion.

## Workflow

### Stage 00 — Context Gathering (Optional)

**Check**: Does the user have existing artifacts (repo, paper, docs)?
- If yes: invoke [00-context](../00-context/SKILL.md)
  - Includes Phase 1C: Template Classification (see [template-registry.md](../template-registry.md))
- If no: skip, set status to `skipped`

**Template selection**: If 00-context runs, it classifies the project and selects a
template during Phase 1C. If 00-context is skipped, template selection defers to
01-requirements Phase 0.

### Stage 01 — Product Requirements Interview

**Check**: Does `workflow-state.yaml` show 01-requirements as `completed`?
- If yes: ask reuse or regenerate
- If no: invoke [01-requirements](../01-requirements/SKILL.md)
  - If no template selected yet, 01-requirements runs template selection first (Phase 0)

### Stage 02 — Verify Product Plan

**Check**: 02-verify-plan status?
- If `completed`: skip
- If `in_progress`: invoke to resume
- If `pending`: invoke fresh

### Stage 03 — Plan Tooling (BLOCKING GATE)

**Check**: 03-plan-tooling status?
- If `completed`: verify tooling still exists on disk
- If not: invoke [03-plan-tooling](../03-plan-tooling/SKILL.md)

**Phase A→B Gate Check**:
- [ ] All spec documents generated (01-requirements), including `docs/user-journeys.md`
- [ ] **test-plan.md** defines connectivity tiers (H0c, H0i, H4, H5) per connectivity-gates
- [ ] **deployment-integration.md** documents `VITE_*` + `VECINITA_CORS_ORIGINS` (or BFF ADR)
- [ ] Product audit complete (02-verify-plan)
- [ ] Plan tooling installed (03-plan-tooling)

If gate fails, report unmet criteria and ask user how to proceed.

### Stage 04 — Technical Planning Interview

**Check**: 04-tech-plan status?
- If `completed`: ask reuse or regenerate
- If not: invoke [04-tech-plan](../04-tech-plan/SKILL.md)

### Stage 05 — Verify Technical Plan

**Check**: 05-verify-tech status?
- If `completed`: skip
- Otherwise: invoke to start or resume

### Stage 06 — Technical Tooling (BLOCKING GATE)

**Check**: 06-tech-tooling status?
- If `completed`: verify tooling on disk
- If not: invoke [06-tech-tooling](../06-tech-tooling/SKILL.md)

**Phase B→C Gate Check**:
- [ ] Execution plan approved (04-tech-plan + 05-verify-tech)
- [ ] Execution plan includes connectivity tasks (CORS middleware, integration tests, verify script)
- [ ] Consistency check passed (05-verify-tech)
- [ ] Technical tooling installed (06-tech-tooling)
- [ ] CI will run `test_cors_policy.py` + `tests/integration` (06-tech-tooling)

### Stage 07 — Technical Execution (Build)

**Check**: Read `docs/execution-plan.md` §Current State
- If all tasks `completed`: skip
- If in progress: invoke to resume
- If not started: invoke [07-build](../07-build/SKILL.md)

### Stage 08 — Verify Build

Not invoked separately — called by 07-build at milestone/phase boundaries.

### Stages 09+10 — QA and E2E (PARALLEL)

**Phase C→D Gate Check** (before launching):
- [ ] All execution plan tasks completed
- [ ] All milestone PRs created
- [ ] Latest verify-build passes
- [ ] **H0c + H0i green** (`test_cors_policy.py`, `tests/integration`)

Launch both in parallel:
- [09-qa](../09-qa/SKILL.md) — full codebase QA
- [10-e2e](../10-e2e/SKILL.md) — E2E behavior verification

Wait for both to complete before proceeding.

### Stage 11 — Verify Implementation (BLOCKING)

**Requires**: 09-qa + 10-e2e both `completed`

Invoke [11-verify-impl](../11-verify-impl/SKILL.md) with results from both stages.

### Stage 12 — Verify Deploy Strategy (BLOCKING)

Invoke [12-verify-deploy](../12-verify-deploy/SKILL.md).

### Stage 13 — Deploy & Smoke Check (BLOCKING)

**Deploy Gate Check**:
- [ ] QA passed (09-qa)
- [ ] E2E passed (10-e2e)
- [ ] Implementation verified (11-verify-impl) — UI features have connectivity plan or waiver
- [ ] Deploy strategy verified (12-verify-deploy) — H0c/H4/H5 checklist rows

Invoke [13-deploy-smoke](../13-deploy-smoke/SKILL.md). Post-deploy must pass **H4–H5**
browser connectivity ([connectivity-gates.md](../connectivity-gates.md)), not only H1–H3 API smokes.

### Stage 14 — Hotfix (On-Demand, Repeatable)

Not part of the linear pipeline. Available any time after Phase C (code exists).

**Check**: User reports a bug, patch request, dependency bump, or config fix.
- Invoke [14-hotfix](../14-hotfix/SKILL.md)
- Can be invoked multiple times — each invocation is a separate hotfix
- Does not reset or re-run any pipeline phase
- Test-driven: user failure → failing repro test (red) → interactive confirm → fix → green;
  verification plan, layered checks, optional 15-service-health follow-up
- Records all fixes in `docs/hotfix-log.md`

### Stage 15 — Service Health (On-Demand, Repeatable)

Not part of the linear pipeline. Best after 13-deploy-smoke when a deployed environment exists.

**Check**: User wants production health review, retrieval quality issues, DB/migration problems,
or evidence before a hotfix.
- Invoke [15-service-health](../15-service-health/SKILL.md)
- Interview → infra (health, migrations, secrets) + behavior (H3 + **H4–H5** on UI issues)
- Test-driven failures; 14-hotfix handoff with repro test
- Records in `docs/service-health-reports/` and `docs/service-health-state.md`

### Stage 16 — Evolve (On-Demand, Repeatable)

Primary entry for **adding features** to an existing app (including **multiple Fn in one
cycle**), scope/API/arch changes, and structured change requests. Any stage 00–17 may accept
feature requests; when no evolve cycle is active, **workflow-state-manager** blocks and
recommends 16-evolve.

**Check**: User says "add features X, Y, Z", "new capability", scope/API/arch change, or
structured change request.
- Invoke [16-evolve](../16-evolve/SKILL.md)
- Feature intake → allocate Fn(s) → routing plan → re-invoke 00–15 **selectively** in delta mode
- Mandatory phase checkpoints (A–D, deploy); 11-verify-impl signs off each Fn
- Does not replace 14-hotfix (bugs) or greenfield [pipeline](SKILL.md)

### Stage 17 — Retrospective (On-Demand, Repeatable)

Not part of the linear greenfield pipeline. Use after any meaningful stretch of work
(milestone, phase gate, hotfix cluster, evolve cycle, or deploy) when the user wants to
**improve the process** — not change product behavior.

**Check**: User asks for retrospective, lessons learned, pipeline tuning, or skill review.
- Invoke [17-retrospective](../17-retrospective/SKILL.md)
- Mines agent conversation logs (with consent), `workflow-state.yaml`, and `docs/`
- Compares evidence to skills **00–17**; interviews user via AskQuestion (went well / improve)
- Brainstorms solutions; ends with AskQuestion-driven skill patches (Phase 6 workshop)
- Routes remaining actions to backlog, ADR, or commit/PR if user requests
- Does **not** replace 14-hotfix, 16-evolve, or re-running build phases by default

## Transition Checks

Between each stage, verify:

1. **Artifact verification**: Previous stage produced its expected artifacts.
   If missing, surface as `[Ambiguity]`.

2. **Cross-stage consistency**: Downstream inputs match upstream outputs:
   - 01-requirements specs are consistent with 00-context brief
   - 02-verify-plan corrections are reflected in spec documents
   - 03-plan-tooling rules reference current spec sections
   - 04-tech-plan execution plan references existing spec files
   - 05-verify-tech consistency results align with current specs
   - 06-tech-tooling hooks match execution plan tech stack
   - 07-build task statuses match actual codebase state
   - 09-qa/10-e2e results reflect current codebase (not stale)

3. **Scope drift**: If on-the-fly decisions in an earlier stage affect later stages,
   surface as `[Contradiction]`.

4. **Staleness**: If an upstream artifact was modified after a downstream stage consumed
   it, warn: "spec.md was updated after 04-tech-plan ran. The execution plan may be
   out of date."

5. **Template drift** (if template selected): Verify that `workflow-state.yaml` §template
   has not been contradicted by stage outputs. If a stage produced artifacts that diverge
   from the template pattern without an ADR, surface as `[Template Drift]`.

Log all transition issues via **workflow-state-manager** `update` → `issue_log`.

## Feature addition routing

When the user requests new features on an **existing** application:

| Entry point | Behavior |
|-------------|----------|
| **16-evolve** | Recommended orchestrator — multi-Fn cycle, checkpoints, routing |
| **Any stage 00–17** | Agent `read_context` detects feature intent; runs delta mode if cycle active, else blocks → 16-evolve |
| **pipeline** | Greenfield only; if specs exist, suggest 16-evolve instead |

See [pipeline-preamble.md](../pipeline-preamble.md) §Feature addition.

## Feedback Loop: Fix in Place

When verification (stages 08-11) reveals issues:

| Issue Type | Fix |
|-----------|-----|
| Code bug | Targeted code patch in 07-build branch |
| Spec mismatch | Surgical spec document update |
| Missing feature | Add task to execution plan, implement |
| Tooling gap | Patch the specific hook or rule |

**Never re-run entire phases.** All fixes are targeted patches.

## Safe Stopping Points

Every stage boundary is safe to stop. Natural pause points:
- **After 03-plan-tooling** — Product planning complete
- **After 06-tech-tooling** — All planning complete
- **After 07-build milestone boundaries** — Partial build saved
- **After 11-verify-impl** — Build and verification complete
- **After 13-deploy-smoke** — Done (deploy complete)
- **14-hotfix** — On-demand surgical patches
- **15-service-health** — On-demand Modal ops investigation
- **16-evolve** — On-demand features (multi-Fn), scope/API/arch, delta 00–15
- **17-retrospective** — On-demand process improvement (any time after work has run)

## Summary

When all stages complete (or user stops):

```
Pipeline Complete.

  Template: [utility / job / none] — cognichem-[service_name]
  Source:   template-modal-[type] (selected at [00-context / 01-requirements])

  Phase A: Product Planning
    00-context ────────── [status]
    01-requirements ───── completed ([N] documents)
    02-verify-plan ────── completed ([N] statements, [N] auto-approved)
    03-plan-tooling ───── completed ([N] rules, [N] hooks, [N] skills)

  Phase B: Technical Planning
    04-tech-plan ──────── completed ([N] phases, [N] milestones, [N] tasks)
    05-verify-tech ────── completed ([N] statements, consistency check passed)
    06-tech-tooling ───── completed ([N] rules, [N] hooks, [N] configs)

  Phase C: Build
    07-build ──────────── completed ([N] tasks, [N] PRs)
    08-verify-build ───── completed ([N] runs, [N] auto-fixes)

  Phase D: Verification & Deploy
    09-qa ─────────────── completed (all checks pass)
    10-e2e ────────────── completed ([N] journeys passing)
    11-verify-impl ────── completed ([N] features approved)
    12-verify-deploy ──── completed (checklist approved)
    13-deploy-smoke ───── completed ([URL])

  Phase E: Maintenance & Ops
    14-hotfix ──────────── [N] applied (docs/hotfix-log.md)
    15-service-health ────── [last: healthy | degraded | none]

  Phase F: Evolve
    16-evolve ──────────── [N] cycles (last: EV-00N — completed | in_progress | none)

  Phase G: Retrospective
    17-retrospective ───── [N] cycles (last: RET-00N — completed | in_progress | none)

  Deployment: [URL]
  Total issues surfaced: [N]
  Total artifacts: [N] documents in docs/
  State file: workflow-state.yaml
```

## Output Rules

1. **One stage at a time**: Complete each stage before starting the next (except 09+10 parallel).
2. **Skip completed stages**: Never re-run without user request.
3. **Transition checks mandatory**: Verify artifacts and consistency between stages.
4. **User controls re-runs**: Always ask before re-running a completed stage.
5. **State persists**: YAML state survives sessions. Any session can resume.
6. **Cross-stage issues**: Issues spanning multiple skills are the pipeline's responsibility.
7. **Fix in place**: Never re-run entire phases. Targeted patches only.
8. **Gates are blocking**: Phase gates must pass before the next phase begins.
