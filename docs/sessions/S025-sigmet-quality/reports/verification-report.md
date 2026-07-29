# 08-verify-build — S025 / EV-019 (F23 SIGMET quality / #733+#739)

**Date**: 2026-07-29  
**Scope**: Phase C closeout — M0–M5 through T5.3; T5.4 08-verify-build  
**Branch**: `evolve/EV-019-sigmet-quality`  
**Tip**: `6335842` (`[T5.3] test: API smoke SIGMET/VA lint+convert + catalog GET`)

## Result: **PASS**

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Format | PASS | 0 | — | `make format-check` |
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
| workspace / shared py | passed (44 workspace + 76 shared) |
| shared js | passed |
| backend | **1199** passed |
| frontend Vitest | **734** passed (84 files); coverage S/B/F/L **94.94 / 85.27 / 96.32 / 95.45** |
| tac2iwxxm | **260** passed, 10 skipped |
| iwxxm-validate | **76** passed, 1 skipped |
| tac-validate | **599** passed |
| dissemination | **127** passed, 15 deselected |
| worker | **11** passed |
| bugs (non-live) | **32** passed, 5 skipped, 1 deselected |

## Connectivity (stage 08)

- **Blocking H0c**: `tests/unit/test_cors_policy.py` — **PASS** (6)
- Artifacts present:
  - `tests/smoke/test_staging_connectivity.py`
  - `scripts/deploy/verify_connectivity.sh`

## Security detail

```bash
uv export --format requirements-txt --no-emit-workspace --all-groups -o /tmp/project-reqs-ev019.txt
uvx pip-audit -r /tmp/project-reqs-ev019.txt --disable-pip \
  $(grep -v '^#' audit/pip-audit-ignore.txt | grep -v '^$' | sed 's/^/--ignore-vuln /')
```

| Package | Version | IDs | Disposition |
|---------|---------|-----|-------------|
| ecdsa | 0.19.2 | PYSEC-2026-1325 | Ignored — `audit/pip-audit-ignore.txt` (S013 QA-001) |

Result: **No known vulnerabilities found, 1 ignored**.

## Template

- Template `static+api+worker` unchanged (ADR-018).
- F23 deepen stays in `packages/tac-validate` / `tac2iwxxm` + FE catalog filters; no new deployable.

## Milestone status

| Milestone | Status |
|-----------|--------|
| M0–M4 | Done |
| M5 FE catalog SIGMET/VA + smoke + verify | T5.1–T5.4 done; T5.5–T5.6 (10-e2e, 13-deploy-smoke) remaining |

## Next

1. **T5.5** — 10-e2e (Lean+build; 09 skipped) — UJ-034 / TC-F23-001..006.
2. Then **T5.6** — 13-deploy-smoke (H1–H3 if API; **H4–H5 required** for FE catalog).
3. Evolve PR to `main` after M5 / Phase D (`do_not_auto_merge: true`).
