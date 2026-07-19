# iwxxm_xsd (generated)

Pydantic models from pinned `vendor/schemas/iwxxm` via
`scripts/codegen/iwxxm_xsd.py` (ADR-027 / E10-40).

```bash
make codegen-iwxxm-xsd
# or a single pin:
uv run python scripts/codegen/iwxxm_xsd.py --version 2025-2
```

Committed trees: `v2023_1/`, `v2025_2/` (regenerate on vendor pin bumps —
`.github/workflows/vendor-sync.yml` invokes codegen after sync).

Do not hand-edit generated `v*` modules.

## Imports

```python
from metar_shared.iwxxm_xsd import available_versions, import_version_leaf

mod = import_version_leaf("2025-2", "xlink")  # safe leaf import
```

Version package `__init__` re-exports can hit GML circular imports — use
`import_version_leaf` (or import leaf modules after a namespace stub).

Optional deps: `metar-shared[xsd]` (`pydantic`, `xsdata-pydantic`).

## Adapt follow-on

`adapt.pydantic_to_msgspec` / `adapt.pydantic_to_rust_hint` are placeholders
(ADR-027). Validate hot path remains Rust (`iwxxm-validate`).
