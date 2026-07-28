# 08-verify-build — S023 / EV-017 (F21 public app + F22 privacy / #783)

**Date**: 2026-07-28  
**Scope**: Phase C closeout — M1–M7 complete (28/28); post-merge #786/#787/#788  
**Branch**: `evolve/EV-017-public-app-privacy`  
**Tip**: `73f8389`  
**Note**: Security WIP stashed (`stash@{0}`) for this run

## Result: **PASS**

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Format | PASS | 0 | — | `make format-check` (ruff + prettier) |
| Lint | PASS | 0 | — | `make lint` (ruff + eslint) |
| Typecheck | PASS | 0 | — | `make typecheck` (basedpyright + tsc) |
| Secrets | PASS | 0 | — | gitleaks |
| YAML / Actions | PASS | 0 | — | yamllint + actionlint |
| ISSUE_CATALOG | PASS | 0 drift | — | catalog-check |
| Issue registry guard | PASS | — | — | ISSUE_REGISTRY_GUARD_STRICT |
| Tests (unit) | PASS | all green | — | `make test` |
| CORS H0c | PASS | 6/6 | — | `tests/unit/test_cors_policy.py` |
| Connectivity artifacts | present | smoke + verify script | — | paths below |
| Integration (Compose) | SKIPPED | Docker unavailable on host | — | `make test-integration` |
| Security (pip-audit) | PASS | 0 known; 1 ignored (`ecdsa`) | `pyasn1` → 0.6.4 | lockfile export |

Overall: **PASS**

## Unit test rollup (`make test`)

| Suite | Result |
|-------|--------|
| workspace / shared py | 44 + 76 passed |
| shared js | 4 passed |
| backend | **1199** passed |
| frontend Vitest | **698** passed (80 files) |
| tac2iwxxm | 231 passed, 10 skipped |
| iwxxm-validate | 76 passed, 1 skipped |
| tac-validate | 471 passed |
| dissemination | 127 passed, 15 deselected |
| worker | 11 passed |
| bugs (non-live) | 32 passed, 5 skipped, 1 deselected |

## Connectivity (stage 08)

- **Blocking H0c**: `tests/unit/test_cors_policy.py` — **PASS** (6)
- Artifacts present:
  - `tests/smoke/test_staging_connectivity.py`
  - `scripts/deploy/verify_connectivity.sh`
- Live H4–H5 already recorded under M7: `reports/t7.2-h4-h5-connectivity.md`

## Template / F21 structural

- `packages/auth`: **ABSENT** (expected after T5.4)
- Template `static+api+worker` unchanged (ADR-018 / ADR-031)

## Security detail

Project-scoped:

```bash
uv export --format requirements-txt --no-emit-workspace --all-groups -o /tmp/project-reqs.txt
uvx pip-audit -r /tmp/project-reqs.txt --disable-pip \
  $(grep -v '^#' audit/pip-audit-ignore.txt | grep -v '^$' | sed 's/^/--ignore-vuln /')
```

| Package | Version | IDs | Disposition |
|---------|---------|-----|-------------|
| ecdsa | 0.19.2 | PYSEC-2026-1325 | Ignored — `audit/pip-audit-ignore.txt` (S013 QA-001) |
| pyasn1 | **0.6.4** | — | **Upgraded** (D-S023-08-pyasn1-A) from 0.6.3; `uv.lock` + `apps/backend/uv.lock` |

Re-audit after bump: **No known vulnerabilities found, 1 ignored**.

## Auto-corrections

- Lockfile bump: `pyasn1` 0.6.3 → 0.6.4 (root + `apps/backend/uv.lock`).

## Next

Phase C checkpoint → Phase D (`09-qa` + `10-e2e` in parallel) → `11-verify-impl` → `12` → `13`.
