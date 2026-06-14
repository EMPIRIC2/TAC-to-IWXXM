---
name: 11-verify-impl
description: >
  Overall verification that the implementation matches what the user wanted. Collects results
  from 09-qa and 10-e2e, performs feature-level completeness checking against the product plan,
  and walks the user through approval of each feature area. Produces targeted patches for
  flagged issues (fix in place, no phase re-runs).
---

# 11 — Verify Implementation

Collect all verification results and walk the user through a final check that the
implementation matches their requirements.

**Preamble:** [pipeline-preamble.md](../pipeline-preamble.md) — shared conventions for stages 00–17.
**Cross-cutting:** [considerations.md](../considerations.md), [connectivity-gates.md](../connectivity-gates.md).
**State agent:** [workflow-state-manager](../../agents/workflow-state-manager.md) — mandatory read/update.

## Connectivity (stage 11)

Before approving **UI features** (e.g. F11 Chat UI, F12 Admin UI):

| Check | Source |
|-------|--------|
| T0 passes | e2e-report (in-process — not browser CORS) |
| Connectivity plan exists | test-plan H4–H5 + deploy-checklist rows from 12 |
| Waiver | User AskQuestion if staging H4–H5 deferred to 13 only — document in e2e-report |

Per-journey AskQuestion for browser UJs: “Does T0 prove this in production browser?” — if no,
record **T3/connectivity pending**; do not mark journey approved without waiver.

## Prerequisites

1. **09-qa** must be `completed` — QA report available
2. **10-e2e** must be `completed` — E2E report available
3. Product plan documents from Phase A must exist
4. `docs/feature-list.md` — the authoritative scope
5. `docs/user-journeys.md` — UJ-NNN interview prompts (§Interview per journey)

## Deployment state (consumed from `workflow-state.yaml`)

Read `workflow-state.yaml` §`deployment` on invocation to determine what is available
for verification without re-discovering URLs or re-running builds:

| Field | Use in 11-verify-impl |
|-------|----------------------|
| `deployment.local_build.status` | T0 pass/fail — skip re-run if `green` and `commit` matches HEAD |
| `deployment.local_build.t0_journeys_passed` | Pre-fill journey signoff table |
| `deployment.staging.urls.*` | Pass to T3 / H4–H5 checks (or flag `null` as blocker) |
| `deployment.staging.health_tiers.*` | Pre-fill tier status; only re-run `pending` tiers |
| `deployment.staging.drift` | If `true`, note that deployed commit lags HEAD |
| `deployment.url_discovery.method` | Command to refresh URLs when `null` |

Do **not** re-discover staging URLs manually. If `deployment.staging.urls` has `null`
entries needed for UI feature verification, run `deployment.url_discovery.method` and
update `workflow-state.yaml` before proceeding.

## Why This Stage Blocks

This is the user's final say before deployment. Every previous stage was about
correctness against specs; this stage is about correctness against **user intent**.

## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).
**Stage key:** `stages.11-verify-impl`.

Invoke **workflow-state-manager** `read_context` before any other action; `update` after each
substep. **Do not** edit `workflow-state.yaml` directly.

each feature/journey approval substep.

## Delta / feature-addition mode

- **Interactive approval per Fn** — present acceptance criteria status for each feature in cycle.
- Block deploy gate until user approves, denies, or modifies each new capability.

## Workflow

### Phase 1 — Collect Verification Results

Read and merge:
- `docs/qa-report.md` from 09-qa
- `docs/e2e-report.md` from 10-e2e
- `docs/verification-report.md` from 08-verify-build (latest)
- `docs/feature-list.md` for scope reference
- `docs/user-journeys.md` for per-journey interview questions
- `docs/acceptance-criteria.md` for pass/fail criteria

### Phase 2 — Feature Completeness Check (Embedded Consistency)

For each feature in `docs/feature-list.md`:

| Check | Method |
|-------|--------|
| **Implemented** | Does the codebase contain the implementation? (file/function exists) |
| **Tested** | Does the test suite include tests for this feature? |
| **QA clean** | Are there QA findings related to this feature's files? |
| **E2E passing** | Does the E2E journey for this feature pass? |
| **Acceptance met** | Do acceptance criteria for this feature pass? |

Also check for:
- **Undocumented features**: Code that doesn't map to any feature (scope creep)
- **Missing features**: Features with no corresponding implementation (scope gap)
- **Template conformance** (if template selected): Read QA report Agent 8 (template
  conformance). Flag any deviations from template patterns that weren't covered by an
  ADR. Deviations with ADRs are accepted; undocumented deviations are flagged.

### Phase 3a — Journey signoff (required)

Before feature-by-feature approval, walk **each journey** in `docs/user-journeys.md`:

| Check | Source |
|-------|--------|
| T0 test exists and passed | `docs/e2e-report.md` + pytest module |
| T3 status (if live tier) | e2e-report or 15-service-health / `LIVE_E2E=1` |
| User intent | AskQuestion per UJ-NNN |

Use AskQuestion (one journey per call or batch of 2):

- "Does UJ-NNN match your expected caller experience?"
- Options: Approve · Flag · Defer · Let me explain

Do **not** mark 11-verify-impl `completed` if any **modal-tier** journey lacks T0 pass
or documented T3 waiver. Feed flags into Phase 4 patches or 14-hotfix / 16-evolve routing.

### Phase 3 — Present to User

Present a unified view via AskQuestion, feature by feature:

```
prompt: "Implementation Verification: Feature 1 of [N]

  Feature: [Feature name from feature-list.md]

  ✓ Implemented — [component in spec.md]
  ✓ Tests passing — [N] tests, all green
  ⚠ QA: 2 lint warnings in [file]
  ✓ E2E: User journey passes (browser test)
  ✓ Acceptance criteria: all met

  Does this feature match your expectations?"

options:
  1. "Approve — this feature is correct"
  2. "Flag — this needs changes, I'll explain"
  3. "Defer — review later"
  4. "Let me explain / provide more context"
```

For features with failures:

```
prompt: "Implementation Verification: Feature 3 of [N]

  Feature: [Feature name]

  ✓ Implemented
  ✓ Tests passing
  ✗ E2E FAILED: Step 3 — expected 'dashboard' page, got '404'
  ✗ Acceptance: criterion 2 not met (missing role field in response)

  Recommendation: Fix the routing for /dashboard and add role field to API response."

options:
  1. "Approve fix — apply the recommended changes"
  2. "Flag — I'll describe a different fix"
  3. "Accept as-is — these failures are known/acceptable"
  4. "Let me explain / provide more context"
```

### Phase 4 — Apply Targeted Fixes (Fix in Place)

For each flagged or approved-fix feature:

1. **Classify the issue**: Code bug, spec mismatch, or missing feature
2. **Apply targeted fix**: Patch only the specific code or spec section
3. **Re-run affected checks**: Only the checks relevant to the fix
4. **Commit**: `fix: [description] per implementation verification`

**Never re-run entire phases.** Fixes are surgical patches.

### Phase 5 — Check for Scope Issues

Report scope analysis:

```
Scope Analysis:
  Features in spec: [N]
  Features implemented: [N]
  Features with passing E2E: [N]
  Features with passing acceptance: [N]

  Undocumented features (scope creep): [N]
  Missing features (scope gap): [N]
```

If scope issues exist, present via AskQuestion:
- For scope creep: "Remove, document, or accept this unplanned feature?"
- For scope gaps: "Implement now, defer, or remove from requirements?"

For each resolved scope decision, create an ADR in `docs/adr/` per
[considerations.md](../considerations.md) §ADR logging. Set the Stage field to
`11-verify-impl`.

### Phase 6 — Summary

```
Implementation Verification Complete.

Features verified: [N] / [N]
  Approved:    [N]
  Fixed:       [N] (targeted patches applied)
  Deferred:    [N]
  Accepted as-is: [N]

QA status:     [PASS/FAIL] — [N] issues remaining
E2E status:    [PASS/FAIL] — [N] journeys passing
Acceptance:    [PASS/FAIL] — [N] criteria met

Scope:
  Creep:  [N] items (resolved)
  Gaps:   [N] items (resolved)

Artifacts:
  docs/implementation-verification.md — full report
  docs/qa-report.md — QA results
  docs/e2e-report.md — E2E results
  docs/adr/                           — [N] ADRs from scope/fix decisions

Deploy gate (partial):
  ✓ QA checks [status]
  ✓ E2E behaviors [status]
  ✓ Implementation verified by user
  ○ Deploy strategy pending (next step)

Next step: 12-verify-deploy
```

Write `docs/implementation-verification.md`.
**State**: Set status to `completed`.

## Output Rules

1. **User is final arbiter**: The user approves each feature, not automated checks alone.
2. **Fix in place**: Targeted patches only. Never re-run entire phases.
3. **Feature-level granularity**: Present results per feature, not per file or per check.
4. **Scope awareness**: Detect both creep and gaps.
5. **Evidence-backed**: Every finding cites QA report, E2E report, or acceptance criteria.
