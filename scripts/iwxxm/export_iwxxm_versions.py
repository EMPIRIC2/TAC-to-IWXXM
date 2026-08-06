#!/usr/bin/env python3
"""
Export IWXXM supported-versions SoT to committed JSON for FE + OpenAPI/CI.

Source: ``apps/backend/src/config/iwxxm_versions.py`` (``DEFAULT_VERSION``,
``SUPPORTED_VERSIONS[*].status`` → ``role``).

Output: ``apps/frontend/src/generated/iwxxm_versions.json``

  { "default": "<id>", "versions": [{"id", "role": "latest"|"previous"}] }

S046 / EV-038 / #851 / ``D-S046-sot``. Run via ``make export-iwxxm-versions``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_SRC = _REPO_ROOT / "apps" / "backend" / "src"
_OUT = _REPO_ROOT / "apps" / "frontend" / "src" / "generated" / "iwxxm_versions.json"


def _load_versions_module():  # noqa: ANN202
    sys.path.insert(0, str(_BACKEND_SRC))
    from config import iwxxm_versions as versions  # type: ignore[import-not-found]

    return versions


def build_payload(versions_mod: object) -> dict[str, object]:
    """Map Python SoT to the locked FE/CI JSON shape."""
    default = str(getattr(versions_mod, "DEFAULT_VERSION"))
    supported: dict[str, dict[str, object]] = getattr(versions_mod, "SUPPORTED_VERSIONS")
    out_versions: list[dict[str, str]] = []
    for version_id, meta in supported.items():
        role = str(meta.get("status", ""))
        if role not in {"latest", "previous"}:
            raise SystemExit(f"{version_id}: status={role!r} must be latest|previous")
        out_versions.append({"id": version_id, "role": role})
    if default not in {v["id"] for v in out_versions}:
        raise SystemExit(f"DEFAULT_VERSION {default!r} not in SUPPORTED_VERSIONS")
    return {"default": default, "versions": out_versions}


def main() -> int:
    """Write generated JSON; return 0 on success."""
    payload = build_payload(_load_versions_module())
    _OUT.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, ensure_ascii=True) + "\n"
    _OUT.write_text(text, encoding="utf-8")
    print(f"Wrote {_OUT.relative_to(_REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
