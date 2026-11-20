"""Pack IR projection TypedDicts.

[Corpus: product §F9]
"""

from __future__ import annotations

from typing import TypedDict


class IrSpan(TypedDict):
    """One matched span projected into pack IR."""

    rule_id: str
    code: str
    start: int
    end: int
    explanation: str


class IrResidual(TypedDict):
    """One residual span projected into pack IR."""

    code: str
    start: int
    end: int


class PackIr(TypedDict):
    """Versioned pack IR beside the legacy parser IR."""

    ir_version: int
    product: str
    pack_id: str
    iwxxm_version: str | None
    profile: str | None
    spans: list[IrSpan]
    residuals: list[IrResidual]


__all__ = ["IrResidual", "IrSpan", "PackIr"]
