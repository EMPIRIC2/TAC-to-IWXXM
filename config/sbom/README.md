# Software bill of materials

Live dependency inventory for this monorepo. This replaces the former prose list
in `docs/dependency-inventory.md`.

| File | Role |
|------|------|
| `cyclonedx.json` | CycloneDX 1.6 JSON from `uv export` (third-party pins) |
| `requirements.frozen.txt` | Pin list used to build the CycloneDX file |

## Commands

```bash
make sbom         # regenerate
make sbom-check   # fail on drift vs HEAD
```

CI runs the drift check on push. Add new libraries only after an explicit
decision; this folder records what the lockfile pins.

## Publishable first-party packages

Workspace members published via `.github/workflows/pypi-publish.yml` (OIDC trusted
publisher; tag-driven). Dist name may differ from the import path:

| Dist / PyPI name | Path | Import |
|------------------|------|--------|
| `tac-validate` | `packages/tac-validate` | `tac_validate` |
| `iwxxm-validate` | `packages/iwxxm-validate` | `iwxxm_validate` |
| `tac2iwxxm` | `packages/tac2iwxxm` | `tac2iwxxm` |
| `tac-decoding` | `packages/tac-decoding` | `tac_decoding` |
| `metar-shared` | `packages/shared` | `metar_shared` |
| `reference-lookup` | `packages/reference-lookup` | `reference_lookup` |
| `iwxxm-dissemination` | `packages/dissemination` | `dissemination` |

This table replaces the former prose list that lived in `docs/dependency-inventory.md`.
