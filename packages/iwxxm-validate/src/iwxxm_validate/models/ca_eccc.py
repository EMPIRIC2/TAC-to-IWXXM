"""CA_ECCC schema bundle model."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class CaEcccSchemaBundle:
    """
    Resolved on-disk paths for the CA_ECCC validation bundle.

    Attributes
    ----------
    iwxxm_version : str
        IWXXM release line.
    core_xsd : Path
        Core XSD.
    schematron : Path
        Schematron.
    extension_root : Path
        Extension root.
    aggregate_ca_xsd : Path or None
        Aggregate CA XSD.
    """

    iwxxm_version: str
    core_xsd: Path
    schematron: Path
    extension_root: Path
    aggregate_ca_xsd: Path | None


__all__ = ["CaEcccSchemaBundle"]
