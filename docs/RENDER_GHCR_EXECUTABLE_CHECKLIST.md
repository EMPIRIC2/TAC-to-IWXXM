# Render + GHCR Executable Checklist

Last updated: 2026-02-21

## Scope

Goal: deploy frontend, auth, and API with a production-safe workflow and verify live behavior end-to-end.

Canonical live services currently validated:
- API: `metar-to-iwxxm-api` (`srv-d69v688gjchc73cn9kg0`)
- Auth: `metar-to-iwxxm-auth-v2` (`srv-d6chmq24d50c73a4a2ig`)
- Frontend: `metar-to-iwxxm-frontend-v4-web` (`srv-d6cvj2i4d50c73aelapg`)

## Status Summary

- [x] Frontend preflight failure fixed by setting:
  - `VITE_SUPABASE_URL`
  - `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY`
- [x] API/Auth/Frontend latest deploys are `live`
- [x] Live endpoints respond:
  - API `/health` = healthy
  - Auth `/health` = healthy
  - Frontend UI renders
- [ ] Full conversion of all 3 services to image-backed GHCR services is still pending completion

---

## 1) Build locally ensure they are working

- [ ] Build `linux/amd64` backend image locally
- [ ] Build `linux/amd64` auth image locally
- [ ] Build `linux/amd64` frontend image locally
- [ ] Run local smoke test for all 3 containers

Pass criteria:
- All images build successfully
- Health endpoints respond in local run

Note:
- In the current coding environment, Docker CLI is unavailable (`docker: command not found`).
- Execute this step on a machine with Docker installed.

Suggested commands (run outside this container):

```bash
# backend
docker build --platform linux/amd64 -f backend/docker/Dockerfile -t ghcr.io/joseph-c-mcguire/metar-to-IWXXM/backend:manual-test backend

# auth
docker build --platform linux/amd64 -f auth/Dockerfile -t ghcr.io/joseph-c-mcguire/metar-to-IWXXM/auth:manual-test auth

# frontend (repo-specific Dockerfile/location may differ)
docker build --platform linux/amd64 -f frontend/Dockerfile -t ghcr.io/joseph-c-mcguire/metar-to-IWXXM/frontend:manual-test frontend
```

## 2) Ensure their communicating properly

- [x] Live API health verified
- [x] Live Auth health verified
- [x] Live Frontend reachable after env fix
- [ ] Perform browser E2E flow against live stack (login/register + one conversion action)

Pass criteria:
- No preflight env error banner on frontend
- Auth flow succeeds
- Frontend request reaches backend conversion endpoint successfully

## 3) Push to GitHub

- [x] Monorepo update pushed (`render.yaml` change)
- [x] Frontend repo update pushed (strict env validation + startup preflight)

Pass criteria:
- Remote `main` includes expected commits

## 4) Ensure pushes and builds were successful

- [x] Frontend production build succeeded in workspace
- [ ] CI image build/push verification for all 3 images (GHCR tags/digests) still required

Pass criteria:
- GHCR contains backend/auth/frontend images for deployment tags

## 5) Push to Render

- [x] Render env updates applied to API/Auth/Frontend
- [x] Frontend required Supabase env vars applied
- [ ] Full GHCR image-backed rollout for all 3 services still pending (new image-backed services or runtime migration)

Pass criteria:
- Services deploy from intended GHCR image tags/digests

## 6) Wait for build

- [x] API latest deploy reached `live` (`dep-d6d0os8gjchc73e56elg`)
- [x] Auth latest deploy reached `live` (`dep-d6d0os7pm1nc739h24bg`)
- [x] Frontend latest deploy reached `live` (`dep-d6d14lvfte5s73d3j7b0`)

## 7) Ensure build succeeded

- [x] Live service checks succeeded for current production URLs
- [ ] Final GHCR image-backed verification pending completion of step 5 image migration

Pass criteria:
- Deploy status `live` for all 3 image-backed services
- Endpoint and user-flow checks pass post-cutover

---

## Remaining Actions to Complete Full GHCR Image-Backed Target

1. Ensure all three deploy targets are truly image-backed (not source/runtime-backed).
2. Verify GHCR credentials configured in Render workspace for private pulls.
3. Trigger deploys using deploy hooks with explicit `imgURL` tags/digests.
4. Re-run step 2 E2E checks after image-backed cutover.
5. Optionally decommission/suspend superseded services after burn-in.
