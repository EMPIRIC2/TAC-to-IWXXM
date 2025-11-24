"""METAR TAC -> IWXXM conversion utilities (src layout)."""
from __future__ import annotations

import pathlib
import sys
import xml.etree.ElementTree as ET


def _ensure_gifts_on_path() -> None:
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    gifts_dir = repo_root / "GIFTs"
    if gifts_dir.exists():
        if str(gifts_dir) not in sys.path:
            sys.path.insert(0, str(gifts_dir))
    else:  # pragma: no cover
        raise ImportError(
            f"GIFTs submodule not found at {gifts_dir}. Run: git submodule update --init --recursive"
        )


_ensure_gifts_on_path()

try:  # pragma: no cover
    from gifts import metarDecoder, metarEncoder  # type: ignore
except Exception:  # pragma: no cover
    metarDecoder = None  # type: ignore
    metarEncoder = None  # type: ignore


class ConversionError(Exception):
    pass


def convert_metar_tac(tac_text: str) -> str:
    if metarDecoder is None or metarEncoder is None:
        raise ConversionError(
            "GIFTs metar modules unavailable (import failed).")
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
