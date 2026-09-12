# 08-verify-build — S027 / EV-021 (F26 VAA + F27 TCA / #736/#737)

**Date**: 2026-07-30  
**Scope**: Phase C closeout — M0–M5 + T6.1; T6.2 08-verify-build  
**Branch**: `evolve/EV-021-vaa-quality`  
**Tip (pre T6.2)**: `0580c78` (`[T6.1] test: VAA/TCA workbench smoke + multi-line convert keep-whole`)

## Result: **PASS**

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Format | PASS | 0 | helper test formatted | `make format-check` |
| Lint | PASS | 0 | — | `make lint` (ruff + eslint) |
| Typecheck | PASS | 0 | — | `make typecheck` |
| Secrets | PASS | 0 | — | gitleaks |
| YAML / Actions | PASS | 0 | — | yamllint + actionlint |
| ISSUE_CATALOG | PASS | 0 drift | — | `make catalog-check` |
| Issue registry guard | PASS | — | — | ISSUE_REGISTRY_GUARD_STRICT |
| Tests (unit) | PASS | all green | — | `make test` |
| WMO quality pack | PASS | 279 passed, 9 skipped | — | `make test-wmo-quality` |
| CORS H0c | PASS | 6/6 | — | `tests/unit/test_cors_policy.py` |
| Connectivity artifacts | present | smoke + verify script | — | paths below |
| Integration (Compose) | SKIPPED | Docker not required for this gate | — | `make test-integration` |
| Security (pip-audit) | PASS | 0 known; 1 ignored (`ecdsa`) | — | lockfile export + `uvx pip-audit` |

Overall: **PASS**

## Fixes applied during verify

1. **tac2iwxxm coverage** — pack was **94.2%** (< `fail-under=95`, pre-existing since F26/F27 parsers). Added
   `packages/tac2iwxxm/tests/test_vaa_tca_coverage_helpers.py` (VAA/TCA + glossary + convert helpers)
   → **95.13%**.
2. **tac-validate regressions** — F27 theme `T1` collided with F20 TAF theme `T1` in
   `test_tc_f20_t1_nil_cnl_amd_cor.py` (filter `product==TAF`); TCA smoke sample in
   `test_tc_f12_001_template_gates.py` missing `TC:` after F27 `MISSING_TC` rule.

## Unit test rollup (`make test`)

| Suite | Result |
|-------|--------|
| workspace / shared py | passed (44 + 76) |
| shared js | passed (4) |
| backend | **1200** passed |
| frontend Vitest | **744** passed (84 files) |
| tac2iwxxm | **359** passed, 10 skipped (cov ≥95%) |
| iwxxm-validate | **76** passed, 1 skipped |
| tac-validate | **675** passed |
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
uv export --format requirements-txt --no-emit-workspace --all-groups -o /tmp/project-reqs-ev021.txt
uvx pip-audit -r /tmp/project-reqs-ev021.txt --disable-pip --ignore-vuln PYSEC-2026-1325
```

| Package | Version | IDs | Disposition |
|---------|---------|-----|-------------|
| ecdsa | 0.19.2 | PYSEC-2026-1325 | Ignored — `audit/pip-audit-ignore.txt` |

Result: **No known vulnerabilities found, 1 ignored**.

## Template

- Template `static+api+worker` unchanged (ADR-018).
- F26/F27 deepen stays in packages + FE catalog; no new deployable.

## Milestone status

| Milestone | Status |
|-----------|--------|
| M0–M5 | Done |
| T6.1 | Done |
| T6.2 (08) | **PASS** — handoff T6.3 / 10-e2e |
