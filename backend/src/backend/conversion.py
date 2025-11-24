"""METAR TAC -> IWXXM conversion utilities (src layout)."""
from __future__ import annotations

import pathlib
import sys
import xml.etree.ElementTree as ET


def _ensure_gifts_on_path() -> None:
    """Resolve and add the GIFTs directory to sys.path.

    Handles both source layout (running from repo) and installed package
    layout inside a container (site-packages). We attempt several plausible
    ancestor locations plus explicit /app path used in Docker builds.
    """
    file_path = pathlib.Path(__file__).resolve()
    candidates = []

    # Ancestor traversals: parents[0] .. parents[5] (defensive upper bound)
    for depth in range(0, 6):  # pragma: no cover (loop logic simple)
        try:
            parent = file_path.parents[depth]
        except IndexError:
            break
        candidates.append(parent / "GIFTs")

    # Explicit Docker workdir copy location
    candidates.append(pathlib.Path("/app/GIFTs"))

    for cand in candidates:
        if cand.exists():
            if str(cand) not in sys.path:
                sys.path.insert(0, str(cand))
            return

    # If we reach here, none of the candidates existed.
    raise ImportError(
        "GIFTs submodule not found in any expected location. "
        "Tried: " + ", ".join(str(c) for c in candidates)
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
