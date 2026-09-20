"""Map pack match spans into legacy convert IR slots.

Span IR stays in ``tac-decoding``. Slot mapping and emit live here.
[Corpus: adr/ADR-045]
"""

from __future__ import annotations

from typing import Any

from tac_decoding.match import MatchResult

from tac2iwxxm.products.metar_speci import parse_metar_speci

_ALLOWED_RESIDUALS = frozenset({"="})
_PACK_PRODUCTS = frozenset({"METAR", "SPECI"})


class PackIrMapError(ValueError):
    """Pack match cannot be mapped into convert IR slots."""


def map_spans_to_convert_ir(
    match: MatchResult,
    *,
    tac: str,
    product: str,
) -> dict[str, Any]:
    """
    Build convert IR from a pack match.

    Parameters
    ----------
    match :
        Result of ``tac_decoding.match.match_tac``.
    tac :
        Original TAC (used only for error context).
    product :
        ``METAR`` or ``SPECI``.

    Returns
    -------
    dict[str, Any]
        Legacy convert IR slots for annex3 / profile emitters.

    Raises
    ------
    PackIrMapError
        When residuals remain (other than ``=``), spans are empty, or the
        product is not supported for pack mapping.
    """
    product_u = product.upper()
    if product_u not in _PACK_PRODUCTS:
        msg = f"pack IR mapping not supported for product {product_u!r}"
        raise PackIrMapError(msg)
    bad = [span.code for span in match.residuals if span.code not in _ALLOWED_RESIDUALS]
    if bad:
        sample = bad[0]
        msg = f"pack match left residual {sample!r} in {tac!r}"
        raise PackIrMapError(msg)
    body_spans = [span for span in match.spans if span.rule_id != "equal"]
    if not body_spans:
        msg = "pack match produced no body spans"
        raise PackIrMapError(msg)
    rebuilt = " ".join(span.code for span in body_spans)
    try:
        return parse_metar_speci(rebuilt, product=product_u)
    except ValueError as exc:
        msg = f"pack spans could not fill convert slots: {exc}"
        raise PackIrMapError(msg) from exc
