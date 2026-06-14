<!-- TEMPLATE: user-journeys.md -->
# User Journeys

> **Project**: [project name]
> **Source**: [feature-list.md], [api-contract.md], [requirements-decisions.md or research-brief.md]
> **Last updated**: [YYYY-MM-DD]

Product-facing journeys describe what a **caller** does — not internal module tests.
Each journey maps to automated E2E tests (`tests/e2e/`) and a stage **11-verify-impl**
interview prompt.

## Journey Index

| ID | Journey | Entry point | Feature | E2E tier |
|----|---------|-------------|---------|----------|
| UJ-001 | [Short title] | [Class.method or CLI] | F# | local / modal / both |

**E2E tier** (define per project):

- **local** — CPU, no cloud/GPU; core logic and mocks.
- **modal** — Deployed app + GPU (or equivalent production path).

Run all local E2E: `[command]`

## Journey Details

### UJ-001: [Journey title]

**Actor**: [who invokes the system]

**Goal**: [outcome in one sentence]

**Steps**:

1. ...
2. ...
3. ...

**Acceptance**: [Link to acceptance-criteria.md §feature or inline measurable criteria]

**Automated tests**: `tests/e2e/test_uj001_[slug].py` ([local / modal])

**Interview (11)**: "[Single question for human verification in 11-verify-impl]"

---

<!-- Repeat ### UJ-NNN sections for each journey -->
