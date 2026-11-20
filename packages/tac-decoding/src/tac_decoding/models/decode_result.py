"""Decode result msgspec models for the operator decode panel.

[Corpus: product §F9]
"""

from __future__ import annotations

import msgspec

from tac_decoding.models.remarks import RemarkGroup


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
    remarks : list[RemarkGroup]
        Structured RMK code groups for METAR/SPECI (F9). Default empty.
    """

    product: str
    segments: list[DecodeSegment] = msgspec.field(default_factory=list)
    residuals: list[DecodeResidual] = msgspec.field(default_factory=list)
    summary: str = ""
    remarks: list[RemarkGroup] = msgspec.field(default_factory=list)


__all__ = ["DecodeResidual", "DecodeResult", "DecodeSegment"]
