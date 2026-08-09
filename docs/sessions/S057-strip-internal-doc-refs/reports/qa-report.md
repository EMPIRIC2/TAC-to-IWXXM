# QA Report — S057 / EV-048 (09-qa)

> Generated: 2026-08-08  
> Scope: delta — deepen F7 (operator UI copy) + F21 (OpenAPI/error surfaces) — #951  
> Branch: `evolve/EV-048-strip-internal-doc-refs` @ `3a43da37`  
> Mode: delta  
> Corpus: [Corpus: product §F7] [Corpus: product §F21] [Corpus: api] [Corpus: tests]

```text
QA Results:
  Lint:           PASS — 0 issues (ruff + eslint)
  Format:         PASS — 0 files (ruff format + prettier)
  Typecheck:      PASS — 0 errors (pre-existing basedpyright warnings only)
  Tests (Python): PASS — TC-EV048 4/4; H0c CORS 6/6; 08 validate-fast green
  Tests (FE):     PASS — internalDocRefGuard + SoftPreviewControl 5/5
  Security:       PASS — uvx pip-audit 0 CVEs; gitleaks pre-commit Passed
  Cross-file:     PASS — lint clean; dangerous-pattern rg only benign RegExp.exec
  Dependencies:   N/A delta — no new runtime deps (06 skipped)
  Template:       PASS — apps/{backend,frontend,worker} + packages layout
  Data / Modal:   N/A — no Modal/data-staging this cycle
  Connectivity:   PASS (H0c); H4–H5 staging waived (12/13 skipped)
  Tip CI:         PENDING push — branch has no upstream yet
```

## Overall: **pass_with_advisories**

### Blocking

| Check | Status | Evidence |
|-------|--------|----------|
| Lint / format / typecheck | PASS | `make validate-fast` |
| H0c CORS | PASS | `tests/unit/test_cors_policy.py` 6/6 |
| TC-EV048 OpenAPI guard | PASS | `test_tc_ev048_*` 4/4 (`--no-cov`) |
| FE string catalog guard | PASS | Vitest 5/5 |
| Secrets (tree) | PASS | `pre-commit run gitleaks --all-files` |
| pip-audit | PASS | 0 known vulnerabilities |

### Advisories (QA-IDs for 11-verify-impl)

| ID | Finding | Severity | Suggested action |
|----|---------|----------|------------------|
| QA-001 | Tip not pushed — no remote CI run for `3a43da37` | advisory | Push branch before PR to `stage`; watch `ci.yml` |
| QA-002 | H4–H5 / 12/13 deploy smoke waived by routing | advisory | Merge gate = tip CI → `stage` (no live deploy required) |
| QA-003 | Privacy inventory still mentions product Fn IDs (`F5`/`F31`) — outside locked guard regex | advisory | Accept for #951; optional follow-on if Fn IDs should be stripped |
| QA-004 | T3.3 Playwright UJ-055 skipped (no FE visible hits) | advisory | Accept T0/T2 unit guards per D-S057-04-t3 / Gate B |

### AC → evidence map

| AC | TC | Status |
|----|-----|--------|
| AC1 audit findings | TC-EV048-001 | met — `reports/audit-internal-doc-refs.md` |
| AC2 OpenAPI clean | TC-EV048-002 | met — pytest OpenAPI walk green |
| AC3 FE catalogs clean | TC-EV048-003 | met — Vitest catalog scan green |
| AC4 client errors | TC-EV048-004 | met — audit T2.3 + no detail leaks |
| AC5 synthetic inject | TC-EV048-005 | met — BE+FE inject tests |
| AC6 soft-preview copy | TC-EV048-002/003 | met — SoftPreviewControl + OpenAPI rewrite |

### Commands run (reproducible)

```bash
make validate-fast
cd apps/backend && uv run pytest tests/unit/test_tc_ev048_openapi_internal_doc_refs.py -q --tb=line --no-cov
uv run pytest tests/unit/test_cors_policy.py -q --tb=line --no-cov
cd apps/frontend && pnpm exec vitest run \
  src/utils/internalDocRefGuard.test.ts \
  src/app/components/SoftPreviewControl.test.tsx
uvx pip-audit
```

### Next

1. **10-e2e** (parallel) — UJ-055 light / T0  
2. **11-verify-impl** — AC + journey sign-off + advisory disposition  
3. Push + PR to `stage` after 11 approval (do not auto-merge)
