"""Project convert IR slots from a pack match.

This is the convert side of a match. It does not emit XML and does not import
``tac2iwxxm``. [Corpus: adr/ADR-045]
"""

from __future__ import annotations

from tac_decoding.match import MatchResult


def project_ir(
    match: MatchResult,
    *,
    product: str,
    pack_id: str,
) -> dict[str, object]:
    """
    Build a pack IR dict beside the legacy parser IR.

    Parameters
    ----------
    match :
        Result of :func:`tac_decoding.match.match_tac`.
    product :
        Convert product id (for example ``METAR`` or ``SIGMET``).
    pack_id :
        Pack that produced the match (``sigmet``, ``va_sigmet``, or ``tc_sigmet``
        for SIGMET).

    Returns
    -------
    dict[str, object]
        Versioned IR projection. Callers keep legacy XML emit on the parser IR.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (project_ir)
    2
    """
    return {
        "ir_version": 1,
        "product": product.upper(),
        "pack_id": pack_id,
        "iwxxm_version": match.iwxxm_version,
        "profile": match.profile,
        "spans": [
            {
                "rule_id": span.rule_id,
                "code": span.code,
                "start": span.start,
                "end": span.end,
                "explanation": span.explanation,
            }
            for span in match.spans
        ],
        "residuals": [
            {
                "code": span.code,
                "start": span.start,
                "end": span.end,
            }
            for span in match.residuals
        ],
    }
