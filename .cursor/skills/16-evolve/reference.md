# 16-evolve — Reference

Canonical state file: repo-root [`workflow-state.yaml`](../../workflow-state.yaml).
Shared rules: [workflow-state-reference.md](../workflow-state-reference.md).

## Evolve cycle YAML schema

Append to `workflow-state.yaml`:

```yaml
evolve_cycles:
  - id: EV-001                    # Sequential: EV-001, EV-002, ...
    cycle_type: general           # general | feature (multi-Fn feature addition)
    feature_ids: []               # e.g. [F19, F20, F21] — multi-Fn in one cycle
    feature_id: null              # deprecated; use feature_ids
    title: "Add batch export API" # Short label from intake
    status: in_progress           # pending | in_progress | completed | cancelled
    started: "2026-05-17"
    completed: null
    scope_summary: |              # Verbatim approved scope from Phase 0
      ...
    routing_plan:                 # User-approved stage list
      required_stages:
        - 01-requirements
        - 02-verify-plan
        - 04-tech-plan
        - 05-verify-tech
        - 07-build
        - 09-qa
        - 10-e2e
        - 11-verify-impl
        - 12-verify-deploy
        - 13-deploy-smoke
      skipped_stages:
        - 00-context
        - 03-plan-tooling
        - 06-tech-tooling
    current_stage: 01-requirements
    stages:
      01-requirements:
        status: in_progress       # pending | in_progress | completed | skipped
        started: "2026-05-17"
        completed: null
        artifacts_updated:
          - docs/feature-list.md
          - docs/api-contract.md
      # ... one entry per routed stage
    gates:
      a_to_b: pending             # pending | passed | waived
      b_to_c: pending
      c_to_d: pending
      deploy: pending
    checkpoints:                  # mandatory for feature cycles; recommended for all
      phase_a: pending
      phase_b: pending
      phase_c: pending
      phase_d: pending
      deploy: pending
    adrs:
      - docs/adr/ADR-004.md
    artifacts:
      - path: docs/evolve-decisions.md
        status: in_progress
      - path: docs/evolve-report-EV-001.md
        status: pending
    issues: []                    # Cycle-local issues; also mirror to §issue_log
```

### Issue log entries

When logging to top-level `issue_log`, include:

```yaml
- id: 42
  evolve_cycle_id: EV-001
  stage: 16-evolve
  category: contradiction
  issue: "api-contract POST /run conflicts with spec §Batch"
  resolution: null
```

## Stage routing matrix

Use this to propose `routing_plan.required_stages`. User approval overrides defaults.

| Trigger | 00 | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 |
|---------|----|----|----|----|----|----|----|----|----|----|----|----|----|-----|
| New feature Fn in feature-list | — | ✓ | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| New config parameter | — | ✓ | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| API contract change only | — | ✓ | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Test plan / acceptance only | — | ✓ | ✓ | — | — | — | — | — | — | ✓ | ✓ | ✓ | — | — |
| Execution plan task add (spec already OK) | — | — | — | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| New Cursor rule / hook | — | — | — | ✓ | — | — | ✓ | — | — | ✓ | — | — | — | — |
| New dependency (inventory change) | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Data / weights staging change | — | ✓ | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Docs-only fix (spec was wrong) | — | ✓ | ✓ | — | — | — | — | — | — | — | — | — | — | — |
| New upstream repo / paper | ✓ | ✓ | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

Legend: ✓ = include by default; — = skip unless user requests.

**03 / 06**: Also run when plan-adherence or template-registry patterns need new guardrails.

**13-deploy-smoke**: Skip only if user explicitly chooses "build + verify, no deploy this cycle".

## Delta mode conventions

When invoking child skills during evolve:

### 01-requirements (delta)

- Open only templates/sections listed in `affected_artifacts`.
- Prefix new content with evolve cycle ID in `requirements-decisions.md`.
- Do not delete unrelated sections; mark deprecated features with status + ADR if removed.

### 02-verify-plan (delta)

- Full **consistency pass** across all spec docs (contradictions hide at boundaries).
- Statement audit focused on changed sections + any doc that references changed identifiers.

### 04-tech-plan (delta)

- Append tasks to `workflow-state.yaml + execution plan artifact`; do not reset completed tasks.
- New milestone/phase only if scope warrants; user approves via AskQuestion.

### 07-build (delta)

- Implement only pending tasks tagged with `evolve_cycle_id` or listed in cycle scope.
- Branch per execution-plan git strategy; PR references evolve cycle in title/body.

## Consistency checklist

Run after 02-verify-plan and 05-verify-tech (and before deploy gate):

- [ ] Every new/changed feature in `feature-list.md` has spec section + test coverage
- [ ] Parameter names match `config-spec.md` (no synonyms)
- [ ] `api-contract.md` matches Modal entry points in `deployment-integration.md`
- [ ] `test-plan.md` and `acceptance-criteria.md` reference same journey IDs
- [ ] `dependency-inventory.md` lists every new package from 04-tech-plan
- [ ] `data-management-plan.md` covers new weights/datasets if any
- [ ] `execution-plan.md` tasks trace to feature IDs
- [ ] New ADRs referenced inline in updated spec sections (`<!-- ADR-NNN -->`)
- [ ] `workflow-state.yaml` §template not contradicted without ADR
- [ ] No orphaned statements in audit reports marked `denied` still present in specs

On any failure: AskQuestion with category, evidence (file + section), and recommended fix.

## evolve-decisions.md template

Create or append per cycle:

```markdown
# Evolve decisions

## Cycle EV-001 — {title}
**Started**: {date}
**Scope** (approved):
{verbatim scope}

### Intake decisions
| ID | Category | Question | Decision | ADR |
|----|----------|----------|----------|-----|
| E1-1 | decision | ... | ... | ADR-004 |

### Stage log
| Stage | Completed | Notes |
|-------|-----------|-------|
| 01-requirements | | |
```

## evolve-report template

`docs/evolve-report-{cycle-id}.md`:

```markdown
# Evolve report — {title}

- **Cycle**: EV-001
- **Status**: completed
- **Scope**: ...
- **Stages run**: 01, 02, 04, 05, 07, 09, 10, 11, 12, 13
- **ADRs**: ADR-004, ADR-005
- **Deploy**: {URL or "not deployed"}
- **Open issues**: ...

## Summary
...

## Artifacts changed
- docs/feature-list.md — added F10
- ...

## Verification
- 09-qa: pass
- 10-e2e: pass (journeys UJ-013, UJ-014)
```

## Handoff to 14 / 15

| Outcome | Next skill |
|---------|------------|
| Production bug found during 09/10/13 | [14-hotfix](../14-hotfix/SKILL.md) with repro test |
| Deploy OK but ops uncertainty | [15-service-health](../15-service-health/SKILL.md) |
| Scope grew beyond cycle | New evolve cycle EV-{N+1} — do not expand silently |

---

## Fn allocation (multi-feature cycles)

**Default:** one evolve cycle, multiple Fn (F19, F20, F21).

1. Open `docs/feature-list.md` Summary table.
2. Assign next ids sequentially (highest F# + 1, +2, …).
3. Add rows: `| Fnn | {title} | Planned | {category} | {apps} | 16-evolve EV-NNN |`
4. Add **Feature Details** §Fnn for each feature.
5. Update cross-linked docs in `affected_artifacts` — do not delete unrelated Fn.

Removed features: mark Deprecated + ADR; never reuse Fn ids.

## Feature intake batches

Use **AskQuestion** per batch (2–4 questions). Wait for all answers before the next batch.
For **multiple features**, repeat behavior/platform batches per feature or group related Fn.

### Batch 1 — Problem

| Prompt theme | Purpose |
|--------------|---------|
| Who uses this and when? | Personas, journey anchor |
| What problem does it solve? | Motivation |
| How will we know it works? | Measurable success |

### Batch 2 — Behavior

| Prompt theme | Purpose |
|--------------|---------|
| Primary user flow (step by step) | user-journeys.md |
| Inputs and outputs (types, formats) | spec, api-contract |
| Error / empty / loading behavior | test-plan edge cases |

### Batch 3 — Boundaries

| Prompt theme | Purpose |
|--------------|---------|
| Explicitly out of scope | Scope creep guard |
| Breaking API or config changes? | versioning, deploy risk |
| Privacy / PII / retention | deployed service guardrails |

### Batch 4 — Platform

| Prompt theme | Purpose |
|--------------|---------|
| Which app(s): API, auth, frontend? | feature-list Category/App |
| New env vars or secrets? | config-spec, 12-verify-deploy |
| Browser / CORS / VITE_* changes? | connectivity-gates |

### Batch 5 — Quality & tests

| Prompt theme | Purpose |
|--------------|---------|
| Latency / throughput expectations | 04-tech-plan, perf in test-plan |
| Acceptance scenarios (Given/When/Then) | test-plan, 11-verify-impl |
| Smoke vs full E2E tier (T0/T2/T3) | 10-e2e, 13-deploy-smoke |

## Default routing (net-new feature(s))

| Stage | Default |
|-------|---------|
| 00-context | Skip |
| 01-requirements | Run (delta) |
| 02-verify-plan | Run |
| 03-plan-tooling | Run if new guardrails; else confirm skip via AskQuestion |
| 04-tech-plan | Run |
| 05-verify-tech | Run |
| 06-tech-tooling | Run if new deps or hooks |
| 07-build, 08 | Run |
| 09-qa, 10-e2e | Run (parallel) |
| 11-verify-impl | Run — **user signs off each Fn** |
| 12, 13 | Run unless user waives deploy |

## Checkpoint digest

After phases A, B, C, D, and deploy — present to user before continuing:

```markdown
## Evolve cycle {EV-NNN} — {title}

**Phase completed:** {A|B|C|D|Deploy}
**Feature IDs:** {F19, F20, F21}
**Stages run:** {list}
**Specs touched:** {paths}
**Code:** branch `{branch}`, commits {n}, PR {url or "none"}
**Tests:** pytest {pass/fail}
**Smokes:** {H1–H5 summary or "not run"}
**Open issues:** {issue_log ids or "none"}

### What changed (plain language)
{2–4 sentences}

### Your review
- Does behavior match what you asked for?
- Any acceptance scenario missing?
```

| Field | Source |
|-------|--------|
| pytest summary | Last `08-verify-build` or local run |
| E2E / smoke | `docs/e2e-report.md`, deploy H1–H5 |
| Spec paths | `evolve_cycles[].artifacts` |
| PR URL | `git_history` / gh |
| Acceptance | `docs/test-plan.md` rows per Fn |

## Spec documents typically touched (features)

| Document | Typical delta |
|----------|----------------|
| `docs/feature-list.md` | New Fn rows + details |
| `docs/spec.md` | Component behavior |
| `docs/user-journeys.md` | New or extended journey |
| `docs/test-plan.md` | Tests + H tiers |
| `docs/acceptance-criteria.md` | Fn acceptance |
| `docs/config-spec.md` | New parameters |
| `docs/api-contract.md` | New/changed endpoints |
| `workflow-state.yaml + execution plan artifact` | Tasks, milestones |
| `docs/dependency-inventory.md` | New packages |
| `docs/spec.md §Data` | Corpus/schema if ingest changes |

Prefix decisions in `docs/requirements-decisions.md` / `docs/tech-decisions.md` with
`EV-NNN / Fnn`.
