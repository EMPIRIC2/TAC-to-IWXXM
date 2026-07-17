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

**Overall: PASS** (advisories QA-001, QA-002 — both **resolved 2026-07-17**, see §QA remediation)

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
| QA-001 | Advisory — **RESOLVED 2026-07-17** | Ambient pip-audit noise was system-env packages; project-scoped audit found one real transitive finding (`ecdsa` PYSEC-2026-1325, no fix upstream) — risk accepted with HS256 justification in `audit/pip-audit-ignore.txt` | Done — see §QA remediation |
| QA-002 | Advisory — **RESOLVED 2026-07-17** | H4–H5 live connectivity run pre-deploy against production URLs: H0c 6/6, H4 2/2, H5 PASS | Done — re-runs post-deploy at 13-deploy-smoke |

## QA remediation — 2026-07-17 (user opted "Address both" at 11-verify-impl)

### QA-001 — resolved (project-scoped audit + documented ignore)

Re-ran pip-audit against the **project lockfile only** (removes system-env noise):

```bash
uv export --format requirements-txt --no-emit-workspace --all-groups > /tmp/project-reqs.txt
uv run pip-audit -r /tmp/project-reqs.txt --disable-pip
```

Result: **1 finding** — `ecdsa 0.19.2` / PYSEC-2026-1325 (CVE-2024-23342, Minerva timing
attack on P-256; CVSS 7.4). Transitive via `python-jose` (packages/auth, apps/backend).
Upstream declares side-channel attacks out of scope — **no fix version exists**.
Risk accepted with justification: all project JWT signing/verification uses **HS256 (HMAC)**
(`packages/auth/src/security.py`), and `python-jose[cryptography]` delegates EC crypto to
pyca/cryptography, so the vulnerable `ecdsa.SigningKey.sign_digest()` path is never called.
Ignore recorded in `audit/pip-audit-ignore.txt`; scoped audit is **clean** with it applied.

### QA-002 — resolved (live H0c/H4/H5 run now, pre-deploy)

`bash scripts/deploy/verify_connectivity.sh` with `LIVE_API_URL=https://metar-to-iwxxm-api.onrender.com`
and `LIVE_FRONTEND_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com` (2026-07-17):

| Gate | Result |
|------|--------|
| H0c CORS policy units | 6/6 PASS |
| H4 live CORS preflight (frontend origin + work-sessions PATCH) | 2/2 PASS |
| H5 frontend runtime config (`config.json` api.baseUrl; no deprecated refs) | PASS |

S013 adds **no new origins or endpoints** (UJ-020/021 reuse decode-tac/lint-tac/convert), so
current-production connectivity is representative. H4–H5 still re-run post-deploy at
13-deploy-smoke per connectivity-gates.

## Consistency (delta scope)

- F9/F10 rows present in `docs/feature-list.md` with spec sections (spec §tac2iwxxm/tac-validate/frontend S013 deltas) and test coverage (TC-F9-001/002, TC-F10-001/002) — verified in 02/05 audits, unchanged since.
- `api-contract.md` §decode-tac documents additive `summary`; §lint-tac documents `fixes[]` + info severity — matches live behavior (see e2e-report live API check).
- Decode contract backward-compatible: `DecodeTacResponse.summary` has default `""`; no removed fields.

## Phase / execution-plan alignment

- M1–M3 complete; T4.1 (08) PASS; this report + `e2e-report.md` complete T4.2.
- Deferred gates: H1–H5 live smokes → T4.5 (13-deploy-smoke); per-Fn acceptance sign-off → T4.3 (11-verify-impl).
