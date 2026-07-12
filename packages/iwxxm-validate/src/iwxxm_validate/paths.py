"""Resolve vendored IWXXM / IWXXM-US schema paths (read-only)."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_REPO_ROOT = _PACKAGE_ROOT.parents[1]


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
    """Return ``vendor/schemas/iwxxm``."""
    return repo_root() / "vendor" / "schemas" / "iwxxm"


def vendor_iwxxm_us_root() -> Path:
    """Return ``vendor/schemas/iwxxm-us``."""
    return repo_root() / "vendor" / "schemas" / "iwxxm-us"


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

    Prefers ``3.0/united-states-catalog.xml`` under the vendored pin.
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


__all__ = [
    "codelists_dir",
    "repo_root",
    "schematron_path",
    "us_catalog_path",
    "vendor_iwxxm_root",
    "vendor_iwxxm_us_root",
    "version_dir",
    "xsd_path",
]
