"""Resolve IWXXM / IWXXM-US schema paths (packaged, cache, or vendor).

Resolution order (FR-077 / NFR-016 / D-019):

1. ``IWXXM_VALIDATE_REPO_ROOT`` / ``IWXXM_SCHEMAS_ROOT`` environment overrides
2. Packaged runtime subset under ``iwxxm_validate/schemas/`` (wheel / after sync)
3. Explicit ``IWXXM_SCHEMA_CACHE`` when set
4. Default ``.cache/iwxxm-schemas/`` when present (fetch materialization)
5. Monorepo ``vendor/schemas/*`` materialization (not SoT)

``vendor_iwxxm_root()`` prefers packaged, then explicit cache, then vendor so
existing wheel/sync behavior stays stable. ``version_dir()`` searches all
candidate roots (including the default cache) and fail-closes when missing.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, cast

_PACKAGE_DIR = Path(__file__).resolve().parent
_PACKAGE_SCHEMAS = _PACKAGE_DIR / "schemas"
_PACKAGE_ROOT = _PACKAGE_DIR.parents[1]
_DEFAULT_REPO_ROOT = _PACKAGE_ROOT.parents[1]

# Product pin id ↔ on-disk directory aliases (legacy vendor used ``3.0.0``).
_PIN_ALIASES: dict[str, tuple[str, ...]] = {
    "3.0": ("3.0", "3.0.0"),
    "3.0.0": ("3.0.0", "3.0"),
}


def packaged_schemas_root() -> Path | None:
    """
    Return the packaged schema subset root when materialised.

    The subset is present after ``make sync-iwxxm-validate-schemas`` or inside a
    published wheel. ``MANIFEST.json`` alone does not count as materialised.


    Returns
    -------
    Path or None
        The packaged schema subset root when materialised.
    """
    iwxxm = _PACKAGE_SCHEMAS / "iwxxm"
    if iwxxm.is_dir() and any(iwxxm.iterdir()) and any((iwxxm / child).is_dir() for child in iwxxm.iterdir()):
        # Require at least one version tree (not only empty placeholder).
        return _PACKAGE_SCHEMAS
    return None


def repo_root() -> Path:
    """
    Return the monorepo root containing ``vendor/schemas``.

    Honours ``IWXXM_SCHEMAS_ROOT`` parent when set to ``…/vendor/schemas/iwxxm``.


    Returns
    -------
    Path
        The monorepo root containing ``vendor/schemas``.
    """
    env = os.environ.get("IWXXM_VALIDATE_REPO_ROOT")
    if env:
        return Path(env).resolve()
    schemas_root = os.environ.get("IWXXM_SCHEMAS_ROOT")
    if schemas_root:
        path = Path(schemas_root).resolve()
        # …/vendor/schemas/iwxxm → repo root two parents up from iwxxm
        if path.name == "iwxxm" and path.parent.name == "schemas":
            return path.parent.parent.parent
        # …/.cache/iwxxm-schemas → treat as schemas root parent for repo guess
        if path.name.endswith("iwxxm-schemas") or path.name == "iwxxm-schemas":
            return _DEFAULT_REPO_ROOT
        return path
    return _DEFAULT_REPO_ROOT


def official_pins_catalog_path() -> Path:
    """Return path to ``config/schemas/iwxxm-official-pins.json``."""
    return repo_root() / "config" / "schemas" / "iwxxm-official-pins.json"


def _cache_root_from_env_or_default(*, explicit_only: bool = False) -> Path | None:
    """
    Return a schema cache directory path when configured / present.

    Parameters
    ----------
    explicit_only :
        When True, only honour ``IWXXM_SCHEMA_CACHE`` (used by
        ``vendor_iwxxm_root`` so default ``.cache`` does not override packaged
        / vendor preference).
    """
    env = os.environ.get("IWXXM_SCHEMA_CACHE")
    if env:
        root = Path(env).expanduser().resolve()
    elif explicit_only:
        return None
    else:
        catalog = official_pins_catalog_path()
        rel = ".cache/iwxxm-schemas"
        if catalog.is_file():
            try:
                loaded = json.loads(catalog.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    data = cast(dict[str, Any], loaded)
                    default_rel = data.get("default_cache_rel")
                    if default_rel:
                        rel = str(default_rel)
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                pass
        root = (repo_root() / rel).resolve()
    if not root.is_dir():
        return None
    for child in root.iterdir():
        if child.is_dir() and (child / "IWXXM").is_dir():
            return root
    return None


def schema_cache_root() -> Path | None:
    """
    Return the official schema cache root when it contains at least one pin tree.

    Honours ``IWXXM_SCHEMA_CACHE``. Otherwise uses the catalog default
    (``.cache/iwxxm-schemas``) when that directory has pin trees.


    Returns
    -------
    Path or None
        Cache root, or ``None`` when absent / empty.
    """
    return _cache_root_from_env_or_default(explicit_only=False)


def pin_dirnames(iwxxm_version: str) -> tuple[str, ...]:
    """
    Return candidate on-disk directory names for a pin id.

    Parameters
    ----------
    iwxxm_version :
        Product pin such as ``2025-2`` or legacy ``3.0.0``.
    """
    pin = iwxxm_version.strip()
    return _PIN_ALIASES.get(pin, (pin,))


def vendor_iwxxm_root() -> Path:
    """
    Return ``iwxxm`` schema root (packaged subset, explicit cache, or vendor).


    Returns
    -------
    Path
        ``iwxxm`` schema root used as the parent of pin directories.
    """
    packaged = packaged_schemas_root()
    if packaged is not None:
        return packaged / "iwxxm"
    explicit_cache = _cache_root_from_env_or_default(explicit_only=True)
    if explicit_cache is not None:
        return explicit_cache
    return repo_root() / "vendor" / "schemas" / "iwxxm"


def vendor_iwxxm_us_root() -> Path:
    """
    Return ``iwxxm-us`` schema root (packaged subset or vendor pin).


    Returns
    -------
    Path
        ``iwxxm-us`` schema root (packaged subset or vendor pin).
    """
    packaged = packaged_schemas_root()
    if packaged is not None:
        return packaged / "iwxxm-us"
    return repo_root() / "vendor" / "schemas" / "iwxxm-us"


def vendor_iwxxm_ca_root() -> Path:
    """
    Return ``iwxxm-ca`` schema root (packaged subset or vendor pin).


    Returns
    -------
    Path
        ``iwxxm-ca`` schema root (packaged subset or vendor pin).
    """
    packaged = packaged_schemas_root()
    if packaged is not None:
        return packaged / "iwxxm-ca"
    return repo_root() / "vendor" / "schemas" / "iwxxm-ca"


def ca_xsd_path(*, tag: str = "3.0") -> Path | None:
    """
    Return MSC ``iwxxm-ca.xsd`` aggregate when the vendor pin is present.

    Parameters
    ----------
    tag : str, optional
        Pin subdirectory (default ``3.0`` per ``vendor/manifest.json``).


    Returns
    -------
    Path or None
        MSC ``iwxxm-ca.xsd`` aggregate when the vendor pin is present.
    """
    root = vendor_iwxxm_ca_root()
    candidates = [
        root / tag / "iwxxm-ca.xsd",
        root / "iwxxm-ca.xsd",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _candidate_iwxxm_roots() -> list[Path]:
    """Ordered roots that may contain pin directories."""
    roots: list[Path] = []
    packaged = packaged_schemas_root()
    if packaged is not None:
        roots.append(packaged / "iwxxm")
    explicit_cache = _cache_root_from_env_or_default(explicit_only=True)
    if explicit_cache is not None and explicit_cache not in roots:
        roots.append(explicit_cache)
    default_cache = _cache_root_from_env_or_default(explicit_only=False)
    if default_cache is not None and default_cache not in roots:
        roots.append(default_cache)
    vendor = repo_root() / "vendor" / "schemas" / "iwxxm"
    if vendor.is_dir() and vendor not in roots:
        roots.append(vendor)
    primary = vendor_iwxxm_root()
    if primary not in roots:
        roots.insert(0, primary)
    return roots


@lru_cache(maxsize=32)
def version_dir(iwxxm_version: str) -> Path:
    """
    Return the IWXXM version tree (contains ``IWXXM/``).

    Parameters
    ----------
    iwxxm_version : str
        Release line such as ``2023-1``, ``2025-2``, or ``3.0``.


    Returns
    -------
    Path
        The IWXXM version tree (contains ``IWXXM/``).

    Raises
    ------
    FileNotFoundError
        When no candidate root contains the pin (fail closed).
    """
    names = pin_dirnames(iwxxm_version)
    tried: list[str] = []
    for root in _candidate_iwxxm_roots():
        for name in names:
            path = root / name
            tried.append(str(path))
            if path.is_dir() and (path / "IWXXM").is_dir():
                return path
    msg = (
        f"IWXXM pin cache missing for {iwxxm_version!r} "
        f"(tried: {', '.join(tried)}). "
        "Run `make fetch-iwxxm-schemas` or set IWXXM_SCHEMA_CACHE."
    )
    raise FileNotFoundError(msg)


def require_pin_cache(iwxxm_version: str) -> Path:
    """
    Fail closed: return ``version_dir`` or raise ``FileNotFoundError``.

    Parameters
    ----------
    iwxxm_version :
        Official pin id.
    """
    return version_dir(iwxxm_version)


def xsd_path(iwxxm_version: str) -> Path:
    """
    Return path to ``iwxxm.xsd`` for ``iwxxm_version``.


    Parameters
    ----------
    iwxxm_version : str
        IWXXM release line.

    Returns
    -------
    Path
        Path to ``iwxxm.xsd`` for ``iwxxm_version``.
    """
    path = version_dir(iwxxm_version) / "IWXXM" / "iwxxm.xsd"
    if not path.is_file():
        raise FileNotFoundError(f"XSD not found for {iwxxm_version}: {path}")
    return path


def schematron_path(iwxxm_version: str) -> Path:
    """
    Return path to ``rule/iwxxm.sch`` for ``iwxxm_version``.


    Parameters
    ----------
    iwxxm_version : str
        IWXXM release line.

    Returns
    -------
    Path
        Path to ``rule/iwxxm.sch`` for ``iwxxm_version``.
    """
    path = version_dir(iwxxm_version) / "IWXXM" / "rule" / "iwxxm.sch"
    if not path.is_file():
        raise FileNotFoundError(f"Schematron not found for {iwxxm_version}: {path}")
    return path


def codelists_dir(iwxxm_version: str) -> Path:
    """
    Return directory of bundled RDF codelists for Schematron ``document()``.


    Parameters
    ----------
    iwxxm_version : str
        IWXXM release line.

    Returns
    -------
    Path
        Directory of bundled RDF codelists for Schematron ``document()``.
    """
    path = version_dir(iwxxm_version) / "IWXXM" / "rule"
    if not path.is_dir():
        raise FileNotFoundError(f"Codelists directory not found for {iwxxm_version}: {path}")
    return path


def us_catalog_path() -> Path | None:
    """
    Return IWXXM-US catalog path when present.

    Prefers ``3.0/united-states-catalog.xml`` under the vendored / packaged pin.


    Returns
    -------
    Path or None
        IWXXM-US catalog path when present.
    """
    root = vendor_iwxxm_us_root()
    candidates = [
        root / "3.0" / "united-states-catalog.xml",
        root / "united-states-catalog.xml",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def clear_path_caches() -> None:
    """
    Clear cached version directory lookups (tests / after schema sync).
    """
    version_dir.cache_clear()


__all__ = [
    "ca_xsd_path",
    "clear_path_caches",
    "codelists_dir",
    "official_pins_catalog_path",
    "packaged_schemas_root",
    "pin_dirnames",
    "repo_root",
    "require_pin_cache",
    "schema_cache_root",
    "schematron_path",
    "us_catalog_path",
    "vendor_iwxxm_ca_root",
    "vendor_iwxxm_root",
    "vendor_iwxxm_us_root",
    "version_dir",
    "xsd_path",
]
