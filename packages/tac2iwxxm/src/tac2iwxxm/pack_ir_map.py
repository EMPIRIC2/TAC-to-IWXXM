"""Map pack match spans into convert IR slots.

Span IR stays in ``tac-decoding``. Slot builders (not ``products/*.py``) fill IR.
[Corpus: adr/ADR-045]
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from tac_decoding.match import MatchResult

from tac2iwxxm.slot_builders.metar_speci import parse_metar_speci
from tac2iwxxm.slot_builders.sigmet_airmet import parse_airmet, parse_sigmet
from tac2iwxxm.slot_builders.swxa import parse_swxa
from tac2iwxxm.slot_builders.taf import parse_taf
from tac2iwxxm.slot_builders.vaa_tca import parse_tca, parse_vaa
from tac2iwxxm.slot_builders.vona import parse_vona

_ALLOWED_RESIDUALS = frozenset({"="})
_TOKEN_STREAM_PRODUCTS = frozenset({"METAR", "SPECI", "TAF", "SIGMET", "AIRMET"})
_LABEL_PRODUCTS = frozenset({"VAA", "TCA", "SWXA", "VONA"})
_PACK_PRODUCTS = _TOKEN_STREAM_PRODUCTS | _LABEL_PRODUCTS
_VA_HINT = re.compile(r"\bVA\b")
_TC_HINT = re.compile(r"\bTC\b")

_PARSERS: dict[str, Callable[..., dict[str, Any]]] = {
    "METAR": parse_metar_speci,
    "SPECI": parse_metar_speci,
    "TAF": parse_taf,
    "SIGMET": parse_sigmet,
    "AIRMET": parse_airmet,
    "VAA": parse_vaa,
    "TCA": parse_tca,
    "SWXA": parse_swxa,
    "VONA": parse_vona,
}


class PackIrMapError(ValueError):
    """Pack match cannot be mapped into convert IR slots."""


def pack_id_for_product(product: str, tac: str) -> str:
    """
    Choose the builtin pack id for a convert product.

    Parameters
    ----------
    product :
        Convert product id (for example ``SIGMET``).
    tac :
        TAC text used to distinguish VA / TC SIGMET packs.

    Returns
    -------
    str
        Pack id such as ``metar`` or ``va_sigmet``.
    """
    product_u = product.upper()
    if product_u != "SIGMET":
        return product_u.lower()
    if _VA_HINT.search(tac.upper()):
        return "va_sigmet"
    if _TC_HINT.search(tac.upper()):
        return "tc_sigmet"
    return "sigmet"


def map_spans_to_convert_ir(
    match: MatchResult,
    *,
    tac: str,
    product: str,
) -> dict[str, Any]:
    """
    Build convert IR from a pack match without importing ``products/*.py``.

    Token-stream products must leave no residuals other than ``=``.
    Label-field products may leave unlabeled header / continuation residuals;
    convert IR is filled from the original TAC via slot builders.

    Parameters
    ----------
    match :
        Result of ``tac_decoding.match.match_tac``.
    tac :
        Original TAC.
    product :
        Convert product id.

    Returns
    -------
    dict[str, Any]
        Legacy convert IR slots for profile emitters.

    Raises
    ------
    PackIrMapError
        When the pack match is incomplete for the product layout, or the
        product is not supported for pack mapping.
    """
    product_u = product.upper()
    if product_u not in _PACK_PRODUCTS:
        msg = f"pack IR mapping not supported for product {product_u!r}"
        raise PackIrMapError(msg)

    if product_u in _LABEL_PRODUCTS:
        if not match.spans:
            msg = "label pack match produced no labeled spans"
            raise PackIrMapError(msg)
    else:
        bad = [span.code for span in match.residuals if span.code not in _ALLOWED_RESIDUALS]
        if bad:
            sample = bad[0]
            msg = f"pack match left residual {sample!r} in {tac!r}"
            raise PackIrMapError(msg)
        body_spans = [span for span in match.spans if span.rule_id != "equal"]
        if not body_spans:
            msg = "pack match produced no body spans"
            raise PackIrMapError(msg)

    parser = _PARSERS[product_u]
    try:
        return parser(tac, product=product_u)
    except ValueError as exc:
        msg = f"pack spans could not fill convert slots: {exc}"
        raise PackIrMapError(msg) from exc
