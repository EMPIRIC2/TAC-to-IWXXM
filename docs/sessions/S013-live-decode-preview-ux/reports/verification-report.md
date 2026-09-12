# Verification Report — S013 / EV-009 (T4.1, stage 08-verify-build)

> Generated: 2026-07-16
> Scope: M4 T4.1 — full verify after M1–M3 (F9 value-aware decode + summary; F10 preview pane + terminator lint UX)
> Branch: `evolve/S013-live-decode-preview-ux` (tip `efa80c2`, 23 commits ahead of `main`)

## Summary

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Lint (py) | PASS | 0 | 0 | ruff (`make lint-py`) |
| Lint (js) | PASS | 0 (max-warnings 0) | 0 | eslint (`make lint-js`) |
| Format | PASS | 0 (436 py files clean; prettier clean) | 0 | ruff format + prettier |
| Typecheck (py) | PASS | 0 errors across tac2iwxxm, iwxxm-validate, tac-validate, auth, backend | — | basedpyright |
| Typecheck (js) | PASS | 0 (frontend, shared, e2e) | — | tsc --noEmit |
| Tests (full `make test`) | PASS | 0 failures, exit 0 | — | pytest + vitest |
| Connectivity (H0c) | PASS | 29 passed (`tests/unit/test_cors_policy.py` + backend CORS config unit) | — | pytest |
| Security (secrets) | PASS | 0 | — | gitleaks (`make secrets-check`) |
| Security (deps) | PASS (advisory) | 0 project-dep CVEs; see note | — | pip-audit |
| Performance | SKIPPED | no perf thresholds in scope for F9/F10 | — | — |
| Data integrity | SKIPPED | no data deps this cycle | — | — |

**Overall: PASS**

## Test suite detail (canonical `make test` scope)

| Suite | Result |
|-------|--------|
| Backend unit (`apps/backend/tests/unit`) | 1182 passed; coverage 98.01% (gate ≥98%) |
| Frontend Vitest (`@metar/frontend`) | 631 passed / 67 files (includes DecodePanel, IwxxmPreviewPane, WorkbenchConsole.terminator, prettyXml, tacEditorSpans.terminator) |
| tac2iwxxm (`packages/tac2iwxxm/tests`) | 136 passed, 3 skipped (includes test_decode_value_aware, test_decode_summary — TC-F9-001/002) |
| tac-validate (`packages/tac-validate/tests`) | 33 passed (includes test_tc_f10_002_terminator_info — TC-F10-002) |
| Worker (`apps/worker/tests`) | 11 passed |
| Bug regressions (`tests/bugs`) | 39 passed, 1 deselected (live) |

## Connectivity artifacts (connectivity-gates §Stage 08)

- `tests/smoke/test_staging_connectivity.py` — present
- `scripts/deploy/verify_connectivity.sh` — present
- `configure_cors` equivalent: CORSMiddleware wired in `apps/backend/src/api.py` (L282); policy tests green

## Security notes

- gitleaks over all files: **Passed** — no hardcoded secrets.
- `pip-audit` run in the shared dev environment reports CVEs only for packages **not in
  `uv.lock`** (aiohttp, crawl4ai, click, babel, twisted, urllib3, vecinita-*, cloud-init —
  system/site packages from unrelated projects on this host). No project dependency has an
  open advisory. No dependency changes this cycle (execution plan: "no new deps").

## Out-of-scope observation (pre-existing, non-blocking)

Running the **entire** `apps/backend/tests` tree (beyond the canonical `tests/unit` CI scope)
shows 52 failures in environment-dependent suites (integration full-stack auth 401s, docker
schematron container, OpenAIP network, schematron validation suite). These paths are untouched
by S013 (backend delta is limited to additive `DecodeTacResponse.summary` passthrough) and are
excluded from `make test` / `ci-cd.yml`. Recorded for awareness only.

## Auto-corrections

None required — no lint/format findings.
