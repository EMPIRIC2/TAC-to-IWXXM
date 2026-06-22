---
name: 05-verify-tech
description: >
  Verifies technical plan documents by breaking them into provable statements, risk-classifying
  each, and presenting medium/low confidence statements for user review. Includes embedded
  consistency checking between technical plan and product plan. Runs a consistency agent in
  the background while the user reviews statements.
---

# 05 — Verify Technical Plan

Break technical plan documents into provable statements, risk-classify, and verify
consistency with the approved product plan.

**Preamble:** [pipeline-preamble.md](../pipeline-preamble.md) — shared conventions for stages 00–19.
**Cross-cutting:** [considerations.md](../considerations.md), [connectivity-gates.md](../connectivity-gates.md).
**State agent:** [workflow-state-manager](../../agents/workflow-state-manager.md) — mandatory read/update.

## Connectivity (stage 05)

Verify technical statements:

- Execution plan lists connectivity tasks (not only “deploy” and “health check”)
- Test plan H0c/H0i/H4/H5 align with [connectivity-gates.md](../connectivity-gates.md)
- Secrets matrix includes CORS + VITE rows for every browser path
- No task assumes “smoke script = UI verified” without H4–H5

Auto-approve only when product plan already requires connectivity tiers (02 pass).

## Prerequisites

1. **04-tech-plan** must be `completed`.
2. Required documents:
   - `workflow-state.yaml + execution plan artifact` — the technical execution plan
   - `docs/dependency-inventory.md` — dependency list
   - Any ADRs in `docs/adr/`
   - Deployment plan document
   - `docs/spec.md §Data` (if applicable)
3. Product plan documents from Phase A must still exist and be current.

## Uncertainty Resolution Protocol

Follow [considerations.md](../considerations.md) §Uncertainty. Technical verification
surfaces issues at the intersection of product requirements and technical implementation.

## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).
**Stage key:** `stages.05-verify-tech`.

Invoke **workflow-state-manager** `read_context` before any other action; `update` after each
substep. **Do not** edit `workflow-state.yaml` directly.


### On invocation — check state

1. Use **workflow-state-manager** context brief for §stages.05-verify-tech (from agent `read_context`).
2. **If `completed`**: Ask: "Reuse existing audit, or re-run?"
3. **If `in_progress`**: Resume from where we left off.
4. **If `pending`**: Start fresh.

### Commit-as-you-go

Commit artifacts to an appropriate branch before transitioning to the next stage or
asking the user a blocking question. Branch type per
[workflow-state-reference.md](../workflow-state-reference.md) §Git history.
Record every commit in `workflow-state.yaml` §`git_history.commits` with
`stage: "05-verify-tech"`.

## Delta / feature-addition mode

- Verify **changed** technical statements and cross-doc consistency vs updated product specs.
- Focus audit on new Fn, new dependencies, and affected execution-plan tasks.

## Workflow

### Phase 1 — Inventory Documents

Read all technical documents. Build audit list ordered by criticality:

1. Execution plan (highest — drives implementation)
2. Deployment plan (high — infrastructure decisions)
3. Dependency inventory (medium — package choices)
4. ADRs (medium — architectural decisions)
5. Data management plan (if applicable)
6. API contract (if applicable)

### Phase 2 — Extract Provable Statements

Same approach as 02-verify-plan. For technical documents, additional statement types:

| Type | Example | Why provable |
|------|---------|-------------|
| Task dependency | "T1.2 depends on T1.1" | Could be independent |
| Phase gate | "Phase 1 requires all tests passing" | Could require more/less |
| GPU allocation | "Inference uses H100 with A100 fallback" | Could be wrong GPU type |
| Package version | "Requires torch >= 2.1" | Could need different version |
| ADR consequence | "Microservice approach increases deployment complexity" | Debatable |
| Timeline estimate | "Milestone 1 has 8 tasks" | Could be more or fewer |

### Phase 3 — Risk Classification

Same tiers as 02-verify-plan:

| Confidence | Criteria | Action |
|------------|----------|--------|
| **High** | Directly from user's technical interview answers | Auto-approve |
| **Medium** | Agent-inferred from user answers or product specs | Present for review |
| **Low** | Assumed, generated, or from context brief | Present for review |

### Phase 4 — Consistency Check (Embedded, Background)

Launch a consistency check agent in the background while preparing statements for
user review. This agent verifies:

#### Product ↔ Technical Alignment

| Check | Verifies |
|-------|----------|
| Feature coverage | Every feature in feature-list.md has at least one task in execution-plan.md |
| Acceptance coverage | Every acceptance criterion has a corresponding test task |
| Component mapping | Every component in spec.md maps to implementation tasks |
| Constraint compliance | Technical choices don't violate product constraints |
| Scope alignment | No tasks implement features not in the approved scope |
| Config mapping | Every config option in config-spec.md has implementation coverage |

#### Internal Technical Consistency

| Check | Verifies |
|-------|----------|
| Dependency graph | No circular dependencies in task ordering |
| Gate criteria | Gate criteria are achievable with the phase's tasks |
| TDD ordering | Every code task has a preceding test task |
| Branch strategy | Branch names match the execution plan's git strategy |
| Data deps | Tasks with data deps have correct asset references |
| ADR alignment | ADR decisions match the execution plan's tech stack |
| Template alignment | If template selected: Phase 1 is a scaffold phase, file layout matches template structure, deploy targets match `workflow-state.yaml` §template.gpu_tiers and [deployment-catalog.md](../deployment-catalog.md), deploy command is ` platform deploy -m src.app` |

For each inconsistency, create a Low-confidence statement with `[Contradiction]` category.

The consistency agent results merge into the statement walk — inconsistencies appear as
additional statements for user review.

### Phase 5 — Walk Through Statements

Same flow as 02-verify-plan Phase 5:

1. Auto-approve high-confidence statements
2. Present medium/low confidence (including consistency findings) for user review
3. Verdicts: Approve / Deny / Modify / Skip
4. Immediate state persistence after each verdict
5. Surgical source document updates for Deny/Modify
6. For verdicts that resolve a `[Decision]`, `[Contradiction]`, or `[Ambiguity]` between
   multiple valid approaches, create an ADR in `docs/adr/` per
   [considerations.md](../considerations.md) §ADR logging. Set the Stage field to
   `05-verify-tech`. Reference the statement ID in the ADR's Context section.

### Phase 6 — Second Pass (Skipped Statements)

Same as 02-verify-plan Phase 6.

### Phase 7 — Create Audit Artifacts

Write to output directory:

1. **`docs/tech-audit.md`** — Full technical audit report
2. **`docs/tech-decisions.md`** — Technical decision log (extends from product decisions)

### Phase 8 — Summary

```
Technical Plan Verification Complete.

Results:
  Documents audited: [N]
  Total statements: [N]

  Auto-approved (high confidence): [N] ([%])
  User-approved (medium/low):     [N] ([%])
  Denied:                          [N] ([%])
  Modified:                        [N] ([%])
  Skipped:                         [N] ([%])

Consistency checks:
  Product ↔ Technical: [N] checks, [N] issues
  Internal Technical:  [N] checks, [N] issues
  All resolved: [Yes/No]

Source documents updated: [N] changes across [M] documents

Artifacts:
  docs/tech-audit.md      — technical audit report
  docs/tech-decisions.md   — technical decision log
  docs/adr/                — [N] ADRs created from tech audit verdicts

Phase B gate check (partial):
  ✓ Execution plan audited
  ✓ Consistency check complete
  ○ Technical tooling pending (next step)

Next step: 06-tech-tooling
```

**State**: Set status to `completed`.

## Output Rules

1. **Risk-based filtering**: Auto-approve high-confidence statements.
2. **Consistency is embedded**: Cross-plan checks run as part of this skill.
3. **Background agent**: Consistency check runs in parallel with statement preparation.
4. **Progress visible**: Every question shows position and completion percentage.
5. **Immediate persistence**: State writes after every verdict.
6. **Surgical updates**: Change only the specific claim in source documents.
7. **Product alignment**: Technical decisions must not violate product requirements.
