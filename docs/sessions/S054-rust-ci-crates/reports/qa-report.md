# QA Report — S054 / EV-045 (09-qa)

> Generated: 2026-08-08  
> Scope: delta — deepen F13 + F14 Rust CI (#725)  
> Branch: `evolve/EV-045-rust-ci` @ `09ce2bef`  
> Mode: delta  
> Corpus: [Corpus: product §F13] [Corpus: product §F14] [Corpus: tests]
> [Corpus: tech-spec] [Corpus: adr/ADR-017] [Corpus: decisions]

```text
QA Results:
  Lint:           PASS — 0 issues (ruff + eslint)
  Format:         PASS — 0 files (ruff format + prettier)
  Typecheck:      PASS — 0 errors (17 pre-existing basedpyright warnings in tac2iwxxm iwxxm_us)
  Tests (Python): PASS — TC-EV045 8/8; H0c 6/6; H0i non-live 4 skipped (env); tip CI full matrix green
  Tests (FE):     PASS — Vitest 798 passed / 4 skipped (89 files)
  Security:       PASS — uvx pip-audit 0 CVEs; no pickle.loads; rg eval/exec only benign RegExp.exec
  Cross-file:     PASS — F401/F841 clean on scoped trees
  Dependencies:   N/A delta — no new runtime deps (06 skipped ADR-017)
  Template:       PASS — apps/{backend,frontend,worker} + packages layout
  Data / Modal:   N/A — CI-only; no Modal/data-staging this cycle
  Connectivity:   PASS (H0c); H4–H5 N/A (no UI); H0i live deferred (CI-only + tip CI)
  Tip CI:         PASS — run 31273500621 @ f270618c (D-S054-t17-ci=1)
```

## Overall: **pass_with_advisories**

### Blocking

| Check | Status | Evidence |
|-------|--------|----------|
| Lint / format | PASS | `make lint` / `make format-check` |
| Typecheck | PASS | `make typecheck` — 0 errors |
| TC-EV045 contracts | PASS | `tests/test_tc_ev045_rust_ci.py` 8/8 |
| H0c CORS | PASS | `tests/unit/test_cors_policy.py` 6/6 |
| `make rust-check` | PASS | both crates cargo + both maturin smokes |
| Frontend Vitest | PASS | 798 passed, 4 skipped |
| Security (pip-audit) | PASS | 0 known vulns |
| Tip CI (Rust/maturin/tests) | PASS | [31273500621](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31273500621) |

### Advisories (QA-IDs for 11-verify-impl)

| ID | Finding | Severity | Suggested action |
|----|---------|----------|------------------|
| QA-001 | AC6 **ops** half deferred — GH rulesets/required checks not applied live (`D-S054-ac6-waive=2`) | advisory | Admin run `scripts/deploy/apply_gh_branch_rulesets.sh` when token has admin; docs+script already list locked contexts |
| QA-002 | Local `tests/integration -m "not live"` selected 4 tests all **skipped** (DB/env); tip CI covered full matrix | advisory | Accept for CI-only cycle; no H0i blocker on tip evidence |
| QA-003 | `scripts/check_secrets.sh` / gitleaks not installed in this environment | advisory | Rely on CI secret scan + pip-audit; optional install for local parity |
| QA-004 | H4–H5 / deploy smoke skipped by routing (no UI / CI-only) | advisory | N/A this cycle — confirm at 11 |
| QA-005 | Pre-existing basedpyright warnings in `tac2iwxxm/profiles/iwxxm_us.py` (17) | advisory | Out of EV-045 scope; do not block |

### AC → locked CI job / local target map

| AC / TC | Mechanism | Locked name / target | Status |
|---------|-----------|----------------------|--------|
| F13/F14 AC1 + TC-EV045-001 | `rust-crates` matrix → gate | **`Rust crates (fmt/clippy/test)`** | met (CI + contracts) |
| F13/F14 AC2 + TC-EV045-002 | same gate (`clippy -D warnings`) | **`Rust crates (fmt/clippy/test)`** | met |
| F13/F14 AC3 + TC-EV045-003 | same gate (`cargo test`) | **`Rust crates (fmt/clippy/test)`** | met |
| F13 AC4 + TC-EV045-004 | native matrix | **`iwxxm-validate PyO3 (maturin)`** | met |
| F14 AC4 + TC-EV045-004 | native matrix | **`tac2iwxxm PyO3 (maturin)`** | met |
| F14 AC5 + TC-EV045-005 | Makefile | **`make rust-check`** | met (local + contracts) |
| AC6 / TC-EV045-006 docs | test-plan + ruleset script | contexts listed above | **docs met**; ops waived QA-001 |
| TC-EV045-007 | default `ci-cd.yml` triggers | no `paths:` filter on workflow | met |
| Deploy gate | `deploy.needs` | `rust-crates-gate`, `tac2iwxxm-native` (matrix) | met (contracts + workflow) |

### Commands run (reproducible)

```bash
make format-check
make lint
make typecheck
uv run pytest tests/test_tc_ev045_rust_ci.py tests/unit/test_cors_policy.py -q --tb=line
uv run pytest tests/integration -q --tb=line -m "not live"
make rust-check
pnpm --filter @metar/frontend exec vitest run
uvx pip-audit
uv run ruff check --select F401,F841 --force-exclude \
  apps/backend/src packages/auth/src packages/shared \
  packages/tac2iwxxm/src packages/iwxxm-validate/src \
  packages/tac-validate/src packages/dissemination/src tests
```

### Phase / plan alignment

- M1 T1.1–T1.7 **completed**; Phase C approved (`D-S054-phaseC=1`)
- Tip CI accepted (`D-S054-t17-ci=1`); PR [#953](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/953) → `stage`
- 10-e2e / 12 / 13 **skipped** per routing

### Next

1. **11-verify-impl** — AC checklist + advisory disposition (QA-001..005)  
2. Merge still requires user approval on #953 (do not auto-merge)
