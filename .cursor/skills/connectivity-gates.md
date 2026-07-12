# Connectivity Gates

Cross-stage requirements for browser ↔ API wiring when the project includes a frontend
(monorepo or separate repo). API-only backends may skip H4–H5.

## Health tier summary

| Tier | What it checks |
|------|----------------|
| H0c | CORS config unit tests (code) |
| H0i | Local integration (DB + API) |
| H3 | Live API smoke (pytest against Render) |
| H4 | Live CORS from browser origin |
| H5 | Frontend build-time `VITE_*` URLs resolve |
| H6 | Live Playwright UJ-001–007 (+ UJ-008) against Render frontend |
| **H7** | Live bulletin → split → convert → Schematron (UJ-011 / TC-LIVE-F6-030) |

## Stage expectations

| Stage | Connectivity requirement |
|-------|--------------------------|
| **01-requirements** | Specs cover `VITE_*` build URLs, CORS origins, browser UJ steps |
| **12-verify-deploy** | `docs/deploy.md` §Integration documents cross-service wiring |
| **13-deploy-smoke** | Run H4–H5 when frontend exists |
| **15-service-health** | UI reports → H4–H5 before deep API smokes |

## Topology (staging)

| Service | Build-time env | Points to |
|---------|----------------|-----------|
| Frontend | `VITE_API_BASE_URL` | API base URL (includes `/api/v1/*` and `/auth/*`) |
| API | `METAR_CORS_ORIGINS` | Allowed browser origins |

Exact variable names documented in `docs/deploy.md` and `docs/ops/staging-secrets-matrix.md`.

## Run-time CORS

API services must allow origins where the frontend is hosted. Document in `docs/deploy.md`.

## Smoke commands

```bash
# Example — replace with project scripts
curl -sf "{{STAGING_URL}}/health"
# Optional: bash scripts/deploy/verify_connectivity.sh
```

## Common failures

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| UI “Failed to fetch” | Missing CORS origin | Update CORS env + redeploy API |
| Wrong API host in UI | Empty `VITE_*` at build | Set build-time secrets + redeploy frontend |
| H3 pass, UI fails | Stale frontend bundle | Redeploy frontend after API URL change |

## References

- [deployment-catalog.md](deployment-catalog.md)
- `docs/deploy.md` §Integration
