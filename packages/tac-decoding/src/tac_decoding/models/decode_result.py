"""Decode result msgspec models for the operator decode panel.

[Corpus: product §F9]
"""

from __future__ import annotations

import msgspec


class DecodeSegment(msgspec.Struct, frozen=True):
    """
    One annotated TAC span for the Code | Explanation panel.

    Attributes
    ----------
    start : int
        Start.
    end : int
        End.
    code : str
        Machine-readable error code.
    explanation : str
        Explanation.
    """

    start: int
    end: int
    code: str
    explanation: str


class DecodeResidual(msgspec.Struct, frozen=True):
    """
    Undecoded character span (explicit residuals - G4).

    Attributes
    ----------
    start : int
        Start.
    end : int
        End.
    text : str
        Input text.
    """

    start: int
    end: int
    text: str


class DecodeResult(msgspec.Struct, frozen=True):
    """
    Result of :func:`decode_tac`.

    Attributes
    ----------
    product : str
        Product name.
    segments : list[DecodeSegment]
        Segments.
    residuals : list[DecodeResidual]
        Residuals.
    summary : str
        Summary. Default ``''``.
    """

    product: str
    segments: list[DecodeSegment] = msgspec.field(default_factory=list)
    residuals: list[DecodeResidual] = msgspec.field(default_factory=list)
    summary: str = ""


__all__ = ["DecodeResidual", "DecodeResult", "DecodeSegment"]
