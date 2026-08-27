"""Follow-on adapters from xsdata pydantic models (ADR-027 / T3.7).

Validate hot path stays Rust (`iwxxm-validate`). These helpers expose version
discovery and a stable seam for later msgspec/Rust adapt tasks - they do not
rewrite generated ``v*`` trees.
"""

from __future__ import annotations

import json
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any, cast

_PACKAGE_ROOT = Path(__file__).resolve().parent
_STATUS_PATH = _PACKAGE_ROOT / "STATUS.json"


def version_package(version: str) -> str:
    """Map release line ``2025-2`` → package segment ``v2025_2``."""
    return "v" + version.replace("-", "_").replace(".", "_")


def available_versions() -> list[str]:
    """Return pinned IWXXM versions recorded in ``STATUS.json``."""
    if not _STATUS_PATH.is_file():
        return []
    loaded: object = json.loads(_STATUS_PATH.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        return []
    data = cast(dict[str, Any], loaded)
    versions_field: object = data.get("versions", [])
    if not isinstance(versions_field, list):
        return []
    versions: list[str] = []
    versions.extend(
        str(item)
        for item in cast(list[object], versions_field)
        if isinstance(item, (str, int, float))
    )
    return versions


def package_name(version: str) -> str:
    """Fully-qualified package for a release line."""
    return f"metar_shared.iwxxm_xsd.{version_package(version)}"


def import_version_leaf(version: str, leaf: str = "xlink") -> ModuleType:
    """
    Import a leaf module without executing the version package ``__init__``.

    Generated ``__init__`` re-exports trigger known GML circular imports; leaf
    modules such as ``xlink`` are the supported import surface until adapt work
    lands.
    """
    import sys
    import types

    pkg = package_name(version)
    version_dir = _PACKAGE_ROOT / version_package(version)
    if not version_dir.is_dir():
        raise FileNotFoundError(
            f"generated models missing for {version}: {version_dir}"
        )

    import_module("metar_shared")
    import_module("metar_shared.iwxxm_xsd")

    existing = sys.modules.get(pkg)
    if existing is None or not hasattr(existing, "__path__"):
        stub = types.ModuleType(pkg)
        stub.__file__ = str(version_dir / "__init__.py")
        stub.__path__ = [str(version_dir)]  # type: ignore[attr-defined]
        stub.__package__ = pkg
        sys.modules[pkg] = stub

    return import_module(f"{pkg}.{leaf}")


def pydantic_to_msgspec(_model: object) -> object:
    """
    Placeholder for msgspec Struct adaptation (ADR-027 follow-on).

    Raises
    ------
    NotImplementedError
        Always - convert builders wire this in a later task.
    """
    raise NotImplementedError(
        "msgspec adaptation of xsdata pydantic models is a follow-on (ADR-027)"
    )


def pydantic_to_rust_hint(_model: object) -> str:
    """
    Placeholder for Rust type-hint export (ADR-027 follow-on).

    Raises
    ------
    NotImplementedError
        Always - native convert builders wire this in a later task.
    """
    raise NotImplementedError(
        "Rust adapt hints from xsdata pydantic models are a follow-on (ADR-027)"
    )
