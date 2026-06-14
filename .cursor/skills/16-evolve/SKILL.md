---
name: 16-evolve
description: >
  Evolves an existing deployed service: add one or more product features (multiple Fn in one
  cycle), scope/API/arch changes, or structured change requests. Interviews the user, routes
  selectively through product planning, technical planning, build, verification, and deploy
  with delta spec updates, mandatory phase checkpoints, and ADR logging. Use when adding
  features X Y Z to the current app, changing scope after deployment, or running a change
  request — not for surgical bugs (14-hotfix) or greenfield (pipeline). Any stage 00–17 may
  accept feature requests; this skill orchestrates multi-feature cycles when no cycle is active.
---

# 16 — Evolve

Take an **existing** service from change request (including **multiple new features in one
cycle**) through updated specs, verified plans, implementation, and redeploy — reusing stages
**00–15** in **delta mode**.

**Preamble:** [pipeline-preamble.md](../pipeline-preamble.md) — shared conventions for stages 00–17.
**Cross-cutting:** [considerations.md](../considerations.md), [connectivity-gates.md](../connectivity-gates.md).
**State agent:** [workflow-state-manager](../../agents/workflow-state-manager.md) — mandatory read/update.

**Connectivity:** Any evolve cycle that adds or changes **browser-facing** surfaces must re-run
the applicable rows in connectivity-gates §Pipeline stages 00–15 (at minimum: 01/04 spec delta,
07 implementation, 12–13 redeploy with H4–H5).

**User is the source of truth.** Interview before editing specs or code. Every ambiguous,
uncertain, or contradictory finding uses **AskQuestion** — never guess.

## When to use

| Situation | Use |
|-----------|-----|
| **Add feature(s)** — "add X, Y, Z", new Fn, user-visible capability | **16-evolve** |
| Scope/API/arch change (may or may not add Fn) | **16-evolve** |
| Change scope, API, config, or acceptance criteria | **16-evolve** |
| Architectural or dependency change affecting multiple docs | **16-evolve** |
| Bug fix, regression, small patch on production | [14-hotfix](../14-hotfix/SKILL.md) |
| Greenfield service from scratch | [pipeline](../pipeline/SKILL.md) |
| Modal ops / health investigation only | [15-service-health](../15-service-health/SKILL.md) |
| Lessons learned / improve skills 00–17 | [17-retrospective](../17-retrospective/SKILL.md) |

**Any stage 00–17** may receive a feature-addition request. If no active evolve cycle exists,
that stage's workflow-state-manager context will **block** and recommend **16-evolve** — start
here for net-new feature work on an existing app.

## Prerequisites

Before starting an evolve cycle:

1. **`workflow-state.yaml` exists** with prior pipeline progress (ideally Phase D complete).
2. **Spec documents exist** under `docs/` (at minimum `feature-list.md`, `spec.md`, `test-plan.md`).
3. **Codebase exists** with a deployable artifact (or user confirms build-only evolve).

If prerequisites are missing, ask via AskQuestion: run full [pipeline](../pipeline/SKILL.md) first,
or proceed with a reduced doc set (record waiver via workflow-state-manager).

## Interactive questions (required)

**Every user-facing question must use the AskQuestion tool** — same protocol as
[14-hotfix](../14-hotfix/SKILL.md) and [considerations.md](../considerations.md) §7.

| Situation | Pattern |
|-----------|---------|
| Change / feature intake | 2–4 `questions` per batch; wait for all answers |
| Single gate or approval | One AskQuestion; first option = recommendation; last = `Let me explain / provide more context` |
| Impact / stage routing | Present recommended stage list; user confirms or adjusts |
| Ambiguity / contradiction | Category label in prompt: `[Decision]`, `[Ambiguity]`, `[Contradiction]`, `[Uncertainty]` |
| Phase gate failure | List unmet criteria; **block** until resolved (no silent proceed) |
| Phase checkpoint (A–D, deploy) | Progress digest + AskQuestion before next phase |

Do not post interview prompts as markdown lists expecting inline replies.

## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).

**Primary state:** `evolve_cycles[]` (not under `stages`). Schema: [reference.md](reference.md).

On invocation:

1. Invoke **workflow-state-manager** `read_context` with `skill_id: 16-evolve` and `user_intent`.
2. If an evolve cycle is `in_progress`, report position; AskQuestion: resume / abandon / start new.
3. If none in progress, start **Phase 0 — Change / feature intake**.

After every substep: agent `update` on the active cycle (status, `current_stage`, artifacts, ADRs,
checkpoints, `git_history`).

### Git branch and commit-as-you-go

Each evolve cycle works on `evolve/{cycle-id}-{slug}`. Record branch via agent on creation.
Commit deltas as you go; agent `update` appends `git_history.commits` with `stage: "16-evolve"`.
When complete, create a PR from the evolve branch to main.

## Delta / feature-addition mode

This skill **orchestrates** delta mode for all child stages. See [reference.md](reference.md)
for multi-Fn cycles, intake batches, checkpoints, and routing matrix.

## Workflow overview

```
Change / feature intake (Phase 0)
       │
       ▼
Fn allocation (multi-Fn) + impact analysis → routing plan (user approves)
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  A: Product     01* → 02* → 03*                          │
├──────────────────────────────────────────────────────────┤
│  B: Technical   04* → 05* → 06*                          │
├──────────────────────────────────────────────────────────┤
│  C: Build       07* ◄── 08*                              │
├──────────────────────────────────────────────────────────┤
│  D: Verify      09* + 10* → 11* → 12* → 13*              │
└──────────────────────────────────────────────────────────┘
       │
       ▼
Evolve summary + optional 14-hotfix / 15-service-health / 17-retrospective

* = invoke only if routing plan marks stage required
**Checkpoints:** mandatory digest + AskQuestion after phases A, B, C, D, and deploy
```

## Phase 0 — Change / feature intake

Interview until the change is concrete enough for Fn allocation and impact analysis.

**For net-new features**, use intake batches in [reference.md](reference.md) §Feature intake batches.

**For general changes**, use:

| Batch | Topics |
|-------|--------|
| **Intent** | What to change, why now, success criteria |
| **Scope** | In/out of scope, breaking vs compatible, features affected |
| **Constraints** | Cost, latency, data, deploy target |

Surface **immediately** via AskQuestion anything ambiguous, uncertain, or contradictory.

**Approval gate:** AskQuestion — "Proceed to allocate Fn(s) and impact analysis on this scope?"

Record approved scope in `docs/evolve-decisions.md` §Cycle {id} — Scope (via committed doc;
agent records cycle metadata).

## Phase 1 — Fn allocation, impact analysis, routing

1. **Multi-feature default:** one cycle, multiple Fn — assign F19, F20, F21 from `feature-list.md`.
2. List **artifacts to update** and **routing_plan** — [reference.md](reference.md) §Stage routing matrix.
3. Default for net-new features: 01, 02, 03 (if guardrails), 04, 05, 06 (if stack), 07–13.
4. Present plan via AskQuestion; user confirms or adjusts stages.
5. Agent `update`: create evolve cycle with `feature_ids: [F19, F20, ...]`, `checkpoints`, routing.

## Phase 2 — Execute routed stages (delta mode)

Invoke child skills **one at a time** (except 09+10 parallel). Pass evolve context:

```yaml
mode: evolve
evolve_cycle_id: EV-NNN
feature_ids: [F19, F20, F21]
scope: <approved Phase 0>
affected_artifacts: [paths]
delta_only: true
```

Child skills invoke **workflow-state-manager** themselves; 16-evolve verifies transition checks
between stages.

### Interactive checkpoint

After phases **A, B, C, D**, and after **13-deploy-smoke**, present progress digest then AskQuestion
before continuing. Template: [reference.md](reference.md) §Checkpoint digest.

For **11-verify-impl**, include **per–acceptance-criterion** status for each Fn.

### Phase gates (blocking)

| Gate | Criteria |
|------|----------|
| **A→B** | Fn in feature-list; delta specs; 02 pass; 03 if routed |
| **B→C** | Execution-plan tasks approved; 05 pass; 06 if routed |
| **C→D** | All Fn tasks done; latest 08 pass |
| **Deploy** | 09+10 pass; 11+12 user-approved; deploy approved |

On failure: list unmet criteria → AskQuestion → fix in place per considerations §2.

## Phase 3 — Consistency verification

After **02-verify-plan** and **05-verify-tech**, run [reference.md](reference.md) §Consistency checklist.

## Phase 4 — Close evolve cycle

1. Write `docs/evolve-report-{cycle-id}.md`.
2. Agent `update`: cycle `status: completed`, timestamps, artifacts.
3. Append CHANGELOG / deploy-report if deployed.
4. AskQuestion: done / 15-service-health / 14-hotfix / 17-retrospective.

## Fix in place

Same as pipeline — never re-run entire phases for verification failures.

## Safe stopping points

- After Phase 0–1 (Fn + routing approved; no code)
- After Phase A (specs + 03 guardrails)
- After Phase B (execution plan approved)
- After Phase C (implemented, not deployed)
- After 11-verify-impl (verified; deploy optional)

## Output rules

1. **One routed stage at a time** (except 09+10).
2. **Delta by default** — full regeneration only with user approval.
3. **Multi-Fn in one cycle** unless user splits via AskQuestion.
4. **Checkpoints mandatory** between phases A–D and deploy.
5. **Child skills own detail** — 16-evolve orchestrates; read child SKILL.md when invoking.
6. **State via agent only** — never edit `workflow-state.yaml` directly.

## Additional resources

- YAML schema, feature intake, checkpoints: [reference.md](reference.md)
- Full pipeline diagram: [pipeline/SKILL.md](../pipeline/SKILL.md)
