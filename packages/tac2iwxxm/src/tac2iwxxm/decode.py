"""Compatibility shim — decode implementation lives in ``tac_decoding`` (ADR-044).

Replaces this module object with ``tac_decoding.decode`` so private helpers remain
importable for one release. Prefer ``from tac_decoding import decode_tac``.
"""

from __future__ import annotations

import sys

from tac_decoding import decode as _impl
from tac_decoding.decode import DecodeResidual as DecodeResidual
from tac_decoding.decode import DecodeResult as DecodeResult
from tac_decoding.decode import DecodeSegment as DecodeSegment
from tac_decoding.decode import decode_tac as decode_tac

__all__ = [
    "DecodeResidual",
    "DecodeResult",
    "DecodeSegment",
    "decode_tac",
]

sys.modules[__name__] = _impl
