"""METAR TAC -> IWXXM conversion utilities.

Provides a single function `convert_metar_tac` that takes a METAR/SPECI TAC
string and returns an IWXXM XML document serialized to Unicode text. The caller
can persist the string as `.txt` (per GUI requirement) or `.xml`.
"""

from __future__ import annotations

import pathlib
import sys
import xml.etree.ElementTree as ET
from typing import Optional


def _ensure_gifts_on_path() -> None:
    """Add GIFTs submodule directory to sys.path for imports."""
    # Try multiple possible locations for GIFTs
    # 1. Development: backend/conversion.py -> repo_root/GIFTs
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    gifts_dir = repo_root / "GIFTs"

    # 2. Docker container: /app/GIFTs (when installed as package)
    if not gifts_dir.exists():
        gifts_dir = pathlib.Path("/app/GIFTs")

    if gifts_dir.exists():
        if str(gifts_dir) not in sys.path:
            sys.path.insert(0, str(gifts_dir))
    else:
        raise ImportError(
            f"GIFTs submodule not found at {gifts_dir}. "
            "Run: git submodule update --init --recursive"
        )


_ensure_gifts_on_path()

try:  # Lazy import; failures surfaced at first conversion call.
    from gifts import metarDecoder, metarEncoder  # type: ignore
except Exception:  # pragma: no cover
    metarDecoder = None  # type: ignore
    metarEncoder = None  # type: ignore


class ConversionError(Exception):
    """Raised when METAR -> IWXXM conversion fails."""


def convert_metar_tac(tac_text: str) -> str:
    """Convert a single METAR/SPECI TAC string to IWXXM XML text.

    Returns:
        XML document as a Unicode string.
    Raises:
        ConversionError: if decoding or encoding fails.
    """

    if metarDecoder is None or metarEncoder is None:
        raise ConversionError(
            "GIFTs metar modules unavailable (import failed).")

    # Create fresh instances per call for thread-safety.
    try:
        decoder = metarDecoder.Annex3()  # type: ignore[attr-defined]
        encoder = metarEncoder.Annex3()  # type: ignore[attr-defined]
    except Exception as e:  # pragma: no cover
        raise ConversionError(
            f"Failed to construct decoder/encoder: {e}") from e

    try:
        decoded = decoder(tac_text)
        xml_root = encoder(decoded, tac_text)
    except Exception as e:
        raise ConversionError(f"Decoding/encoding error: {e}") from e

    if xml_root is None:
        raise ConversionError("Encoder returned None (no XML produced).")

    try:
        return ET.tostring(xml_root, encoding="unicode")
    except Exception as e:
        raise ConversionError(f"Serialization error: {e}") from e


__all__ = ["convert_metar_tac", "ConversionError"]
