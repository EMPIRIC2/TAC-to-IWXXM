---
name: 02-verify-plan
description: >
  Verifies product plan documents by breaking them into provable statements, risk-classifying
  each (high/medium/low confidence), auto-approving high-confidence statements derived from
  user's own answers, and presenting medium/low confidence statements for user review. Includes
  embedded consistency checking across all spec documents. Produces audit report and decision log.
---

# 02 — Verify Product Plan

Break spec documents into provable statements, risk-classify each, and walk the user through
medium/low confidence statements for approval/denial/modification.

**Preamble:** [pipeline-preamble.md](../pipeline-preamble.md) — shared conventions for stages 00–17.
**Cross-cutting:** [considerations.md](../considerations.md), [connectivity-gates.md](../connectivity-gates.md).
**State agent:** [workflow-state-manager](../../agents/workflow-state-manager.md) — mandatory read/update.

## Connectivity (stage 02)

When auditing product specs, include **falsifiable statements** such as:

- “Staging smoke is only `GET /health`” → **deny** for UI products; require H4–H5 in test-plan
- “E2E is covered by Vitest component tests” → **deny** as sole live proof; mocks ≠ CORS
- “Frontends and APIs share one origin” → verify against deployment-integration topology

Flag contradictions where `user-journeys.md` describes browser flows but `test-plan.md` has no
connectivity tiers. Record fixes in audit report before 03-plan-tooling.

## Prerequisites

1. **01-requirements** must be `completed`. Spec documents must exist in `docs/`.
2. At minimum: `docs/feature-list.md`, `docs/spec.md`, `docs/user-journeys.md`,
   `docs/test-plan.md`.
3. `docs/requirements-decisions.md` — the interview decision log from 01-requirements.

If any prerequisite is missing, inform the user and invoke 01-requirements first.

## Uncertainty Resolution Protocol

Follow [considerations.md](../considerations.md) §Uncertainty. Issues found during
verification are surfaced via AskQuestion with category labels.

## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).
**Stage key:** `stages.02-verify-plan`.

Invoke **workflow-state-manager** `read_context` before any other action; `update` after each
substep. **Do not** edit `workflow-state.yaml` directly.


### On invocation — check state

1. Use **workflow-state-manager** context brief for §stages.02-verify-plan (from agent `read_context`).
2. **If `completed`**: Ask: "Reuse existing audit, or re-run?"
3. **If `in_progress`**: Report which document/statement paused at. Ask:
   "Resume from where we left off, or restart?"
4. **If `pending`**: Start fresh.

### Idempotency

Progress is never lost. Every verdict is written to the decision log and state
immediately after the user responds.

### Commit-as-you-go

Commit artifacts to an appropriate branch before transitioning to the next stage or
asking the user a blocking question. Branch type per
[workflow-state-reference.md](../workflow-state-reference.md) §Git history.
Record every commit in `workflow-state.yaml` §`git_history.commits` with
`stage: "02-verify-plan"`.

## Delta / feature-addition mode

During evolve / feature addition:

- Run **full consistency pass** across all spec docs (contradictions hide at boundaries).
- Audit changed sections plus any doc referencing new/changed Fn or API identifiers.
- Block on `[Contradiction]` via AskQuestion before downstream stages proceed.

## Workflow

### Phase 1 — Inventory Documents

Read all spec documents from the output directory. Build an ordered audit list:

| # | Document | Path | Sections | Statements | Status |
|---|----------|------|----------|------------|--------|
| 1 | Feature List | docs/feature-list.md | [N] | [N] | pending |
| 2 | Spec | docs/spec.md | [N] | [N] | pending |
| 3 | User Journeys | docs/user-journeys.md | [N] | [N] | pending |
| 4 | Test Plan | docs/test-plan.md | [N] | [N] | pending |
| ... | ... | ... | ... | ... | ... |

Audit mandatory documents first, then by priority from the manifest.

Skip `requirements-decisions.md` (reference input, not a spec to audit) and
`context-brief.md` (input, not output).

### Phase 2 — Extract Provable Statements

When a statement covers **runtime validation** or **deploy behavior**, cross-check
`docs/hotfix-log.md` and `docs/incidents/`. If a hotfix superseded the statement, create
a Low-confidence follow-up: "Statement may be stale post-hotfix #N" with link to incident.

For each document, read section-by-section and extract **provable statements** —
claims that are falsifiable.

#### What counts

| Type | Example | Why provable |
|------|---------|-------------|
| Feature claim | "The system supports batch processing of up to 100 items" | Could be wrong about the limit |
| Architecture claim | "The API uses a REST architecture with JSON responses" | Could be GraphQL, could be XML |
| Dependency | "Requires Python >= 3.10" | Verifiable against setup files |
| Pipeline order | "Authentication runs before authorization" | Could be reversed |
| Performance target | "Response time under 200ms at p95" | Measurable |
| Config mapping | "The `--verbose` flag enables debug logging" | Testable |
| Scope claim | "The MVP includes 3 user roles" | Could be more or fewer |
| Assumed fact | "⚠️ Assumed: Redis is used for caching" | Explicitly uncertain |

#### What is NOT provable (skip)

- Section headers and labels
- Template boilerplate
- Subjective guidance
- References/citations themselves

#### Statement format

```
S[doc#].[stmt#]:
  Document: [doc name]
  Section:  [section path]
  Statement: "[exact claim, quoted]"
  Source: User interview / Context brief / Inferred / Assumed
  Confidence: High / Medium / Low
```

### Phase 3 — Risk Classification

Classify each statement's confidence level:

| Confidence | Criteria | Action |
|------------|----------|--------|
| **High** | Derived directly from user's own interview answer. The user explicitly stated this fact. Traceable to `requirements-decisions.md`. | **Auto-approve.** Log in audit report with verdict `auto-approved (high confidence)`. |
| **Medium** | Synthesized or inferred by the agent from user answers. Reasonable inference but not directly stated. | **Present to user** for review. |
| **Low** | From context-brief, assumed by agent, or generated to fill a template gap. Marked with `⚠️ Assumed:` or `⚠️ Inferred:`. | **Present to user** for review. |

**Classification evidence**: For each statement, cite the specific source:
- High: "User stated in interview batch 3, Q2: '[exact answer]'"
- Medium: "Inferred from user's answer about X combined with template section Y"
- Low: "From context-brief R3" or "Agent-generated to fill gap in §Z"

### Phase 4 — Consistency Check (Embedded)

Before presenting statements to the user, run cross-document consistency checks:

1. **Feature ↔ Spec**: Every feature in feature-list.md maps to at least one component
   in spec.md
2. **Feature ↔ Journey**: Every in-scope feature has at least one UJ-NNN in user-journeys.md
3. **Journey ↔ Test**: Every UJ-NNN in user-journeys.md appears in test-plan.md (E2E section
   or TC table); journey IDs are consistent (UJ-001, not "journey 1")
4. **Feature ↔ Test**: Every feature has at least one test case in test-plan.md
5. **Spec ↔ Config**: Config defaults in config-spec.md match descriptions in spec.md
6. **Test ↔ Acceptance**: Test cases cover all acceptance criteria
7. **Cross-doc naming**: Same concepts use same names across documents
8. **Scope boundaries**: No document claims features that another document excludes
9. **Template conformance** (if template selected): Read `workflow-state.yaml` §template
   and [template-registry.md](../template-registry.md). Verify:
   - Spec architecture matches template type (utility specs shouldn't claim GPU usage
     or `@modal.enter()` unless the template is `job` or user overrode)
   - Deployment claims match template CI/CD pattern
   - API patterns match template function signatures
   - If template is `job`, spec includes model weight management and GPU allocation for
     every tier in [deployment-catalog.md](../deployment-catalog.md) or an explicit prune list
     in `workflow-state.yaml` §template.gpu_tiers
   - If template is `utility`, spec doesn't include volumes or warmup lifecycle

For each inconsistency found, create an additional statement at Low confidence with
category `[Contradiction]` and present it to the user.

### Phase 5 — Walk Through Statements

Process statements in two passes:

#### Pass 1 — Auto-approve high confidence

Log all high-confidence statements as `auto-approved`. Report the count:

```
Auto-approved: [N] high-confidence statements
  (These were derived directly from your interview answers.)

Remaining for review: [N] medium-confidence, [N] low-confidence
```

#### Pass 2 — Present medium/low confidence

For each medium or low confidence statement, present via AskQuestion:

```
prompt: "[S1.3] From Spec, §System Architecture (Confidence: Medium):
  'The system uses a microservice architecture with 4 services communicating via gRPC.'
  Source: Inferred from your description of 'separate services for auth, data, processing,
  and frontend' in interview batch 2.

  Progress: Document 1/5, Statement 3/8 remaining (37% of review complete)"

options:
  1. "Approve — this statement is correct"
  2. "Deny — this statement is incorrect, remove or flag it"
  3. "Modify — I'll provide the correct version"
  4. "Skip for now — come back to this later"
```

#### Processing verdicts

**Approve**: Mark as approved. No changes to source document.

**Deny**: Mark as denied. In the source document:
- Remove the claim if entirely wrong
- Or replace with `⚠️ Denied in audit (S1.3): [original] — User: "[feedback]"`

**Modify**: User provides corrected version. Update both audit report and source document.

**Skip**: Mark as `skipped`. Revisit in second pass after all other statements.

#### After each verdict

1. Update `workflow-state.yaml` — increment counters, advance position
2. Append to `docs/product-decisions.md`
3. Update `docs/product-audit.md` with verdict
4. If Deny or Modify: update the source spec document surgically
5. If the verdict resolves a `[Decision]`, `[Contradiction]`, or `[Ambiguity]` between
   multiple valid approaches (including Deny or Modify that changes an architectural
   choice), create an ADR in `docs/adr/` per [considerations.md](../considerations.md)
   §ADR logging. Set the Stage field to `02-verify-plan`. Reference the statement ID
   (e.g., S1.3) in the ADR's Context section.

#### Between documents

Report document summary:

```
Document 2 of 5 complete: Spec
  Total statements: 15
  Auto-approved (high): 9
  Reviewed: 6 (4 approved, 1 denied, 1 modified)

  Moving to Document 3: Test Plan
```

### Phase 6 — Second Pass (Skipped)

If any statements were skipped, ask: "Review [N] skipped statements now, or leave
as pending?" Process if the user chooses to review.

### Phase 7 — Create Audit Artifacts

Write to output directory:

1. **`docs/product-audit.md`** — Full audit report: per-statement records with section,
   claim, source, confidence, verdict, user feedback, action taken.

2. **`docs/product-decisions.md`** — Chronological decision log: timestamped table of
   every verdict (auto-approved, user-approved, denied, modified, skipped).

### Phase 8 — Summary

```
Product Plan Verification Complete.

Results:
  Documents audited: [N]
  Total statements: [N]

  Auto-approved (high confidence): [N] ([%])
  User-approved (medium/low):     [N] ([%])
  Denied:                          [N] ([%])
  Modified:                        [N] ([%])
  Skipped:                         [N] ([%])

  Consistency issues found: [N]
  Consistency issues resolved: [N]

Source documents updated: [N] changes across [M] documents

Artifacts:
  docs/product-audit.md      — full audit report
  docs/product-decisions.md  — decision log
  docs/adr/                  — [N] ADRs created from audit verdicts

Next step: 03-plan-tooling
```

**State**: Set status to `completed`.

## Output Rules

1. **Risk-based filtering**: Never present high-confidence statements for manual review
   unless the consistency check flagged them.
2. **Progress visible**: Every question shows position and completion percentage.
3. **Immediate persistence**: Write to all artifacts after every verdict.
4. **Surgical source updates**: Change only the specific claim, not surrounding content.
5. **Falsifiable only**: Do not extract non-falsifiable content.
6. **Cite the source**: Every statement notes its origin and confidence rationale.
7. **Consistency is embedded**: Cross-document checks run as part of this skill, not as
   a separate invocation.
