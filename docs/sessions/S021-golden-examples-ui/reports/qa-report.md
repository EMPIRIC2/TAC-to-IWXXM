# QA Report — S021 / EV-016 (F7.g / #780)

> Generated: 2026-07-26  
> Scope: F7.g golden examples UI (FE-only delta)  
> Branch: `evolve/EV-016-golden-examples-ui` @ `3d1c58b`  
> Mode: evolve delta (09-qa) · parallel with 10-e2e

```text
QA Results:
  Lint:           PASS — 0 issues (ruff + eslint)
  Format:         PASS — 0 files (ruff + prettier)
  Typecheck:      PASS — 0 errors (basedpyright + tsc)
  Tests (Python): PASS — H0c CORS 6 passed (delta; full py suite not re-run — FE-only)
  Tests (FE):     PASS — 688 passed / 75 files (@metar/frontend)
  Security:       PASS — gitleaks --no-git 0 leaks; check_secrets.sh absent (advisory)
  Cross-file:     PASS — no pickle.loads/eval/exec app misuse (WorkbenchConsole RegExp.exec OK)
  Dependencies:   ADVISORY — pip-audit skipped (S020 posture; no new deps this cycle)
  Template:       PASS — static+api+worker; FE fixtures under apps/frontend only
  Data / Modal:   N/A — no Modal/data assets for F7.g; docs/data-staging-state.md absent
```

## Summary

| Check | Status | Notes |
|-------|--------|-------|
| Format | PASS | `make format-check` — 535 py formatted; prettier clean |
| Lint | PASS | `make lint` — ruff All checks passed; eslint max-warnings 0 |
| Typecheck | PASS | `make typecheck` — basedpyright 0; `tsc --noEmit` FE/shared/e2e |
| Tests (FE) | PASS | `pnpm --filter @metar/frontend test` — **688** passed (75 files) |
| H0c CORS | PASS | `uv run pytest tests/unit/test_cors_policy.py` — **6** passed |
| Secrets (tree) | PASS | `gitleaks detect --no-git` — no leaks (~1.31 GB scanned) |
| Secrets script | ADVISORY | `scripts/check_secrets.sh` not present |
| OpenAPI script | ADVISORY | `scripts/check_openapi_specs.sh` not present (FE-only cycle) |
| Staging H4–H5 | ADVISORY | Deferred to 13-deploy-smoke (routing / E16-9) |
| pip-audit | ADVISORY | Not treated as F7.g gate (no new PyPI deps) |

**Overall: pass_with_advisories**

## Blocking

None.

## Advisories (for 11-verify-impl)

| ID | Severity | Finding | Suggested action |
|----|----------|---------|------------------|
| QA-001 | advisory | H4–H5 browser connectivity not exercised in 09 | Required at **13-deploy-smoke** when FE static site ships (`make test-live-connectivity`) |
| QA-002 | advisory | `scripts/check_secrets.sh` / `check_openapi_specs.sh` absent | Rely on gitleaks + CI validate job; optional restore scripts later |
| QA-003 | advisory | Host-wide `pip-audit` not run | Same posture as S015/S020; no new workspace deps in F7.g |
| QA-004 | advisory | Full Python unit matrix not re-run in delta 09 | FE-only change; H0c green; prior 08-verify-build covered M1–M3 |

## Connectivity (stage 09)

| Tier | Result |
|------|--------|
| H0c | PASS (`tests/unit/test_cors_policy.py`) |
| H0i | N/A for F7.g (no API surface) — not blocking |
| H4–H5 | pending → 13-deploy-smoke |

## Commands run

```bash
make format-check
make lint
make typecheck
pnpm --filter @metar/frontend test
uv run pytest tests/unit/test_cors_policy.py -q --no-cov
gitleaks detect --no-git --config .gitleaks.toml
```

## Phase / plan alignment

- Execution plan M1–M3 complete (11/11); 08-verify-build PASS at `90a8507` (session tip `3d1c58b`).
- F7.g: no backend / env / DB — template conformance OK.
- Gate **c_to_d** remains pending until 09+10+11.
