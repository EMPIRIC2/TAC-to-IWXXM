# T4.4 — PyPI publish workflow dry-run / checklist gate

**Date**: 2026-07-19  
**Gate**: pypi-release-checklist (TestPyPI / `act` not configured)

## Result

| Check | Status |
|-------|--------|
| Workflow exists (`.github/workflows/pypi-publish.yml`) | PASS |
| Tag filters for three packages | PASS |
| Package matrix (3 rows) | PASS |
| `id-token: write` on publish | PASS |
| Environment `pypi` | PASS |
| No `secrets.PYPI_API_TOKEN` | PASS |
| `workflow_dispatch.publish` default `false` (dry-run) | PASS |
| Unit tests | `tests/unit/test_tc_f14_001_pypi_publish_workflow.py` — 2 passed |

## Operator dry-run

1. Actions → **PyPI Publish** → Run workflow  
2. Pick a package; leave **publish** = false  
3. Confirm build + smoke succeed; publish job skipped  

## Next

**T4.5** — manylinux + macOS + Windows maturin wheel jobs for native packages.
