---
name: 10-e2e
description: >
  Verifies that user journeys from product requirements work end-to-end. Mechanism is adaptive:
  browser automation for web apps, API calls for services, shell execution for CLIs, import/call
  for libraries. Runs asynchronously in parallel with 09-qa. Results collected by 11-verify-impl.
---

# 10 — E2E Behavior Verification

Verify that user journeys described in product requirements actually work end-to-end.

**Preamble:** [pipeline-preamble.md](../pipeline-preamble.md) — shared conventions for stages 00–17.
**Cross-cutting:** [considerations.md](../considerations.md), [connectivity-gates.md](../connectivity-gates.md).
**State agent:** [workflow-state-manager](../../agents/workflow-state-manager.md) — mandatory read/update.

## Connectivity (stage 10)

| Tier | What it validates | What it does **not** validate |
|------|-------------------|-------------------------------|
| T0 | In-process UJ (`tests/e2e`, not live) | CORS, `VITE_*` bundle |
| T1 | `tests/integration` (H0i) | Browser |
| T2 | 13-deploy-smoke H1–**H5** | — |
| T3 | Live UJ + optional browser MCP | — |

Record in `docs/e2e-report.md`: separate columns for **T0**, **T2 connectivity**, **T3 browser**.
Mocks passing T0 ≠ production UI connected. See connectivity-gates §Stage 10.

## When to Use

- **After 07-build completes**: Verify the built product matches user expectations
- Runs **in parallel** with 09-qa (async)
- Results collected by 11-verify-impl

## Mechanism Selection

Determined from product requirements at runtime:

| Project Type | Signals | Mechanism | Tool |
|-------------|---------|-----------|------|
| Web app | UI components, routes, pages in spec | Browser automation | cursor-ide-browser MCP (after H4–H5 pass) |
| API / service | REST/gRPC endpoints in spec | HTTP requests | curl / httpx / requests |
| CLI tool | CLI flags in config-spec | Shell execution | Shell tool |
| Library | Import/call patterns in spec | Import + call | Python/Node REPL |
| RAG API | Template `api` or `monolith` | HTTP | httpx / pytest against TestClient |
| Ingest worker | Template `worker` or `monolith` | Job trigger + poll | API or CLI per spec |
| Mixed | Multiple signals | Multiple mechanisms | Adaptive per journey |

**Template-aware selection**: Read `workflow-state.yaml` §template.
- **api / monolith**: `POST /query`, `POST /ingest`, `GET /health` per `docs/api-contract.md`
- **worker**: enqueue ingest job → assert DB rows → optional query smoke

If ambiguous, surface `[Decision]` for 11-verify-impl.

## E2E tiers (deployed service)

| Tier | Owner stage | Command / action |
|------|-------------|------------------|
| T0 Local | **10-e2e** | `pytest tests/e2e/ -m "e2e and not live"` (TestClient + test DB) |
| T1 Integration | **10-e2e** or **08-verify-build** | `pytest tests/integration/` |
| T2 Deploy smoke | **13-deploy-smoke** | H1–H3 API + **H4–H5 browser connectivity** on staging |
| T3 Live | **15-service-health** | Full UJ suite vs staging URLs; optional browser UJ (H6) |

### Journey → test file matrix

Maintain 1:1 mapping in `docs/user-journeys.md`:

| Journey | Test module | T0 | T3 |
|---------|-------------|----|----|
| UJ-001 | `tests/e2e/test_uj001_ingest_and_query.py` | ✓ | live |
| UJ-002 | `tests/e2e/test_uj002_admin_collection.py` | per plan | live |
| … | … | … | … |

Before marking 10-e2e `completed`, verify every UJ-NNN in `docs/user-journeys.md` has a
corresponding `tests/e2e/test_uj*.py` (or documented waiver in e2e-report). **Mocks
passing T0 does not satisfy T3** — record T3 status separately.

## Prerequisites

1. **07-build** `completed` — implementation exists
2. Required:
   - `docs/user-journeys.md` — primary source for UJ-NNN definitions (actor, steps, E2E tier)
   - `docs/test-plan.md` — TC ↔ UJ mapping and run commands
   - `docs/feature-list.md` — feature scope
   - `docs/spec.md` — component details for verification
   - `docs/acceptance-criteria.md` — pass/fail when present (secondary to user-journeys)
3. For web apps: a running instance (local dev server or deployed)
4. For APIs: endpoint accessible for testing
5. For CLIs: binary/script executable

## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).
**Stage key:** `stages.10-e2e`.

Invoke **workflow-state-manager** `read_context` before any other action; `update` after each
substep. **Do not** edit `workflow-state.yaml` directly.


## Delta / feature-addition mode

- Add or extend E2E tests for **new user journeys** and acceptance scenarios per Fn.
- Run parallel with 09-qa; scope to cycle `feature_ids`.

## Workflow

### Phase 1 — Extract User Journeys

Read `docs/user-journeys.md` first (UJ-001, UJ-002, …). Cross-check `docs/test-plan.md` for
TC ↔ UJ mapping and run commands; use `docs/acceptance-criteria.md` for pass/fail detail when
present.

For each journey, extract:

| Field | Source |
|-------|--------|
| Journey ID | user-journeys.md (UJ-NNN) |
| Journey name | user-journeys.md §Journey Details |
| Steps | user-journeys.md §Steps |
| Expected outcomes | user-journeys.md §Acceptance; acceptance-criteria.md |
| Feature reference | user-journeys.md Journey Index → feature-list.md |
| E2E tier | user-journeys.md (local / modal / both) |
| Mechanism | Determined from project type + E2E tier |

If `docs/user-journeys.md` is missing (legacy project), surface `[Decision]` to generate it
via 01-requirements or doc-planner before proceeding. Do not silently invent UJ-IDs.

### Phase 2 — Determine Mechanism

Based on the project type signals, select the testing mechanism.

For **mixed** projects, assign mechanisms per journey:
- "User logs in and sees dashboard" → browser
- "API returns user profile" → HTTP request
- "CLI generates report" → shell execution

### Phase 3 — Execute Journeys (Parallel Agents)

Launch parallel agents for independent journeys:

#### Browser-based journeys

Use the `cursor-ide-browser` MCP server:
1. Navigate to the application URL
2. Follow journey steps (click, fill, navigate)
3. Verify expected outcomes (element presence, content, state)
4. Capture screenshots at key steps for evidence
5. Report: pass/fail per step, screenshots, timing

#### API-based journeys

Use shell commands (curl/httpx) or a test script:
1. Send requests per journey steps
2. Verify response status codes, body content, headers
3. Report: pass/fail per step, response details, timing

#### CLI-based journeys

Use Shell tool:
1. Execute CLI commands per journey steps
2. Verify stdout/stderr content, exit codes, output files
3. Report: pass/fail per step, command output

#### Library-based journeys

Use a REPL or test script:
1. Import the library
2. Call functions per journey steps
3. Verify return values, side effects
4. Report: pass/fail per step, values

### Phase 4 — Compile Results

Produce an E2E report:

```markdown
# E2E Behavior Report

> Generated: [date]
> Mechanism: [browser / API / CLI / library / mixed]
> Journeys tested: [N]

## Summary

| # | Journey | Mechanism | Steps | Passed | Failed | Status |
|---|---------|-----------|-------|--------|--------|--------|
| 1 | [name] | browser | 5 | 5 | 0 | PASS |
| 2 | [name] | API | 3 | 2 | 1 | FAIL |
| ... |

## Journey Details

### Journey 1: [name]
- **Feature**: [feature-list reference]
- **Mechanism**: browser
- **Steps**:
  1. Navigate to /login — PASS
  2. Fill username and password — PASS
  3. Click "Sign In" — PASS
  4. Verify dashboard loads — PASS
  5. Verify user name displayed — PASS

### Journey 2: [name]
- **Feature**: [feature-list reference]
- **Mechanism**: API
- **Steps**:
  1. GET /api/users/me — PASS (200 OK)
  2. Verify response contains email — PASS
  3. Verify response contains role — FAIL
     Expected: role field present
     Actual: role field missing from response
```

Write to `docs/e2e-report.md`.

**State**: Set status to `completed`.

## Output Rules

1. **Adaptive mechanism**: Select testing approach based on project type, not hardcoded.
2. **Evidence-based**: Capture screenshots (browser), responses (API), output (CLI).
3. **Parallel journeys**: Independent journeys run concurrently.
4. **No user interaction**: This stage does not ask questions. Findings go to 11-verify-impl.
5. **Async-safe**: Results are self-contained for 11-verify-impl consumption.
6. **Feature-traced**: Every journey maps to a feature-list entry.
