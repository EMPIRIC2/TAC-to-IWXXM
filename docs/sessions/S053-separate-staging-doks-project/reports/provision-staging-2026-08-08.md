# Staging provision — S053 / EV-044 (2026-08-08)

[Corpus: adr/ADR-034] [Corpus: deploy] [Corpus: product §F30]

## DO Projects

| Project | Resources |
|---------|-----------|
| **Staging TAC-to-IWXXM** (`2e56d1cb-…`) | DOKS `metar-iwxxm-staging` + Postgres `metar-iwxxm-staging` |
| **TAC-to-IWXXM** (`ae6ecdab-…`) | DOKS `metar-iwxxm` + Postgres `metar-iwxxm` (unchanged) |

## Resources

| Kind | Name | ID | Spec | Region |
|------|------|-----|------|--------|
| DOKS | `metar-iwxxm-staging` | `9a595c0a-c07a-4ee5-a939-c65f371ff827` | 1× `s-2vcpu-4gb`, k8s `1.34.10-do.0` | `nyc1` |
| Postgres | `metar-iwxxm-staging` | `c50ae4dd-30c7-4c2b-a884-0f73439a40bf` | `db-s-1vcpu-1gb` / PG 16 | `nyc1` |

## Firewall

- Staging DB trusted source: DOKS cluster `9a595c0a-…` (k8s rule)

## Ingress / cert-manager (T2.3)

| Item | Value |
|------|-------|
| ingress-nginx | installed (cloud provider manifest v1.12.2) |
| cert-manager | installed (v1.17.2) |
| **Staging LB** | `143.244.202.13` |

## Remaining (T2.4–T3.*)

- [ ] Porkbun A: `api.staging` / `app.staging` → `143.244.202.13`
- [ ] Apply `deploy/doks/overlays/staging` + secrets against staging context
- [ ] Set GH Environment `staging` `KUBE_CONFIG` to staging cluster
- [ ] Tear down prod-cluster ns `metar-iwxxm-staging` after smoke
- [x] Workflow parity: `stage` branch triggers (this commit)

**Secrets:** connection password is **not** recorded here — use `doctl databases connection` / DO UI.
