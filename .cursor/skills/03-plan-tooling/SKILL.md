---
name: 03-plan-tooling
description: >
  Creates project-specific Cursor hooks, rules, skills, and agents that prevent drift from
  the approved product plan. These are guardrails — not dev tools. Produces scope-checking
  hooks, plan-adherence rules, and domain-specific skills/agents tailored to the project.
  Blocking stage — must complete before technical planning begins.
---

# 03 — Plan Tooling

Create Cursor tooling (hooks, rules, skills, agents) that prevent drift from the approved
product plan. These guardrails enforce scope boundaries and plan adherence during all
subsequent stages.

**Preamble:** [pipeline-preamble.md](../pipeline-preamble.md) — shared conventions for stages 00–19.
**Sessions:** [sessions-reference.md](../sessions-reference.md) — requires `active_session` unless waived; reports under `docs/sessions/{id}/reports/`.
**Cross-cutting:** [considerations.md](../considerations.md), [connectivity-gates.md](../connectivity-gates.md).
**State agent:** [workflow-state-manager](../../agents/workflow-state-manager.md) — mandatory read/update.

## Connectivity (stage 03)

Plan guardrails must prevent **UI-without-wiring** drift:

| Tooling | Enforcement |
|---------|-------------|
| Rule (plan-adherence or domain) | New browser-facing API → must trace to connectivity tasks in execution plan |
| Skill pointer | Link [connectivity-gates.md](../connectivity-gates.md) from README or 07-build rule |
| Scope reviewer | Flag features F11/F12 (frontends) without H4/H5 in approved test-plan |

Do not mark 03 complete if specs lack connectivity tiers and no ADR waives browser E2E.

## Prerequisites

1. **02-verify-plan** must be `completed`. Spec documents must be audited.
2. At minimum: `docs/feature-list.md`, `docs/spec.md`, `docs/user-journeys.md` with audit
   verdicts applied.
3. `docs/decisions/product-audit.md` and `docs/decisions/product-decisions.md` must exist.

## Why This Stage Blocks

Tooling must be installed **before** technical planning (Stage 04) because:
- Technical decisions must stay within the approved product scope
- Architecture choices must align with approved features
- Without guardrails, drift accumulates silently and is expensive to fix later


## Session management

Per [sessions-reference.md](../sessions-reference.md) §10 and [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).

1. Agent `read_context` must return `active_session` (or blocking deviation).
2. Current stage must appear in `active_session.routing_plan` unless user amends plan.
3. Write stage reports to `active_session.artifacts_dir/reports/` when this stage produces a report.
4. On completion: update routing-plan entry status; mirror `project.stages.{key}` via agent `update`.
5. **00-context** exempt from active_session requirement (session opener).

## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).
**Stage key:** `stages.03-plan-tooling`.

Invoke **workflow-state-manager** `read_context` before any other action; `update` after each
substep. **Do not** edit `workflow-state.yaml` directly.


### On invocation — check state

1. Use **workflow-state-manager** context brief for §stages.03-plan-tooling (from agent `read_context`).
2. **If `completed`**: Ask: "Reuse existing tooling, update, or regenerate?"
3. **If `in_progress`**: Report what was created so far. Ask: "Resume or restart?"
4. **If `pending`**: Start fresh.

### Commit-as-you-go

Commit artifacts to an appropriate branch before transitioning to the next stage or
asking the user a blocking question. Branch type per
[workflow-state-reference.md](../workflow-state-reference.md) §Git history.
Record every commit via **workflow-state-manager** `update` → `git_history.commits` with
`stage: "03-plan-tooling"`.

## Delta / feature-addition mode

When new features need guardrails:

- Add or update **rules, hooks, skills, agents** only for risks introduced by new Fn.
- Skip if pure code-only change behind existing plan-adherence rules (confirm via AskQuestion).
- Register **workflow-state-manager** in agents if not already present.

## Workflow

### Phase 1 — Analyze Plan for Tooling Needs

Read the approved spec documents and identify:

1. **Scope boundaries**: Features in-scope vs out-of-scope from feature-list.md
2. **Component structure**: Components and their responsibilities from spec.md
3. **Naming conventions**: Any naming patterns established in the specs
4. **Data model**: If spec.md defines a data model, its entities and relationships
5. **API surface**: If an API contract exists, its endpoints and schemas
6. **Domain terms**: Project-specific vocabulary that should be used consistently
7. **Constraints**: Hard constraints from the specs (performance, compatibility, etc.)

For each finding, determine what type of tooling can enforce it:

| Finding | Tooling Type | Enforcement |
|---------|-------------|-------------|
| Feature scope | Rule | Warn when code doesn't map to an approved feature |
| Component boundaries | Hook | Check file creation aligns with component list |
| Naming conventions | Rule | Enforce naming patterns in code |
| Data model | Skill | Validate schema changes against spec |
| API surface | Skill | Validate endpoint changes against contract |
| Browser connectivity | Rule + connectivity-gates.md | UI features require CORS/VITE test tiers in approved test-plan |
| Domain vocabulary | Rule | Suggest correct terms when wrong ones are used |

### Phase 2 — Present Tooling Plan

Present the planned tooling to the user via AskQuestion:

```
prompt: "Plan tooling analysis identified [N] guardrails to create:
  Rules:  [N] (scope adherence, naming, constraints)
  Hooks:  [N] (file creation scope check, feature drift detection)
  Skills: [N] (domain-specific validation)
  Agents: [N] (specialized review)

  Review the plan?"

options:
  1. "Approve all — create all guardrails"
  2. "Review individually — I'll approve each one"
  3. "Minimal — rules and hooks only, skip skills and agents"
  4. "Let me explain / provide more context"
```

If reviewing individually, present each guardrail with approve/skip/modify options.

### Phase 3 — Create Tooling (Parallel Agents)

Launch parallel agents for each tooling category in a single message:

#### Agent A — Rules

Create `.cursor/rules/` files:

**`plan-adherence.mdc`** (always-apply):
- Before implementing any feature, verify it exists in `docs/feature-list.md`
- When creating new files, verify the component is listed in `docs/spec.md`
- When adding dependencies, check against approved tech stack
- Surface `[Scope Drift]` via AskQuestion if work falls outside approved scope
- Reference the specific feature-list entry or spec section that authorizes the work

**`template-conformance.mdc`** (always-apply, if template selected):
- Read `workflow-state.yaml` §template and [template-registry.md](../template-registry.md)
- **File structure**: Warn if files are created outside the template's expected layout
  (e.g., creating `src/routes/` in a RAG API service)
- **Service layout**: Match template type (api / worker / monolith) per template-registry
- **Separation of concerns**: RAG logic in `src/rag/` without FastAPI/SQLAlchemy imports
- **Naming**: Service id `deployed-service`; routes and tables per `docs/api-contract.md`
- Surface `[Template Drift]` if code diverges from template patterns without an ADR

**Project-specific rules** (scoped by file pattern):
- Naming convention rules derived from spec patterns
- Constraint enforcement rules from spec constraints
- Domain vocabulary rules (e.g., "collection" vs "index", "chunk" vs "document" per spec)

#### Agent B — Hooks

Create `.cursor/hooks/` scripts and update `.cursor/hooks.json`:

**`scope-check.sh`** (fires on `preToolUse` for file creation):
- Reads the new file path
- Checks if it maps to an approved component in `docs/spec.md`
- Returns warning in `additional_context` if the file doesn't match any component
- Does NOT block — provides advisory context

**`feature-drift.sh`** (fires on `afterFileEdit`):
- Reads the edited file path
- Lightweight check: is this file related to the current task/feature?
- Cross-references with `workflow-state.yaml + execution plan artifact` §Current State (when it exists later)
- Returns context about which feature/component this file belongs to

Hook scripts:
- Read `filePath` from stdin JSON
- Run checks
- Return `additional_context` with findings or empty on success
- Always exit 0 (advisory, not blocking)

#### Agent C — Skills (if approved)

Create project-specific skills in `.cursor/skills/`:

Based on the project's domain, create skills that know the project's data model,
API surface, or other domain-specific concerns. Examples:

- **Data model validator**: If spec.md defines entities, create a skill that validates
  schema changes, migration scripts, or ORM models against the spec's data model
- **API contract validator**: If an API contract exists, create a skill that validates
  endpoint implementations against the contract
- **Domain expert**: A skill that can answer questions about the project's domain using
  the spec documents as its knowledge base

Each skill gets a `SKILL.md` with:
- Name and description
- When to use (trigger conditions)
- Input: the relevant spec section(s)
- Validation logic
- Output: pass/fail with specific findings

#### Agent D — Agents (if approved)

Create project-specific agents in `.cursor/agents/`:

- **workflow-state-manager** (required): Sole writer of `workflow-state.yaml` — see
  [`.cursor/agents/workflow-state-manager.md`](../../agents/workflow-state-manager.md)
- **Scope reviewer**: An agent that reviews PRs or changes for scope alignment
- **Spec consultant**: An agent that can answer "does this align with the spec?" questions

Each agent gets a metadata file with model, description, and prompt template.

### Phase 4 — Verify Installation

After all agents complete:

1. Verify all rule files exist and have valid `.mdc` frontmatter
2. Verify `.cursor/hooks.json` is valid JSON with correct event bindings
3. Verify hook scripts exist and are executable (or have correct permissions)
4. Verify skill files have valid YAML frontmatter
5. Run a smoke test: trigger a hook and verify it returns expected context

Report verification results:

```
Plan Tooling Installed.

  Rules created:  [N]
    - plan-adherence.mdc (always-apply)
    - [project-specific].mdc (scoped: [patterns])

  Hooks created:  [N]
    - scope-check.sh (preToolUse: file creation)
    - feature-drift.sh (afterFileEdit)

  Skills created: [N]
    - [skill-name] (trigger: [condition])

  Agents created: [N]
    - [agent-name] (purpose: [description])

  Verification: All [N] artifacts valid ✓
```

**State**: Set status to `completed`.

### Phase 5 — Summary

```
Plan Tooling Complete.

Guardrails installed: [N] total
  Rules:  [N] — enforcing scope, naming, constraints
  Hooks:  [N] — monitoring file creation and edits
  Skills: [N] — domain-specific validation
  Agents: [N] — specialized review

These guardrails will:
  ✓ Warn when work falls outside approved scope
  ✓ Enforce naming conventions from the spec
  ✓ Validate changes against the data model / API contract
  ✓ Provide domain context on every file edit

Phase A gate check:
  ✓ Spec documents generated and audited
  ✓ Plan tooling installed
  → Ready for Phase B: Technical Planning

Next step: 04-tech-plan
```

## Idempotency

On re-invocation:
- Read existing tooling files and merge new guardrails rather than overwriting
- Preserve any user-added rules or hooks
- Update only what changed in the spec documents since last run

## Output Rules

1. **Spec-grounded**: Every guardrail traces to a specific spec section.
2. **Non-blocking hooks**: Hooks provide advisory context, never block the agent.
3. **Merge, don't overwrite**: Respect existing hooks.json and rule files.
4. **Verify installation**: Always confirm tooling is valid before marking complete.
5. **Domain-specific**: Skills and agents are tailored to THIS project, not generic.
