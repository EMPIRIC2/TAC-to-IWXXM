"""Project convert IR slots from a pack match.

This is the convert side of a match. It does not emit XML and does not import
``tac2iwxxm``. [Corpus: product §F9]
"""

from __future__ import annotations

from tac_decoding.match import MatchResult
from tac_decoding.models.ir import IrResidual, IrSpan, PackIr


def project_ir(
    match: MatchResult,
    *,
    product: str,
    pack_id: str,
) -> PackIr:
    """
    Build a pack IR dict beside the legacy parser IR.

    Parameters
    ----------
    match : MatchResult
        Result of :func:`tac_decoding.match.match_tac`.

    product : str
        Convert product id (for example ``METAR`` or ``SIGMET``).

    pack_id : str
        Pack that produced the match (``sigmet``, ``va_sigmet``, or ``tc_sigmet``
        for SIGMET).

    Returns
    -------
    PackIr
        Versioned IR projection. Callers keep legacy XML emit on the parser IR.
    """
    spans: list[IrSpan] = [
        {
            "rule_id": span.rule_id,
            "code": span.code,
            "start": span.start,
            "end": span.end,
            "explanation": span.explanation,
        }
        for span in match.spans
    ]
    residuals: list[IrResidual] = [
        {
            "code": span.code,
            "start": span.start,
            "end": span.end,
        }
        for span in match.residuals
    ]
    return {
        "ir_version": 1,
        "product": product.upper(),
        "pack_id": pack_id,
        "iwxxm_version": match.iwxxm_version,
        "profile": match.profile,
        "spans": spans,
        "residuals": residuals,
    }


__all__ = ["IrResidual", "IrSpan", "PackIr", "project_ir"]
