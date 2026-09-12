# Pre-commit tooling plan — EV-002

**Stage**: 03-plan-tooling  
**Cycle**: EV-002 / M5

## Current state

- `.pre-commit-config.yaml`: gitleaks + `make ci` (always_run) — runs full suite on every commit
- Cursor `ci-quality-guard.sh`: blocks git commit/push on ruff format + prettier only
- CI: 13 jobs with duplicated setup in `ci-cd.yml`

## Target state

### Hook tiers

| Tier | When | Hooks |
|------|------|-------|
| **Fast** (default `pre-commit`) | Every commit | gitleaks, ruff format/check, prettier, eslint, basedpyright, tsc, actionlint*, yamllint* |
| **Slow** (manual / CI) | `make ci`, CI test job | unit tests, integration, badge-audit |

\* actionlint/yamllint: `files: ^\.github/` filter — skip when no workflow changes.

### `.pre-commit-config.yaml` structure

```yaml
repos:
  - repo: gitleaks  # unchanged
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks: [ruff-format, ruff-check]
  - repo: local
    hooks:
      - id: prettier-check (entry: pnpm run format:check)
      - id: eslint (entry: pnpm run lint:js)
      - id: tsc (entry: pnpm run typecheck:js)
      - id: basedpyright-shared (packages/shared)
      - id: basedpyright-auth (packages/auth)
      - id: basedpyright-backend (apps/backend)
      - id: actionlint (files: ^\.github/, pass_filenames: false)
      - id: yamllint-github (files: ^\.github/, ...)
  - repo: local  # REMOVED from default: make-ci
    hooks:
      - id: make-ci  # stages: [manual] OR document as `pre-commit run make-ci --hook-stage manual`
```

### Makefile addition

```makefile
validate-fast: format-check typecheck lint
# Used by pre-commit local hooks and CI validate job first step
```

### Cursor hook alignment

- `ci-quality-guard.sh`: expand to match validate-fast OR defer to pre-commit install (`pre-commit install`)
- Recommend developers run `pre-commit install` — document in DEVELOPMENT.md

## New dev dependencies (06-tech-tooling)

| Tool | Add to | Purpose |
|------|--------|---------|
| actionlint | pre-commit repo hook (bundled binary via rhysd/actionlint-pre-commit) | Workflow lint |
| yamllint | pre-commit mirror | `.github/` YAML |

No Husky — per user decision R3.

## Guardrails

- No new Cursor rules required; update `dependency-inventory.md` §Workspace Tooling
- `make ci` target unchanged — still full local parity with CI test job
