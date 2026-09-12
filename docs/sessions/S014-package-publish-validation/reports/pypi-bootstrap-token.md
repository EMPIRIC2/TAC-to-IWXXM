# PyPI project bootstrap via API token (UJ-023 path B)

> **Date:** 2026-07-19  
> **Decision:** D-S014-EV010-pypi-bootstrap-3 — create projects with one-time `PYPI_API_TOKEN`, then attach normal Trusted Publishers  
> **Why:** PyPI blocks multiple *pending* publishers for the same `(repo, workflow, environment)`

## Uploaded (production PyPI)

| Project | Version | Artifacts |
|---------|---------|-----------|
| `tac-validate` | `0.1.0` | wheel + sdist |
| `iwxxm-validate` | `0.1.0` | pure wheel (schemas bundled; no maturin native in bootstrap) |
| `tac2iwxxm` | `0.1.0` | wheel + sdist |

URLs:

- https://pypi.org/project/tac-validate/0.1.0/
- https://pypi.org/project/iwxxm-validate/0.1.0/
- https://pypi.org/project/tac2iwxxm/0.1.0/

Token used from local `.env` `PYPI_API_TOKEN` only (not committed; not added to GHA secrets).

## Operator next — Trusted Publishers on **existing** projects

Pending publishers are no longer needed. For **each** project:

1. Open Project → **Publishing** (e.g. https://pypi.org/manage/project/tac-validate/settings/publishing/)
2. Add GitHub Trusted Publisher:

| Field | Value |
|-------|--------|
| Owner | `joseph-c-mcguire` |
| Repository | `metar-to-IWXXM` |
| Workflow | `pypi-publish.yml` |
| Environment | `pypi` |

3. Repeat for `iwxxm-validate` and `tac2iwxxm`.
4. On [account publishing](https://pypi.org/manage/account/publishing/), **remove** any leftover *pending* publisher for this repo if still listed.
5. Ensure GitHub Environment `pypi` exists on the repo.
6. Do **not** push tags `*-v0.1.0` — that version is already on PyPI. Next OIDC publish should be `0.1.1` (or later) after bumping `pyproject.toml`.

## Notes

- Bootstrap wheels for native packages are **pure Python** (`py3-none-any`). Future tag publishes via maturin can ship platform wheels on a new version.
- GHA must stay OIDC-only (no `PYPI_API_TOKEN` secret) per E10-37 / pypi-package-publish rule.
- Prefer rotating/deleting the bootstrap token after Trusted Publishers are attached if it was account-scoped.
