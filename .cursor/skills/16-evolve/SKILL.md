---
name: 16-evolve
description: >
  Orchestrator for feature and new_service sessions: adds product capabilities, scope/API/arch
  changes, breaking refactors, new dependencies, and multi-doc spec updates. Uses Cursor Plan
  mode as the default orchestrator for intake, Fn allocation, impact, and routing (Phase 0–1),
  then Agent mode to run routed child stages; 04/07 keep their own Plan→Agent batch loops.
  Requires active_session (00-context) with type feature or new_service. Every change must cite
  the project doc corpus. Use after 00-context for structured change on an existing app — not
  for surgical bugs (14-hotfix) or greenfield (pipeline).
---
<!--
Personal skill (project-agnostic). Paths like docs/ and workflow-state.yaml refer to the
*active workspace project*, not this skills directory. Fill {{PLACEHOLDER}} tokens from
the project's docs/CORPUS.md, feature-list, and deploy docs.
-->
# 16 — Evolve (Features & Large Changes)

Take an **existing** service from change request (including **multiple new features in one
cycle**) through updated specs, verified plans, implementation, and redeploy — reusing stages
**00–15** in **delta mode**.

**Protocol:** [protocol-card.md](../protocol-card.md) — corpus-first, Lean/Standard/Full, batched state.
**Detail:** [reference.md](reference.md) · [pipeline-preamble.md](../pipeline-preamble.md)
**Sessions:** [sessions-reference.md](../sessions-reference.md) — requires `feature` or `new_service` active_session.
**Routing:** `docs/skill-routing.md` (active project) — when to use evolve vs hotfix vs pipeline.
**Plan ↔ Agent:** [plan-mode-loop.md](../plan-mode-loop.md) — **Plan mode is the default
  orchestrator** for Phase 0–1 (scope → Fn → routing); Agent runs child stages; 04/07 Plan
  separately for execution batches.
**State agent:** project `.cursor/agents/workflow-state-manager.md` if present; else edit `workflow-state.yaml` per [workflow-state-reference.md](../workflow-state-reference.md) — mandatory read/update.

**Corpus:** Open `docs/CORPUS.md` (active project) rows for **touched features only** — not the
entire minimal corpus on every cycle. Domain/guides opt-in. See **Doc corpus citations** below
(and always-apply rule `doc-corpus-citations` — canonical:
`packages/agent-tooling/docs/conventions/doc-corpus-citations.md`).

**Connectivity:** Browser-facing changes → applicable [connectivity-gates.md](../connectivity-gates.md)
rows (at minimum 01/04 delta, 07, 12–13 with H4–H5 when UI ships).

**User is the source of truth.** Interview before editing specs or code. Every ambiguous,
uncertain, or contradictory finding uses **AskQuestion** — never guess.

## Doc corpus citations (mandatory)

Every **change**, **claim**, and **reference** in an evolve cycle must cite the doc corpus.

| Form | When |
|------|------|
| `[Corpus: <id>]` | `docs/CORPUS.md` exists and lists the row |
| `[path §section]` | No corpus id yet — still cite the standing doc |
| `[Corpus: WAIVED — <topic>; reason: …; decided: EV-NNN\|date]` | Coverage missing and user chose proceed |

**Missing coverage** (`CORPUS.md` absent, no row, or no authoritative section):

1. **Interview** via AskQuestion — recommend **add doc/row now**; always offer waive-and-proceed and re-scope.
2. **Proceed only** with an explicit **waiver citation** (table above) if the user chooses waive.
3. Log the waiver under `docs/decisions/evolve-decisions.md` §Cycle {id}.
4. **Do not** invent normative docs silently; draft only after the user picks add-now.

Pass citation obligations to child stages in evolve context (`corpus_cites` / waiver ids). Checkpoint
digests and impact/routing plans must list cites (or waivers) for each Fn and artifact edit.

## When to use

**Default for existing apps:** if the work adds capability, changes contracts, or touches multiple
specs — use **16-evolve**, not **14-hotfix** or ad-hoc **07-build**.

| Situation | Use |
|-----------|-----|
| **Add feature(s)** — "add X, Y, Z", new Fn, user-visible capability | **16-evolve** |
| **Large change** — multi-service, breaking API, major refactor | **16-evolve** |
| **General change** — scope, acceptance criteria, config surface | **16-evolve** (`cycle_type: general`) |
| Scope/API/arch change (may or may not add Fn) | **16-evolve** |
| Change scope, API, config, or acceptance criteria | **16-evolve** |
| Architectural or dependency change affecting multiple docs | **16-evolve** |
| Bug fix, regression, small patch on production | [14-hotfix](../14-hotfix/SKILL.md) |
| Greenfield service from scratch | [pipeline](../pipeline/SKILL.md) |
| Modal ops / health investigation only | [15-service-health](../15-service-health/SKILL.md) |
| Lessons learned / improve skills 00–19 | [17-retrospective](../17-retrospective/SKILL.md) |

**Stages 00–15** may receive a feature or large-change request during an **active session** with
type `feature` or `new_service` and an active evolve cycle. If no session exists, workflow-state-manager
**blocks** and recommends **00-context** — then **16-evolve** for net-new feature work.

## Prerequisites

Before starting an evolve cycle:

1. **`active_session`** exists with type `feature` or `new_service` (opened by **00-context**).
2. `routing-plan.md` lists required stages; user approved plan.
3. **`workflow-state.yaml` exists** with prior pipeline progress (ideally Phase D complete).
4. **Spec documents exist** under `docs/` (at minimum `feature-list.md`, `spec.md`, `test-plan.md`).
5. **Codebase exists** with a deployable artifact (or user confirms build-only evolve).

If `active_session` is null, route to [00-context](../00-context/SKILL.md) first.
If prerequisites are missing, ask via AskQuestion: run full [pipeline](../pipeline/SKILL.md) first,
or proceed with a reduced doc set (record waiver via workflow-state-manager).

## Plan mode as orchestrator (default)

**16-evolve uses Cursor Plan mode as the default orchestrator** for cycle design — not a rare
exception. Pattern:

| When | Mode | Purpose |
|------|------|---------|
| Phase 0–1 start / resume / re-route | **Plan** | Scope, Fn allocation, impact, Lean/Standard/Full routing, stage order |
| After Plan approval | **Agent** | Write evolve-plan-card, decisions, invoke child skills |
| Phase checkpoints (A/B/C/D) when replan needed | **Plan** | Adjust remaining routing / batch before continuing |
| Child **04** / **07** | Their own Plan→Agent | Execution plan + Build Plan Card / milestone batches |
| Child 01–03, 05–06, 08–15 | **Agent only** | Interviews, audits, tooling, verify, deploy |

### Evolve Plan Card

Write/update: `docs/sessions/{id}/evolve-plan-card.md` (alongside `routing-plan.md`).

```markdown
# Evolve Plan Card

> Cycle: EV-NNN | Session: SNNN-slug | Updated: ISO-8601

## Goal
[one sentence]

## Features
- F{n} — [title] — [Corpus: …]

## In / out of scope
- In: …
- Out: …

## Preset + routing
- Preset: Lean | Standard | Full
- Stages (ordered): …

## Next child stage
[NN-name] — delta context summary

## Risks / open decisions
- …
```

### Plan session prompt (evolve)

```
You are orchestrating an evolve cycle (16-evolve), not implementing code.

Read:
1. docs/sessions/{id}/session-brief.md + routing-plan.md
2. docs/sessions/{id}/evolve-plan-card.md (if present)
3. docs/CORPUS.md rows for touched Fn only (+ feature-list excerpts)

Produce:
1. Concrete Goal, In/Out of scope, Fn list with corpus cites
2. Recommended preset (Lean default on existing apps) + ordered stage list + skip rationale
3. Impacted docs / packages
4. Updated Evolve Plan Card body
5. First child stage to invoke after Agent switch

Do not edit product code or run 07 Task Loop. AskQuestion categories for ambiguities.
When approved → Agent mode continues 16-evolve Phase 1 write + Phase 2 child invocation.
```

**SwitchMode:** at Phase 0 start (and when re-routing mid-cycle), `SwitchMode` → `plan` with
the prompt above; after user approval → `agent` to persist the card and execute. Skip Plan
only when the user already approved a complete evolve-plan-card this turn.

---

## Interactive questions (required)

**Every user-facing question must use the AskQuestion tool** — same protocol as
[14-hotfix](../14-hotfix/SKILL.md) and [considerations.md](../considerations.md) §7.
If the AskQuestion tool is unavailable, use the **markdown numbered-options fallback** in
considerations §7 — same option rules; do not invent answers.

| Situation | Pattern |
|-----------|---------|
| Change / feature intake | 2–4 `questions` per batch; wait for all answers |
| Single gate or approval | One AskQuestion; first option = recommendation; last = `Let me explain / provide more context` |
| Impact / stage routing | Present recommended stage list; user confirms or adjusts |
| Ambiguity / contradiction | Category label in prompt: `[Decision]`, `[Ambiguity]`, `[Contradiction]`, `[Uncertainty]` |
| **Missing corpus coverage** | AskQuestion: add doc/row now (recommended) / waive-and-proceed / re-scope; record cite or waiver |
| Phase gate failure | List unmet criteria; **block** until resolved (no silent proceed) |
| Phase checkpoint (A–D, deploy) | Progress digest + AskQuestion before next phase |
| **UI in scope** | AskQuestion: offer a **non-deployed** (local) UI preview — see §UI preview |

Do not invent user answers. Prefer the AskQuestion tool; markdown lists are allowed only as the §7 fallback.

## UI preview (when the cycle includes UI)

Whenever the evolve cycle adds or changes a **browser UI** surface, offer a preview via
AskQuestion. Label it clearly as a **non-deployed / local instance** — not staging or
production (those remain 12/13 / H4–H5).

**When to ask (at least once per cycle with UI; re-ask after material UI changes):**

| Moment | Ask |
|--------|-----|
| Phase 0 intake (UI mentioned) | Optional early look at current local UI to ground scope |
| After Phase C (07/08 done) | Preview the built UI before Verify |
| When **11-verify-impl** is routed | Child skill runs its required preview AskQuestion; orchestrator ensures it was offered |
| Phase D / close checkpoint | If user skipped earlier, offer once more before deploy |

```
prompt: "UI preview (non-deployed): Preview the UI on a local / non-deployed instance?

  Not staging or production — local build only."

options:
  1. "Yes — open non-deployed preview"
  2. "No — continue without preview"
  3. "Remind me at 11-verify-impl"
  4. "Let me explain / provide more context"
```

Record accept/decline in the cycle checkpoint digest / evolve summary.

## Session management

Orchestrator for `feature` and `new_service` sessions. Requires `active_session` from **00-context**.
Writes summary to `docs/sessions/{id}/reports/evolve-summary.md`. Links `evolve_cycles[].session_id`.

Per [sessions-reference.md](../sessions-reference.md) §10.

## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).

**Primary state:** `evolve_cycles[]` (not under `stages`). Schema: [reference.md](reference.md).

On invocation:

1. Invoke **workflow-state-manager** `read_context` with `skill_id: 16-evolve` and `user_intent`.
2. Verify `active_session.type` is `feature` or `new_service`; else block → **00-context**.
3. Set `active_session.orchestrator: 16-evolve`; link `evolve_cycles[].session_id` to `active_session.id`.
4. If an evolve cycle is `in_progress`, report position; AskQuestion: resume / abandon / start new.
5. If none in progress, start **Phase 0 — Change / feature intake**.

After every substep: agent `update` on the active cycle (status, `current_stage`, artifacts, ADRs,
checkpoints, `git_history`).

### Mid-evolve interrupt → 14-hotfix

When **live** H3 (or other P0 production) fails during an `in_progress` evolve cycle (often
from 13-deploy-smoke or 15-service-health):

1. **AskQuestion** immediately (do not silently keep building the next milestone):
   - **Pause evolve and open 14-hotfix** (recommended)
   - Continue evolve with explicit waiver (record risk)
   - Investigate only (stay on 15) then re-AskQuestion
   - Let me explain / provide more context
2. If pause+14: set `evolve_cycles[].interrupted_by_hotfix: true`, `interrupt_reason`, and
   `hotfix_ref` (BUG/PR when known). Update `HANDOFF.md` with an **Interrupt** section
   (symptom, tip SHA, next = 14-hotfix).
3. Resume **16-evolve** only after hotfix close AskQuestion clears the interrupt flag
   (or the user explicitly abandons the cycle).

Deploy gates still require tip CI/CD green and honest `env_role` (`staging` vs `prod` when
dual DOKS envs exist — ADR-034; sole stack = live/prod only when staging is absent).

### Git branch and commit-as-you-go

Each evolve cycle works on `evolve/{cycle-id}-{slug}`. Record branch via agent on creation.
Commit deltas as you go; agent `update` appends `git_history.commits` with `stage: "16-evolve"`.
When complete, create a PR from the evolve branch to main.

## Delta / feature-addition mode

This skill **orchestrates** delta mode for all child stages. See [reference.md](reference.md)
for multi-Fn cycles, intake batches, checkpoints, and routing matrix.

## Workflow overview

```
Plan mode (orchestrator): intake → Fn → impact → routing
       │  approve → Agent writes evolve-plan-card + routing-plan
       ▼
┌──────────────────────────────────────────────────────────┐
│  A: Product     01* → 02* → 03*     (Agent)              │
├──────────────────────────────────────────────────────────┤
│  B: Technical   04* → 05* → 06*     (04: Plan+Agent)     │
├──────────────────────────────────────────────────────────┤
│  C: Build       07* ◄── 08*         (07: Plan+Agent)     │
├──────────────────────────────────────────────────────────┤
│  D: Verify      09* + 10* → 11* → 12* → 13*  (Agent)     │
└──────────────────────────────────────────────────────────┘
       │  (re-enter Plan at checkpoints if re-routing)
       ▼
Evolve summary + optional 14-hotfix / 15-service-health / 17-retrospective

* = invoke only if routing plan marks stage required
**Checkpoints:** mandatory digest + AskQuestion after phases A, B, C, D, and deploy
```

## Phase 0 — Change / feature intake

**Default:** enter **Plan mode** (see §Plan mode as orchestrator) before locking scope.
Use AskQuestion inside Plan or after Agent return for corpus gaps and the proceed gate.

Interview until the change is concrete enough for Fn allocation and impact analysis.

**For net-new features**, use intake batches in [reference.md](reference.md) §Feature intake batches.

**For general changes**, use:

| Batch | Topics |
|-------|--------|
| **Intent** | What to change, why now, success criteria |
| **Scope** | In/out of scope, breaking vs compatible, features affected |
| **Constraints** | Cost, latency, data, deploy target |

Surface **immediately** via AskQuestion anything ambiguous, uncertain, or contradictory.
Map each in-scope area to a corpus cite (or interview for missing docs / waiver) before the
proceed gate.

**Approval gate:** AskQuestion — "Proceed to allocate Fn(s) and impact analysis on this scope?"

Record approved scope in `docs/decisions/evolve-decisions.md` §Cycle {id} — Scope (via committed doc;
agent records cycle metadata). Include **Corpus cites / waivers** for the approved scope.
Update **Evolve Plan Card** Goal / In-Out / Features.

## Phase 1 — Fn allocation, impact analysis, routing

Stay in or re-enter **Plan mode** until preset + stage list are approved; then **Agent**
writes artifacts.

1. **Multi-feature default:** one cycle, multiple Fn — assign next Fn ids from `feature-list.md`.
2. List **docs to update** and **routing_plan** — [reference.md](reference.md) (Stage routing matrix).
3. **Presets** (AskQuestion; default **Lean** on existing apps — see protocol-card):

   | Preset | Required stages (typical) |
   |--------|---------------------------|
   | **Lean** | `00 → 16 → 01 → 02 → 10 → 13` |
   | **Standard** | Lean + `04 → 07 → 08 → 09 → 11 → 12` |
   | **Full** | Standard + `03` / `05` / `06` as needed |

4. Present preset + skip rationale via AskQuestion; user confirms or adjusts.
5. Persist `evolve-plan-card.md` + `routing-plan.md`; agent `update`: create evolve cycle with
   `feature_ids`, `checkpoints`, routing.
6. **Checkpoints:** mandatory after A/B/C/D/deploy on **Standard/Full**; on **Lean**, only on
   gate failure or user request (token/step savings — RET-001).
7. If checkpoint requires re-route: **Plan** again, then Agent continues Phase 2.

## Phase 2 — Execute routed stages (delta mode)

Invoke child skills **one at a time** (except 09+10 parallel). Pass evolve context:

```yaml
mode: evolve
evolve_cycle_id: EV-NNN
feature_ids: [F19, F20, F21]
scope: <approved Phase 0>
affected_artifacts: [paths]
delta_only: true
corpus_cites: ["[Corpus: id]", "[docs/… §…]"]
corpus_waivers: []   # explicit WAIVED cites if any
```

Child skills invoke **workflow-state-manager** themselves; 16-evolve verifies transition checks
between stages.

### Interactive checkpoint

**Standard/Full:** after phases **A, B, C, D**, and after **13-deploy-smoke**, present digest then
AskQuestion. Template: [reference.md](reference.md) §Checkpoint digest.

**Lean:** skip routine checkpoints; AskQuestion only on gate failure or user request.

For **11-verify-impl** (when routed), include **per–acceptance-criterion** status for each Fn.

### Phase gates (blocking)

| Gate | Criteria |
|------|----------|
| **A→B** | Fn in feature-list; delta specs; 02 pass; 03 if routed |
| **B→C** | Execution-plan tasks approved; 05 pass; 06 if routed |
| **C→D** | All Fn tasks done; latest 08 pass |
| **Deploy** | 09+10 pass; 11+12 user-approved; deploy approved; tip CI/CD green unless waived; `env_role` honest (`staging`/`prod` or sole stack = live/prod) |

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
4. **Checkpoints** — Standard/Full: after A–D and deploy; Lean: on gate failure only.
5. **Child skills own detail** — read child `SKILL.md` when invoking; not full `reference.md` unless needed.
6. **State via agent** — batch start+exit updates per protocol-card; never edit YAML directly.
7. **Do not `@`-attach** full skill bodies — name + routing-plan is enough.
8. **UI preview** — when UI is in scope, AskQuestion for a **non-deployed** preview; never
   present staging/production as that preview unless the user explicitly requests it.
9. **Corpus cites** — every change/reference includes `[Corpus: …]` / path+§ or an explicit
   `[Corpus: WAIVED — …]` after interview; never silent undocumented invent.
10. **Plan orchestrates, Agent executes** — Phase 0–1 (and re-routes) in Plan mode; persist
    Evolve Plan Card in Agent; do not implement feature code while still in Plan.

## Additional resources

- YAML schema, feature intake, checkpoints: [reference.md](reference.md)
- Full pipeline diagram: [pipeline/SKILL.md](../pipeline/SKILL.md)
