# Typing Policy

> **Project**: METAR to IWXXM Converter  
> **Last updated**: 2026-08-27 (EV-strict-lint-typecheck)  
> **Source**: execution plan §Tech Stack, ADR-005, ADR-007

## Python

| Setting | Value |
|---------|-------|
| Runtime | Python **3.12** (pinned) |
| Typechecker | **basedpyright** (`strict` on `apps/backend`, `packages/*`) |
| Linter / formatter | **Ruff** (all Python packages including `packages/gifts`) |

### Ruff rule sets (monorepo root `ruff.toml`)

| Code | Purpose |
|------|---------|
| E, F, I | pycodestyle errors, pyflakes, isort |
| UP, B, SIM, RUF | pyupgrade, bugbear, simplify, ruff-specific |
| PERF, ASYNC | perflint, async blocking-I/O guard |
| PT | pytest-style (raises match, assert layout) |
| ANN | annotations on `apps/` + `packages/` **src** (`**/tests/**` ignores ANN) |

Per-package `pyproject.toml` files **extend** root `ruff.toml` (line-length 120 where noted) — do not reintroduce thin `E,W,F,I`-only overrides.

**ANN401 waivers:** lxml / PyO3 boundary modules in `packages/iwxxm-validate` (`c14n`, `native`, `schematron`, `xsd`) — third-party handles without complete stubs.

### basedpyright

| Setting | Value |
|---------|-------|
| `typeCheckingMode` | `strict` (root + `apps/backend`) |
| `reportUnknownMemberType` | **error** |
| `reportUnknownVariableType` | **error** |
| `reportMissingTypeStubs` | `false` |

Use typed JSON/XML boundaries (`cast`, `TypedDict`, `XmlElement` protocol in `apps/backend/src/utilities/xml_types.py`) instead of broad `# pyright: ignore`.

### Conventions

- Public functions and methods require explicit parameter and return types.
- Prefer `TypedDict`, `Protocol`, and concrete collections over untyped `dict`.
- Use `object` instead of `Any` when the shape is genuinely unknown; justify `Any` in code review.
- Third-party stubs: `reportMissingTypeStubs = false` in `pyproject.toml` / `pyrightconfig.json`.

### Commands

```bash
# From repo root (after uv sync)
make typecheck-py   # basedpyright per package + backend
make lint-py        # ruff check (PY_LINT scope)
uv run ruff format --check apps packages tests
```

Strict enforcement applies to new code under `apps/` and `packages/`. Legacy paths (`backend/`, `GIFTs/`, `auth/`) are included during migration and tightened as packages move (Phase 1–3).

**packages/gifts exception:** upstream GIFTs is linted and formatted with Ruff but excluded from
basedpyright enforcement (`packages/gifts/pyrightconfig.json`, `typeCheckingMode: off`) until
upstream typing remediation is merged.

## TypeScript

| Setting | Value |
|---------|-------|
| Runtime | Node **22** (pinned) |
| Frontend | React 18 + Vite 6 + TypeScript 5 |
| Linter | ESLint 9 + typescript-eslint (frontend, e2e, shared) |
| Formatter | Prettier 3 (all TypeScript workspaces) |

### Compiler strictness

All TS workspaces enable:

- `"strict": true`
- `"noUncheckedIndexedAccess": true` — array/tuple/index reads may be `undefined`; guard before use

### ESLint

Key rules at **error** (root `eslint.config.js` + `apps/frontend/eslint.config.js`):

- `@typescript-eslint/no-explicit-any`
- `@typescript-eslint/no-unused-vars`
- `@typescript-eslint/no-empty-object-type`
- `@typescript-eslint/no-require-imports`

`pnpm run lint:js` uses `--max-warnings 0`.

### Commands

```bash
pnpm run format:check   # from repo root
pnpm run lint:js
pnpm run typecheck:js
cd apps/frontend && pnpm exec eslint src
cd apps/frontend && pnpm exec tsc --noEmit
```

## Coverage gate (ADR-007 / EV-047)

**95%** line/branch coverage on all workspace members — pytest for Python, Vitest for frontend.
Configured in root `pyproject.toml` `[tool.coverage.report]` and per-package overrides
(Phase 1 T1.9). **EV-047 / D-S056-cov95-scope=2:** every measured Python source file must
also be ≥95% (`scripts/ci/check_per_file_coverage.py` after package unit jobs); auth and
worker use hard `fail_under = 95` (no longer soft-report-only).

## References

- `docs/dependency-inventory.md` — toolchain versions
- `.cursor/rules/optional/strict-typing.mdc` — agent guardrail
- `docs/adr/ADR-005-runtime-toolchain-pins.md` (if present) — version pins
