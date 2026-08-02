"""General TAC → IWXXM converter (F6)."""

from __future__ import annotations

from tac2iwxxm.bulletin import BulletinSplitError, split_bulletin
from tac2iwxxm.convert import ConvertError, convert
from tac2iwxxm.decode import DecodeResidual, DecodeResult, DecodeSegment, decode_tac
from tac2iwxxm.models import BulletinMeta, BulletinSplit, ConvertIssue, ConvertResult
from tac2iwxxm.native import rust_available, rust_module, scan_metar_tokens

__version__ = "0.1.1"

__all__ = [
    "BulletinMeta",
    "BulletinSplit",
    "BulletinSplitError",
    "ConvertError",
    "ConvertIssue",
    "ConvertResult",
    "DecodeResidual",
    "DecodeResult",
    "DecodeSegment",
    "__version__",
    "convert",
    "decode_tac",
    "rust_available",
    "rust_module",
    "scan_metar_tokens",
    "split_bulletin",
]
