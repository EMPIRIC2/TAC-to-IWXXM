# Sessions reference (pipeline 00–19)

**Session-first work model.** Every bounded unit of work runs inside a **session** with an
explicit routing plan. Project standing docs remain long-lived truth; session artifacts live
under `docs/sessions/{session-id}/`.

**Preamble integration:** [pipeline-preamble.md](pipeline-preamble.md) §Sessions.
**State schema:** [workflow-state-reference.md](workflow-state-reference.md) §Sessions.
**Agent protocol:** [workflow-state-agent-protocol.md](workflow-state-agent-protocol.md).

---

## 1. Two corpora

| Corpus | Location | Examples |
|--------|----------|----------|
| **Project (standing)** | `docs/` corpus | See [`docs/CORPUS.md`](../../docs/CORPUS.md) — `feature-list`, `spec`, `tech-spec`, `api-contract`, `test-plan`, `deploy`, …; decisions under `docs/decisions/`; ADRs under `docs/adr/` |
| **Session (ephemeral)** | `docs/sessions/{session-id}/` | `session-brief.md`, `routing-plan.md`, `reports/*`, `checkpoints/*` |

Scoped context briefs (`docs/context/<slug>.md`) remain valid; link them from
`session-brief.md` when used.

---

## 2. Session types

| Type | Orchestrator | Typical routing plan |
|------|--------------|----------------------|
| `greenfield` | [pipeline](pipeline/SKILL.md) | 00→01→…→13 (full phases A–D) |
| `feature` | [16-evolve](16-evolve/SKILL.md) | Subset of 01–13 in delta mode |
| `new_service` | [16-evolve](16-evolve/SKILL.md) or direct stages | 00, 01*, 04, 07, 12–13 |
| `hotfix` | [14-hotfix](14-hotfix/SKILL.md) | 14 (+ 15 if prod verify) |
| `integration` | Direct stages | 00 (scoped), 10, 11, 15 |
| `ops` | [15-service-health](15-service-health/SKILL.md) | 15 |
| `process` | 17 / 18 / 19 | Single review or retro stage |

`*` = only when standing docs need delta.

---

## 3. Session ID and folder layout

**Format:** `S{NNN}-{slug}` — sequential counter from `workflow-state.yaml` §`session_counter`
(e.g. `S001-greenfield`, `S042-live-e2e`).

```
docs/sessions/
  README.md                         # index table
  S042-live-e2e/
    session-brief.md                # intent, type, scope, branch, links
    routing-plan.md                 # approved stage list + skip rationale
    reports/                        # stage outputs for this session
      qa-report.md
      e2e-report.md
      verification-report.md
      deploy-smoke.md
      service-health.md
    checkpoints/                    # optional phase gate digests
```

**Branch naming:** `feat/{session-id}` or type-specific (`fix/`, `evolve/`) — record in
`session-brief.md` and `active_session.branch`.

---

## 4. Session lifecycle

### Open (00-context recommended)

1. User provides intent (prompt, feature, bug, integration goal).
2. **00-context** (or resume) classifies **session type** and magnitude.
3. Allocate next `S{NNN}`; create folder + `session-brief.md`.
4. Propose `routing-plan.md` (explicit stages + skip rationale).
5. **AskQuestion** — user approves routing plan.
6. Agent sets `active_session`; create branch if code changes expected.

**Entry without 00:** Allowed when recent context exists (project brief or scoped brief covers
work). Stage checks `active_session`; if missing, block and recommend **00-context**.

### During

- Every stage reads `active_session` via workflow-state-manager `read_context`.
- Stage must appear in `active_session.routing_plan` (or orchestrator adds it).
- Session reports → `docs/sessions/{id}/reports/` (not project root).
- Standing doc updates → delta on session branch + §Session changelog footer (below).
- `project.stages.*` updated on stage **completion** (historical baseline).
- `active_session.current_stage` tracks session position.

### Close

When **all routing-plan stages** are `completed` (or `skipped` with rationale):

1. Final checkpoint **AskQuestion** — "Close session SNNN?"
2. Archive to `sessions[]`; set `active_session: null`.
3. Append row to `docs/sessions/README.md`.
4. For `feature` / `new_service`: link `evolve_cycles[].session_id` if evolve ran.

---

## 5. `session-brief.md` template

```markdown
---
session_id: S042-live-e2e
type: integration
status: in_progress
branch: feat/S042-live-e2e
started_at: YYYY-MM-DD
intent: "One sentence user goal"
orchestrator: null | pipeline | 16-evolve | 14-hotfix
evolve_cycle_id: null
context_briefs: []
standing_docs_touched: []
---

# Session S042 — live-e2e

## Intent
...

## Scope
In / out of scope bullets.

## Routing plan
See [routing-plan.md](./routing-plan.md).

## Links
- Standing: [test-plan.md](../../test-plan.md), [deploy.md](../../deploy.md)
```

---

## 6. `routing-plan.md` template

```markdown
# Routing plan — S042-live-e2e

| Stage | Required | Mode | Skip rationale |
|-------|----------|------|----------------|
| 00-context | yes | scoped | — |
| 10-e2e | yes | full | — |
| 11-verify-impl | yes | full | — |

## Approved
User approval recorded: YYYY-MM-DD
```

---

## 7. Standing doc changelog

When a session updates standing docs, append (do not replace prior entries):

```markdown
## Session changelog

### S042-live-e2e (2026-06-22)
- Added H5 live browser gate to §Live tiers
```

---

## 8. Dual-layer state

| Layer | YAML key | Purpose |
|-------|----------|---------|
| Project baseline | `project.stages.*` | Last completed status per stage (historical) |
| Active work | `active_session` | Current session position and routing plan |
| Archive | `sessions[]` | Completed sessions summary |

`evolve_cycles[]` remains for feature orchestration; each cycle **must** include
`session_id` linking to `docs/sessions/{id}/`.

---

## 9. Per-stage session report paths

Write session reports here (legacy root paths remain valid for **pre-session** artifacts only;
new work uses session paths):

| Stage | Session report path |
|-------|---------------------|
| 08-verify-build | `reports/verification-report.md` |
| 09-qa | `reports/qa-report.md` |
| 10-e2e | `reports/e2e-report.md` |
| 11-verify-impl | `reports/verify-impl.md` |
| 12-verify-deploy | `reports/deploy-checklist.md` |
| 13-deploy-smoke | `reports/deploy-smoke.md` |
| 14-hotfix | `reports/hotfix.md` (+ `docs/bug-reports/` for BUG-*) |
| 15-service-health | `reports/service-health.md` |
| 16-evolve | `reports/evolve-summary.md` |
| 17-retrospective | `reports/retrospective.md` |
| 18-pr-review | `reports/pr-review.md` |
| 19-address-pr-review | `reports/pr-remediation.md` |

Mirror path in agent `update` §`artifacts[]` with `session_id` tag.

---

## 10. Stage obligations (all numbered skills)

Every stage **00–19** (except 00 when opening a session):

1. Invoke workflow-state-manager `read_context` with `session_id` from `active_session` if set.
2. If `active_session` is null and skill is not **00-context**: **block** — recommend 00 or resume `SNNN`.
3. If current skill not in `active_session.routing_plan`: AskQuestion — add to plan or waive.
4. Write outputs to `active_session.artifacts_dir` per table above.
5. On completion: update `active_session.routing_plan` entry status; advance `current_stage`.
6. Update `project.stages.{key}` when stage completes (project baseline).

**00-context** additionally: session open, type classification, routing plan proposal, and
`active_session` creation after user approval.

**Orchestrators** (pipeline, 16-evolve): ensure routing plan stages run in order; enforce phase
checkpoints for feature/greenfield types.

---

## 11. Session type classification (00-context Phase 0)

| User signal | Session type |
|-------------|--------------|
| New repo / no specs / "build from scratch" | `greenfield` |
| "Add feature", new Fn, API/UI capability | `feature` |
| New deployable in existing monorepo | `new_service` |
| Bug, regression, hotfix | `hotfix` |
| Live E2E, staging integration, connectivity | `integration` |
| Health check, ops, no product change | `ops` |
| Retrospective, PR review, process | `process` |

When ambiguous, AskQuestion once before proposing routing plan.

---

## 12. Default routing presets (starting points)

User may edit before approval. 00 proposes; user owns final plan.

| Type | Default stages |
|------|----------------|
| greenfield | 00, 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13 |
| feature | 00 (scoped), 01, 02, 04, 05, 07, 08, 09, 10, 11, 12, 13 |
| new_service | 00, 01, 04, 07, 08, 12, 13 |
| hotfix | 14, 15 (optional) |
| integration | 00 (scoped), 10, 11, 15 |
| ops | 15 |
| process | 17 or 18 or 19 |

Skip rationale required for every omitted stage.
