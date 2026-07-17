# Deploy Checklist — S013 / EV-009 (stage 12-verify-deploy, T4.4)

> Generated: 2026-07-17
> Status: **ready** (pending user sign-off + PR CI green)
> Deployment plan: `docs/deploy.md` + `docs/tech-spec.md` (unchanged this cycle — execution-plan §Tech Stack "Deploy: Unchanged")
> Branch tip: `c31e2d7` on `evolve/S013-live-decode-preview-ux` (31 commits ahead of `main` @ `4b6cff8`)
> PR: **#723** `[EV-009] F9/F10 — live decode translations + preview UX` → `main`

## Target topology (unchanged from S011 checklist)

| Role | Render service | URL |
|------|----------------|-----|
| API | `metar-to-iwxxm-api` | https://metar-to-iwxxm-api.onrender.com |
| Frontend | `metar-to-iwxxm-frontend-v4-web` | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| Worker | `metar-to-iwxxm-worker` | untouched this cycle |

Deploy mode: **image** (`RENDER_DEPLOY_MODE=image` in `ci-cd.yml`) → GHCR `main-latest` images + Render deploy hooks on **main** push after merge.

## Delta scope (what this deploy actually changes)

- Changed surfaces: `apps/backend` (additive `decode-tac` `summary`; lint-tac `info` severity + `fixes[]` passthrough), `apps/frontend` (Plain-language block, `IwxxmPreviewPane`, quick fix), `packages/tac2iwxxm`, `packages/tac-validate`, `apps/e2e`.
- **No** new endpoints, env vars, secrets, CORS origins, DB migrations, or dependencies (verified: `git diff origin/main...HEAD` touches no `render.yaml`, `.github/workflows/`, or `supabase/` files).
- Decode/lint contracts additive-only (qa-report §Consistency; api-contract §decode-tac/§lint-tac).

## Pre-deploy checks

| Area | Status | Evidence |
|------|--------|----------|
| Configuration complete | PASS | No infra/config delta vs main; `render.yaml` + `ci-cd.yml` untouched |
| Secrets | PASS | No new secrets required; existing prod env unchanged (S011 matrix still current) |
| Data / volumes / migrations | N/A | No DB or schema changes this cycle |
| Resource allocation | PASS | No compute/scaling change; same services and plans |
| H0c CORS unit tests | PASS | `pytest tests/unit/test_cors_policy.py` — 6 passed (re-run fresh at stage 12, 2026-07-17) |
| `VITE_*` ↔ API URL matrix | PASS | `docs/ops/staging-secrets-matrix.md` — `VITE_API_BASE_URL` ↔ `METAR_CORS_ORIGINS` rows complete; no new rows needed |
| `METAR_CORS_ORIGINS` documented | PASS | Live prod `corsOrigins` = frontend URL (verified via `/config.json` 2026-07-17) |
| Live health (current prod) | PASS | API `/health` 200; frontend `/config.json` 200 with matching `api.baseUrl` (2026-07-17) |
| Live H4–H5 (pre-deploy) | PASS | QA-002 resolution: `verify_connectivity.sh` H0c 6/6, H4 2/2, H5 PASS (2026-07-17) |
| Connectivity scripts present | PASS | `scripts/deploy/verify_connectivity.sh` + `tests/smoke/test_staging_connectivity.py` |
| 11-verify-impl | PASS | F9 + F10 user-approved ("1 / 1"); `verify-impl.md` |
| PR to main | OPEN | #723 — CI (`ci-cd.yml` pull_request) must be green before merge |
| CI watch script | WARN | `scripts/ci/watch_github_ci.sh` referenced by rules does not exist in repo — watched via `gh pr checks` instead |

## Failure modes & mitigations

| # | Risk | Mitigation | Status |
|---|------|-----------|--------|
| 1 | Deploy image without EV-009 commits | Merge PR #723 → main before CI image build; image tags follow main push | mitigated by sequence |
| 2 | CI red on PR (image build / test failure) | `gh pr checks 723 --watch`; fix before merge (ci-after-push rule) | in progress |
| 3 | Frontend/backend version skew during rollout (frontend expects `summary`) | `summary` is additive with default `""`; DecodePanel renders block only when summary present — old API + new FE degrades gracefully | accepted (by design) |
| 4 | CORS regression | No origin changes; H4–H5 re-run post-deploy at 13 (`verify_connectivity.sh`) | mitigated |
| 5 | Lint severity change breaks existing clients | `ok` semantics unchanged (keyed off `error`); severity enum already included `info`; contract test T2.3 | mitigated |
| 6 | Cold start / memory | No new dependencies or workloads; image footprint unchanged | accepted |
| 7 | Rollback needed post-deploy | Redeploy previous Render deploy / prior GHCR image tag from dashboard (same as S011) | documented below |

## Rollback

- **Command**: Render dashboard (or API `POST /services/{id}/deploys` with prior image) → redeploy previous deploy for `metar-to-iwxxm-api` and `metar-to-iwxxm-frontend-v4-web`.
- **Procedure**: identify last-known-good deploy (pre-merge `main` @ `4b6cff8`, images `main-latest` prior tags) → trigger rollback deploy per service → re-run `verify_connectivity.sh` + `/health`.
- **Data**: no migrations this cycle → rollback is image-only, no DB restore needed.
- **Last known good**: `main` @ `4b6cff8` (PR #722 merge; prod verified healthy 2026-07-17).

## Recommended deploy sequence (T4.4 → T4.5)

1. This checklist + state bookkeeping committed to the evolve branch (done with this commit).
2. PR **#723** CI green (`ci-cd.yml` pull_request run).
3. **Explicit user approval** → merge #723 into `main`.
4. `main` push builds GHCR images + fires Render deploy hooks (API, frontend).
5. Stage 13 (T4.5): H1–H3 API smokes → `verify_connectivity.sh` (H4–H5) → H6′ UJ-020/021 live smokes.

## Sign-Off

- [x] User approved implementation (11-verify-impl — F9/F10 "1 / 1")
- [ ] Deploy strategy verified (user AskQuestion at this checkpoint)
- [ ] PR #723 CI green
- [ ] Ready to deploy (merge approval → 13-deploy-smoke)
