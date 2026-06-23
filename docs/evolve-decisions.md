# Evolve Decisions

> Standing log of approved evolve-cycle scope and product decisions.
> Cycle metadata also recorded in `workflow-state.yaml` §`evolve_cycles`.

## Cycle EV-001 — Convert & Convert&Send UI (S001)

**GitHub**: [#656](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/656)  
**Session**: S001-convert-send-buttons  
**Feature**: F1 (conversion UI + database send)  
**Approved**: 2026-06-22

### Scope

**In scope**

- **Convert** button — conversion only (already present; verify UX).
- **Convert&Send** button — convert then immediately upload with fixed defaults.
- Success/failure toast feedback for the send step.

**Out of scope**

- Auto-clear input panel (#555 sibling).
- In-app error log preview (#555 sibling).
- Backend API changes.

### Decisions

| ID | Category | Decision |
|----|----------|----------|
| R1 | Ambiguity | Convert&Send uses fixed defaults: `format: iwxxm`, `destination: primary`, `includeOriginal: false`; no upload dialog |
| R2 | Decision | Keep all three actions: Convert, Convert&Send, Upload to Database |
| R3 | Scope | #656 only — exclude #555 auto-clear and log preview |

### Artifacts updated

- `docs/feature-list.md` — F1 UI actions
- `docs/user-journeys.md` — UJ-001 steps
- `docs/test-plan.md` — E2E module for convert-and-send
- `apps/frontend/` — `FileConverter`, shared `databaseUpload` util
- `apps/e2e/tac-file-upload-database.e2e.spec.ts` — one-click path

## Cycle EV-002 — CI consolidation (M5)

**Session**: S002-ci-consolidation (pending open)  
**Feature**: M5 (Workspace tooling)  
**Approved**: 2026-06-22  
**Cycle type**: general

### Scope

**In scope**

- Consolidate PR/push CI from 13+ jobs across multiple workflows to **≤3 jobs** in a single `ci-cd.yml`:
  1. **validate** — format, lint, typecheck, gitleaks, actionlint/yamllint, config-guard, frontend npm audit
  2. **test** — unit tests + coverage (matrix: backend, auth, gifts, frontend, shared), integration matrix, Codecov uploads (thresholds unchanged)
  3. **deploy** — build/push images + Render deploy hooks (main push only, unchanged behavior)
- Extend **pre-commit** with fast hooks mirroring validate checks (dual-run: local + CI).
- **Delete** standalone PR/push workflows after merge: `secret-scan.yml`, `github-yaml-lint.yml`; fold `frontend-audit.yml` into validate job.
- Fix monorepo paths in any remaining references (legacy `backend/`, `frontend/`).

**Out of scope**

- Scheduled workflows: `e2e-tests.yml`, `load-tests.yml`, `vendor-sync.yml`
- Legacy manual workflow `test-coverage-95.yml` (delete if still present; no behavior change)
- Broken `smoke-tests-deploy.yml` (fix trigger reference or delete — not in PR/push path)
- Path-filtered CI (P2) — deferred to future cycle
- Coverage threshold changes (98% pytest `--cov-fail-under`, Codecov 95% per-service)
- Product feature changes (F1–F4)

### Decisions

| ID | Category | Decision |
|----|----------|----------|
| R1 | Intent | Reduce CI cost/complexity without lowering quality bar |
| R2 | Jobs | Target ≤3 jobs on PR: validate → test → (deploy on main only) |
| R3 | Local hooks | Extend pre-commit only (no Husky); fast hooks = format/lint/typecheck/secrets/yaml |
| R4 | Dual-run | Pre-commit runs fast checks locally; CI still runs all checks on every PR |
| R5 | Test structure | Single test job with matrix strategy for per-package unit+coverage |
| R6 | Workflows | Single `ci-cd.yml` for PR/push; delete secret-scan + yaml-lint; merge frontend-audit |
| R7 | Coverage | Keep per-service pytest 98% gates and Codecov 95% uploads exactly as today |
| R8 | Security | **Accepted trade-off:** deleted `secret-scan.yml` scanned full git history (`fetch-depth: 0`); validate/pre-commit gitleaks scans the working tree only. Historical commits are not re-scanned on PR/push. Rationale: pre-commit gitleaks on every commit + CI validate dual-run catches new leaks; full-history scan cost duplicated validate job checkout depth. Revisit if org policy requires history scans. |

### Acceptance criteria

- [ ] PR to main/dev runs ≤3 jobs (validate, test; deploy skipped on PR)
- [ ] All checks that ran before EV-002 still execute in CI (no dropped gates)
- [ ] Pre-commit fast hooks match quality-gates + secrets + yaml lint
- [ ] `make ci` behavior unchanged (still the local full-suite entry point)
- [ ] CI green on evolve branch before merge

### Artifacts to update

- `docs/feature-list.md` — M5 CI/pre-commit detail
- `docs/test-plan.md` — CI/CD section
- `.pre-commit-config.yaml` — fast hook split
- `.github/workflows/ci-cd.yml` — consolidated jobs
- Delete: `.github/workflows/secret-scan.yml`, `.github/workflows/github-yaml-lint.yml`, `.github/workflows/frontend-audit.yml`
