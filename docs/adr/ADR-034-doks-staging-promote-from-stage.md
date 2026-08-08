# ADR-034: DOKS staging + promote-from-stage CD (F30 deepen / #886)

> **Status**: Accepted (S052 / EV-043); **Amended** (S053 / EV-044 — dual DOKS clusters)  
> **Date**: 2026-08-08  
> **Deciders**: User (issue #886 + Evolve Plan Card; EV-044 project visibility)  
> **Amends**: [ADR-033](ADR-033-platform-independence-auth-do-doks.md) (single prod DOKS → dual env)  
> **Related**: F30; [docs/deploy.md](../deploy.md); EV-034 CD rollout  
> **Sessions**: S052-doks-staging-prod-branch-deploys / EV-043; S053-separate-staging-doks-project / EV-044

## Context

Production already runs on DOKS (`metar-iwxxm`, `api|app.tac-to-iwxxm.com`). Issue #886 asks
for staging + prod environments, protected branches, and deploy wiring. Solo-dev workflow
needs a **manual promote** without multi-reviewer Environment gates: PRs are the gate.

EV-043 shipped staging as a **second namespace on the prod cluster**. That left DO Project
**Staging TAC-to-IWXXM** empty (namespaces are not assignable DO resources). EV-044 moves
staging to a **dedicated DOKS cluster + managed Postgres** under that project so staging is
visible and isolated in the DigitalOcean control plane.

## Decision

1. **Dual DOKS clusters** (EV-044 amend) — prod cluster `metar-iwxxm` on DO Project
   **TAC-to-IWXXM**; staging cluster `metar-iwxxm-staging` on DO Project
   **Staging TAC-to-IWXXM**. In-cluster namespace for workloads remains `metar-iwxxm-staging`
   (staging) and `metar-iwxxm` (prod).
2. **Dual managed Postgres** — prod DB `metar-iwxxm` (defaultdb) on **TAC-to-IWXXM**;
   staging DB `metar-iwxxm-staging` (`db-s-1vcpu-1gb`) on **Staging TAC-to-IWXXM**.
   Never share prod `DATABASE_URL` with staging.
3. **Branches** — `stage` → staging CD; `main` → prod CD. Both require PRs (no direct push /
   no force-push via rulesets when admin can apply them).
4. **DNS** — Staging: `api.staging.tac-to-iwxxm.com` / `app.staging.tac-to-iwxxm.com` →
   **staging cluster LB** (new EXTERNAL-IP after provision). Prod hosts unchanged on prod LB
   (`168.144.12.70` until rotated).
5. **Promote path** — Only PRs from `stage` → `main`. CI job `staging-gate` requires green
   **Staging smoke** for the tip SHA. After merge to `main`, prod Deploy runs automatically.
6. **Solo-dev** — No required Environment reviewers; the PR is the manual step.
7. **IaC** — Kustomize overlays `deploy/doks/overlays/{staging,prod}`; CD uses
   **per-environment kubeconfig** (`KUBE_CONFIG` / `KUBE_CONFIG_STAGING` or GH Env secrets).
8. **Teardown** — After staging cluster smokes green, delete shared-cluster namespace
   `metar-iwxxm-staging` from the **prod** cluster (EV-043 leftover).

## Consequences

- Skills 12/13/15/16 and ci-after-push must distinguish `env_role: staging | prod` **and**
  cluster/project (not only namespace).
- Staging and prod no longer share node-pool memory; staging worker may run at 1 replica
  without starving prod.
- Cost: second cheapest DOKS node + cheapest managed PG.
- DNS for staging lives at the domain registrar (Porkbun NS), not DigitalOcean DNS.

## Alternatives considered

- App Platform dual apps — rejected (diverges from F30 DOKS).
- Environment approval for prod — rejected for solo-dev friction.
- Same-cluster two namespaces (EV-043) — superseded for DO Project visibility / isolation
  (EV-044); promote CD policy retained.
