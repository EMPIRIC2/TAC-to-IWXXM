# QA Report — S046 / EV-038 (T5.2 / 09-qa delta)

> Generated: 2026-08-06  
> Scope: Delta QA after Phase C — UJ-050 (#854 Latest/Previous) + residual M1–M4 keep-green  
> Branch: `evolve/EV-038-iwxxm-corpus-residuals` @ `f0280673` (+ T5.2 commits)  
> Mode: evolve delta (Standard Phase D)  
> Prior 08: T5.1 **PASS** (`verification-report.md`)  
> Checkpoint: `D-S046-phase-c`=1 (push + T5.2)  
> Corpus: `[Corpus: tests]` · `[Corpus: product]` · UJ-050 · TC-EV038-007

## Summary

| Check | Status | Notes |
|-------|--------|-------|
| Format / lint / typecheck / secrets | PASS | pre-push `make ci` + prior `validate-fast` |
| `make ci` (ci-prepush + integration) | PASS | local pre-push on tip push |
| UJ-050 Vitest (`iwxxmVersions` + FileConverter labels) | PASS | 8 tests (incl. `(Latest)`/`(Previous)` option text) |
| H0c CORS | PASS | 6 |
| H0i integration (no Docker) | SKIPPED locally | 4 skipped / 6 deselected — Compose green via pre-push `make ci` |
| VA SIGMET + VONA quality (08 residual) | PASS | prior T5.1 |
| Staging H4–H5 | ADVISORY → T5.4 / 13 | FE #854 shipped; live connectivity at deploy |
| pip-audit | SKIPPED | gitleaks + frontend `audit:ci` via hooks |

**Overall: pass_with_advisories** (H4–H5 deferred to T5.4 / 13-deploy-smoke)

## Feature / journey coverage (delta)

| Item | Status |
|------|--------|
| UJ-050 / TC-EV038-007 picker labels | PASS — Vitest SoT + FileConverter option text |
| F4/F7 deepen (#851–#854) | PASS — SoT JSON roles in UI |
| Encode residuals (#849/#856) | PASS — covered at 08 (VA/VONA packs) |
| Docs residuals (#858/#861/#855/#850) | PASS — docs-only; no QA code path |

## Advisories

1. **H4–H5** — live browser connectivity for Latest/Previous picker deferred to **T5.4 / 13-deploy-smoke** (`scripts/deploy/verify_connectivity.sh`; `LIVE_API_URL` + `LIVE_FRONTEND_URL`)
2. Branch push does not trigger `ci-cd.yml` (main/dev/PR only) — local `make ci` is the gate until PR
3. Full-repo remediating QA not run (delta mode)

## Blocking findings

None.

## H4–H5 prep checklist (for T5.4)

- [x] FE version options use SoT JSON roles (`Latest` / `Previous`)
- [x] Vitest asserts option labels
- [x] Playwright UJ-050 assert added (`f6e-product-profile-pickers.e2e.spec.ts`)
- [x] `scripts/deploy/verify_connectivity.sh` present
- [ ] Redeploy API + static (T5.4)
- [ ] Run H1–H3 + H4–H5 against live URLs (T5.4)
