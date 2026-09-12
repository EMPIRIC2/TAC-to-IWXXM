# Deploy Checklist — S050 / EV-042 (12-verify-deploy)

> Generated: 2026-08-07  
> Status: **READY** — strategy signed off (`D-S050-12=1`)  
> Prior: 11 **APPROVED** (`D-S050-11-verify`)  
> Deployment: [docs/deploy.md](../../../deploy.md) · DOKS CD on `main`  
> Tip: `4fe4c37f` (docs) · product tip CI `18d028ed` · PR [#899](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/899)  
> Tip CI: [31195470994](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31195470994) **success**  
> `env_role`: **live = prod** (sole DOKS stack `api|app.tac-to-iwxxm.com`)  
> Corpus: [Corpus: tech-spec] [Corpus: product §F7/F16–F19/F33] [Corpus: tests]  
> connectivity-gates §12–13  
> **OOS:** Sync database migrations CI fail (not EV-042 gate)

## Scope (delta)

| Surface | Change | Deploy action |
|---------|--------|---------------|
| `apps/frontend` | Hide Convert&Send / Disseminate / **Upload to Database**; F33 mass Folder/Zip; work queue | FE rebuild via CD on merge |
| `apps/backend` | `POST /api/v1/ingest/mass` + caps/sniff/zip-bomb; mass body limit | API image rebuild via CD |
| `apps/e2e` | UJ-051..053; skip upload-database until #898 | CI Playwright only |
| Env / secrets | Existing mass-ingest knobs in `.env.example`; no new prod secrets required | Document in ops |
| Worker / DB migrations | None | N/A (Sync database migrations CI OOS) |
| Dissemination API | Unchanged (UI-only hide) | No allowlist change |

**Live stack:** DOKS sole env = live/prod. Merge #899 → `main` → CD → **13** H1–H5 (incl. mass route).

## Pre-Deploy

- [x] Configuration complete — destinations gate + mass ingest env knobs documented
- [x] Secrets — no new keys; JWT already required for mass path
- [x] Data assets — N/A
- [x] Resource allocation — unchanged
- [x] Rollback — prior DOKS/GHCR tag / previous rollout
- [x] H0c CORS — `tests/unit/test_cors_policy.py` **6/6 PASS** (2026-08-07)
- [x] Connectivity scripts — `scripts/deploy/verify_connectivity.sh` + `tests/smoke/test_staging_connectivity.py` present (mass H4 wired in T4.1)
- [x] Branch pushed — tip `18d028ed` (product) / `4fe4c37f` (checklist docs)
- [x] Tip CI green — [CI/CD Pipeline 31195470994](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31195470994) **success** @ `18d028ed`
- [x] PR open — [#899](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/899)
- [x] Merge + CD — #899 MERGED @ `e3d1c7c8`; Deploy [31197264636](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31197264636) success
- [x] Post-deploy H1 + **H4–H5** mass ingest (13) — see `deploy-smoke.md`; awaiting `D-S050-13`

## Failure Mitigations

| # | Risk | Mitigation | Status |
|---|------|------------|--------|
| 1 | Image/CD failure | PR CI + DOKS Deploy on `main` | **approved** |
| 2 | CORS miss on `/api/v1/ingest/mass` | H0i local PASS; live H4 at 13 | **approved** (verify at 13) |
| 3 | Operators still see Upload to Database | Gate behind `destinationsEnabled` (`adad127c`); UJ-053 | **approved** |
| 4 | Mass ingest zip-bomb / oversized body | Caps + dedicated body limit (D-S050-C1); TC-F33 | **approved** |
| 5 | Accidental restore of destinations | #898 tracks restore; flag stays false | **approved** |
| 6 | Sync database migrations CI red (OOS) | Not EV-042 gate | **accepted OOS** |

## Rollback

- Roll back DOKS deployments to prior GHCR/DOKS tag
- Re-run `bash scripts/deploy/verify_connectivity.sh`
- No DB migrations this cycle
- Destinations restore is product work (#898), not emergency rollback

## Recommended path (13)

1. Tip CI green on `18d028ed`.
2. User approved this checklist (12) — **done** (`D-S050-12=1`).
3. **Merge** #899 (explicit approval) → DOKS CD.
4. H1–H3 → H4–H5 via `verify_connectivity.sh` (mass route + FE `api.baseUrl`).
5. Optional live Playwright UJ-051..053.

## Sign-Off

- [x] User approved implementation (11) — `D-S050-11-verify`
- [x] User approved deploy strategy (this checklist) — `D-S050-12=1` (2026-08-07)
- [x] Ready for 13-deploy-smoke after merge
