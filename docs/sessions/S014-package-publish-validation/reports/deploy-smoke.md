# Deploy smoke — S014 / EV-010 (F11–F14)

> Date: 2026-07-19  
> Status: **deployed** — T6.5 APPROVED (D-S014-EV010-t65-approve-A); T6.6 PARTIAL (lib hard FAIL)  
> PR: [#726](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/726) (merged `c73e0ad`)  
> Main tip: `c73e0ad` → CI/CD run `29707270877` Deploy **SUCCESS**  
> API: https://metar-to-iwxxm-api.onrender.com (`dep-d9elikt7vvec739dpf7g` live 2026-07-19T23:10:48Z)  
> Frontend: https://metar-to-iwxxm-frontend-v4-web.onrender.com (`dep-d9elilbtqb8s73ao52hg` live 2026-07-19T23:10:30Z)

## Pre-deploy

| Check | Result |
|-------|--------|
| 12-verify-deploy checklist | Approved (D-S014-EV010-t64-deploy-A) |
| Merge approval | User A (D-S014-EV010-t64-merge-A); PR already MERGED |
| PR #726 CI (pre-merge) | All required checks SUCCESS (tip `bd0aee5`) |
| Merge → main | `c73e0ad` |
| GHCR image build + Render deploy hooks | CI Deploy job success; API + frontend `live` |

## Smoke results

| Tier | What | Result |
|------|------|--------|
| H0ci | CI/CD on `main` @ `c73e0ad` (incl. Deploy) | **PASS** |
| H1 | API `/health` 200 + `tac2iwxxm_available` | **PASS** |
| H0c | CORS policy + msgspec CORS suite | **PASS** 37 (6+8+23) / script path 6/6 |
| H3 | `make test-live-api` | **PASS** 21/21 |
| H4 | Live CORS preflight (FE origin + work-sessions PATCH) | **PASS** 2/2 |
| H5 | Frontend `/config.json` `api.baseUrl` → API | **PASS** |
| H6′ UJ-022 | Live multipart convert → validate → lint-tac → decode-tac | **PASS** |
| UJ-023 tag publish | Live PyPI install | **PASS (bootstrap)** — `0.1.0` on PyPI via API token; TP on existing projects for next tags |

### H6′ UJ-022 detail (live)

| Step | Result |
|------|--------|
| `POST /auth/login` | 200, session JWT |
| `POST /api/v1/convert` multipart golden KJFK | 200, `successful=1`, XML len 2611; keys include `results`/`metadata`/`ok` |
| `POST /api/v1/validate` multipart IWXXM | 200, `is_valid=true` |
| `POST /api/v1/lint-tac` | 200, `ok` + `issues` |
| `POST /api/v1/decode-tac` | 200, `summary` + `segments` |

Commands:

```bash
make test-live-connectivity   # H0c + H4 + H5
make test-live-api            # H3
# H6′: admin login + multipart convert/validate/lint/decode (see above)
```

## Health

- API reachable; convert/auth/validate paths green in H3 + H6′
- CORS matrix unchanged; H4 green post-msgspec (clears prior staging H4 fail / QA-S014-001)
- FE `config.json` points at production API; `corsOrigins` = FE URL

## PyPI

- `0.1.0` published for all three packages (token bootstrap; see `pypi-bootstrap-token.md`)
- Clean-venv install of `tac-validate` / `iwxxm-validate` / `tac2iwxxm[validate]==0.1.0` **PASS**
- Trusted Publishers on **existing** projects for future OIDC tags (`pypi-publish.yml` + env `pypi`)
- Do **not** re-push `*-v0.1.0` tags; next OIDC cut is `0.1.1+`
- T6.6 hard gates: XSD/combined 0.85× + HTTP + wheels **PASS** (`t66-hard-publish-gates.md`)

## Rollback

- Redeploy prior Render deploy / previous GHCR `main-latest` for API then frontend
- Re-run `verify_connectivity.sh` + `/health`
- Last known good pre-EV-010: `main` @ `971c675` (pre-merge tip)
- No DB migrations this cycle — image-only rollback
- PyPI: versions immutable; yank only if critical

## Verdict

**T6.5 / T6.6 / 13-deploy-smoke complete.** F11–F14 live on Render; PyPI `0.1.0` live
(token bootstrap); Trusted Publishers on existing projects for later OIDC tags.
