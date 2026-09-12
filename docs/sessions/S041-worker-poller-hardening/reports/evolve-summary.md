# Evolve summary — EV-033 / S041 (worker poller hardening)

> Date: 2026-08-05  
> Status: **completed** (lean-close `D-S041-1+3`)  
> Branch: `main` @ `5245f8de` (PR #865 merge `963a2777`; feature tip `753bc94d`)  
> Features: deepen **F8**  
> Close decision: **D-S041-1+3** = lean-close (waive 09–13) + one-shot DOKS rollout, then open CD session

## What shipped

F8 `metar-worker` **`INGEST_POLLER_URL`** cutover hardening (prevention 1–5 + code guard):

1. Fail-closed scale when poller URL unset/placeholder
2. CI/ops preflight for worker poller URL
3. Docs/env default fixture URL (no `REPLACE_ME` as runnable default)
4. Runbook — do not copy unverified Render poller URLs
5. CrashLoop check + optional PrometheusRule
6. Code guard rejecting `REPLACE_ME` / non-https poller URLs

Merged via **PR #865**.

## Stages

| Stage | Result |
|-------|--------|
| 00 → 16 → 01 → 02 → 04 → 07 → 08 | **completed** (08 PASS @ `5245f8de`) |
| 09-qa / 10-e2e / 11-verify-impl / 12-verify-deploy / 13-deploy-smoke | **waived** (`D-S041-1+3`) |
| Gates A→B / B→C / C→D | **passed** |
| Deploy gate | **passed_via_ops** (DOKS one-shot) |

## DOKS one-shot (ops)

| Item | Value |
|------|-------|
| Tag | `20260805003332-5245f8d` |
| Source | CI Deploy run 30963357296 / #866 merge tip `5245f8de` |
| Workloads | `metar-api`, `metar-frontend`, `metar-worker` in `metar-iwxxm` |
| Rollouts | successful ~2026-08-05 00:49Z |
| Live verify | `/health` 200; OpenAPI `/auth/login` + `/auth/me`; POST login → 422; GET `/auth/me` → 401; logs `metar_auth /auth router successfully` |

## Artifacts

- `reports/verification-report.md` (08 PASS)
- `reports/evolve-progress.md`
- `deploy/doks/README-worker-hardening.md`
- `apps/worker/src/metar_worker/poller_url.py` + validate scripts/tests
- `deploy/doks/observability/prometheusrule-metar-worker.yaml`

## Follow-ups

- **S042 / EV-034** — automate DOKS image rollout in CD (opened after this close)
- **S040 / EV-032** — remains **suspended**; `resume_after` = S042 (do not auto-resume)
- Remaining AC depth for formal 09–13 deferred by lean-close

## Decisions

| ID | Choice |
|----|--------|
| D-S041-open | proceed_1-5_plus_code |
| D-S041-cd-defer | finish_S041_first (superseded for Phase D depth by 1+3) |
| D-S041-1+3 | lean_close_and_doks_oneshot |
