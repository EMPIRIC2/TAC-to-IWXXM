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
