# Evolve summary — EV-034 / S042 (DOKS CD auto-rollout)

> Date: 2026-08-05  
> Status: **completed** (`D-S042-13` = 1 — approve 11+12+13 / close)  
> Branch: `main` @ `d3f4bb95` (PR #867 + hotfix #868)  
> Features: deepen **F30** (AC7 / TC-F30-007) — no new Fn  
> Close decision: Phase D approved; automated CD proven live

## What shipped

On `main` Deploy after GHCR push, CD pins DOKS workloads to the immutable
`TIMESTAMP-SHA` tag without manual kubectl:

1. `scripts/deploy/doks_rollout_images.sh` — set image + `rollout status` for
   `metar-api` / `metar-frontend` / `metar-worker` in `metar-iwxxm`
2. Wire Deploy job: required `KUBE_CONFIG` (fail-closed); Render hooks optional/non-blocking
3. Static kubeconfig guard — reject `doctl` exec auth (#868)
4. Docs: `docs/deploy.md` CD section; doks README pointer; TC-F30-007

Merged via **PR #867** (feature) + **PR #868** (doctl guard).

## Stages

| Stage | Result |
|-------|--------|
| 00 → 16 → 01 → 02 → 04 → 07 → 08 → 09 | **completed** |
| 10-e2e | **skipped** (CD acceptance, not browser UJ) |
| 11-verify-impl / 12-verify-deploy / 13-deploy-smoke | **completed** (`D-S042-13` = 1) |
| Gates A→B / B→C / C→D / Deploy | **passed** |

## Live proof (13)

| Item | Value |
|------|-------|
| CI Deploy | [31003268652](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31003268652) **success** |
| Tag | `20260805115809-d3f4bb9` |
| Workloads | api / frontend / worker — all `successfully rolled out` |
| Live | `/health` 200; OpenAPI `/auth/login` + `/auth/me`; app 200 |
| Guard | doctl exec-auth check passed before rollout |

## Artifacts

- `reports/verification-report.md` (08)
- `reports/qa-report.md` (09)
- `reports/verify-impl.md` (11)
- `reports/deploy-checklist.md` (12)
- `reports/deploy-smoke.md` (13)
- `reports/execution-plan.md`

## Follow-ups

- **S040 / EV-032** — still **suspended**; eligible to resume now that S042 is closed (do not auto-resume)
- No further CD work required for TC-F30-007

## Decisions

| ID | Choice |
|----|--------|
| E34-1..5 | A,A,A,B,A — Standard; API+FE+worker; immutable tag; `KUBE_CONFIG`; Render optional |
| D-S042-868-hold | hold #868 until user approve → **resolved** (choice 1 merge) |
| D-S042-13 | **1** — approve 11+12+13 and close EV-034 / S042 |
