"""General TAC → IWXXM converter (F6)."""

from __future__ import annotations

from tac2iwxxm.bulletin import BulletinSplitError, split_bulletin
from tac2iwxxm.convert import ConvertError, convert
from tac2iwxxm.models import BulletinMeta, BulletinSplit, ConvertIssue, ConvertResult

__version__ = "0.1.0"

__all__ = [
    "BulletinMeta",
    "BulletinSplit",
    "BulletinSplitError",
    "ConvertError",
    "ConvertIssue",
    "ConvertResult",
    "__version__",
    "convert",
    "split_bulletin",
]
