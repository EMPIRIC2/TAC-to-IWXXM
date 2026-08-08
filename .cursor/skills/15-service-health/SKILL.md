---
name: 15-service-health
description: >
  Investigates a deployed service in two layers: platform infra health (API up, DB migrations,
  secrets, deploy drift, GitHub main CI green via H0ci) and live behavior (API smokes, E2E tiers).
  AskQuestion-driven depth and budget before running checks. Test-driven on user failures (repro
  test red → confirm → investigate → fix via 14-hotfix). Opens docs/bug-reports/BUG-*.md for code
  bugs. Use for production health, ambiguous API/DB errors, periodic ops, post-deploy verification,
  or confirming main CI passes after merge/hotfix.
---
<!--
Personal skill (project-agnostic). Paths like docs/ and workflow-state.yaml refer to the
*active workspace project*, not this skills directory. Fill {{PLACEHOLDER}} tokens from
the project's docs/CORPUS.md, feature-list, and deploy docs.
-->
# 15 — Service Health

Investigate the **live** deployment: correct version, database ready, API paths working,
and alignment with `docs/deploy.md` §Integration — without assuming a hotfix is required.

**Code failures:** [bug-investigation](../bug-investigation/SKILL.md) → `docs/bug-reports/BUG-*.md`
+ `tests/bugs/test_bug_*.py` before 14-hotfix.

**Preamble:** [pipeline-preamble.md](../pipeline-preamble.md)
**Sessions:** [sessions-reference.md](../sessions-reference.md) — requires `active_session` unless waived; reports under `docs/sessions/{id}/reports/`.
**Cross-cutting:** [considerations.md](../considerations.md), [deployment-catalog.md](../deployment-catalog.md), [connectivity-gates.md](../connectivity-gates.md).
**State agent:** project `.cursor/agents/workflow-state-manager.md` if present; else edit `workflow-state.yaml` per [workflow-state-reference.md](../workflow-state-reference.md)

## Connectivity (stage 15)

When a browser frontend exists, default depth: **H4–H5 before H3** for UI-related reports.
See connectivity-gates for tier definitions.

**User is source of truth.** AskQuestion sets infra depth, health tier (H0–H6), target URL, and
whether to run costly full E2E suites.


## Session management

Per [sessions-reference.md](../sessions-reference.md) §10 and [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).

1. Agent `read_context` must return `active_session` (or blocking deviation).
2. Current stage must appear in `active_session.routing_plan` unless user amends plan.
3. Write stage reports to `active_session.artifacts_dir/reports/` when this stage produces a report.
4. On completion: update routing-plan entry status; mirror `project.stages.{key}` via agent `update`.
5. **00-context** exempt from active_session requirement (session opener).
Report: `reports/service-health.md`.

## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).
**Stage key:** `stages.15-service-health`.

Invoke **workflow-state-manager** `read_context` before any other action; `update` after each
substep. **Do not** edit `workflow-state.yaml` directly.

Per-run reports under `docs/service-health-reports/` (ephemeral).

## Two-layer model

| Layer | Question | Pass when |
|-------|----------|-----------|
| **Infra** | Is the right thing deployed and wired? | Health 200, DB migrated, secrets present |
| **Behavior** | Do primary API flows work end-to-end? | Approved smokes return expected status/body |

Record **Infra overall**, **E2E overall**, and **Overall** separately in the report.

## Health ≠ primary-journey-ready

Liveness/`/health` and dependency probes can be green while the **primary user journey** fails
(hang, timeout, wrong runtime).

- If H3 is in scope: **H3 fail or hang ⇒ Overall FAIL** (and Behavior FAIL) even when H1 is PASS.
- Do not report Overall PASS on infra-only evidence when the requested depth includes H3.
- On H3 P0 during an active evolve cycle: recommend pause **16-evolve** → **14-hotfix**.

## Single-env / live role

If only one deployed stack exists (`env_role: staging_as_live`), label checks and reports as
**live/prod** — do not imply a safer non-prod target.

**TAC-to-IWXXM (ADR-034):** Dual DOKS — use `env_role: staging` vs `prod` and the matching
hosts (`*.staging.tac-to-iwxxm.com` vs `api|app.tac-to-iwxxm.com`). Do not use sole-stack
language when `metar-iwxxm-staging` is provisioned.

## Health tiers (default recommendations)

| Tier | Scope | Example |
|------|-------|---------|
| H0 | Local integration | `uv run pytest tests/integration -v` |
| **H0ci** | **GitHub main CI** | Latest required workflow on `main` → `success` |
| H1 | Liveness | `GET {{HEALTH_ENDPOINT}}` → 200 |
| H2 | DB ready | migrations at head; pool connects |
| H3 | API smoke | documented curl/pytest against `{{STAGING_URL}}` |
| H4 | Browser CORS | connectivity pytest or `verify_connectivity.sh` |
| H5 | Frontend bundle | `VITE_*` wiring check (when frontend exists) |
| H6 | Full UJ suite | `pytest tests/e2e/ -m live` or browser automation |

| Trigger | Recommend infra | Recommend behavior |
|---------|-----------------|-------------------|
| Routine | H1 + H2 + **H0ci** (advisory) | H3 |
| Post-deploy / post-hotfix | H1–H2 + deploy metadata + **H0ci (blocking)** | H3 + **H4–H5** if UI |
| User-reported CI failure on `main` | **H0ci first** | H3 only if CI green |
| User-reported “UI broken / Failed to fetch” | H4–H5 first | H3 |
| Weekly deep | H1–H2 + backlog metrics | H6 (explicit approval) |

Never auto-run **H6** without AskQuestion approval.

## Main CI (H0ci)

```bash
gh run list --branch main --workflow ci-cd.yml --limit 5
gh run view <run-id> --json conclusion,status,headSha,url,workflowName
```

Pass when `conclusion` is `success` for the run matching the SHA under investigation.
Record run URL in the service-health report.

Update `workflow-state.yaml` §`deployment.staging.health_tiers.h0ci_github_main` when H0ci runs.

## Test-driven investigation

Same as [bug-investigation](../bug-investigation/SKILL.md): repro test first, confirm with user,
then production checks.

## Delta / feature-addition mode

If user request is **feature addition**: recommend [16-evolve](16-evolve/SKILL.md) instead.
After feature deploy, optional health pass scoped to new Fn journeys.

## Workflow (summary)

### Phase 0 — Interview

- Target environment (local / staging / production)
- Base URL `{{STAGING_URL}}`, DB reachability (read-only ok?)
- Depth: infra only vs include H3/H4
- Known symptoms, recent deploys, failing UJ-NNN

### Phase 1 — Infra checks

- Deploy revision matches expected git SHA / image tag
- **H0ci** when post-deploy/post-hotfix (blocking unless waived)
- `GET {{HEALTH_ENDPOINT}}`
- Migration status (`{{MIGRATION_COMMAND}}` or platform equivalent)
- Required env vars present (names only in report, never values)

### Phase 2 — Behavior checks

- Run approved H3 script from `docs/user-journeys.md` or `docs/deploy.md` §Runbook
- If UI involved: H4–H5 per connectivity-gates
- Capture latency (informational)

### Phase 3 — Report & route

Write `docs/service-health-reports/YYYY-MM-DD-[slug].md` with remediation routing:
none | config | data reseed | **fix main CI** | **14-hotfix** (code).

Update `workflow-state.yaml` §`stages.15-service-health`.

## Output rules

1. No secret values in reports.
2. Infra fail → do not claim API broken without evidence.
3. Code defects → bug report before hotfix.
4. Compare live routes to `docs/api-contract.md` when applicable.
5. Do not mark **Overall PASS** when main CI is red after recent merge/hotfix unless user waives.
