"""CA_ECCC profile-pinned IWXXM 3.0.0 + ``iwxxm-ca`` bundle resolution (EV-068 M2).

Centralizes catalog roots for the native xmloxide resolver so MSC extension XSDs
that import ``http://schemas.wmo.int/iwxxm/3.0/`` or ``…/3.0.0/`` URLs resolve
against the vendored ``vendor/schemas/iwxxm/3.0.0`` tree plus ``externalSchema``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from iwxxm_validate.paths import (
    ca_xsd_path,
    repo_root,
    schematron_path,
    vendor_iwxxm_ca_root,
    vendor_iwxxm_root,
    version_dir,
    xsd_path,
)

CA_ECCC_IWXXM_VERSION = "3.0.0"
CA_ECCC_EXTENSION_TAG = "3.0"


@dataclass(frozen=True, slots=True)
class CaEcccSchemaBundle:
    """Resolved on-disk paths for the CA_ECCC validation bundle."""

    iwxxm_version: str
    core_xsd: Path
    schematron: Path
    extension_root: Path
    aggregate_ca_xsd: Path | None


def resolve_ca_eccc_bundle(
    *,
    iwxxm_version: str = CA_ECCC_IWXXM_VERSION,
    extension_tag: str = CA_ECCC_EXTENSION_TAG,
) -> CaEcccSchemaBundle | None:
    """
    Resolve the CA_ECCC schema bundle when vendor pins are present.

    Parameters
    ----------
    iwxxm_version :
        Profile-pinned IWXXM release line (default ``3.0.0``).
    extension_tag :
        MSC ``iwxxm-ca`` pin subdirectory (default ``3.0``).

    Returns
    -------
    CaEcccSchemaBundle | None
        ``None`` when core or extension pins are missing (fail-closed).
    """
    if iwxxm_version != CA_ECCC_IWXXM_VERSION:
        return None
    if ca_xsd_path(tag=extension_tag) is None:
        return None
    try:
        core_xsd = xsd_path(iwxxm_version)
        sch = schematron_path(iwxxm_version)
    except FileNotFoundError:
        return None
    return CaEcccSchemaBundle(
        iwxxm_version=iwxxm_version,
        core_xsd=core_xsd,
        schematron=sch,
        extension_root=vendor_iwxxm_ca_root(),
        aggregate_ca_xsd=ca_xsd_path(tag=extension_tag),
    )


def ca_eccc_catalog_roots(
    iwxxm_version: str = CA_ECCC_IWXXM_VERSION,
    *,
    extension_tag: str = CA_ECCC_EXTENSION_TAG,
) -> list[str]:
    """
    Return directory roots for xmloxide ``SchemaResolver`` on the CA_ECCC path.

    Includes WMO ``3.0.0`` core, ``externalSchema`` (GML/AIXM/W3C), MSC extension
    tree, and optional monorepo translation fallback. URL imports such as
    ``http://schemas.wmo.int/iwxxm/3.0/iwxxm.xsd`` resolve via suffix/basename
    indexing against these roots (no network fetch).

    Parameters
    ----------
    iwxxm_version :
        Profile-pinned IWXXM release line.
    extension_tag :
        MSC pin subdirectory under ``iwxxm-ca``.

    Returns
    -------
    list[str]
        Absolute directory paths suitable for ``catalog_roots`` on the Rust path.
    """
    try:
        vdir = version_dir(iwxxm_version)
    except FileNotFoundError:
        return []

    root = vendor_iwxxm_root()
    ca_root = vendor_iwxxm_ca_root()
    candidates: list[Path] = [
        vdir / "IWXXM",
        vdir,
        root / "externalSchema",
        root / "externalSchema" / "schemas.opengis.net",
        root / "externalSchema" / "schemas.wmo.int",
        root,
        ca_root / extension_tag,
        ca_root,
        repo_root() / "vendor" / "schemas" / "iwxxm-translation" / "externalSchema",
    ]
    return [str(p) for p in candidates if p.is_dir()]


def ca_eccc_bundle_available(
    *,
    iwxxm_version: str = CA_ECCC_IWXXM_VERSION,
    extension_tag: str = CA_ECCC_EXTENSION_TAG,
) -> bool:
    """Return whether ``resolve_ca_eccc_bundle`` would succeed."""
    return resolve_ca_eccc_bundle(iwxxm_version=iwxxm_version, extension_tag=extension_tag) is not None


__all__ = [
    "CA_ECCC_EXTENSION_TAG",
    "CA_ECCC_IWXXM_VERSION",
    "CaEcccSchemaBundle",
    "ca_eccc_bundle_available",
    "ca_eccc_catalog_roots",
    "resolve_ca_eccc_bundle",
]
