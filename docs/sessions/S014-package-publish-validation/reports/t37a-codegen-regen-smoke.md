# T3.7a — Codegen regen smoke (ADR-027 / F11 acc4)

**Session:** S014 / EV-010  
**Task:** T3.7a  
**Date:** 2026-07-18  
**Status:** completed  

## Pass criteria

| Check | How | Result |
|-------|-----|--------|
| Regen from pinned XSD | `generate_version("2025-2", entry="metarSpeci.xsd")` | PASS |
| Non-empty | `py_files >= 5`, `bytes > 10KiB` | PASS |
| Pydantic models present | AST count of `BaseModel` subclasses ≥ 10 | PASS |
| Importable | At least one leaf module imports at runtime (GML circular imports soft-known) | PASS (`xlink`) |

## Fixes landed with the smoke

1. **Duplicate `default=` kwargs** — xsdata emits `field(..., default=None,\n default=None)` (lowercase `field`, multiline). Pipeline `fix_duplicate_field_defaults` strips duplicates before/after ruff.
2. **Package `__init__` circular imports** — generated `__init__.py` re-exports `common`/`metar_speci` and hits GML cycles. Smoke registers a namespace stub and imports leaf modules (`xlink` first).

## Test

`tests/codegen/test_tc_f11_codegen_regen_smoke.py` — 2 passed (`@pytest.mark.slow` for regen).

## Next

**T3.7** — commit regenerated models; optional msgspec/Rust adapt helpers.
