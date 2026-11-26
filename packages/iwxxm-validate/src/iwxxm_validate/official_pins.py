"""Official IWXXM pin catalog helpers (FR-077 / NFR-016 / D-019).

The catalog at ``config/schemas/iwxxm-official-pins.json`` is the acquisition
source of truth. Vendored trees are optional materialization only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from iwxxm_validate.paths import official_pins_catalog_path, require_pin_cache, version_dir

OFFICIAL_PIN_IDS: tuple[str, ...] = ("3.0", "2021-2", "2023-1", "2025-2")


class OfficialPinError(ValueError):
    """Official pin catalog or cache check failed."""


def load_official_pins_catalog(path: Path | None = None) -> dict[str, Any]:
    """
    Load and lightly validate the official pin catalog.

    Parameters
    ----------
    path :
        Catalog path. Defaults to the monorepo catalog.
    """
    catalog_path = path or official_pins_catalog_path()
    try:
        raw = catalog_path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        msg = f"invalid official pin catalog: {catalog_path}: {exc}"
        raise OfficialPinError(msg) from exc
    if not isinstance(data, dict):
        msg = "official pin catalog root must be a JSON object"
        raise OfficialPinError(msg)
    catalog = cast(dict[str, Any], data)
    pins_raw = catalog.get("pins")
    if not isinstance(pins_raw, dict) or not pins_raw:
        msg = "official pin catalog must declare a non-empty pins object"
        raise OfficialPinError(msg)
    pins = cast(dict[str, Any], pins_raw)
    for pin_id, entry_raw in pins.items():
        if not isinstance(entry_raw, dict):
            msg = f"pin entry must be an object: {pin_id}"
            raise OfficialPinError(msg)
        entry = cast(dict[str, Any], entry_raw)
        for field in ("tag", "commit_sha", "cache_dirname", "namespace_fragment"):
            value = entry.get(field)
            if not str(value or "").strip():
                msg = f"pin {pin_id} missing required field {field}"
                raise OfficialPinError(msg)
    return catalog


def official_pin_ids(catalog: dict[str, Any] | None = None) -> tuple[str, ...]:
    """Return pin ids from ``catalog`` or the default official set."""
    if catalog is None:
        return OFFICIAL_PIN_IDS
    pins_raw = catalog.get("pins")
    if not isinstance(pins_raw, dict):
        return OFFICIAL_PIN_IDS
    pins = cast(dict[str, Any], pins_raw)
    return tuple(str(key) for key in pins)


def assert_official_pin_cache_present(iwxxm_version: str) -> Path:
    """
    Fail closed when the official pin tree is missing from resolvable roots.

    Parameters
    ----------
    iwxxm_version :
        Official pin id (``3.0``, ``2021-2``, ``2023-1``, ``2025-2``).
    """
    try:
        return require_pin_cache(iwxxm_version)
    except FileNotFoundError as exc:
        raise OfficialPinError(str(exc)) from exc


def assert_official_runtime_subset(
    iwxxm_version: str,
    *,
    catalog: dict[str, Any] | None = None,
) -> Path:
    """
    Fail closed: pin tree present and XSD + Schematron files exist.

    Parameters
    ----------
    iwxxm_version :
        Official pin id.
    catalog :
        Optional pre-loaded catalog (unused for path resolve; reserved for
        future hash checks against ``runtime_subset_sha256``).
    """
    del catalog  # reserved for hash verify call sites
    root = assert_official_pin_cache_present(iwxxm_version)
    xsd = root / "IWXXM" / "iwxxm.xsd"
    sch = root / "IWXXM" / "rule" / "iwxxm.sch"
    if not xsd.is_file():
        msg = f"official XSD missing for pin {iwxxm_version}: {xsd}"
        raise OfficialPinError(msg)
    if not sch.is_file():
        msg = f"official Schematron missing for pin {iwxxm_version}: {sch}"
        raise OfficialPinError(msg)
    # Touch version_dir for alias consistency (3.0 ↔ 3.0.0).
    version_dir(iwxxm_version)
    return root


__all__ = [
    "OFFICIAL_PIN_IDS",
    "OfficialPinError",
    "assert_official_pin_cache_present",
    "assert_official_runtime_subset",
    "load_official_pins_catalog",
    "official_pin_ids",
]
