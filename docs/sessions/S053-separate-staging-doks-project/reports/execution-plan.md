# Execution plan — S053 / EV-044

[Corpus: product §F30] [Corpus: adr/ADR-034] [Corpus: deploy] [Corpus: tests]

## Goal

Separate staging onto its own DOKS + Postgres under DO Project **Staging TAC-to-IWXXM**;
keep prod on **TAC-to-IWXXM**; preserve promote-from-stage CD.

## Out of scope

Product UI; App Platform; changing staging-gate / promote policy; Render reopen.

## Milestones

| ID | Name | Tasks |
|----|------|-------|
| M1 | Specs + tooling | T1.* (Phase A — done) |
| M2 | Provision + assign | T2.* |
| M3 | CD + cutover + teardown | T3.* |
| M4 | Verify + smoke | T4.* |

## Tasks

| ID | Type | Task | Spec Source | Depends On | Status |
|----|------|------|-------------|------------|--------|
| T1.1 | docs | F30 AC8–13 + ADR-034 amend + evolve-decisions EV-044 + deploy/test/runbook | feature-list; ADR-034; #886 residual | — | **completed** |
| T1.2 | rule | promote-from-stage rule dual DO Project / dual cluster | ADR-034 | T1.1 | **completed** |
| T2.1 | ops | Provision staging DOKS `metar-iwxxm-staging` 1× `s-2vcpu-4gb` nyc1; assign to **Staging TAC-to-IWXXM** | D-S053-size; ADR-034 | T1.1 | **completed** |
| T2.2 | ops | Provision staging Postgres `metar-iwxxm-staging` `db-s-1vcpu-1gb`; assign to Staging project; Alembic upgrade; firewall DOKS | D-S053-db; TC-F30-008 | T2.1 | **completed** (Alembic pending apply) |
| T2.3 | ops | Install ingress-nginx + cert-manager on staging cluster; note LB EXTERNAL-IP | deploy.md; DNS runbook | T2.1 | **completed** (`143.244.202.13`) |
| T3.0 | ci | Add `stage` to all workflows that push/PR on `main` (parity) | user 2026-08-08 | T1.1 | **completed** |
| T2.4 | ops | Apply `deploy/doks/overlays/staging` + secrets (staging DB URL, Auth, GHCR pull) | overlays; staging-secrets-matrix | T2.2, T2.3 | **completed** (Host-header `/health` 200) |
| T3.1 | ci | Ensure GH Env `staging` `KUBE_CONFIG` = staging cluster (prod Env keeps prod kubeconfig); document if workflow change needed | ci-cd.yml; TC-F30-010 | T2.1 | **completed** (`gh secret set` staging+production+repo) |
| T3.2 | ops | Porkbun A records → staging LB; wait TLS Ready | TC-F30-009; DNS runbook | T2.3, T2.4 | pending |
| T3.3 | ops | Tear down prod-cluster ns `metar-iwxxm-staging` after staging smoke green | D-S053-teardown; TC-F30-013 | T3.2, T4.1 | **completed** (2026-08-08; Host-header green; HTTPS pending DNS) |
| T3.4 | docs | Update deploy README / skills notes for dual kubeconfig; drop shared-LB wording | deploy.md | T3.1 | pending |
| T4.1 | verify | Staging Host-header + HTTPS smoke; project resource list check | TC-F30-008..010 | T2.4, T3.1 | pending |
| T4.2 | verify | Promote path still green (staging-gate); prod `/health` unchanged | TC-F30-012 | T4.1 | pending |

## CD note

`.github/workflows/ci-cd.yml` already selects `environment: staging|production` and reads
`secrets.KUBE_CONFIG` from that Environment. Prefer **per-Environment secret values** over
a new secret name unless admin UI forces otherwise.

## Provision sizes (locked)

| Resource | Spec |
|----------|------|
| Staging DOKS | 1× `s-2vcpu-4gb`, k8s ~1.34, `nyc1`, name `metar-iwxxm-staging` |
| Staging PG | `db-s-1vcpu-1gb`, PG 16, `nyc1`, name `metar-iwxxm-staging` |

## Build Plan Card seed

- **Goal**: Dual DOKS / dual DO Project staging isolation without breaking promote CD  
- **First build batch**: T2.1–T2.4 then T3.1  
- **Risk**: GH admin 403 on Environment secrets; Porkbun DNS lag; cost ~2× cheapest node + PG
