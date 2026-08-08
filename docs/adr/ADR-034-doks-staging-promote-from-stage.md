# ADR-034: DOKS staging + promote-from-stage CD (F30 deepen / #886)

> **Status**: Accepted (S052 / EV-043; D-S052-* Phase 0 locks)  
> **Date**: 2026-08-08  
> **Deciders**: User (issue #886 + Evolve Plan Card)  
> **Amends**: [ADR-033](ADR-033-platform-independence-auth-do-doks.md) (single prod DOKS → dual env)  
> **Related**: F30; [docs/deploy.md](../deploy.md); EV-034 CD rollout  
> **Session**: S052-doks-staging-prod-branch-deploys / EV-043

## Context

Production already runs on DOKS (`metar-iwxxm`, `api|app.tac-to-iwxxm.com`). Issue #886 asks
for staging + prod environments, protected branches, and deploy wiring. Solo-dev workflow
needs a **manual promote** without multi-reviewer Environment gates: PRs are the gate.

## Decision

1. **Same DOKS cluster, two namespaces** — prod `metar-iwxxm`; staging `metar-iwxxm-staging`.
2. **Branches** — `stage` → staging CD; `main` → prod CD. Both require PRs (no direct push /
   no force-push via rulesets when admin can apply them).
3. **DNS** — Staging: `api.staging.tac-to-iwxxm.com` / `app.staging.tac-to-iwxxm.com` → LB
   `168.144.12.70`. Prod hosts unchanged.
4. **Secrets isolation** — Staging uses DB `metar_iwxxm_staging` on DO Postgres; never share
   prod `DATABASE_URL`.
5. **Promote path** — Only PRs from `stage` → `main`. CI job `staging-gate` requires green
   **Staging smoke** for the tip SHA. After merge to `main`, prod Deploy runs automatically.
6. **Solo-dev** — No required Environment reviewers; the PR is the manual step.
7. **IaC** — Kustomize overlays `deploy/doks/overlays/{staging,prod}`.

## Consequences

- Skills 12/13/15/16 and ci-after-push must distinguish `env_role: staging | prod`.
- Hotfixes that skip staging violate the gate unless explicitly waived.
- DNS for staging lives at the domain registrar (Porkbun NS), not DigitalOcean DNS.

## Alternatives considered

- App Platform dual apps — rejected (diverges from F30 DOKS).
- Environment approval for prod — rejected for solo-dev friction.
- Second DOKS cluster — deferred (cost); namespace isolation sufficient for now.
