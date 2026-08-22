"""Resolve IWXXM / IWXXM-US schema paths (packaged subset or monorepo vendor).

Resolution order (E10-34 / E10-6):

1. ``IWXXM_VALIDATE_REPO_ROOT`` / ``IWXXM_SCHEMAS_ROOT`` environment overrides
2. Packaged runtime subset under ``iwxxm_validate/schemas/`` (wheel / after sync)
3. Monorepo ``vendor/schemas/*`` when developing inside this repository
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parent
_PACKAGE_SCHEMAS = _PACKAGE_DIR / "schemas"
_PACKAGE_ROOT = _PACKAGE_DIR.parents[1]
_DEFAULT_REPO_ROOT = _PACKAGE_ROOT.parents[1]


def packaged_schemas_root() -> Path | None:
    """
    Return the packaged schema subset root when materialised.

    The subset is present after ``make sync-iwxxm-validate-schemas`` or inside a
    published wheel. ``MANIFEST.json`` alone does not count as materialised.
    """
    iwxxm = _PACKAGE_SCHEMAS / "iwxxm"
    if iwxxm.is_dir() and any(iwxxm.iterdir()):
        # Require at least one version tree (not only empty placeholder).
        if any((iwxxm / child).is_dir() for child in iwxxm.iterdir()):
            return _PACKAGE_SCHEMAS
    return None


def repo_root() -> Path:
    """
    Return the monorepo root containing ``vendor/schemas``.

    Honours ``IWXXM_SCHEMAS_ROOT`` parent when set to ``…/vendor/schemas/iwxxm``.
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
        return path
    return _DEFAULT_REPO_ROOT


def vendor_iwxxm_root() -> Path:
    """Return ``iwxxm`` schema root (packaged subset or ``vendor/schemas/iwxxm``)."""
    packaged = packaged_schemas_root()
    if packaged is not None:
        return packaged / "iwxxm"
    return repo_root() / "vendor" / "schemas" / "iwxxm"


def vendor_iwxxm_us_root() -> Path:
    """Return ``iwxxm-us`` schema root (packaged subset or vendor pin)."""
    packaged = packaged_schemas_root()
    if packaged is not None:
        return packaged / "iwxxm-us"
    return repo_root() / "vendor" / "schemas" / "iwxxm-us"


def vendor_iwxxm_ca_root() -> Path:
    """Return ``iwxxm-ca`` schema root (packaged subset or vendor pin)."""
    packaged = packaged_schemas_root()
    if packaged is not None:
        return packaged / "iwxxm-ca"
    return repo_root() / "vendor" / "schemas" / "iwxxm-ca"


def ca_xsd_path(*, tag: str = "3.0") -> Path | None:
    """
    Return MSC ``iwxxm-ca.xsd`` aggregate when the vendor pin is present.

    Parameters
    ----------
    tag :
        Pin subdirectory (default ``3.0`` per ``vendor/manifest.json``).
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


@lru_cache(maxsize=32)
def version_dir(iwxxm_version: str) -> Path:
    """
    Return the IWXXM version tree (contains ``IWXXM/``).

    Parameters
    ----------
    iwxxm_version :
        Release line such as ``2023-1`` or ``2025-2``.
    """
    path = vendor_iwxxm_root() / iwxxm_version
    if not path.is_dir():
        raise FileNotFoundError(f"IWXXM version directory not found: {path}")
    return path


def xsd_path(iwxxm_version: str) -> Path:
    """Return path to ``iwxxm.xsd`` for ``iwxxm_version``."""
    path = version_dir(iwxxm_version) / "IWXXM" / "iwxxm.xsd"
    if not path.is_file():
        raise FileNotFoundError(f"XSD not found for {iwxxm_version}: {path}")
    return path


def schematron_path(iwxxm_version: str) -> Path:
    """Return path to ``rule/iwxxm.sch`` for ``iwxxm_version``."""
    path = version_dir(iwxxm_version) / "IWXXM" / "rule" / "iwxxm.sch"
    if not path.is_file():
        raise FileNotFoundError(f"Schematron not found for {iwxxm_version}: {path}")
    return path


def codelists_dir(iwxxm_version: str) -> Path:
    """Return directory of bundled RDF codelists for Schematron ``document()``."""
    path = version_dir(iwxxm_version) / "IWXXM" / "rule"
    if not path.is_dir():
        raise FileNotFoundError(f"Codelists directory not found for {iwxxm_version}: {path}")
    return path


def us_catalog_path() -> Path | None:
    """
    Return IWXXM-US catalog path when present.

    Prefers ``3.0/united-states-catalog.xml`` under the vendored / packaged pin.
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
    """Clear cached version directory lookups (tests / after schema sync)."""
    version_dir.cache_clear()


__all__ = [
    "ca_xsd_path",
    "clear_path_caches",
    "codelists_dir",
    "packaged_schemas_root",
    "repo_root",
    "schematron_path",
    "us_catalog_path",
    "vendor_iwxxm_ca_root",
    "vendor_iwxxm_root",
    "vendor_iwxxm_us_root",
    "version_dir",
    "xsd_path",
]
