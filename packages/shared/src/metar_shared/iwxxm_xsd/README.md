# iwxxm_xsd (generated)

Pydantic models from pinned `vendor/schemas/iwxxm` via
`scripts/codegen/iwxxm_xsd.py` (ADR-027 / E10-40).

```bash
make codegen-iwxxm-xsd
# or a single pin:
uv run python scripts/codegen/iwxxm_xsd.py --version 2025-2
```

Do not hand-edit generated `v*` modules — re-run on vendor pin bumps
(`.github/workflows/vendor-sync.yml` invokes codegen after sync).

Validate hot path remains Rust (`iwxxm-validate`); these models are for typed
bind / convert follow-on (T3.7).
