# Service Health — S022 / #781 rename cutover

> Date: 2026-07-27  
> Stage: 15-service-health  
> Session: S022-rename-cutover  
> Status: **infra cutover PASS** — hand off to 13 for browser UJ-032

## Summary

Retargeted live Render primary services to Empiric2 GHCR with a classic
`read:packages` credential. API + FE + worker deploys **live**. H0c / H1 / H4 / H5
script checks **PASS**. Goldens Examples UI present in live App chunk.

## Mutations applied

| Action | Result |
|--------|--------|
| Render credential `empiric2-ghcr-read-packages` (`rgc-d9jbaq7lk1mc73fspkag`) | Updated with classic PAT (`read:packages`) |
| API `imagePath` | `ghcr.io/empiric2/tac-to-iwxxm/backend:main-latest` + credential |
| FE `imagePath` | `ghcr.io/empiric2/tac-to-iwxxm/frontend:main-latest` + credential |
| Worker `repo` | `https://github.com/EMPIRIC2/TAC-to-IWXXM` |
| Redeploy API / FE / worker | All **live** |

### Deploy IDs

| Service | Deploy | Image / commit |
|---------|--------|----------------|
| API | `dep-d9jbdsvaqgkc73b84i90` | empiric2 backend `main-latest` |
| FE | `dep-d9jbdternols738fsmd0` | empiric2 frontend `main-latest` (`20260727011653-6b9d2b9`) |
| Worker | `dep-d9jbdtbeo5us73b4udog` | build @ `6b9d2b9` from EMPIRIC2 repo |

## Health matrix

| Tier | Result | Notes |
|------|--------|-------|
| H0c | **PASS** | 6 CORS unit tests |
| H1 | **PASS** | `GET /health` → 200 healthy; tac2iwxxm available |
| H2 | deferred | No DB migration in this cutover; reuse prior green |
| H3 | deferred → 13 | Full API smoke optional in 13 |
| H4 | **PASS** | Live CORS preflight (2 tests) |
| H5 | **PASS** | `/config.json` → API base URL correct |
| Goldens bundle | **PASS** | `App-*.js` contains `Examples`, `Load golden`, `annex3_golden`, `ahl_bulletin` |
| UJ-032 browser | **→ 13** | Click-to-load Examples on live workbench |

## Credential notes

- Fine-grained PATs **cannot** access GitHub Packages; classic `read:packages` required.
- First fine-grained attempt lacked scope; classic PAT verified (packages API 200 + GHCR pull 200).
- **Rotate** chat-pasted tokens after session (exposed in transcript).

## Remaining #781 (not blocking 13)

| Item | Status |
|------|--------|
| PyPI Trusted Publisher → EMPIRIC2 | pending (org admin) |
| Optional missing Actions secrets (e2e/load) | pending if workflows needed |
| Legacy joseph-repo Render services | out of primary cutover (deferred) |
| Hostname rename `tac-to-iwxxm-*` | out of scope |

## Next

Run **13-deploy-smoke**: browser UJ-032 Examples load on live FE; close #781 AC when PyPI/secrets disposition decided.
