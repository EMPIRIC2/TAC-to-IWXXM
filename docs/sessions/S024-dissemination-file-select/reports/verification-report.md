# 08-verify-build — S024 / EV-018 (F16 dissemination multi-select / #785)

**Date**: 2026-07-28  
**Scope**: Phase C closeout — M1–M4 complete (14/14); FE multi-select + interleaved queue + progress  
**Branch**: `evolve/EV-018-dissemination-file-select`  
**Base tip**: `a4b75f2` (07 work still **uncommitted**)

## Result: **PASS**

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Format | PASS | 8 then 1 Prettier drift | prettier `--write` | `make format-check` |
| Lint | PASS | 0 | — | `make lint` (ruff + eslint) |
| Typecheck | PASS | 0 | — | `make typecheck` (basedpyright + tsc) |
| Secrets | PASS | 0 | — | `make secrets-check` (gitleaks) |
| YAML / Actions | PASS | 0 | — | yamllint + actionlint |
| ISSUE_CATALOG | PASS | 0 drift | — | `make catalog-check` |
| Issue registry guard | PASS | — | — | ISSUE_REGISTRY_GUARD_STRICT |
| Tests (unit) | PASS | all green | — | `make test` |
| CORS H0c | PASS | 6/6 | — | `tests/unit/test_cors_policy.py` |
| Connectivity artifacts | present | smoke + verify script | — | paths below |
| Integration (Compose) | SKIPPED | Docker unavailable on host | — | `make test-integration` |
| Security (pip-audit) | PASS | 0 known; 1 ignored (`ecdsa`) | — | lockfile export + `uvx pip-audit` |

Overall: **PASS**

## Unit test rollup (`make test`)

| Suite | Result |
|-------|--------|
| workspace / shared py | passed |
| shared js | passed |
| backend | **1199** passed |
| frontend Vitest | **727** passed (83 files); coverage S/B/F/L **94.92 / 85.27 / 96.3 / 95.44** |
| tac2iwxxm | passed (skips as before) |
| iwxxm-validate | passed |
| tac-validate | passed |
| dissemination | **127** passed, 15 deselected |
| worker | **11** passed |
| bugs (non-live) | **32** passed, 5 skipped, 1 deselected |

## Auto-corrections during 08

1. **Prettier** on EV-018 FE/e2e files (format-check gate).
2. **Coverage** — first `make test` failed FE thresholds (functions 95.98% / branches 84.73%). Fixed by:
   - Extra `disseminationQueue` edge-failure tests (throw / `ok:false` / non-Error stringify).
   - Removed unreachable missing-handle branch (already gated by `isPreflightGreen`).
   - Drawer tests: sole-candidate expand + per-row checkbox toggle.
3. Re-ran full `make format-check && make lint && make typecheck && make test` → **PASS**.

## Connectivity (stage 08)

- **Blocking H0c**: `tests/unit/test_cors_policy.py` — **PASS** (6)
- Artifacts present:
  - `tests/smoke/test_staging_connectivity.py`
  - `scripts/deploy/verify_connectivity.sh`

## Security detail

```bash
uv export --format requirements-txt --no-emit-workspace --all-groups -o /tmp/project-reqs-ev018.txt
uvx pip-audit -r /tmp/project-reqs-ev018.txt --disable-pip \
  $(grep -v '^#' audit/pip-audit-ignore.txt | grep -v '^$' | sed 's/^/--ignore-vuln /')
```

| Package | Version | IDs | Disposition |
|---------|---------|-----|-------------|
| ecdsa | 0.19.2 | PYSEC-2026-1325 | Ignored — `audit/pip-audit-ignore.txt` (S013 QA-001) |

Result: **No known vulnerabilities found, 1 ignored**.

## Template

- Template `static+api+worker` unchanged (ADR-018).
- F16–F19 drawer remains FE + backend-mediated egress; no new deployable.

## Next

1. **Commit** EV-018 working tree when user requests (still uncommitted).
2. **10-e2e** (Lean+build) — UJ-027–030; screenshot baseline generated on first run.
3. Then **13-deploy-smoke** (H6′).
