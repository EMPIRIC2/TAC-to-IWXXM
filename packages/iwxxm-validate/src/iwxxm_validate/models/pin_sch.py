"""Pin ↔ Schematron bundle model."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class PinSchError(ValueError):
    """
    IWXXM pin and Schematron bundle do not match.

    Attributes
    ----------
    args : tuple
        Arguments passed to the exception constructor.
    """


@dataclass(frozen=True, slots=True)
class PinSchBundle:
    """
    Resolved XSD + Schematron paths for one IWXXM pin.

    Attributes
    ----------
    pin : str
        Pin.
    version_root : Path
        Version root.
    xsd : Path
        XSD.
    schematron : Path
        Schematron.
    namespace_uri : str
        Namespace URI.
    """

    pin: str
    version_root: Path
    xsd: Path
    schematron: Path
    namespace_uri: str


__all__ = ["PinSchBundle", "PinSchError"]
