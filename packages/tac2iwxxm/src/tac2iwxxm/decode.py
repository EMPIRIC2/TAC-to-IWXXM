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
from tac_decoding.decode import set_bulletin_splitter

__all__ = [
    "DecodeResidual",
    "DecodeResult",
    "DecodeSegment",
    "decode_tac",
]


def _split_for_decode(tac: str, product: str) -> object:
    """
    Internal helper ``_split_for_decode``.

    Parameters
    ----------
    tac : object
        Argument ``tac``.
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    from tac2iwxxm import bulletin as bulletin_mod

    try:
        return bulletin_mod.split_bulletin(tac, product=product)
    except bulletin_mod.BulletinSplitError:
        return None


set_bulletin_splitter(_split_for_decode)

sys.modules[__name__] = _impl
