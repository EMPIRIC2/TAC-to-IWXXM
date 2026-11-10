# Software Bill of Materials (SBOM)

Live dependency inventory for this monorepo. Replaces the former
`docs/dependency-inventory.md` prose list.

| File | Role |
|------|------|
| `cyclonedx.json` | CycloneDX 1.6 JSON from `uv export` (third-party pins) |
| `requirements.frozen.txt` | Intermediate pin list used to build the SBOM |

## Commands

```bash
make sbom         # regenerate
make sbom-check   # fail on drift vs HEAD
```

CI runs the drift check on push. New dependencies still need an evolve
`[Decision]` before you add them; the SBOM records what is locked.
