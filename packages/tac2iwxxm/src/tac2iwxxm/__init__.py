"""General TAC → IWXXM converter (F6)."""

from __future__ import annotations

from tac2iwxxm.bulletin import (
    BulletinSplitError,
    bbb_to_report_status,
    format_ahl,
    iwxxm_filename,
    map_t1t2,
    parse_ahl,
    split_bulletin,
)
from tac2iwxxm.convert import ConvertError, convert
from tac2iwxxm.decode import DecodeResidual, DecodeResult, DecodeSegment, decode_tac
from tac2iwxxm.models import (
    AhlParts,
    BulletinMeta,
    BulletinSplit,
    ConvertIssue,
    ConvertResult,
)
from tac2iwxxm.native import rust_available, rust_module, scan_metar_tokens

__version__ = "0.2.4"

__all__ = [
    "AhlParts",
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
    "bbb_to_report_status",
    "convert",
    "decode_tac",
    "format_ahl",
    "iwxxm_filename",
    "map_t1t2",
    "parse_ahl",
    "rust_available",
    "rust_module",
    "scan_metar_tokens",
    "split_bulletin",
]
