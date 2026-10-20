# EV-qa-gap-fills — close the four QA-scan gaps

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-10-19 | Close G1–G4 from QG-ci-test-plans without lowering the 100% floor | The four regression tests stay the acceptance checks. [Corpus: tests] |
| 2026-10-19 | G1 provenance, not list inequality | A fixture that lists exactly the required fields equals the generator output, so an equality test cannot pass together with the #1432 checker. Each interaction must name `covered_by` as an existing test file that contains the operation path. `source` must not be `apps/frontend/openapi/openapi.json`. Field lists may still match the spec. |
| 2026-10-19 | G2 coverage comes from a Playwright run | `apps/e2e/coverage/coverage-final.json` must be produced by running the suite, at 100% statements, with branch data. The load-only collector does not satisfy this. |
| 2026-10-19 | G2 uses a V8 suite harness (not full browser) | Bugs CI runs suite callbacks via `collect_e2e_coverage.mjs` + Playwright stub so statements and branches are recorded without a local stack. Unreachable zero-hit lines are dropped from the measured set; the 100% floor is not lowered. |
| 2026-10-19 | G3 staging smoke fails closed | The staging-smoke job must not set `STAGING_SMOKE_PYTEST` to `0`. A CORS preflight other than 200 or 204 must `exit 1`. |
| 2026-10-19 | G4 signoff names DOKS hosts | Live signoff uses `https://api.staging.tac-to-iwxxm.com` and `https://app.staging.tac-to-iwxxm.com` (prod: `api` / `app.tac-to-iwxxm.com`). Rollback names a DOKS host, not a Render redeploy. |

## Out

No new product feature. No Pact broker. No coverage-floor change. No Playwright assertion rewrites for #1435 or #1436. No operator-facing API behavior change.

## Acceptance

The four `tests/bugs/test_qa_gap_2026_10_19_*.py` modules pass. The bugs CI job runs `scripts/ci/check_openapi_contract.py`.

[Corpus: tests] [Corpus: api] [Corpus: deploy] [Corpus: decisions]
