# 13-deploy-smoke — S052 / EV-043

`env_role`: staging + prod (dual)

## Staging

| Check | Result |
|-------|--------|
| Deploy (stage) + Staging smoke | PASS (runs 31264462312 / successive) |
| Host-header API `/health` | 200 |
| HTTPS DNS/TLS | pending Porkbun |
| Worker replicas | 0 (single-node capacity) |

## Prod

| Check | Result |
|-------|--------|
| Promote PR #941 | MERGED |
| Image tip | `20260808153602-018ea72` |
| `https://api.tac-to-iwxxm.com/health` | 200 |
| CD rollout | timed out once (OOM); completed via brief staging scale-down |

## Staging gate

PASS on promote PR (run 31264463945, ~6m poll).
