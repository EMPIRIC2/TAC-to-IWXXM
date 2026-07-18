# 06-tech-tooling report — S014 / EV-010

**Date**: 2026-07-18  
**Mode**: delta (Rust / maturin / xsdata / PyPI)  
**User plan**: **49A** — full delta set

## Installed / updated

| Artifact | Change |
|----------|--------|
| `.cursor/rules/optional/rust-maturin-xsdata.mdc` | **new** — maturin packages, Makefile targets, xsdata/ADR-027 |
| `.cursor/rules/core/pypi-package-publish.mdc` | matrix workflow (E10-37) |
| `.cursor/skills/pypi-release-checklist/SKILL.md` | matrix checklist |
| `.cursor/hooks/pypi_release_guard.py` | advisory on `Cargo.toml` / `rust/**` / codegen paths |
| `Makefile` | `build-iwxxm-validate-native`, `bench-validation-stack`, `codegen-iwxxm-xsd` (fail-clear until T1/T3) |
| `pyproject.toml` + `uv.lock` | `maturin>=1.7`, `xsdata[cli]>=24.5`, `xsdata-pydantic>=24.5` in `dev` |
| `docs/dependency-inventory.md` | versions pinned to workspace `dev` |

## Connectivity (06 verification)

| Check | Result |
|-------|--------|
| `tests/unit/test_cors_policy.py` | present |
| `scripts/deploy/verify_connectivity.sh` | executable |
| H4–H5 in plan T5.6 / T6.5 | present (05) |
| Full publish CI job for iwxxm-validate | deferred to T3/T4 build (not invented in 06) |

## Smoke

| Check | Result |
|-------|--------|
| Hook on `iwxxm-validate/rust/Cargo.toml` | advisory context returned |
| `make build-iwxxm-validate-native` | exits 1 with T3.1 message (expected) |
| `make bench-validation-stack` | exits 1 with T1.1 message (expected) |
| `make codegen-iwxxm-xsd` | exits 1 with T3.6 message (expected) |
| `uv lock` | maturin 1.14.1, xsdata 26.2, xsdata-pydantic 24.5 |

## Phase B gate

- [x] Execution plan approved
- [x] 05-verify-tech PASS
- [x] 06-tech-tooling installed
- → Ready for Phase C: **07-build** (M1 T1.1)
