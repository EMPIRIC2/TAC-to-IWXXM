"""Resolve convert IR source (legacy parser vs pack-IR path).

[Corpus: adr/ADR-045]
"""

from __future__ import annotations

import os
from typing import Literal

IrSource = Literal["legacy", "pack"]

IR_SOURCE_ENV = "TAC2IWXXM_CONVERT_IR_SOURCE"
# METAR/SPECI default to pack IR after EV-pack-ir-convert-wire flip (D-PACKIR-05).
_PACK_DEFAULT_PRODUCTS = frozenset({"METAR", "SPECI"})


def resolve_ir_source(
    product: str,
    *,
    ir_source: str | None = None,
) -> IrSource:
    """
    Choose legacy parser IR or pack-IR mapping.

    Parameters
    ----------
    product :
        Convert product id.
    ir_source :
        Explicit ``legacy``, ``pack``, or ``auto``. ``None`` reads the env
        (default ``auto``).

    Returns
    -------
    IrSource
        ``legacy`` or ``pack``.
    """
    raw = (ir_source if ir_source is not None else os.environ.get(IR_SOURCE_ENV, "auto")).strip().lower()
    if raw in {"legacy", "pack"}:
        return raw  # type: ignore[return-value]
    if raw not in {"", "auto"}:
        msg = f"ir_source must be legacy, pack, or auto, got {raw!r}"
        raise ValueError(msg)
    if product.upper() in _PACK_DEFAULT_PRODUCTS:
        return "pack"
    return "legacy"
