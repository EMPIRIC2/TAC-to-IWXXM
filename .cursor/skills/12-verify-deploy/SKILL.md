---
name: 12-verify-deploy
description: >
  Pre-deploy gate. Verifies the deployment strategy is sound and all prerequisites are met.
  Walks through potential failure modes and mitigations with the user. Checks configuration,
  secrets, browser connectivity readiness (CORS + VITE_*), data management, rollback plan,
  and resource allocation against the deployment spec.
---
<!--
Personal skill (project-agnostic). Paths like docs/ and workflow-state.yaml refer to the
*active workspace project*, not this skills directory. Fill {{PLACEHOLDER}} tokens from
the project's docs/CORPUS.md, feature-list, and deploy docs.
-->
# 12 — Verify Deploy Strategy

Pre-deploy gate verifying that the deployment strategy planned in Stage 04 still holds
after implementation, and all deployment prerequisites are met.

**Preamble:** [pipeline-preamble.md](../pipeline-preamble.md) — shared conventions for stages 00–19.
**Sessions:** [sessions-reference.md](../sessions-reference.md) — requires `active_session` unless waived; reports under `docs/sessions/{id}/reports/`.
**Cross-cutting:** [considerations.md](../considerations.md), [connectivity-gates.md](../connectivity-gates.md).
**State agent:** project `.cursor/agents/workflow-state-manager.md` if present; else edit `workflow-state.yaml` per [workflow-state-reference.md](../workflow-state-reference.md) — mandatory read/update.

## Connectivity (stage 12)

Run **Agent 6** and populate deploy-checklist connectivity rows (H0c, VITE matrix, CORS origins,
`verify_connectivity.sh` planned). Sign-off means “ready for 13 including H4–H5,” not API-only.
See connectivity-gates §Stage 12.

## Single-env / live role

Before marking deploy-ready, resolve **what the target stack is**:

| Situation | `env_role` | Agent behavior |
|-----------|------------|----------------|
| Distinct non-prod + prod stacks exist | `staging` then `prod` | Keep separate checklists; never treat staging URLs as prod |
| **Only one** deployed stack (names may still say “staging”) | `staging_as_live` / **live = prod** | Treat that stack as **production** in AskQuestions, checklists, and reports |
| Explicit second env planned but not provisioned | `staging_as_live` | Same as sole-stack; do not imply a safer non-prod cutover target |

**TAC-to-IWXXM (ADR-034 / EV-043):** Dual DOKS envs — `stage`→`metar-iwxxm-staging`
(`api\|app.staging.tac-to-iwxxm.com`); `main`→`metar-iwxxm` (prod hosts). Prefer
`env_role: staging` then `prod`. Promote = PR **stage→main** after **Staging smoke** /
**Staging gate** green. Do not use sole-stack language when both namespaces exist.

Record `env_role` on the deploy checklist and in the session note. Prefer a project ADR when the
workspace documents single-env topology.

## CI/CD tip gate

Tip SHA must have **required** workflows green before deploy-ready / promote:

- Always: project CI workflow(s)
- On default branch / live cutover: deploy-preflight and any CD the project treats as a gate

**Red, cancelled, or missing run** → **hard stop**. Do not continue 12→13 or promote without an
explicit **waiver AskQuestion** (first option = wait/fix; last = explain). Prefer the project’s
CI watch script (if present) and treat non-zero exit as blocking.

## Prerequisites

1. **11-verify-impl** must be `completed` — implementation verified by user
2. Required:
   - Deployment plan document (e.g., `docs/deploy.md §Integration`, `docs/deployment-plan.md`)
   - `workflow-state.yaml + execution plan artifact` — §Tech Stack for deployment tools
   - `docs/reports/implementation-verification.md` — confirmation implementation is approved
3. If data assets exist: `docs/spec.md §Data` and `docs/data-management-state.md`

## Why This Stage Exists Separately from Stage 04

Stage 04 (tech plan) **designs** the deployment strategy. Stage 12 **verifies** that:
- The strategy still applies after implementation (no drift)
- All prerequisites are actually in place (secrets, volumes, configs)
- Failure modes have been addressed
- The user has reviewed the rollback plan


## Session management
> `{artifacts_dir}` = `active_session.artifacts_dir` from workflow-state-manager.


Per [sessions-reference.md](../sessions-reference.md) §10 and [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).

1. Agent `read_context` must return `active_session` (or blocking deviation).
2. Current stage must appear in `active_session.routing_plan` unless user amends plan.
3. Write stage reports to `active_session.artifacts_dir/reports/` when this stage produces a report.
4. On completion: update routing-plan entry status; mirror `project.stages.{key}` via agent `update`.
5. **00-context** exempt from active_session requirement (session opener).
Report: `reports/deploy-checklist.md`.

## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).
**Stage key:** `stages.12-verify-deploy`.

Invoke **workflow-state-manager** `read_context` before any other action; `update` after each
substep. **Do not** edit `workflow-state.yaml` directly.


## Delta / feature-addition mode

- Pre-deploy checklist scoped to **changed surfaces** (API, UI, secrets, Modal) in this cycle.
- Re-run connectivity rows from connectivity-gates for browser-facing changes.

## Workflow

### Phase 1 — Pre-Deploy Checks (Parallel Agents)

Launch parallel agents:

**Agent 1 — Configuration Validation**:
- Read deployment plan
- Verify all required configuration is present (no `⚠️ Needs human input` markers)
- Check app name, entry files, function definitions
- Return: list of missing or incomplete items

**Agent 2 — Secrets Check**:
- Cross-reference deployment plan §Secrets with actual secret configuration
- For Modal: `modal secret list`
- For other platforms: check environment or secret manager
- Return: pass/fail per secret

**Agent 3 — Data & Volume Check** (if applicable):
- Verify data assets are staged for deployment
- For Modal: check volumes exist and contain expected files
- For other platforms: check equivalent storage
- Return: pass/fail per asset

**Agent 4 — Resource Allocation Check**:
- Verify compute resources match deployment plan
- GPU allocation, container count, scaling config
- Return: spec compliance report

**Agent 5 — Template Deploy Validation** (if template selected): Read
`workflow-state.yaml` §template and [template-registry.md](../template-registry.md).
- Verify `.github/workflows/deploy_to_modal.yml` matches template CI/CD pattern
- Verify deploy command is ` platform deploy -m src.app`
- Verify GitHub repo secrets are documented (`MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET`)
- For job template: verify GPU classes match `template.gpu_tiers`, verify cache volume
  name is `cognichem-{service_name}-cache`
- For utility template: verify `min_containers` setting
- Cross-check: deployment plan doc references match actual `src/app.py` app name
- Return: template deploy conformance report

**Agent 6 — Browser connectivity readiness** (required for deployed service hybrid / any static UI + separate API hosts):
- Read [connectivity-gates.md](../connectivity-gates.md)
- Verify `tests/unit/test_cors_policy.py` exists and passes (`H0c`)
- Verify each FastAPI `create_app` uses `deployed-service_shared_schemas.cors.configure_cors`
- Cross-check `docs/ops/staging-secrets-matrix.md`: every `VITE_*` row has a matching API URL + `{{ENV_PREFIX}}_CORS_ORIGINS` entry
- Confirm `scripts/deploy/verify_connectivity.sh` and `tests/smoke/test_staging_connectivity.py` are present
- Return: pass/fail + missing wiring items (do **not** assume H1–H3 alone is enough)

### Phase 2 — Failure Mode Analysis

Walk through potential deployment failure modes with the user:

For each potential failure mode identified from the deployment plan:

```
prompt: "[Deploy Risk] Container image build failure:
  Risk: Dependencies may fail to install in the production image.
  
  Current mitigation: [from deployment plan, or 'none documented']
  
  Recommendation: Add a Dockerfile health check and test the image locally before
  deploying."

options:
  1. "Approve mitigation — this is sufficient"
  2. "Add mitigation — I'll describe what to add"
  3. "Accept risk — no mitigation needed"
  4. "Let me explain / provide more context"
```

Common failure modes to check:
- Image build failure (dependency installation)
- Secret missing at runtime
- Data/volume mount failure
- GPU unavailability
- Network/port binding issues
- Cold start timeout
- Memory exhaustion
- **Auth/CORS / browser connectivity** — static frontend on different origin than API; mitigated by `{{ENV_PREFIX}}_CORS_ORIGINS` + H4/H5 gates (see connectivity-gates)

### Phase 3 — Rollback Plan Review

Present the rollback plan for verification:

```
prompt: "Rollback plan review:
  
  Current plan: [from deployment plan]
  Rollback command: [e.g., 'modal app stop [app-name]']
  
  Is this rollback plan complete and correct?"

options:
  1. "Approve — rollback plan is correct"
  2. "Modify — I'll update the rollback procedure"
  3. "Skip — no rollback needed for this deployment"
  4. "Let me explain / provide more context"
```

### Phase 4 — Produce Deploy Checklist

Write `{artifacts_dir}/reports/deploy-checklist.md``:

```markdown
# Deploy Checklist

> Generated: [date]
> Status: [ready / not ready]
> Deployment plan: [docs/deployment-plan.md]

## Pre-Deploy

- [ ] Configuration complete (no gaps)
- [ ] All secrets configured
- [ ] Data assets staged (if applicable)
- [ ] Resource allocation verified
- [ ] Rollback plan reviewed
- [ ] H0c CORS unit tests pass (`pytest tests/unit/test_cors_policy.py`)
- [ ] Frontend `VITE_*` ↔ API URL matrix complete (connectivity-gates §Wiring)
- [ ] `{{ENV_PREFIX}}_CORS_ORIGINS` documented per API service for staging/prod
- [ ] Post-deploy H4–H5 command documented (`verify_connectivity.sh`)

## Failure Mitigations

| # | Risk | Mitigation | Status |
|---|------|-----------|--------|
| 1 | Image build failure | Local image test | approved |
| 2 | Secret missing | Pre-deploy secret check | approved |
| ... |

## Rollback

- Command: [rollback command]
- Procedure: [step-by-step rollback]
- Last known good: [commit/tag]

## Sign-Off

- [ ] User approved deployment (11-verify-impl)
- [ ] Deploy strategy verified (this checklist)
- [ ] Ready to deploy
```

### Phase 5 — Summary

```
Deploy Strategy Verification Complete.

Pre-deploy checks:
  Configuration: [PASS/FAIL]
  Secrets:       [PASS/FAIL] — [N] configured
  Data/Volumes:  [PASS/FAIL/N/A] — [N] verified
  Resources:     [PASS/FAIL]

Failure mitigations: [N] risks addressed
Rollback plan: [reviewed/updated/skipped]

Deploy gate:
  ✓ QA checks passed (09-qa)
  ✓ E2E behaviors passed (10-e2e)
  ✓ Implementation verified (11-verify-impl)
  ✓ Deploy strategy verified
  → Ready for deployment (API + browser connectivity plan verified)

Artifacts:
  `{artifacts_dir}/reports/deploy-checklist.md` — verified checklist

Next step: 13-deploy-smoke
```

**State**: Set status to `completed`.

## Output Rules

1. **Verification, not planning**: This stage verifies the existing strategy, not creates one.
2. **Failure modes are mandatory**: Walk through potential failures even if plan looks complete.
3. **Rollback is required**: Every deployment must have a documented rollback procedure.
4. **User approves risks**: Every accepted risk requires explicit user acknowledgment.
5. **Checklist persists**: The deploy checklist is a reusable artifact for future deploys.
6. **Single-env honesty**: If only one stack exists, call it **live/prod** in user-facing text —
   do not imply a safer “staging-only” cutover.
7. **CI/CD tip green**: Red tip SHA blocks deploy-ready unless the user waives.
