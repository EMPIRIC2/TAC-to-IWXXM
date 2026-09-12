# T4.3 — PyPI OIDC matrix workflow (TC-F14-001 / E10-37)

**Date**: 2026-07-19  
**Commit target**: `.github/workflows/pypi-publish.yml`

## What landed

| Item | Detail |
|------|--------|
| Triggers | Tags `tac-validate-v*`, `iwxxm-validate-v*`, `tac2iwxxm-v*`; `workflow_dispatch` dry-run |
| Matrix | Three packages (`tac-validate`, `iwxxm-validate`, `tac2iwxxm`); only matching tag row runs |
| OIDC | `publish` job: `permissions.id-token: write` + environment `pypi` |
| Build | `uv build --wheel` from checkout (iwxxm-validate hatch hook needs `vendor/`); sdist for non–schema packages |
| Smoke | Clean-venv wheel install + import/CLI one-liner before publish |
| Token | No `PYPI_API_TOKEN` — Trusted Publisher only |

## Operator follow-up (not in-repo)

Configure PyPI Trusted Publisher for each project against:

- Owner/repo: this GitHub repo  
- Workflow: `pypi-publish.yml`  
- Environment: `pypi` (optional but recommended)

## Next

- **T4.4** — dry-run / checklist gate (`workflow_dispatch` with `publish=false`)  
- **T4.5** — manylinux + macOS + Windows maturin wheel jobs
