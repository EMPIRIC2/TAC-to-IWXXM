# Deploy checklist — S015 / EV-011 (12-verify-deploy)

> Generated: 2026-07-20  
> Prerequisite: `verify-impl.md` PASS (T5.8)  
> Target: Render API `metar-to-iwxxm-api` + static frontend; optional PyPI tag

## Strategy (unchanged from tech plan)

| Service | Runtime | Image / source |
|---------|---------|----------------|
| API | Render web (image) | `ghcr.io/.../backend:main-latest` — **requires merge to `main` before new routes ship** |
| Frontend | Render static | Vite build from `main` (or connected branch) |
| Worker | Background worker | Unchanged this cycle (no F8 delta) |

## Checklist

### Config / secrets

- [x] No new runtime secrets for catalog GET (uses existing auth JWT gate)
- [x] `METAR_CORS_ORIGINS` / frontend origin matrix unchanged (H0c green; re-check H0c after API image)
- [x] `VITE_API_BASE_URL` still points at API host (catalog is same origin path `/api/v1/lint-issue-catalog`)

### Connectivity readiness (Agent 6)

- [x] H0c unit coverage includes `/lint-issue-catalog` GET preflight
- [x] Plan: `scripts/deploy/verify_connectivity.sh` (or project equivalent) after redeploy for H4–H5
- [ ] H4–H5 executed (T5.10)

### Failure modes

| Risk | Mitigation |
|------|------------|
| Image still on pre-F15 `main` | Merge PR #742 → wait GHCR `main-latest` → `POST /deploys` |
| FE bundles old client | Redeploy static site after API is healthy |
| Catalog 401 in browser | Confirm Bearer hydrate (BUG-2026-07-15 pattern) |

### PyPI (E11-25)

- [ ] After F15 acceptance on `main`: tag `tac-validate-v0.1.1` and publish via existing OIDC workflow
- [ ] No iwxxm-validate / tac2iwxxm bump unless convert goldens force it (E11-25)

### Rollback

- Revert merge commit on `main` or pin previous GHCR digest; Redeploy prior image tag.

## Sign-off

**12-verify-deploy: READY** — deploy blocked only on **merge of #742 to `main`** then T5.10 smoke (H1–H5 required).
