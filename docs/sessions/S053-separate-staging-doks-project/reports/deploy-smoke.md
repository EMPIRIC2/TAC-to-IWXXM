# Deploy smoke — S053 / EV-044

[Corpus: adr/ADR-034] [Corpus: deploy] [Corpus: tests §TC-F30-008..012]

`env_role`: staging + prod (dual cluster)

| Check | Result |
|-------|--------|
| Staging DNS A → `143.244.202.13` | PASS |
| Staging TLS (`metar-api-tls`, `metar-frontend-tls`) | READY |
| HTTPS `api.staging…/health` | 200 |
| HTTPS `app.staging…/` | 200 |
| `scripts/deploy/staging_smoke.sh` | PASS |
| Prod `api.tac-to-iwxxm.com/health` | 200 |
| Prod cluster ns `metar-iwxxm-staging` | NotFound (torn down) |
| Promote refs (staging LB in gate/smoke) | updated 2026-08-08 |

**Promote path:** feature → `stage` → Staging smoke → PR `stage`→`main` → Staging gate → prod Deploy.
Full `staging-gate` CI exercises on the next legitimate `stage`→`main` PR (TC-F30-012).
