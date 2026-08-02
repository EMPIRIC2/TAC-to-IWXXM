# 08-verify-build — M1 boundary (EV-029 / S036)

**Date**: 2026-08-02  
**Branch**: `evolve/EV-029-eight-family-ahl-rules`  
**Scope**: Milestone M1 — AHL / COM / shared bulletin model

## Checks

| Check | Result |
|-------|--------|
| `make test-ahl-com-quality` | **PASS** (40 + 9) |
| `ruff check` (bulletin + edis) | **PASS** |
| `basedpyright` (T1.2 files) | **PASS** (0 errors) |
| `packages/tac2iwxxm/tests` | **PASS** (532 passed; prior xfail/xpass unchanged) |
| `make test-unit-dissemination` | **PASS** (≥95% coverage) |
| Pre-commit on T1.1–T1.4 commits | **PASS** |

## Connectivity (H0c / H0i)

M1 is library/CI only (no browser API surface change). H0c/H0i not re-run for this
milestone; remain covered by root `ci.yml` on PR.

## Blocking issues

None.

## Milestone tasks

| Task | Status |
|------|--------|
| T1.1–T1.4 | **completed** |

## Next

Open minor PR for M1; continue **M2** @ T2.1 (METAR deepen).
