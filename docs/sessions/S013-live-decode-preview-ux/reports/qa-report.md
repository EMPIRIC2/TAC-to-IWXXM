# QA Report — S013 / EV-009 (stage 09-qa, T4.2)

> Generated: 2026-07-17
> Scope: delta QA for F9 (value-aware decode + summary) + F10 (preview pane + terminator lint UX); full-suite checks re-run fresh (not reused from T4.1)
> Branch: `evolve/S013-live-decode-preview-ux` (base `7ad28f9`)

## Summary

```text
QA Results:
  Lint:           PASS — 0 issues (ruff apps/packages/tests; eslint --max-warnings 0)
  Format:         PASS — 0 files (ruff format --check 436 files; prettier clean)
  Typecheck:      PASS — 0 errors (basedpyright x5 packages/apps; tsc frontend/shared/e2e)
  Tests (Python): PASS — backend unit 1182; auth 228 (+31 skipped); tac2iwxxm 136 (+3 skipped);
                  iwxxm-validate 49; tac-validate 33; worker 11; bugs 39 — 0 failed
  Tests (FE):     PASS — @metar/frontend Vitest 631 passed / 67 files
  Security:       PASS — 0 secrets (gitleaks all-files); 0 dangerous patterns
                  (pickle.loads/eval/exec in apps+packages); 0 project-dep CVEs (see QA-001)
  Cross-file:     0 unused imports (ruff F401/F841 in lint scope); no new modules outside tree
  Dependencies:   0 new packages this cycle (execution plan: "no new deps") — inventory unchanged
  Template:       PASS — changes confined to apps/backend, apps/frontend, apps/e2e,
                  packages/tac2iwxxm, packages/tac-validate (template static+api+worker)
  Connectivity:   H0c PASS — test_cors_policy.py + backend CORS config unit green (in suite);
                  H4–H5 deferred to 13-deploy-smoke (no staging env vars set) — QA-002
```

**Overall: PASS** (advisories QA-001, QA-002 — non-blocking)

## Commands run

```bash
make lint            # ruff check + eslint            → exit 0
make format-check    # ruff format --check + prettier → exit 0
make typecheck       # basedpyright + tsc             → exit 0
make test            # all unit suites + bugs         → exit 0
make secrets-check   # gitleaks --all-files           → exit 0 (Passed)
uv run pip-audit                                      # see QA-001
rg "pickle\.loads|[^a-zA-Z_]eval\(|[^a-zA-Z_]exec\(" apps packages --type py  # no matches
```

## Findings for 11-verify-impl

| ID | Severity | Finding | Suggested action |
|----|----------|---------|------------------|
| QA-001 | Advisory | `pip-audit` reports CVEs only for **system-environment** packages not in `uv.lock` (aiohttp, crawl4ai, click, urllib3, vecinita-*, cloud-init — unrelated projects sharing this host venv). No project dependency has an open advisory; no dependency changes this cycle. | No action; re-check in CI environment if desired |
| QA-002 | Advisory | H4–H5 live browser connectivity not run at this stage (no staging URLs configured for 09) | Runs in 13-deploy-smoke per connectivity-gates §Pipeline |

## Consistency (delta scope)

- F9/F10 rows present in `docs/feature-list.md` with spec sections (spec §tac2iwxxm/tac-validate/frontend S013 deltas) and test coverage (TC-F9-001/002, TC-F10-001/002) — verified in 02/05 audits, unchanged since.
- `api-contract.md` §decode-tac documents additive `summary`; §lint-tac documents `fixes[]` + info severity — matches live behavior (see e2e-report live API check).
- Decode contract backward-compatible: `DecodeTacResponse.summary` has default `""`; no removed fields.

## Phase / execution-plan alignment

- M1–M3 complete; T4.1 (08) PASS; this report + `e2e-report.md` complete T4.2.
- Deferred gates: H1–H5 live smokes → T4.5 (13-deploy-smoke); per-Fn acceptance sign-off → T4.3 (11-verify-impl).
