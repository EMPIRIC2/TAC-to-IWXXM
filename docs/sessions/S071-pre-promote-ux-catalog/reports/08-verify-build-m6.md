# Verification Report — S071 / EV-061 M6 (#1015)

> Generated: 2026-08-20  
> Scope: 07-build M6 Stricter stage→main promote gate  
> Branch: `evolve/EV-061-pre-promote-ux-catalog`  
> Corpus: [Corpus: product §F34] [Corpus: journeys §UJ-DEV-009] [Corpus: deploy]
> [Corpus: tests §TC-EV061-1015] [Corpus: tech-spec] [Corpus: decisions §EV-061]

## Summary

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Lint | PASS | No product code; workflow/docs only | no | husky lint-fast |
| Format | PASS | format-check | no | `make format-check` |
| Typecheck | N/A | No TS/Python product deltas | — | — |
| Tests (delta) | PASS | TC-EV061-1015-001..002 (9) + EV-045 / EV-036 remote-units | no | pytest `--no-cov` |
| H0c CORS | PASS | 6 passed | no | pytest `--no-cov` |
| H0i | PASS | 10 passed (`apps/backend/tests/integration/test_h0i_connectivity.py`) | no | pytest `--no-cov` |
| Security | N/A | No new deps / secrets | — | — |
| Template | N/A | CI/docs only | — | — |
| Rulesets live apply | DEFERRED | `gh api …/rulesets` length=0; admin required (same pattern as D-S054-ac6-waive) | — | `apply_gh_branch_rulesets.sh` |

## M6 acceptance

- Inventory of promote required-check contexts documented in `docs/deploy.md` §Promote
  (exact job `name:` strings) and mirrored in promote PR template + DOKS admin runbook.
- CI jobs restored/added: **`Lint`**, **`Typecheck`** (all PRs/pushes); **`E2E Full (Playwright)`**
  on `pull_request` → `main` only (distinct from `E2E Smoke (Playwright)`).
- `scripts/deploy/apply_gh_branch_rulesets.sh` lists full `Test (*)`, Lint, Typecheck on
  stage+main; main extras = Staging gate + E2E Full.
- No new app secrets (`D-S071-ci`).
- Live GitHub ruleset apply remains an **admin** step when token has ruleset write
  (repo currently reports zero rulesets).

## Next

08-verify-build M6 PASS (docs/CI half). Push M6 onto [#1016](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1016)
(same evolve branch → `stage`). Update PR title/body for M1–M6. Admin: run
`bash scripts/deploy/apply_gh_branch_rulesets.sh` before the next real promote.
Then Build band continues: 09-qa / 10-e2e / 11+ as routed (or Standard checkpoint).
