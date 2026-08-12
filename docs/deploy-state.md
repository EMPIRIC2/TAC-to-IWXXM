# Deploy State

> Last updated: 2026-08-12  
> Status: **staging current** (Quality metrics detail + collapsible diffs closed on `stage`);
> **production** last promoted 2026-08-10. Promote `stage`→`main` **deferred**.

## Environments

| Env | Branch tip | Cluster / ns | FE | API | Notes |
|-----|------------|--------------|----|-----|-------|
| **Staging** | `stage` @ `c4d2cf68` (docs [#990](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/990); product [#989](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/989) @ `b4a63ab8`) | `metar-iwxxm-staging` | https://app.staging.tac-to-iwxxm.com | https://api.staging.tac-to-iwxxm.com | Quality metrics live; Staging Deploy + smoke + connectivity checks **PASS** |
| **Production** | `main` @ `d7117ca4` ([#976](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/976) promote) | `metar-iwxxm` | https://app.tac-to-iwxxm.com | https://api.tac-to-iwxxm.com | Last CHANGELOG window 2026-08-10; deploy tag path per [deploy.md](deploy.md) |

## Staging log (recent)

| # | Step | Status | Date | Notes |
|---|------|--------|------|-------|
| 1 | Quality metrics tab (official corpus compare) | done | 2026-08-10+ | Landed on `stage`; see session S063 reports |
| 2 | C14N match/diff + IWXXM 2025-2 validate disposition | done | 2026-08-11 | [#985](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/985) → `stage` @ `4b48c8d8`; CD [31534191417](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31534191417) |
| 3 | Pretty-print C14N diffs (readability hotfix) | done | 2026-08-11 | [#987](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/987) → `stage` @ `340b3cf6` |
| 4 | Quality metrics detail page + collapsible diffs | done | 2026-08-11 | [#989](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/989) → `stage` @ `b4a63ab8`; CD [31545833142](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31545833142); docs [#990](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/990) @ `c4d2cf68` |
| 5 | Promote `stage`→`main` | **deferred** | — | Explicit ask required |

## Production log (last promote)

| # | Step | Status | Date | Notes |
|---|------|--------|------|-------|
| 1 | Promote (2026-08-10 window) | done | 2026-08-10 | [#976](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/976) `stage`→`main`; see [CHANGELOG.md](CHANGELOG.md) |
| 2 | Deploy / smoke | done | 2026-08-10 | Tag-driven prod Deploy |
| 3 | Prior | historical | 2026-08-07 | [#899](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/899) @ `e3d1c7c8` |

## Rollback

Prior DOKS/GHCR image tag via `scripts/deploy/doks_rollout_images.sh` against the matching
cluster secret (staging ≠ prod). See [deploy.md](deploy.md).

## Session pointers

| Topic | Report |
|-------|--------|
| Quality metrics detail + collapsible diffs | [evolve-report-EV-056.md](evolve-report-EV-056.md) · [S066 deploy-smoke](sessions/S066-quality-metrics-diff-page/reports/deploy-smoke.md) |
| C14N + 2025-2 validate | [evolve-report-EV-055.md](evolve-report-EV-055.md) |
| Quality metrics tab | [evolve-report-EV-054.md](evolve-report-EV-054.md) |
| Diff long-line hotfix | [BUG-2026-08-11](bug-reports/BUG-2026-08-11-quality-metrics-diff-long-line.md) |
