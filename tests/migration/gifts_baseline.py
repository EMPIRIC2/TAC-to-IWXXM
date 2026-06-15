"""GIFTs conversion helper for TC-M003 migration regression tests.

Uses the legacy ``GIFTs/`` tree until ``packages/gifts`` is wired (T3.2+).
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GIFTS_ROOT = ROOT / "GIFTs"

# Fixed bulletin metadata keeps golden output stable across runs (REQ-018).
FIXED_RECEPTION_TIME = "2023-06-23T17:51:00Z"

_CODES_INITIALIZED = False


def _initialize_gifts_code_registry() -> None:
    """Load WMO code tables so encoder output is deterministic (GIFTs tests parity)."""
    global _CODES_INITIALIZED
    if _CODES_INITIALIZED:
        return

    import gifts.common.xmlConfig as des  # type: ignore[import-untyped]
    import gifts.common.xmlUtilities as deu  # type: ignore[import-untyped]

    required_codes = [
        des.WEATHER,
        des.SEACNDS,
        des.RWYFRCTN,
        des.RWYCNTMS,
        des.RWYDEPST,
        des.RECENTWX,
        des.CVCTNCLDS,
        des.CLDAMTS,
    ]
    deu.parseCodeRegistryTables(des.CodesFilePath, required_codes)
    _CODES_INITIALIZED = True


def ensure_gifts_importable() -> None:
    """Add ``GIFTs/`` to ``sys.path`` when present."""
    if not GIFTS_ROOT.is_dir():
        msg = f"GIFTs directory not found at {GIFTS_ROOT} (required for TC-M003)"
        raise FileNotFoundError(msg)
    gifts_path = str(GIFTS_ROOT)
    if gifts_path not in sys.path:
        sys.path.insert(0, gifts_path)


def convert_tac_bulletin_to_observation_xml(tac_bulletin: str) -> str:
    """Decode and encode a WMO bulletin TAC; return observation element XML.

    Args:
        tac_bulletin: Full bulletin text (header + METAR/SPECI + trailing ``=``).

    Returns:
        Serialized ``iwxxm:observation`` element XML string.

    Raises:
        FileNotFoundError: When ``GIFTs/`` is absent.
        RuntimeError: When decode/encode fails.
    """
    ensure_gifts_importable()
    _initialize_gifts_code_registry()

    try:
        from gifts import metarDecoder, metarEncoder  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ImportError(
            "GIFTs import failed — install GIFTs runtime deps (skyfield, lxml) "
            "or run from an environment with packages/gifts wired."
        ) from exc

    decoder = metarDecoder.Annex3()
    encoder = metarEncoder.Annex3()

    decoded = decoder(tac_bulletin)
    if "err_msg" in decoded:
        raise RuntimeError(f"GIFTs decode failed: {decoded['err_msg']}")

    header_line = tac_bulletin.strip().split("\n")[0]
    decoded["translatedBulletinReceptionTime"] = FIXED_RECEPTION_TIME
    decoded["translatedBulletinID"] = header_line.replace(" ", "")

    encoded = encoder(decoded, tac_bulletin)
    if encoded is None or len(encoded) == 0:
        raise RuntimeError("GIFTs encoder returned empty result")

    observation = encoded[-1]
    if not hasattr(observation, "tag"):
        raise RuntimeError("GIFTs encoder did not return an XML element")

    return ET.tostring(observation, encoding="unicode")
