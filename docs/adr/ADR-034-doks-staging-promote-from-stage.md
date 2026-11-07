# ADR-034: DOKS staging + promote-from-stage CD (F30 deepen / #886)

> **Status**: Accepted (S052 / EV-043); **Amended** (S053 / EV-044 — dual DOKS clusters;
> S056 follow-up — release bump+tag on promote; S060 / EV-051 — tag-driven prod Deploy;
> **2026-11-07 EV-cd-conjoined-calver-release — main merge ships prod CD; drop `v*-deploy`**)  
> **Date**: 2026-08-08 (EV-051 amend 2026-08-09; CD amend 2026-11-07)  
> **Deciders**: User (issue #886 + Evolve Plan Card; EV-044 project visibility; promote-release;
> EV-051 solo tag/dispatch gate; EV-cd-conjoined-calver-release intake)  
> **Amends**: [ADR-033](ADR-033-platform-independence-auth-do-doks.md) (single prod DOKS → dual env)  
> **Related**: F30; F12–F14; [ADR-043](ADR-043-beta-features-pypi-calver.md); [docs/deploy.md](../deploy.md); EV-034 CD rollout  
> **Sessions**: S052 / EV-043; S053 / EV-044; S060 / EV-051; **EV-cd-conjoined-calver-release**

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
3. **Branches** — A push to `stage` starts staging CD after full CI (DOKS + GHCR + TestPyPI
   for packages that changed). A push to `main` runs full CI, then prod CD (DOKS + GHCR +
   GitHub Release + PyPI for packages that changed). Both branches require PRs (no direct
   push / no force-push via rulesets when an admin can apply them). This replaces EV-051
   “CI-only on main”.
4. **DNS** — Staging: `api.staging.tac-to-iwxxm.com` / `app.staging.tac-to-iwxxm.com` →
   staging cluster LB (new EXTERNAL-IP after provision). Prod hosts stay on the prod LB
   (`168.144.12.70` until rotated).
5. **Promote path** — Only PRs from `stage` → `main`. CI job `staging-gate` requires green
   Staging smoke for the tip SHA. A merge to `main` lands the code. After green CI, prod CD
   rolls DOKS/GHCR, creates one GitHub Release, and creates PyPI package tags for packages
   that changed (see (6)/(7)).
6. **Release on promote (required for prod cutover)** — Treat each prod ship as a release.
   Cut `docs/CHANGELOG.md` on `stage` before the promote PR. After merge to `main` and green
   CI, CD creates GitHub Release `vYYYY.M.D[.N]` and `{pkg}-v{version}` tags for packages
   that changed only (CalVer per ADR-043). Docs-only or infra-only: Release + DOKS/GHCR;
   skip PyPI. Staging gate still enforces smoke and path (prints a reminder).
7. **Solo-dev prod gate** — No required Environment reviewers. Manual step: PR `stage`→`main`.
   Manual redeploy: `workflow_dispatch` → production. Do not require `v*-deploy` tags.
   Deploy `needs` include the full unit/native/perf matrix plus `e2e-smoke`.
8. **IaC** — Kustomize overlays `deploy/doks/overlays/{staging,prod}`; CD uses
   **per-environment kubeconfig** (`KUBE_CONFIG` / `KUBE_CONFIG_STAGING` or GH Env secrets).
9. **Teardown** — After staging cluster smokes green, delete shared-cluster namespace
   `metar-iwxxm-staging` from the **prod** cluster (EV-043 leftover).

## Consequences

- Skills 12/13/15/16 and ci-after-push must distinguish `env_role: staging | prod` and
  cluster/project (not only namespace). Prod CD runs on a `main` push after CI. Manual
  `workflow_dispatch` remains for redeploy without a merge.
- Promote PRs should include CHANGELOG prep. Agents follow
  `.cursor/rules/optional/doks-promote-from-stage.mdc` §Release on promote. A merge to
  `main` is what rolls prod.
- Staging and prod no longer share node-pool memory; staging worker may run at 1 replica
  without starving prod.
- Cost: second cheapest DOKS node + cheapest managed PG.
- DNS for staging lives at the domain registrar (Porkbun NS), not DigitalOcean DNS.

## Alternatives considered

- App Platform dual apps: rejected (diverges from F30 DOKS).
- Environment approval for prod: rejected for solo-dev friction.
- Auto Deploy on every `main` push: restored by EV-cd-conjoined-calver-release (replaces
  EV-051 tag-only prod Deploy). `v*-deploy` tags are retired.
- Same-cluster two namespaces (EV-043): replaced for DO Project visibility / isolation
  (EV-044). The promote CD path still ships prod on a merge to `main`.
