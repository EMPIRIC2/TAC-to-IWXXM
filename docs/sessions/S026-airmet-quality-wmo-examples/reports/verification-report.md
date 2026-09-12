# 08-verify-build — S026 / EV-020 (F24 AIRMET + F25 WMO goldens / #731)

**Date**: 2026-07-29  
**Scope**: Phase C closeout — M0–M5 through T6.1; T6.2 08-verify-build  
**Branch**: `evolve/EV-020-airmet-quality`  
**Tip (pre-fix)**: `7e75fff` (`[T6.1] test: AIRMET + WMO METAR/SPECI/TAF API smoke`)  
**Tip (post T6.2)**: `e839a6e` (`[T6.2] test: align FileConverter goldens with WMO A3-1 catalog`)

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
| WMO quality pack | PASS | 215 passed, 9 skipped | — | `make test-wmo-quality` |
| CORS H0c | PASS | 6/6 | — | `tests/unit/test_cors_policy.py` |
| Connectivity artifacts | present | smoke + verify script | — | paths below |
| Integration (Compose) | SKIPPED | Docker unavailable on host | — | `make test-integration` |
| Security (pip-audit) | PASS | 0 known; 1 ignored (`ecdsa`) | — | lockfile export + `uvx pip-audit` |

Overall: **PASS**

## Fix applied during verify

First `make test` failed 3 Vitest cases in `FileConverter.test.tsx` Golden examples (TC-F7-008 C2–C4): labels still targeted removed `METAR basic (annex3)` after T5.4 WMO-passer catalog gate.

- Updated selectors/assertions to `METAR WMO A3-1 (annex3)` and body `METAR YUDO`.
- Re-ran golden suite + full `make test` — green.

## Unit test rollup (`make test`)

| Suite | Result |
|-------|--------|
| workspace / shared py | passed (44 workspace + 76 shared) |
| shared js | passed (4) |
| backend | **1199** passed |
| frontend Vitest | **738** passed (84 files); coverage S/B/F/L **94.95 / 85.3 / 96.32 / 95.45** |
| tac2iwxxm | **294** passed, 10 skipped |
| iwxxm-validate | **76** passed, 1 skipped |
| tac-validate | **637** passed |
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
uv export --format requirements-txt --no-emit-workspace --all-groups -o /tmp/project-reqs-ev020.txt
uvx pip-audit -r /tmp/project-reqs-ev020.txt --disable-pip --ignore-vuln PYSEC-2026-1325
```

| Package | Version | IDs | Disposition |
|---------|---------|-----|-------------|
| ecdsa | 0.19.2 | PYSEC-2026-1325 | Ignored — `audit/pip-audit-ignore.txt` (S013 QA-001) |

Result: **No known vulnerabilities found, 1 ignored**.

## Template

- Template `static+api+worker` unchanged (ADR-018).
- F24/F25 deepen stays in `packages/tac-validate` / `tac2iwxxm` + FE catalog / glossary; no new deployable.

## Milestone status

| Milestone | Status |
|-----------|--------|
| M0–M5 | Done |
| M6 Smoke / verify / AC / deploy | T6.1–T6.2 done; T6.3–T6.5 (10-e2e, 11-verify-impl, 13-deploy-smoke) remaining |

## Next

1. **T6.3** — 10-e2e — UJ-035 / UJ-036 (+ UJ-020/032 deepen).
2. **T6.4** — 11-verify-impl — per-Fn AC sign-off F24/F25/F9/F7.g.
3. **T6.5** — 13-deploy-smoke — redeploy if API/FE; H1–H3 if API; **H4–H5 required**.
4. Evolve PR to `main` after M6 / Phase D (`do_not_auto_merge: true`).
