# 13-deploy-smoke — S046 / EV-038 (T5.4)

> Date: 2026-08-06  
> Status: **APPROVED** (`D-S046-13`=1) — EV-038 / S046 closed  
> Merge: [#890](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/890) @ `619a7ac3`  
> CI Deploy: [31112016561](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31112016561) **success**  
> DOKS tag: `20260806144346-619a7ac`  
> Env: **live/prod** (`api.tac-to-iwxxm.com` / `app.tac-to-iwxxm.com`)  
> Corpus: `[Corpus: tech-spec]` · `[Corpus: tests]` · connectivity-gates §13

## CD rollout

```
metar-api      -> ghcr.io/empiric2/tac-to-iwxxm/backend:20260806144346-619a7ac
metar-frontend -> ghcr.io/empiric2/tac-to-iwxxm/frontend:20260806144346-619a7ac
```

`kubectl` confirmed both deployments on tip tag after Deploy job.

## Smoke matrix

| Tier | Check | Result |
|------|-------|--------|
| H0ci | main CI/CD Pipeline @ `619a7ac3` | **PASS** (Deploy SUCCESS) |
| H1 | `GET /health` | **200** `healthy` + `tac2iwxxm_available` |
| H1 | `GET https://app.tac-to-iwxxm.com/` | **200** |
| H2–H3 | `make test-live-api` | **20 passed, 1 skipped** |
| H0c | CORS unit (`test_cors_policy.py`) | **6/6** |
| H4 | Live CORS preflight (`test_staging_connectivity.py`) | **2/2** |
| H5 | `config.json` `api.baseUrl` | **PASS** → `https://api.tac-to-iwxxm.com` |
| UJ-050 | Live App chunk SoT + `roleLabel` / `versionOptionLabel` | **PASS** (`2025-2`/`latest`, `2023-1`/`previous`; `Latest`/`Previous` in `App-*.js`) |

## Notes

1. **`verify_connectivity.sh` bash 3.2 / `set -u` empty-array** — previously unbound on macOS (S040 advisory). Fixed locally for this run (Host-header helpers only when provisional). Follow-up commit recommended on `main`.
2. UJ-050 strings live in code-split `App-*.js`, not the thin `index-*.js` loader.
3. API `/api/v1/versions` returns `status: latest|previous` aligned with FE SoT.

## Overall

**Technical PASS** — merge → DOKS CD → H1–H5 + UJ-050 live proof complete.

**`D-S046-13`=1** — cycle closed.
