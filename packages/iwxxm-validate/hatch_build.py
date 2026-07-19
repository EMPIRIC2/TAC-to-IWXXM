# hatch_build.py — include E10-34 schema subset in wheels (sync-on-build).
"""Hatch build hook: sync runtime schemas from vendor before packaging."""

from __future__ import annotations

import sys
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

_PACKAGE_ROOT = Path(__file__).resolve().parent
_SYNC_SCRIPT = _PACKAGE_ROOT / "scripts" / "sync_runtime_schemas.py"


class CustomBuildHook(BuildHookInterface):
    """Materialise ``iwxxm_validate/schemas`` from vendor pins (E10-34)."""

    PLUGIN_NAME = "custom"

    def initialize(self, version: str, build_data: dict) -> None:  # noqa: ARG002
        """Run ``sync_runtime_schemas`` so the wheel ships XSD/SCH/catalogs."""
        if not _SYNC_SCRIPT.is_file():
            message = f"schema sync script missing: {_SYNC_SCRIPT}"
            raise RuntimeError(message)
        # Import by path so hatch does not need the package on sys.path.
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "iwxxm_validate_sync_runtime_schemas",
            _SYNC_SCRIPT,
        )
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load sync script: {_SYNC_SCRIPT}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        module.sync(clean=True)
        # Ensure non-Python schema files are always packaged (even if gitignored).
        build_data.setdefault("force_include", {})
        schemas = _PACKAGE_ROOT / "src" / "iwxxm_validate" / "schemas"
        for path in schemas.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(_PACKAGE_ROOT / "src")
            # Hatch force_include maps source path → archive path inside the wheel.
            build_data["force_include"][str(path)] = str(rel).replace("\\", "/")
