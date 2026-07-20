---
name: doc-planner
description: >
  Plans and generates spec-driven development documents (roadmap, test plan, ADRs, feature list,
  API spec, etc.) for a repository. Requires the gather-context skill to have been run first —
  consumes the Research Brief it produces. Synthesizes findings into a prioritized document
  manifest for human review, then generates approved documents from templates.
  Use when the user wants to create project documentation, plan specs, generate a doc suite,
  or build a documentation roadmap for a codebase that has an associated research paper.
---

# Doc Planner

Plan and generate spec-driven development documents by consuming the Research Brief produced by
the [gather-context](../gather-context/SKILL.md) skill.

**Cross-cutting:** [considerations.md](../considerations.md) — feedback loops, release notes,
performance planning, spec vs code root cause.

## Prerequisite — Gather Context

This skill requires the **gather-context** skill to have been run first. Before starting:

1. Check if `{output_directory}/research-brief.md` exists.
2. **If it exists**: Read it. Ask the user whether to reuse it or re-run gather-context.
3. **If it does not exist**: Invoke the [gather-context](../gather-context/SKILL.md) skill with
   the same inputs (repository URL, paper path, output directory). Wait for it to complete.

## State management

**Canonical:** repo-root [`workflow-state.yaml`](../../workflow-state.yaml) §`stages.doc-planner`.
Rules: [workflow-state-reference.md](../workflow-state-reference.md).

On invocation: read §`stages.doc-planner`; on manifest approval and each generated doc, update
substeps and append paths to top-level `artifacts`. If the project uses pipeline
`01-requirements` instead, set `stages.doc-planner.status: skipped` and do not duplicate work.

The Research Brief provides:
- Paper-analyst and repo-researcher reports (full text in collapsible sections)
- Cross-Reference Matrix (paper vs repo alignment on key topics)
- Resolution Log (numbered resolutions from user decisions, R1, R2, ...)
- Unresolved Gaps (flagged for downstream handling)

All subsequent phases consume this Research Brief as their primary evidence source.

## Uncertainty Resolution Protocol

Follow [gather-context — Uncertainty Resolution Protocol](../gather-context/SKILL.md#uncertainty-resolution-protocol).
Extend the Resolution Log from the last gather-context ID (e.g. R5 → R6). Also apply
[considerations.md](../considerations.md).

## Inputs

Collect these from the user (check README.md, conversation context, or ask):

1. **Repository URL** — GitHub URL of the target codebase
2. **Paper path** — local path to the research paper (JATS XML, PDF, or markdown)
3. **Output directory** — where to write generated docs (default: `docs/` in the repo root)

## Workflow

### Phase 1 — Synthesize and Recommend

Analyze the Research Brief — incorporating the Resolution Log and Cross-Reference Matrix from
gather-context — and determine which document types are relevant to this project.

#### Mandatory documents

The following documents are **always included** in the manifest regardless of relevance scoring.
They cannot be excluded or skipped in Phase 2:

| Document | Template | Rationale |
|----------|----------|-----------|
| **Deployment Integration Plan** | merged into `docs/deploy.md` §Integration | API, Postgres, secrets, CI/CD, observability per [deployment-catalog.md](../deployment-catalog.md). |
| **Data Management Plan** | [templates/data-management-plan.md](templates/data-management-plan.md) | Schema migrations, seed corpus, eval fixtures, and verification before build. Consumed by the [data-management](../data-management/SKILL.md) skill. |
| **User Journeys** | [templates/user-journeys.md](templates/user-journeys.md) | Caller-facing flows (UJ-IDs): ingest, query, admin. Generate after `feature-list.md` / `api-contract.md`, before `test-plan.md`. |
| **README.md** | (synthesized, no template) | The public-facing entry point for the project. Synthesized from all generated specs into a user-facing README with install, usage, configuration, and examples. This is different from internal specs — it's what users see first. |

The Uncertainty Resolution Protocol still applies to mandatory documents — surface any
decisions, ambiguities, or contradictions found while evaluating them, but the document itself
is never a candidate for exclusion.

#### Evaluating other document types

For each document type listed in [doc-types.md](doc-types.md) (with templates in [templates/](templates/)), evaluate:

- **Relevance**: Does the paper/repo analysis contain enough material to justify this document?
- **Priority**: How critical is this document for someone trying to use, extend, or contribute?
- **Confidence**: How much of the document can be auto-generated vs needs human input?
- **Performance testing**: If the paper reports benchmarks, latency targets, or throughput
  metrics, ensure the test plan includes performance test cases with measurable thresholds.
  If the paper implies performance matters but gives no concrete targets, surface as
  `[Ambiguity]` — verify-build needs explicit thresholds to run its performance agent.

While building the manifest, apply the Uncertainty Resolution Protocol:

- If a document's relevance is debatable (e.g., the evidence is thin or the project type doesn't
  clearly fit the template's "when relevant" criteria), flag it as a **[Decision]** or **[Bloat]**
  issue.
- If two documents would substantially overlap in content given this project's scope, flag it as
  **[Bloat]** and recommend consolidating or skipping.
- If the priority or confidence rating depends on an unresolved question from the paper or repo,
  flag it as **[Ambiguity]** or **[Uncertainty]**.

**Performance and scalability (planning):** When the Research Brief implies latency, throughput,
cost, GPU memory, or batch sizing, the manifest must include documents (typically `test-plan.md`,
`spec.md`, `deployment-integration.md`) that define measurable targets or benchmark/smoke procedures.
If evidence is insufficient to state SLOs or perf test commands, surface **[Ambiguity]** rather
than omitting perf — see [considerations.md §4](../considerations.md#4-performance-testing).

Batch all manifest-level issues into a single AskQuestion call and wait for blocking responses.

Then produce a **Document Manifest** — a ranked table. Include a new **Issues** column that
references any resolved or outstanding issues:

```markdown
## Document Manifest

### Mandatory
| # | Document | Priority | Confidence | Issues | Rationale |
|---|----------|----------|------------|--------|-----------|
| 1 | Deployment Integration Plan | High | High | — | Mandatory — API, DB, deploy target |
| 2 | Data Management Plan | High | High | — | Mandatory — migrations + corpus fixtures before RAG tests |
| 3 | User Journeys | High | High | — | Mandatory — caller-facing flows; feeds test-plan and 10-e2e |
| 4 | README.md | High | High | — | Mandatory — public-facing entry point, synthesized from all specs |

### Recommended
| # | Document | Priority | Confidence | Issues | Rationale |
|---|----------|----------|------------|--------|-----------|
| 2 | Test Plan | High | High | R1 applied | Paper describes 5 validation experiments with metrics |
| 3 | Feature List | High | High | — | Repo has clear pipeline stages, paper defines capabilities |
| 4 | ADR: Model Architecture | Medium | Medium | R3 assumed | Paper describes design choices with alternatives |
| ... | ... | ... | ... | ... | ... |

### Excluded Documents
- **API Contract**: Not applicable — no REST/gRPC API found
- **Migration Plan**: Skipped per R2 — research tool, no persisted state
```

### Phase 2 — Present for Review

Present the manifest to the user.

**Mandatory documents** (e.g., Deployment Integration Plan) are presented with only two options:

- **Approve** — generate this document as planned
- **Modify** — user will describe changes to scope or content

They cannot be skipped.

**All other documents** are presented with three options:

- **Approve** — generate this document
- **Skip** — don't generate it
- **Modify** — user will describe changes to scope or content

If the user modifies any document, incorporate their feedback into the generation plan.

After all documents are reviewed, summarize the final plan:

```
Final Plan:
  Approved:  6 documents
  Skipped:   2 documents
  Modified:  1 document (Test Plan — user wants to focus on smoke tests only)
```

### Phase 3 — Generate Documents

For each approved document, in priority order:

1. Read the corresponding template file from [templates/](templates/) (e.g., `templates/user-journeys.md`,
   `templates/test-plan.md`, `templates/adr.md`). Use [doc-types.md](doc-types.md) for relevance
   criteria and path conventions. **Generate `user-journeys.md` before `test-plan.md`** so TC-IDs
   can reference UJ-IDs.
2. Fill the template using evidence from the Research Brief (including the full agent reports
   in its collapsible sections). Cite sources:
   - Paper references: `[Paper §2.3]` or `[Paper Table 2]`
   - Repo references: `[Repo: path/to/file:L10-20]`
3. **Apply the Resolution Log**: For every section that touches a resolved issue from
   gather-context or Phase 1, use the user's chosen resolution. For advisory issues where the recommendation
   was assumed, mark the section with `⚠️ Assumed:` and state the assumption.
4. **Surface new issues**: During generation, new issues may emerge that were not caught in
   earlier phases (e.g., a template section requires data that neither agent provided, or filling
   in details reveals a new contradiction). For each:
   - If **blocking** (Decision, Contradiction, Ambiguity): pause generation of this document,
     surface via AskQuestion with findings and a recommendation, wait for the user's response,
     then continue.
   - If **advisory** (Bloat, Uncertainty): note the issue inline with `⚠️ Assumed:` or
     `⚠️ Uncertain:` and continue. Batch advisory issues to report after the document is written.
5. Flag remaining gaps with `⚠️ Needs human input:` prefix where the agents didn't provide
   enough detail and no assumption is reasonable.
6. Write the document to the output directory.
7. After each document is written, briefly report what was generated, any new issues surfaced,
   assumptions made, and gaps flagged.

### Phase 3.5 — Generate README

After all spec documents are written, synthesize them into the project's `README.md`. This is
the public-facing entry point — not an internal spec. It should be readable by someone who has
never seen the paper or the specs.

Pull content from the generated docs:

| README Section | Source |
|----------------|--------|
| **Title & description** | Research Brief §Executive Summary |
| **Installation** | dependency-inventory.md §Runtime Dependencies, config-spec.md |
| **Data setup** | data-management-plan.md §Asset Inventory, §Quick Start (download commands, expected sizes, verification) |
| **Quick start** | spec.md §Pipeline Stages (simplest invocation) |
| **Usage / CLI** | config-spec.md §CLI Flags, spec.md §Component Details |
| **Configuration** | config-spec.md §Configuration Files, §Environment Variables |
| **Examples** | test-plan.md §Recommended Test Cases (adapted as usage examples) |
| **Deployment** | deployment-integration.md §Migration Checklist (condensed) |
| **Architecture** | spec.md §System Architecture (brief overview) |
| **Citation** | Research Brief §Paper Summary (BibTeX if available) |
| **License** | Research Brief §Repository Analysis (from repo-researcher) |

Apply the Uncertainty Resolution Protocol: if a README section requires information not
present in any spec, surface it as `[Ambiguity]` rather than leaving the section empty
or guessing.

Write to `README.md` in the repo root (not in `docs/`). This overwrites the existing stub.

### Phase 4 — Summary

After all documents are generated, produce a final summary that includes the Resolution Log
and a tally of all issues surfaced:

```
Doc Planner Complete.

Generated:
  docs/deploy.md §Integration    — 2 gaps, 1 assumption  [mandatory]
  docs/spec.md §Data    — 1 gap, 0 assumptions  [mandatory]
  docs/user-journeys.md        — [N] journeys, [N] gaps  [mandatory]
  docs/test-plan.md            — 3 gaps, 1 assumption
  docs/feature-list.md         — complete
  docs/adr/001-model-arch.md   — 1 gap, 1 assumption
  docs/roadmap.md              — 5 gaps
  docs/config-spec.md          — complete
  docs/dependency-inventory.md — 1 assumption
  README.md                    — synthesized from specs  [mandatory]

Total: 9 documents (3 mandatory + 6 approved), 12 gaps needing human review, 4 assumptions made.

Resolution Log (7 issues surfaced):
  Blocking — 4 raised, 4 resolved by user
  Advisory — 3 raised, 0 responded to (recommendations assumed)

Run `grep -r "⚠️" docs/` to find all gaps, assumptions, and uncertainties.

Next step: run audit-docs to verify all statements before implementation.
```

## Next Step — Audit Docs

After doc-planner completes, the [audit-docs](../audit-docs/SKILL.md) skill should be
invoked to:

- Break each generated document into provable (falsifiable) statements
- Walk the user through each statement for approval, denial, or modification
- Update source documents with corrections
- Produce an audit report and decision log

After audit-docs completes, the [build-planner](../build-planner/SKILL.md) skill creates
the execution plan from the audited specs.

## Output Rules

1. **Evidence-based**: Every claim in a generated doc must trace back to the Research Brief
   (paper-analyst or repo-researcher output). Never fabricate details.
2. **Gap-aware**: Clearly mark sections that need human input rather than guessing.
3. **Consistent format**: All documents follow the templates in `templates/`.
4. **Atomic files**: Each document is a standalone markdown file, not a monolith.
5. **ADR numbering**: ADRs use sequential numbering (`001-`, `002-`, etc.) in a `docs/adr/` subdirectory.
6. **Never silently resolve ambiguity**: If you encounter a decision, ambiguity, contradiction,
   bloat concern, or uncertainty at any point in the workflow, you must surface it to the user
   via AskQuestion with evidence and a recommendation per the Uncertainty Resolution Protocol.
   Silently picking an answer without user awareness violates this skill's contract. The only
   exception is advisory issues (Bloat, Uncertainty) where the user does not respond; in that
   case, proceed with the recommendation but mark it with `⚠️ Assumed:` in the generated
   document.
7. **Cite the resolution**: When a document section was shaped by a user resolution, include
   a brief inline citation (e.g., `(per Resolution R1)`) so the user can trace why a particular
   choice was made.
