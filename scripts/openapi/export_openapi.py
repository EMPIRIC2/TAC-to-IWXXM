#!/usr/bin/env python3
"""Export FastAPI OpenAPI JSON for FE openapi-typescript (EV-052 / D-S061-openapi-src)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BACKEND = _REPO_ROOT / "apps" / "backend"
_OUT = _REPO_ROOT / "apps" / "frontend" / "openapi" / "openapi.json"


def main() -> int:
    sys.path.insert(0, str(_BACKEND))
    from src import api as api_module  # noqa: PLC0415

    schema = api_module.app.openapi()
    _OUT.parent.mkdir(parents=True, exist_ok=True)
    _OUT.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {_OUT.relative_to(_REPO_ROOT)} ({_OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
