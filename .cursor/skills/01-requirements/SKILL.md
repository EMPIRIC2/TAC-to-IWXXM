---
name: 01-requirements
description: >
  Interviews the user to produce spec-driven development documents (feature-list, spec,
  user-journeys, config-spec, test-plan, etc.) using template-driven questioning. Supports
  delta mode when adding features or large changes to an existing app (multiple Fn per evolve
  cycle via 16-evolve). If 00-context ran, pre-populates answers from the context brief. Use
  for requirements interview, add feature delta specs, evolve-cycle product planning, or
  large-change scope intake.
---

# 01 — Product Requirements Interview

Interview the user to fill spec document templates. Template-driven: for each approved
template section, ask targeted questions to fill it.

**Preamble:** [pipeline-preamble.md](../pipeline-preamble.md) — shared conventions for stages 00–19.
**Cross-cutting:** [considerations.md](../considerations.md), [connectivity-gates.md](../connectivity-gates.md).
**State agent:** [workflow-state-manager](../../agents/workflow-state-manager.md) — mandatory read/update.

## Connectivity (stage 01)

Product specs **must** define browser wiring before build:

| Document | Required content |
|----------|------------------|
| `docs/test-plan.md` | Tiers H0c (CORS unit), H0i (integration), H4–H5 (live connectivity); UJ ↔ test mapping |
| `docs/deploy.md §Integration` | `VITE_*` build-time URLs; `METAR_CORS_ORIGINS`; redeploy order (API CORS before UI sign-off) |
| `docs/user-journeys.md` | Browser steps for UI journeys; E2E tier (T0 vs T2 vs T3) — Vitest alone is not T3 |
| `docs/config-spec.md` | Env names for CORS and frontend API bases |

Ask in interview if UI calls APIs on a **different origin** than the static site.

## Prerequisites

1. **Optional**: `docs/context-brief.md` (00-context **project** mode). If it exists,
   pre-populate interview answers from it. Also check `docs/context/README.md` for scoped
   briefs relevant to the current feature — use those for delta/evolve interviews without
   merging scoped content into standing specs verbatim.
2. **Optional**: Template selection from `workflow-state.yaml` §template. If a template
   was selected in 00-context, use [template-registry.md](../template-registry.md) to
   pre-populate architecture, deployment, and API answers from the template patterns.
   If 00-context was skipped, template selection happens in Phase 1 of this skill instead.
3. **Templates**: Read template files from the existing `templates/` directories in skill
   folders. Use [doc-types.md](../doc-planner/doc-types.md) for relevance criteria.

## Uncertainty Resolution Protocol

Follow [considerations.md](../considerations.md) §Uncertainty. During interviews, surface
any contradictions in user's answers, ambiguities in scope, and decisions that affect
multiple templates.

## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).
**Stage key:** `stages.01-requirements`.

Invoke **workflow-state-manager** `read_context` before any other action; `update` after each
substep. **Do not** edit `workflow-state.yaml` directly.


### On invocation — check state

1. Use **workflow-state-manager** context brief for §stages.01-requirements (from agent `read_context`).
2. **If `completed`**: Ask: "Reuse existing specs, update specific documents, or restart?"
3. **If `in_progress`**: Report progress (templates completed, current position). Ask:
   "Resume from where we left off, or restart?"
4. **If `pending`**: Start fresh.

### State updates

After each template interview completes, update:
- `substeps.interviews.completed` counter
- `substeps.interviews.current_template` pointer
- `substeps.interviews.current_section` pointer
- Write the completed document immediately

### Commit-as-you-go

Commit artifacts to an appropriate branch before transitioning to the next stage or
asking the user a blocking question. Branch type per
[workflow-state-reference.md](../workflow-state-reference.md) §Git history.
Record every commit in `workflow-state.yaml` §`git_history.commits` with
`stage: "01-requirements"`.

## Delta / feature-addition mode

When user adds features or `mode: delta` / active evolve cycle:

- Update **only** Fn sections and templates listed in `affected_artifacts`.
- Support **multiple Fn** in one cycle — one interview batch per feature or grouped by domain.
- Prefix decisions in `requirements-decisions.md` with `EV-NNN / Fnn`.
- Do not delete unrelated spec sections; mark deprecated Fn with status + ADR.

## Workflow

### Phase 0 — Template Selection (if not already done)

If `workflow-state.yaml` §template does not exist (00-context was skipped or didn't
classify), run template classification now:

1. Read [template-registry.md](../template-registry.md) §Classification Heuristics
2. From the user's project description and any available context, classify the project
3. Present classification via AskQuestion (same format as 00-context Phase 1C Step 3)
4. Record template selection in `workflow-state.yaml` §template
5. Confirm database + vector store choices from [deployment-catalog.md](../deployment-catalog.md)

If template already selected, read `workflow-state.yaml` §template and proceed.

### Phase 0B — Template-Driven Pre-Population

When a template is selected (`id` is `api`, `worker`, or `monolith`), read
[template-registry.md](../template-registry.md) §Template Structure Reference and
pre-populate known answers:

**Always known from deployed service templates (confirm, don't ask)**:
- Service id: `deployed-service`
- Primary store: PostgreSQL (document extensions in spec §Data)
- Config: environment variables (`DATABASE_URL`, embedding/LLM keys)
- Migrations: Alembic (or documented equivalent)
- Core RAG logic: `src/rag/` (framework-agnostic tests)

**Known from `api` template**:
- HTTP: FastAPI (or equivalent) in `src/app.py` + `src/api/`
- Routers: query, ingest, admin, health
- E2E: HTTP against local or staging base URL

**Known from `worker` template**:
- Entry: `src/worker.py`, jobs in `src/jobs/`
- Idempotent ingest/reindex; job status in DB
- E2E: trigger job → poll until `completed`

**Known from `monolith` template**:
- Combined API + worker layout; shared `db/` and `rag/`

Present: "Based on the [api/worker/monolith] template, these are pre-set. Confirm or override?"

### Phase 1 — Determine Applicable Templates

Analyze the project type and determine which document templates are relevant.

#### Mandatory documents

Always included regardless of relevance scoring:

| Document | Template Source | Rationale |
|----------|---------------|-----------|
| **Feature List** | `templates/feature-list.md` | Defines implementation scope |
| **Spec** | `templates/spec.md` | Component details, architecture, data flow |
| **User Journeys** | `templates/user-journeys.md` | Caller-facing end-to-end flows (UJ-IDs); feeds test plan and E2E |
| **Test Plan** | `templates/test-plan.md` | Test strategy, cases, metrics (references UJ-IDs from user-journeys) |

#### Evaluating other documents

For each document type in [doc-types.md](../doc-planner/doc-types.md), evaluate based on
what the user has described so far:

- **Config Spec** — if the project has user-facing configuration
  - For each parameter: **include in v1** vs **exclude/defer**, default, validation rules
  - Cross-check upstream CLI defaults (00-context contradictions); document in requirements-decisions.md
  - Validation rules that prevent runtime failures (e.g. `chunk_size` ≥ 15) belong here, not only in build
- **API Contract** — if the project exposes APIs
- **Dependency Inventory** — if the project has non-trivial dependencies
- **Deployment Plan** — if deploying to a platform (Modal, Render, AWS, etc.)
- **Data Management Plan** — if the project needs external data assets
- **ADRs** — if there are non-obvious architectural choices
- **Acceptance Criteria** — if formal acceptance testing is needed
- **Roadmap** — if the project has phased delivery

If 00-context ran, use `context-brief.md` to pre-assess relevance.

Produce a **Document Manifest**:

```markdown
## Document Manifest

### Mandatory
| # | Document | Rationale |
|---|----------|-----------|
| 1 | Feature List | Defines scope — always required |
| 2 | Spec | Architecture and components — always required |
| 3 | User Journeys | Caller flows — always required (interview after Feature List + Spec) |
| 4 | Test Plan | Test strategy — always required (interview after User Journeys) |

### Recommended
| # | Document | Relevance | Rationale |
|---|----------|-----------|-----------|
| 4 | Config Spec | High | User described CLI flags and env vars |
| 5 | API Contract | Medium | REST endpoints mentioned |
| ... | ... | ... | ... |

### Excluded
- **Data Management Plan**: No external data assets identified
```

### Phase 2 — Present Manifest for Review

Present the manifest via AskQuestion.

**Mandatory documents**: Only two options:
- "Approve — include in interview"
- "Modify — I'll adjust scope"

**Recommended documents**: Three options:
- "Approve — include in interview"
- "Skip — don't need this"
- "Modify — I'll adjust scope"

Summarize the final plan:

```
Interview Plan:
  Mandatory:   4 documents
  Approved:    [N] additional documents
  Skipped:     [N] documents
  Modified:    [N] documents
```

**State**: Record approved/skipped/modified templates.

### Phase 3 — Interview by Template

For each approved document, in manifest order:

#### Step 1 — Read the template

Read the template file and identify all sections that need content. Each section becomes
a set of interview questions.

#### Step 2 — Pre-populate from context (if available)

If `context-brief.md` exists, map its findings to template sections:
- For each section, check if the context brief has relevant information
- If yes, present the pre-populated answer and ask: "Is this correct, or would you like
  to modify it?"
- If no, present the question as a fresh prompt

#### Step 3 — Interview in batches

For each template, group sections into themed batches of 3-5 questions. Use AskQuestion
with structured options where possible, and open-ended prompts where the section requires
free-form input.

**Batching strategy**:

| Template | Batch Groups |
|----------|-------------|
| Feature List | Core features → Secondary features → Out of scope |
| Spec | System architecture → Components → Data flow → Constraints |
| User Journeys | Happy paths per feature → Edge/error journeys → E2E tiers (local vs deployed) |
| Test Plan | User Journeys (E2E) cross-ref → Test types → Key test cases (UJ ↔ TC) → CI/CD |
| Config Spec | CLI flags → Environment variables → Config files → Defaults |
| API Contract | Endpoints → Request/response schemas → Auth → Error handling |

For each batch:
1. Present 3-5 questions via AskQuestion
2. Wait for all responses
3. If any response reveals a contradiction with a previous answer, surface it immediately
   as `[Contradiction]` before proceeding
4. Record all answers with template section traceability
5. For answers that resolve a `[Decision]`, `[Contradiction]`, or `[Ambiguity]` between
   multiple valid approaches, create an ADR in `docs/adr/` per
   [considerations.md](../considerations.md) §ADR logging. Set the Stage field to
   `01-requirements`.

#### Step 4 — Generate the document

After all sections are interviewed:
1. Fill the template with user's answers
2. Mark unfilled sections with `⚠️ Not discussed:` prefix
3. Write the document to the output directory
4. Report what was generated

#### Step 5 — Repeat for next template

Move to the next approved template. Between documents, report progress:

```
Document 2 of 6 complete: Spec
  Sections filled: 8/10
  Gaps: 2 (marked with ⚠️ Not discussed)

  Moving to Document 3: Test Plan (5 section batches)
```

**State**: After each document, update progress counters and artifact status.

### Phase 4 — Generate README

After all spec documents are written, synthesize a project README.md:

| README Section | Source |
|----------------|--------|
| **Title & description** | Feature List §Overview or user's project description |
| **Installation** | Dependency Inventory or Config Spec |
| **Quick start** | Spec §Pipeline or primary usage flow |
| **Usage / CLI** | Config Spec §CLI Flags, Spec §Components |
| **Configuration** | Config Spec §Config Files, §Environment Variables |
| **Examples** | Test Plan adapted as usage examples |
| **Architecture** | Spec §System Architecture (brief) |
| **Deployment** | Deployment plan (condensed) |

If a section requires information not in any spec, surface as `[Ambiguity]`.

Write to `README.md` in repo root.

### Phase 5 — Summary

```
Requirements Interview Complete.

Generated:
  docs/feature-list.md     — [N] features, [N] gaps
  docs/spec.md             — [N] components, [N] gaps
  docs/user-journeys.md    — [N] journeys (UJ-001…), [N] gaps
  docs/test-plan.md        — [N] test cases, [N] gaps
  [additional documents]
  README.md                — synthesized from specs

Total: [N] documents, [N] gaps needing review, [N] contradictions surfaced

Interview decisions: [N] questions answered across [N] templates
ADRs created: [N] in docs/adr/

Decisions log: docs/requirements-decisions.md

Next step: 02-verify-plan
```

**State**: Set overall status to `completed`.

## Output Rules

1. **User is source of truth**: Every claim in generated docs traces to user's interview
   answers. Never fabricate or assume answers.
2. **Context as pre-fill only**: When 00-context ran, its findings pre-populate answers but
   the user always confirms or modifies.
3. **Gap-aware**: Mark unfilled sections rather than guessing.
4. **Batched questions**: 3-5 questions per batch to balance thoroughness and flow.
5. **Contradiction detection**: If user answers contradict each other, surface immediately.
6. **Immediate persistence**: Write each document after its interview completes. State
   updates after every batch.
7. **Template-faithful**: Generated documents follow template structure exactly.
