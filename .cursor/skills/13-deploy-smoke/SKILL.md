---
name: 13-deploy-smoke
description: >
  Executes the deployment, runs API smokes (H1–H3) plus browser connectivity gates (H4–H5:
  CORS + frontend bundle wiring), health checks, changelog, and monitoring baseline. Final
  pipeline stage. Blocking — user must approve deployment results.
---

# 13 — Deploy & Smoke Check

Deploy the application and verify it works with smoke tests and health checks.

**Preamble:** [pipeline-preamble.md](../pipeline-preamble.md) — shared conventions for stages 00–19.
**Sessions:** [sessions-reference.md](../sessions-reference.md) — requires `active_session` unless waived; reports under `docs/sessions/{id}/reports/`.
**Cross-cutting:** [considerations.md](../considerations.md), [connectivity-gates.md](../connectivity-gates.md).
**State agent:** [workflow-state-manager](../../agents/workflow-state-manager.md) — mandatory read/update.

## Connectivity (stage 13)

Mandatory sequence: **H0c** (pre) → deploy → **H1–H3** → **`verify_connectivity.sh`** (H4–H5).
Do not mark `deployed` without H4–H5 pass or user-waived checklist entry. See connectivity-gates §Stage 13.

## Prerequisites

1. **12-verify-deploy** must be `completed` — deploy checklist approved
2. Required:
   - `{artifacts_dir}/reports/deploy-checklist.md`` — all items checked
   - Deployment plan document — deploy commands and configuration
   - `docs/test-plan.md` — smoke test definitions
3. Deployment platform CLI/tools must be installed and authenticated


## Session management
> `{artifacts_dir}` = `active_session.artifacts_dir` from workflow-state-manager.


Per [sessions-reference.md](../sessions-reference.md) §10 and [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).

1. Agent `read_context` must return `active_session` (or blocking deviation).
2. Current stage must appear in `active_session.routing_plan` unless user amends plan.
3. Write stage reports to `active_session.artifacts_dir/reports/` when this stage produces a report.
4. On completion: update routing-plan entry status; mirror `project.stages.{key}` via agent `update`.
5. **00-context** exempt from active_session requirement (session opener).
Report: `reports/deploy-smoke.md`.

## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).
**Stage key:** `stages.13-deploy-smoke`.

Invoke **workflow-state-manager** `read_context` before any other action; `update` after each
substep. **Do not** edit `workflow-state.yaml` directly.


**Detail:** `docs/deploy-state.md` — sync URL/status with YAML on each deploy step.

### Deployment record (`workflow-state.yaml` §`deployment`)

This stage **writes** the `deployment` section that downstream skills (11, 15) consume:

| On event | Update |
|----------|--------|
| Deploy succeeds | `deployment.staging.status: deployed`, `commit_deployed`, URLs |
| H1–H3 pass | `deployment.staging.health_tiers.h1/h2/h3: pass` |
| H4–H5 pass | `deployment.staging.health_tiers.h4/h5: pass` |
| H4–H5 not run | `deployment.staging.health_tiers.h4/h5: pending` + note |
| Local T0 verified | `deployment.local_build.status: green`, `t0_result`, journey count |
| URL discovered | `deployment.staging.urls.<app>: <url>` |
| Commit drift | `deployment.staging.drift: true` when `commit_deployed != commit_head` |

**After each smoke phase**, update `workflow-state.yaml` §`deployment` immediately so
that 15-service-health and 11-verify-impl can read current tier status without re-running
checks. Use `deployment.url_discovery.method` to refresh URLs when needed.

### On invocation — check state

1. Read both state sources (`stages.13-deploy-smoke` and `deployment`).
2. **If `deployed`**: Ask: "Re-deploy, validate existing, or rollback?"
3. **If `in_progress` or `failed`**: Report what happened. Resume or restart.
4. **If `pending`**: Start fresh.

### Commit-as-you-go

Commit artifacts to an appropriate branch before transitioning to the next stage or
asking the user a blocking question. Branch type per
[workflow-state-reference.md](../workflow-state-reference.md) §Git history.
Record every commit in `workflow-state.yaml` §`git_history.commits` with
`stage: "13-deploy-smoke"`.

### State file: `docs/deploy-state.md`

```markdown
# Deploy State

> Last updated: [date]
> Status: pending | in_progress | deployed | failed | rolled_back

## Deployment Log

| # | Step | Status | Started | Completed | Notes |
|---|------|--------|---------|-----------|-------|
| 1 | Deploy | pending | — | — | — |
| 2 | Smoke tests | pending | — | — | — |
| 3 | Health check | pending | — | — | — |
| 4 | Changelog | pending | — | — | — |
| 5 | Monitoring baseline | pending | — | — | — |

## Current Deployment

| Field | Value |
|-------|-------|
| App name | — |
| Deploy URL | — |
| Deploy mode | — |
| Commit | — |
| Branch | — |
```

## Delta / feature-addition mode

- Redeploy only services affected by new Fn; run H1–H5 for changed browser/API paths.
- Update deployment block via workflow-state-manager after smokes.

## Workflow

### Phase 1.5 — Pre-deploy integration (T1)

Before production deploy:

1. T0 green: `pytest tests/e2e/ -m "e2e and not live"`
2. **H0c green:** `pytest tests/unit/test_cors_policy.py` (browser CORS on all FastAPI apps)
3. Migrations apply on staging DB: `alembic upgrade head`
4. Optional: `scripts/rag_smoke.py` against local TestClient
5. **Connectivity readiness (12):** `{artifacts_dir}/reports/deploy-checklist.md`` includes H0c + `VITE_*` / `METAR_CORS_ORIGINS` rows per [connectivity-gates.md](../connectivity-gates.md)

**Deploy gate**: T1 fail → 14-hotfix or fix-in-place; do not deploy.

### Phase 1 — Deploy

Execute deploy per `docs/deploy.md §Integration` (Render, Docker, etc.).
Run migrations on target before serving traffic.

Capture full stdout/stderr.

**If deploy succeeds**:
- Record app URL and deployment details in `deploy-state.md`
- Proceed to Phase 2

**If deploy fails**:
- Parse the error
- Present to user via AskQuestion:
  - "Approve fix — apply recommended fix and retry"
  - "Abort deployment"
  - "Modify — I'll fix differently"
  - "Let me explain / provide more context"
- Retry up to 3 times after fixes
- If still failing after 3 attempts, abort and report

### Phase 2 — Smoke Tests (Parallel Agents)

Run **backend** smokes first, then **browser connectivity** (H4–H5). Backend-only pass is **not**
sufficient for deployed service hybrid deploys — see [connectivity-gates.md](../connectivity-gates.md).

**Operator env (staging):**

```bash
uv run --with pydo --with pyyaml scripts/deploy/do_apps.py urls --frontend
# Set METAR_STAGING_ADMIN_API_URL from Modal deploy output
export METAR_STAGING_ADMIN_API_URL=https://deployed-service--deployed-service-data-management-fastapi-app.modal.run
```

**Agent 1 — API connectivity (H1)**:
- `bash scripts/deploy/staging_smoke.sh` or `tests/smoke/test_staging_health.py -m live`
- Verify TLS, `/health` 200 on ChatRAG + write API
- Return: pass/fail, response times

**Agent 2 — Functional smoke (H2–H3)**:
- H2: DB pool + Alembic head (`staging_h2.py`)
- H3: `POST /api/v1/ask` with fixture question (warm LLM first if cold — see deploy-report)
- Negative API paths per test-plan / config-spec where applicable
- Return: pass/fail, response details

**Agent 3 — Browser connectivity (H4–H5)** — **blocking**:
- Run `bash scripts/deploy/verify_connectivity.sh` (H0c + live H4/H5 when URLs set)
- **H4:** CORS `OPTIONS` from each frontend origin → API returns `Access-Control-Allow-Origin`
- **H5:** Live JS bundle contains expected API hosts (not `localhost`)
- Return: pass/fail per tier; cite failing origin/path

**Agent 4 — Resource verification**:
- DB pool healthy; worker backlog below threshold
- No container crash loops on DO/Modal
- Return: resource status report

If any smoke test fails, present to user:
- "Investigate and fix — the service is not working correctly"
- "Accept — the failure is expected / non-critical"
- "Rollback — stop the deployment"

### Phase 3 — Health Check

Verify service health:
- All functions/endpoints respond
- Error rates are acceptable (check logs)
- No container restarts
- Memory/CPU within expected ranges

Record monitoring baseline.

### Phase 4 — Generate Changelog

Aggregate commits and PRs into a structured changelog:

1. `git log --oneline [last-deploy-tag]..HEAD`
2. Group by phase and milestone using `[T{id}]` and `[M{id}]` prefixes
3. Write `CHANGELOG.md`:

```markdown
# Changelog

## [version] — [date]

### Phase 1: [Phase Name]
- **M1**: [milestone] ([PR link])
  - [T1.1] test: [description]
  - [T1.2] feat: [description]
...
```

4. Tag: `git tag v[version]-deploy`

### Phase 5 — Generate Deploy Report

Write `docs/deploy-report.md`:

```markdown
# Deploy Report

> Date: [date]
> Status: deployed
> URL: [deployment URL]

## Pre-Deploy
- Checklist: all items passed (`{artifacts_dir}/reports/deploy-checklist.md`)

## Deployment
- Command: [deploy command]
- Duration: [time]
- Result: SUCCESS

## Smoke Tests
| Test | Status | Response Time |
|------|--------|---------------|
| H1 API connectivity | PASS | [ms] |
| H2 DB | PASS | — |
| H3 RAG ask | PASS | [ms] |
| H4 CORS (browser) | PASS | — |
| H5 Frontend bundle | PASS | — |
| Resources | PASS | — |

## Health Check
- Error rate: [%]
- Avg response time: [ms]
- Container restarts: [N]

## Monitoring Baseline
- [metrics recorded]

## Rollback
- Command: [rollback command]
- Last known good: [commit]

## Changelog
- See CHANGELOG.md
```

### Phase 6 — Summary

```
Deploy & Smoke Check Complete.

  Deployment:     SUCCESS — [URL]
  Smoke tests:    [N] / [N] passed
  Health:         OK
  Changelog:      CHANGELOG.md (v[version]-deploy)
  Monitoring:     baseline recorded

  Report: docs/deploy-report.md
  State:  docs/deploy-state.md (status: deployed)

Pipeline Complete ✓

  Phase A (Product Planning):       completed
  Phase B (Technical Planning):     completed
  Phase C (Build):                  completed
  Phase D (Verification & Deploy):  completed

  Total stages: 14 (00-13)
  Total issues surfaced: [N]
  Total artifacts: [N] documents
```

Update `workflow-state.yaml` overall status to `completed`.
Update `docs/deploy-state.md` status to `deployed`.

## Rollback

If the user requests a rollback:
1. Execute the rollback command from the deployment plan
2. Update `deploy-state.md` status to `rolled_back`
3. Report the rollback and last known good state

## Output Rules

1. **Pre-deploy checks done**: Never deploy without 12-verify-deploy passing.
2. **Failures require user choice**: Every failure gets AskQuestion with options.
3. **Max 3 deploy retries**: Prevent infinite loops.
4. **Smoke tests are minimal**: Quick validation, not full test suite — but **must include H4–H5** for multi-origin UI deploys.
5. **Never mark deployed** if H4/H5 fail without documented user waiver in deploy-checklist.
6. **Rollback documented**: Every deployment has a rollback command.
7. **State persists**: Deploy state survives session boundaries.
8. **Changelog**: Aggregate commits into structured changelog at deploy time.
