# 08-verify-build — S042 / EV-034

**Date:** 2026-08-05  
**Scope:** Delta — F30 DOKS CD rollout (`#867` on `main` @ `318ad304`)  
**Mode:** evolve / Standard

## Result: PASS (scoped)

| Check | Result | Notes |
|-------|--------|-------|
| Format (`make format-check`) | PASS | ruff + prettier |
| Lint (`make lint-py`) | PASS | |
| Typecheck (`make typecheck-py`) | PASS | 0 errors (pre-existing tac2iwxxm warnings only) |
| DOKS CD guard tests | PASS | `tests/test_doks_cd_rollout_guard.py` (3) |
| DOKS kustomize unit | PASS | `tests/unit/test_doks_kustomize_t61.py` (9) |
| H0c CORS (`test_cors_policy.py`) | PASS | 6 |
| Connectivity artifacts | PRESENT | `tests/smoke/test_staging_connectivity.py` |
| Rollout wiring | OK | `scripts/deploy/doks_rollout_images.sh` + Deploy job `KUBE_CONFIG` fail-closed |
| Remote CI (#867 merge) | PASS | PR checks green; Deploy skipped on PR (expected) |

## Catch-up (not blocking 08)

| Item | Status |
|------|--------|
| Deploy fail (`doctl` / exec auth) | Understood — secret was exec-auth kubeconfig |
| Cluster rerun | Succeeded on `…318ad30` (`318ad304` = merge #867) |
| Hotfix [#868](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/868) | OPEN · CI **green** · **merge held** (`D-S042-868-hold`) |

## Gate C→D readiness

- Tasks T1.1–T1.5: completed  
- Latest 08: **pass**  
- **Recommend:** merge #868 before 13-deploy-smoke so CD permanently rejects doctl exec auth  

## Next

09-qa → 11-verify-impl → 12-verify-deploy → 13-deploy-smoke (after #868 merge approval).
