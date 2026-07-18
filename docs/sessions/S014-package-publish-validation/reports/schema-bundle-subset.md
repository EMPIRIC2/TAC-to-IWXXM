# Schema wheel subset — T3.4 / E10-34

**Session:** S014-package-publish-validation  
**Cycle:** EV-010  
**Task:** T3.4  
**Decisions:** E10-34, E10-6  

## Policy

`iwxxm-validate` wheels ship a **runtime-only** schema subset copied from pinned
`vendor/schemas/*` at build time (hatch custom hook → `scripts/sync_runtime_schemas.py`).

| Include | Source |
|---------|--------|
| IWXXM `2023-1` / `2025-2` — `IWXXM/*.xsd` | `vendor/schemas/iwxxm/{version}/IWXXM/` |
| Schematron + RDF codelists — `IWXXM/rule/**` | same |
| Shared XSD catalogs — `externalSchema/**` | `vendor/schemas/iwxxm/externalSchema/` |
| IWXXM-US 3.0 catalog + XSDs | `vendor/schemas/iwxxm-us/` |
| Policy file | `iwxxm_validate/schemas/MANIFEST.json` |

| Exclude | Rationale |
|---------|-----------|
| `**/html/**`, `**/examples/**`, `**/XMI/**`, `**/documentation/**` | Docs / samples — not needed at validate time |
| `iwxxm-modelling/**` | ~139 MiB UML/modelling bulk (E10-34) |
| `iwxxm-translation/**` | Translation tree bulk; wheel uses `iwxxm/externalSchema` only |
| `iwxxm-codelists/**` | Codelists already mirrored under each version `rule/` |

## Developer / CI

```bash
make sync-iwxxm-validate-schemas   # optional local materialisation
uv build --package iwxxm-validate  # hook syncs automatically
```

Generated trees under `src/iwxxm_validate/schemas/{iwxxm,iwxxm-us}/` are **gitignored**;
`MANIFEST.json` is tracked. Path resolution prefers the packaged subset when present,
else monorepo `vendor/schemas/*` (env overrides still win).

## Size (indicative after sync)

Recorded by `LAST_SYNC.json` on each sync (gitignored). Expect roughly **6–8 MiB** of
runtime assets vs **~180 MiB+** if modelling/translation were included.
