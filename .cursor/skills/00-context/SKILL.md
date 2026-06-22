---
name: 00-context
description: >
  Gathers context before planning or building. Two modes: **project** (greenfield — writes
  docs/context-brief.md for Stage 01) and **scoped** (feature/workflow-specific — writes
  docs/context/<slug>.md without bloating the project brief). Runs analysis agents when
  applicable, cross-references findings, surfaces decisions via AskQuestion. Optional for
  greenfield; re-invokable anytime for scoped work (new features, large changes, live E2E,
  new integration, 16-evolve cycles).
---

# 00 — Context Gathering

Analyze existing artifacts (codebase, paper, docs, prior work) and produce a structured
context brief for downstream skills.

**Preamble:** [pipeline-preamble.md](../pipeline-preamble.md) — shared conventions for stages 00–19.
**Cross-cutting:** [considerations.md](../considerations.md), [connectivity-gates.md](../connectivity-gates.md).
**State agent:** [workflow-state-manager](../../agents/workflow-state-manager.md) — mandatory read/update.

## Invocation modes

| Mode | When | Output | Phases run |
|------|------|--------|------------|
| **project** | Greenfield; first run before 01-requirements; full regen | `docs/context-brief.md` | 1A–1C, 2, 3, 4 (full) |
| **scoped** | Feature add, workflow prep, evolve cycle, mid-project discovery | `docs/context/<slug>.md` | 1A (subset), 2, 3, 4 (scoped template) — **skip 1B/1C unless user asks** |

**Default routing** — infer from the user message; confirm with one AskQuestion when ambiguous:

| User signal | Mode |
|-------------|------|
| New repo / paper / "before requirements" / no `context-brief.md` yet | **project** |
| "Adding a feature", "live E2E", "integration tests for staging", "gather context for X" | **scoped** |
| Invoked from **16-evolve** with a feature id | **scoped** (slug = feature or cycle id) |
| "Update context brief" when `docs/context-brief.md` exists | Ask: update **project** brief vs new **scoped** brief |

### Anti-bloat rules (scoped mode)

1. **Never append** feature/workflow findings to `docs/context-brief.md`.
2. **One scoped brief per topic** — file name kebab-case slug (e.g. `live-e2e-integration.md`).
3. **Register in index** — append a row to `docs/context/README.md` (create on first scoped brief).
4. **Cross-link, don't duplicate** — scoped briefs link to standing specs (`spec.md`, `test-plan.md`,
   `deploy.md`); they do not restate template selection or full ecosystem analysis unless the
   scope requires it.
5. **Resolution IDs are local** — scoped briefs use `R1`, `R2` per file; reference as
   `[Context: live-e2e-integration R2]` downstream, not global R-numbers from project brief.
6. **Retire stale scoped briefs** — mark `status: superseded` in the index when a feature ships;
   do not delete without user approval.

## Connectivity (stage 00)

Document **multi-app topology** in whichever brief is being written: browser-facing deployables,
API origins, CORS/BFF plans. Flag **browser integration risk** when static UI and APIs are on
different hosts. Project mode → § in `context-brief.md`; scoped mode → only if relevant to scope
(e.g. live E2E, frontend wiring).

## When to Use

- **Project mode — before 01-requirements**: Existing code, papers, docs, or prior work to analyze
  before the product requirements interview.
- **Scoped mode — anytime**: Before building a specific feature, workflow, or integration where
  targeted discovery reduces rework (live tests, new API surface, deploy topology change, etc.).
- **Standalone**: Deep understanding of existing artifacts without advancing the pipeline.

**When to skip (project only)**: User has no existing artifacts and will provide all requirements
via interviews in Stage 01. Set status to `skipped` in `workflow-state.yaml`. Scoped mode is never
"skipped" — it simply produces a scoped file or reports "nothing new to gather."

## Uncertainty Resolution Protocol

Follow the protocol defined in [considerations.md](../considerations.md) §Uncertainty.
Surface all Decisions, Ambiguities, Contradictions, Bloat, and Uncertainty via AskQuestion.

### What to surface

| Category | Trigger | Example |
|----------|---------|---------|
| **Decision** | Multiple valid approaches or interpretations | Paper describes baseline and ablation winner — which is canonical for implementation? |
| **Ambiguity** | Under-defined requirement, term, or scope | Paper says "standard preprocessing" without specifying steps |
| **Contradiction** | Sources disagree | Paper reports metric X, repo eval script targets metric Y |
| **Bloat** | Content adds noise without clear value | Repo bundles unrelated visualization notebooks |
| **Uncertainty** | Low confidence in a fact, no corroboration | Dependency imported but never visibly called |

### Batching

Group issues by category into batched AskQuestion calls. Blocking issues (Decision,
Contradiction, Ambiguity) must be resolved before proceeding. Advisory issues (Bloat,
Uncertainty) proceed with recommended option if user does not respond, marked with
`⚠️ Assumed:` prefix.

## Inputs

Collect from the user (check conversation context or ask):

| Input | Required | Default | Notes |
|-------|----------|---------|-------|
| **Mode** | Infer or confirm | `scoped` if mid-pipeline feature/workflow; else `project` | See Invocation modes |
| **Scope slug** | If scoped | derived from topic | kebab-case → `docs/context/<slug>.md` |
| **Scope topic** | If scoped | — | One sentence: what we're gathering context for |
| Input type | Project: Yes; Scoped: subset | — | paper, repo, docs, urls, or combination |
| Paper path | If paper | — | JATS XML, PDF, or markdown |
| Repo URL or local path | If repo | — | GitHub URL or local filesystem path |
| Existing docs | If docs | — | Paths to existing documentation |
| Live URLs / env | If deploy/testing scope | — | Staging/production URLs to probe |
| Org directory | No | — | Enables Phase 1B ecosystem scan (**project mode only** unless user requests) |
| Output path | No | mode-dependent | project → `docs/context-brief.md`; scoped → `docs/context/<slug>.md` |

## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).
**Stage key:** `stages.00-context`.

Invoke **workflow-state-manager** `read_context` before any other action; `update` after each
substep. **Do not** edit `workflow-state.yaml` directly.


### On invocation — check state

1. Use **workflow-state-manager** `read_context` for §stages.00-context and §`artifacts`.
2. **Determine mode** (see Invocation modes). If ambiguous, AskQuestion once before Phase 1A.
3. **Project mode** — if `docs/context-brief.md` exists and stage is `completed`:
   - "Reuse the existing project context brief as-is"
   - "Update project brief — re-run only for new/changed inputs"
   - "Regenerate project brief — start from scratch"
   - "New scoped brief instead (feature/workflow-specific)"
   - "Let me explain / provide more context"
4. **Scoped mode** — check `docs/context/README.md` for an existing brief with the same slug:
   - "Refresh this scoped brief" (re-probe, merge deltas)
   - "New scoped brief (different slug)"
   - "Let me explain / provide more context"
5. **If `in_progress`**: Report mode, slug, and phases completed. Ask resume or restart.
6. **If `failed`**: Report which phase failed. Ask retry / restart / abort.
7. **If project `skipped` or `pending`**: Start project mode fresh (unless user explicitly asked scoped).

### State updates

After each phase completes (or fails), immediately update `workflow-state.yaml`:
- Set `stages.00-context.mode` to `project` | `scoped`
- For scoped runs, set `stages.00-context.scoped_slug` and append path to §`artifacts[]`
- Set the phase status
- Update agent status after Phase 1A (project or scoped subset)
- Update ecosystem scan status after Phase 1B (**project mode only**)
- Update issue tracking after Phases 2 and 3
- Set overall status to `completed` after Phase 4

Scoped run schema (append to §`artifacts[]` and index in `docs/context/README.md`):

```yaml
# workflow-state.yaml §artifacts[] entry example
- path: docs/context/live-e2e-integration.md
  kind: context-scoped
  slug: live-e2e-integration
  topic: "Live E2E and integration tests for Render"
  created_at: "2026-06-22"
  status: active | superseded
```

Phase 1B state schema (project mode only):

```yaml
phase1b_ecosystem:
  status: completed | skipped | in_progress | failed
  org_directory: "<path>"
  repos_discovered: <N>
  repos_selected: [<names>]
  constraints_found: <N>
  patterns_adopted: <N>
  divergence_risks: <N>
```

### Commit-as-you-go

Commit artifacts to an appropriate branch before transitioning to the next stage or
asking the user a blocking question. Branch type per
[workflow-state-reference.md](../workflow-state-reference.md) §Git history.
Record every commit in `workflow-state.yaml` §`git_history.commits` with
`stage: "00-context"` and `mode: project | scoped`.

## Scoped context mode (features & workflows)

Use when the user adds a feature, prepares a workflow (live E2E, staging smokes, new
integration), or **16-evolve** invokes 00 for delta discovery.

**Do not merge into `docs/context-brief.md`.** Write a standalone scoped brief instead.

### Scoped workflow (abbreviated)

| Phase | Scoped behavior |
|-------|-----------------|
| 1A | Run only agents relevant to scope (repo explore, live URL probe, doc scan). Skip paper-analyst unless paper cited. |
| 1B | **Skip** unless scope is cross-repo integration |
| 1C | **Skip** — template already set in project |
| 2 | Cross-reference only sources touched by scope |
| 3 | AskQuestion for blocking decisions **about this scope** |
| 4 | Write scoped template (below) + update `docs/context/README.md` |

When invoked from **16-evolve**, set `evolve_cycle_id` and `feature_ids` in frontmatter and
state; link scoped brief from evolve artifact.

### When to add a pointer to the project brief

Only if `docs/context-brief.md` exists **and** the scoped work changes project-level facts
(e.g. new deployable, template drift). Add **at most** a single bullet under a
`## Scoped context briefs` section linking to `docs/context/README.md` — never inline the
scoped content.

## Workflow

### Phase 1A — Run Analysis Agents

Launch available agents in parallel using the Task tool:

**If paper provided — paper-analyst**:
- Invoke with the paper path
- Extract build, run, test, and config insights
- Use `subagent_type: "paper-analyst"` with appropriate model

**If repo provided — repo-researcher**:
- Invoke with the repository URL/path
- Produce comprehensive implementation guide
- Use `subagent_type: "repo-researcher"` with appropriate model

**If existing docs provided — doc-scanner**:
- Invoke with doc paths
- Extract requirements, architecture decisions, constraints, tech choices
- Use `subagent_type: "generalPurpose"`

Wait for all launched agents to complete. Store their full outputs.

**State**: Update agent status for all agents. Set Phase 1A to `completed`.

### Phase 1B — Ecosystem Scan (Sibling Repos)

**Project mode only.** Skip entirely in scoped mode unless the user explicitly requests
cross-repo integration discovery for the current scope.

Scan sibling repositories in the user's organization directory to identify integration
patterns, shared conventions, and dependencies this project must respect.

**When to run**: Project mode and the project belongs to a multi-repo organization.
If the user hasn't provided an org directory, ask:

```
Does this project belong to a multi-repo organization (e.g., a company or org with
other repos in a shared parent directory)?

- "Yes — here's the path: ..."
- "No — this is a standalone project"
- "Let me explain / provide more context"
```

If standalone, skip Phase 1B and set its status to `skipped`.

#### Step 1 — Discover sibling repos

List all directories in the org directory. For each, determine if it's a git repo
(check for `.git/`). Record the repo name and whether it appears active (has recent
commits).

#### Step 2 — Classify repos

For each discovered repo, do a lightweight scan (README, package manifest, entry points)
to classify it:

| Classification | Heuristics |
|----------------|------------|
| **Backend API** | Has server framework (FastAPI, Flask, Express), `routes/`, `endpoints/` |
| **Frontend app** | Has `package.json` with React/Vue/Svelte, `src/components/` |
| **Compute service** | Has Modal/Lambda/Cloud Run config, GPU-heavy deps |
| **Shared library** | Published package, imported by other repos |
| **Data/ML pipeline** | Has training scripts, model configs, dataset loaders |
| **Infrastructure** | Has Terraform, Docker Compose, CI/CD configs, MCP server |
| **Widget/embed** | Has embed script, iframe config, widget build |
| **Documentation** | Primarily markdown, blog posts, knowledge base |
| **Other** | Doesn't match above patterns |

Present the classification table to the user:

```
Found [N] sibling repos in [org_directory]:

| # | Repo | Classification | Key Indicators |
|---|------|----------------|----------------|
| 1 | back-end-api | Backend API | FastAPI, /routes |
| 2 | modal-boltz | Compute service | Modal, GPU deps |
| ...
```

#### Step 3 — User selects relevant repos

Ask the user which repos are relevant to the current project via AskQuestion.
**This is blocking** — the user's selection determines what gets scanned in depth.

```
Which of these repos does [current_project] need to integrate with or follow
patterns from?

Select all that apply:
- [each repo as a checkbox option]
- "None — this project is independent"
- "Let me explain / provide more context"
```

Also ask an open-ended question:

```
What should I look for in these repos? Common reasons:
- "API contracts this project must conform to"
- "Shared deployment patterns (Modal config, image builds, secrets)"
- "Naming conventions, code style, shared utilities"
- "Data flow — how this project sends/receives data from others"
- "Auth patterns — how services authenticate with each other"
- "All of the above"
- "Let me explain / provide more context"
```

#### Step 4 — Deep scan selected repos

For each user-selected repo, launch a `subagent_type: "explore"` agent to extract:

1. **Integration surface**: API endpoints, message schemas, event contracts, shared
   types/models that other repos consume or produce
2. **Deployment patterns**: Platform (Modal, Render, AWS, etc.), image build conventions,
   environment variable naming, secrets management, volume mounts
3. **Code conventions**: Package structure, naming patterns, linting/formatting config,
   import conventions, error handling patterns
4. **Data flow**: How data moves between this repo and others — REST calls, queue
   messages, shared databases, file handoffs, Modal volume paths
5. **Auth & networking**: How services authenticate with each other, **CORS / BFF / same-origin**
   for browser clients, internal vs external endpoints — record gaps in context brief per
   [connectivity-gates.md](../connectivity-gates.md) §Stage 00
6. **Shared dependencies**: Common libraries, pinned versions that must stay aligned,
   internal packages imported across repos

Run agents in parallel (one per selected repo). Each agent should return a structured
report following this schema:

```yaml
repo: <name>
classification: <type>
integration_surface:
  endpoints: [...]
  schemas: [...]
  events: [...]
deployment:
  platform: <name>
  image_pattern: <description>
  env_var_conventions: [...]
  secrets_pattern: <description>
code_conventions:
  package_structure: <description>
  naming: <description>
  linting: <tool and config>
data_flow:
  produces: [...]
  consumes: [...]
  shared_storage: [...]
auth:
  pattern: <description>
  internal_endpoints: [...]
shared_deps:
  pinned: [...]
  internal_packages: [...]
```

#### Step 5 — Synthesize ecosystem patterns

After all repo scans complete, synthesize findings into:

1. **Pattern inventory**: Conventions this project should follow to stay consistent
   with the ecosystem (naming, structure, deployment, error handling)
2. **Integration map**: Concrete integration points between this project and scanned
   repos (API calls, shared data, auth flows)
3. **Constraint list**: Hard requirements from sibling repos that constrain choices
   in this project (e.g., must use Modal, must conform to API schema v2, must use
   shared auth token format)
4. **Divergence risks**: Places where this project might diverge from org patterns
   and why that could cause problems

Surface any **Decisions** or **Ambiguities** discovered:
- `[Decision]` "Backend API expects response schema X, but this project's natural
  output is Y — adapt output, or update the API?"
- `[Ambiguity]` "Three repos use different Modal image base layers — which to follow?"

#### Step 6 — User confirms ecosystem constraints

Present the synthesized findings via AskQuestion, grouped:

**Hard constraints** (blocking — must resolve before proceeding):
```
Based on scanning [N] sibling repos, these constraints affect [current_project]:

[Constraint]: The backend API expects POST /api/v1/tools/deployed-service with schema {...}
  - "Adopt this contract as-is"
  - "Modify — I'll specify changes"
  - "Ignore — this project won't integrate with the backend"
  - "Let me explain / provide more context"
```

**Recommended patterns** (advisory):
```
These org-wide patterns were found. Adopt them?

[Pattern]: Modal services use `modal.Image.debian_slim().pip_install(...)` pattern
  - "Adopt"
  - "Skip — I have a reason to diverge"
  - "Let me explain / provide more context"
```

Record all resolutions in the Resolution Log (continuing the R-numbering from Phase 1A).

**State**: Update ecosystem scan status and issue tracking. Set Phase 1B to `completed`.

### Phase 1C — Template Classification

**Project mode only.** Skip in scoped mode — read existing `workflow-state.yaml` §`template`.

After Phase 1B (or immediately after Phase 1A if 1B was skipped), classify the project
against the [template registry](../template-registry.md) to select a scaffold.

#### Step 1 — Gather classification signals

From all available evidence (agent reports, ecosystem scan, user description), collect:

- **Runtime profile**: Seconds (utility) vs minutes-to-hours (job)
- **GPU requirement**: None/optional (utility) vs required (job)
- **Model weights**: None (utility) vs downloaded on startup (job)
- **State**: Stateless per-request (utility) vs persistent cache volume (job)
- **Job manager**: Not needed (utility) vs `i_am_running()` integration (job)
- **Output format**: `dict` (utility) vs `Tuple[str, bytes]` (job)

#### Step 2 — Classify

Compare signals against the heuristics in `template-registry.md` §Classification
Heuristics. Assign a confidence level:

| Confidence | Criteria |
|------------|----------|
| **High** | All signals align with one template type |
| **Medium** | Most signals align but 1–2 are ambiguous |
| **Low** | Mixed signals or novel project type |

#### Step 3 — Confirm with user

Present classification via AskQuestion:

```
prompt: "Template classification:
  Project type: [utility / job]
  Confidence:   [high / medium / low]
  Signals:      [bullet list of evidence]
  Template:     template-modal-[utility/job]

  Is this correct?"

options:
  1. "Correct — use this template"
  2. "Wrong type — should be [utility/job instead]"
  3. "Neither — this project doesn't fit these templates"
  4. "Let me explain / provide more context"
```

If overridden by the user, record `overridden_by_user: true` in state.

#### Step 4 — Record template selection

Update `workflow-state.yaml` with the template block:

```yaml
template:
  id: utility | job | none
  repo: template-rag-api | template-rag-worker | null
  selected_at: 00-context
  classification_confidence: high | medium | low
  overridden_by_user: false | true
  gpu_tiers: []
  service_name: ""
```

If a job template is selected, ask which deploy targets to include. Use the full Modal catalog in
[deployment-catalog.md](../deployment-catalog.md) — do not omit tiers that Modal publishes.

```
prompt: "Which deploy targets should this job service support? (Each tier becomes a Modal class
  variant per entry point, e.g. PipelineT4, PipelineH200.)"

options (multi-select; default = all):
  - All tiers — full spread (recommended for production APIs)
  - T4 ($0.000164/s — budget inference, smokes)
  - L4 ($0.000222/s)
  - A10 ($0.000306/s)
  - L40S ($0.000542/s)
  - A100 40GB ($0.000583/s)
  - A100 80GB ($0.000694/s)
  - H100 ($0.001097/s)
  - H200 ($0.001261/s)
  - B200 ($0.001736/s)
  - RTX PRO 6000 ($0.000842/s)
```

If the user selects **All tiers**, set `template.gpu_tiers` to every **tier key** from
deployment-catalog.md (B200, H200, H100, RTX_PRO_6000, A100_80, A100_40, L40S, A10, L4, T4).
Otherwise record only the selected tier keys.

Record the selected tiers in `template.gpu_tiers`.

Also ask for the service name (the `{{SERVICE_NAME}}` replacement value):

```
prompt: "What should the service name be? This becomes the service name
  (cognichem-[name]) and repo name (modal-[name]).
  Example: 'boltz', 'rdkit', 'autodockvina'"
```

Record in `template.service_name`.

**State**: Set Phase 1C to `completed`.

### Phase 2 — Cross-Reference & Detect Issues

Systematically compare agent reports (including ecosystem scan results from Phase 1B
when available). Run seven scans:

1. **Contradiction scan**: Align claims from all sources on shared topics
2. **Ambiguity scan**: Identify under-defined terms, metrics, procedures
3. **Decision scan**: Find points where sources describe multiple approaches
4. **Bloat scan**: Identify tangential content
5. **Uncertainty scan**: Note facts cited by only one source with no corroboration
6. **Data & asset scan**: Identify all external data assets (corpus fixtures, datasets,
   checkpoints, tokenizers, embeddings) with source, size, auth requirements, and
   where code loads them
7. **Ecosystem alignment scan** (if Phase 1B ran): Compare this project's planned
   approach against ecosystem patterns. Flag where the project would diverge from
   established org conventions (deployment, naming, API shape, auth, data flow)

**State**: Update issue tracking with counts. Set Phase 2 to `completed`.

### Phase 3 — Surface Issues to User

Collect all issues from Phase 2. Batch into AskQuestion calls grouped by category.

For each issue:
1. Lead with category label: `[Contradiction]`, `[Decision]`, etc.
2. Include evidence with citations: `[Paper §X]`, `[Repo: path/to/file:L10-20]`
3. Provide a recommended option as first choice
4. Include "Let me explain / provide more context" as last option

Wait for responses to all blocking issues. For advisory issues without response, adopt
the recommended option and mark with `⚠️ Assumed:`.

Record all resolutions in a **Resolution Log**:

```
Resolution Log:
  R1: [Contradiction] Dataset split — User chose: paper's spec (SAbDab 90/10)
  R2: [Bloat] Visualization notebook — User chose: Exclude from scope
  ...
```

**ADR logging**: For each resolved `[Decision]`, `[Contradiction]`, or `[Ambiguity]`
that selects between multiple valid approaches, create an ADR in `docs/adr/` per
[considerations.md](../considerations.md) §ADR logging. Set the Stage field to
`00-context`. Reference the resolution number (R1, R2, ...) in the ADR's Context section.

**State**: Update issue tracking. Set Phase 3 to `completed`.

### Phase 4 — Produce Context Brief

Write the brief for the active mode. **Never write scoped content to `context-brief.md`.**

#### Project mode — `docs/context-brief.md`

1. **Executive Summary** — 3-5 sentence overview of what was analyzed
2. **Template Selection** — selected template ID, repo, confidence, service name,
   deploy targets (if job), user override status. References `template-registry.md`.
3. **Resolution Log** — numbered resolutions from Phases 1B, 1C, and 3
4. **Source Analysis Summaries** — key findings per source (paper, repo, docs)
5. **Ecosystem Analysis** (if Phase 1B ran):
   - **Scanned repos** — table of repos scanned with classifications
   - **Integration map** — concrete integration points with this project
   - **Pattern inventory** — conventions this project should follow
   - **Constraint list** — hard requirements from sibling repos
   - **Divergence risks** — where this project may break org consistency
6. **Cross-Reference Matrix** — alignment table across sources (including ecosystem)
7. **Data & Asset Requirements** — inventory of external assets needed
8. **Unresolved Gaps** — flagged for downstream handling
9. **Scoped context briefs** — link to `docs/context/README.md` (index only; no inline copies)
10. **Full Agent Reports** — collapsible sections with raw agent outputs (including
   ecosystem scan reports)

#### Scoped mode — `docs/context/<slug>.md`

Use this **lighter template** (omit sections that don't apply):

```markdown
# Context — <Topic Title>

> **Mode**: scoped | **Slug**: <slug> | **Generated**: YYYY-MM-DD
> **Feature / workflow**: <one line> | **Status**: active

## Executive Summary
3-5 sentences: what was analyzed, current state, main gap.

## Resolution Log
| ID | Category | Decision |
|----|----------|----------|

## Scope & Constraints
What is in/out for this feature or workflow. Link feature id (F1–F4, M*, etc.).

## Environment / Topology (if relevant)
URLs, services, env vars, CORS — only what this scope needs.

## Existing Infrastructure
Table: what already exists in repo (tests, scripts, configs) with paths.

## Cross-Reference Matrix
Scope-specific alignment table.

## Implementation Backlog
Numbered gaps → suggested next steps (for 07-build / hotfix).

## Data & Credentials (if relevant)
Assets, secrets source, never commit rules.

## Unresolved Gaps
Advisory items for downstream.

## Sources
Citations: [Repo: path], [Docs: path], live probe timestamps.
```

**Index update** — append or update row in `docs/context/README.md`:

| Slug | Topic | Status | Created | Linked features |
|------|-------|--------|---------|-----------------|

**State**: Set Phase 4 to `completed`. Set overall status to `completed`.
For scoped runs, do **not** mark `stages.00-context` as blocking 01-requirements if project
brief already exists — scoped completion is additive.

### Phase 5 — Summary

Report to user (adapt by mode):

```
Context Gathering Complete.

Mode:       [project | scoped]
Written to: [docs/context-brief.md | docs/context/<slug>.md]
Index:      docs/context/README.md (scoped only)

Sources analyzed:
  [list with key metrics]

[Project mode only — Template, Ecosystem scan blocks]

[Scoped mode only]
Scope:      [topic]
Backlog:    [N] implementation items
Ready for:  [07-build | 10-e2e | 16-evolve | user-directed next step]

Issues surfaced: [N] total
  Blocking — [N] raised, [N] resolved
  Advisory — [N] raised, [N] assumed
```

If Phase 1B was skipped, omit the "Ecosystem scan" block.
If template is `none`, omit "deploy targets" line.
If scoped mode and project brief exists, note: "Project brief unchanged."

## Output Rules

1. **Evidence-based**: Every claim traces to an agent report or live probe. Never fabricate.
2. **Citation format**: `[Paper §X]`, `[Repo: path/to/file:L#]`, `[Docs: path]`
3. **Full reports preserved**: Complete agent outputs in collapsible sections (**project mode**).
   Scoped mode: summaries only — link to repo paths instead of pasting large dumps.
4. **Resolution traceability**: Numbered resolutions (R1, R2, ...) per brief file.
5. **No silent resolution**: Never resolve blocking issues without user input.
6. **State-managed**: All progress tracked in `workflow-state.yaml`. Immediate writes.
7. **No bloat**: Scoped findings go to `docs/context/<slug>.md` only; project brief stays
   stable unless user explicitly runs project-mode update/regenerate.
