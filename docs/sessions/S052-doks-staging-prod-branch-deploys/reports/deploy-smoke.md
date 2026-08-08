# 13-deploy-smoke — S052 / EV-043

`env_role`: **staging** provisioned + **prod** unchanged

## Staging (Host-header until DNS)

| Check | Result |
|-------|--------|
| `kubectl -n metar-iwxxm-staging get deploy` | api/frontend/worker Running |
| Host-header API `/health` | **200** |
| Host-header FE `/` | **200** |
| HTTPS staging DNS | pending Porkbun A records |
| Certificate Ready | False until DNS |

## Prod

| Check | Result |
|-------|--------|
| `https://api.tac-to-iwxxm.com/health` | unchanged (not redeployed this cycle yet) |

## CD path

Land EV-043 on `stage` first → Staging smoke → PR `stage`→`main` → prod Deploy.
