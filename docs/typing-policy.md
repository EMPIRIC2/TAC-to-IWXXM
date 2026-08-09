# Typing Policy

> **Project**: METAR to IWXXM Converter  
> **Last updated**: 2026-06-14  
> **Source**: execution plan §Tech Stack, ADR-005, ADR-007

## Python

| Setting | Value |
|---------|-------|
| Runtime | Python **3.12** (pinned) |
| Typechecker | **basedpyright** (`strict` on `apps/backend`, `packages/*`) |
| Linter / formatter | **Ruff** (all Python packages including `packages/gifts`) |

### Conventions

- Public functions and methods require explicit parameter and return types.
- Prefer `TypedDict`, `Protocol`, and concrete collections over untyped `dict`.
- Use `object` instead of `Any` when the shape is genuinely unknown; justify `Any` in code review.
- Third-party stubs: `reportMissingTypeStubs = false` in `pyproject.toml` / `pyrightconfig.json`.

### Commands

```bash
# From repo root (after uv sync)
uv run basedpyright
uv run ruff check .
uv run ruff format --check .
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
