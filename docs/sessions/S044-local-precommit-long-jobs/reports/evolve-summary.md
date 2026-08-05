# Evolve summary — EV-036 / S044

**Title:** Local long jobs on pre-commit / slim remote CI  
**Branch:** `evolve/EV-036-local-precommit-long-jobs`  
**Status:** **completed** 2026-08-05 (PR open — merge awaits approval)  
**Features:** deepen **M5** only (no new Fn — B4=1)  
**Preset:** Lean · **Deploy:** waived (`D-S044-12-13-waive`)

## What shipped

1. **pre-commit** — fast gates + `validate-ci-medium`  
2. **pre-push** — `make ci` (units + Compose integration on 18000/18001)  
3. **Remote CI** — drop validate + Compose; **keep** unit matrix + coverage + sticky PR coverage comment  
4. **TC-EV036-001..003** — dense contract tests (25 asserts)  
5. Ops docs — `DEVELOPMENT.md` + test-plan tier model

## Gates

| Gate | Result |
|------|--------|
| A (02) | PASS — amended S02.M2 (keep remote units+coverage) |
| C→D (08/09) | PASS |
| 11 | **APPROVED** (`D-S044-11=1`) |
| Deploy 12/13 | **WAIVED** |

## Resource model

| Tier | Where | What |
|------|-------|------|
| Fast + medium | pre-commit | lint/format + `validate-ci-medium` |
| Long local | pre-push | `make ci` |
| Remote | `ci-cd.yml` | units + coverage + PR comment |

## Corpus cites

`[Corpus: product]` M5 · `[Corpus: tests]` · `[Corpus: tech-spec]` ·  
`[Corpus: decisions]` EV-036 · `[docs/ops/DEVELOPMENT.md]`

## Reports

| Artifact | Path |
|----------|------|
| Requirements | `reports/01-requirements-summary.md` |
| Audit | `reports/02-verify-plan-audit.md` |
| Execution plan | `reports/execution-plan.md` |
| 08 | `reports/verification-report.md` |
| 09 | `reports/09-qa.md` |
| 11 | `reports/verify-impl.md` |
