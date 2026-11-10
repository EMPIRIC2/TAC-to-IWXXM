#!/usr/bin/env python3
"""Export FastAPI OpenAPI JSON/YAML for FE types and api/ corpus (EV-repo-docs-cleanup)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BACKEND = _REPO_ROOT / "apps" / "backend"
_API_DIR = _REPO_ROOT / "api"
_FE_OUT = _REPO_ROOT / "apps" / "frontend" / "openapi" / "openapi.json"
_API_JSON = _API_DIR / "openapi.json"
_API_YAML = _API_DIR / "openapi.yaml"


def _to_yaml(value: Any, indent: int = 0) -> str:
    """Emit a minimal YAML subset for OpenAPI JSON objects."""
    pad = "  " * indent
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        if value == "" or any(c in value for c in ":#{}[],&*!|>'\"%@`\n"):
            return json.dumps(value)
        return value
    if isinstance(value, list):
        if not value:
            return "[]"
        lines: list[str] = []
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}-")
                nested = _to_yaml(item, indent + 1)
                for line in nested.splitlines():
                    lines.append(f"{pad}  {line}" if line else pad)
            else:
                lines.append(f"{pad}- {_to_yaml(item, 0)}")
        return "\n".join(lines)
    if isinstance(value, dict):
        if not value:
            return "{}"
        lines = []
        for key, item in value.items():
            key_s = str(key)
            if isinstance(item, (dict, list)) and item:
                lines.append(f"{pad}{key_s}:")
                nested = _to_yaml(item, indent + 1)
                lines.append(nested)
            else:
                lines.append(f"{pad}{key_s}: {_to_yaml(item, 0)}")
        return "\n".join(lines)
    return json.dumps(value)


def main() -> int:
    """Export OpenAPI schema to api/ and the frontend snapshot."""
    sys.path.insert(0, str(_BACKEND))
    from src import api as api_module

    schema = api_module.app.openapi()
    payload = json.dumps(schema, indent=2, sort_keys=True) + "\n"

    _API_DIR.mkdir(parents=True, exist_ok=True)
    _FE_OUT.parent.mkdir(parents=True, exist_ok=True)
    _API_JSON.write_text(payload, encoding="utf-8")
    _FE_OUT.write_text(payload, encoding="utf-8")
    _API_YAML.write_text(_to_yaml(schema) + "\n", encoding="utf-8")

    print(f"Wrote {_API_JSON.relative_to(_REPO_ROOT)} ({_API_JSON.stat().st_size} bytes)")
    print(f"Wrote {_API_YAML.relative_to(_REPO_ROOT)} ({_API_YAML.stat().st_size} bytes)")
    print(f"Wrote {_FE_OUT.relative_to(_REPO_ROOT)} ({_FE_OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
