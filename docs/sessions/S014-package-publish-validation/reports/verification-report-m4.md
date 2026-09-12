# Verification report — M4 (S014 / EV-010)

**Date**: 2026-07-19  
**Branch**: `evolve/EV-010-package-publish-validation`  
**Scope**: F14 — `tac2iwxxm[validate]` + PyPI OIDC matrix

## Tasks

| Task | SHA | Result |
|------|-----|--------|
| T4.1 | `c48c692` | Clean-venv convert + `[validate]` extra smoke (TC-F14-002) |
| T4.2 | `24ad415` | `tac2iwxxm[validate]` → tac-validate + iwxxm-validate; README |
| T4.3 | `ab0c507` | `.github/workflows/pypi-publish.yml` — matrix + OIDC |
| T4.4 | `4970271` | Structural checklist gate (2 tests) |
| T4.5 | `a5a0fef` | manylinux / macOS / Windows maturin jobs |

## Checks

- `make format-check` — PASS (at T4.5 commit)
- `pytest packages/tac2iwxxm/tests/test_tc_f14_002_validate_extra.py` — PASS (slow)
- `pytest tests/unit/test_tc_f14_001_pypi_publish_workflow.py` — PASS

## Operator follow-up (outside code)

Configure PyPI Trusted Publisher for each project → workflow `pypi-publish.yml`, environment `pypi`.

## Next

**M5** — msgspec high-churn HTTP + FE types (T5.1). Single evolve PR still deferred to M6.
