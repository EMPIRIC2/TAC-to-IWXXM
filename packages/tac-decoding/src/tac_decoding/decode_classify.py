"""Token classification, residual coalesce, and summary.

[Corpus: product §F9]
"""

from __future__ import annotations

from collections.abc import Callable

from tac_decoding.decode_explain_advisory import (
    _explain_advisory,
)
from tac_decoding.decode_explain_metar import _explain_metar_speci
from tac_decoding.decode_explain_sigmet import _explain_sigmet_airmet
from tac_decoding.decode_explain_taf import _explain_taf
from tac_decoding.decode_patterns import *
from tac_decoding.models.decode_result import DecodeResidual, DecodeSegment


def _classify(
    product: str,
) -> Callable[[str, dict[str, int]], str | None]:
    """
    Internal helper ``_classify``.

    Parameters
    ----------
    product : str
        Argument ``product``.

    Returns
    -------
    Callable[[str, dict[str, int]], str | None]
        Return value.
    """
    if product in {"METAR", "SPECI"}:

        def _metar(tok: str, seen: dict[str, int]) -> str | None:
            """
            Internal helper ``_metar``.

            Parameters
            ----------
            tok : str
                Argument ``tok``.

            seen : dict[str, int]
                Argument ``seen``.

            Returns
            -------
            str | None
                Return value.
            """
            return _explain_metar_speci(tok, product=product, seen=seen)

        return _metar
    if product == "TAF":

        def _taf(tok: str, seen: dict[str, int]) -> str | None:
            """
            Internal helper ``_taf``.

            Parameters
            ----------
            tok : str
                Argument ``tok``.

            seen : dict[str, int]
                Argument ``seen``.

            Returns
            -------
            str | None
                Return value.
            """
            return _explain_taf(tok, seen=seen)

        return _taf
    if product in {"SIGMET", "AIRMET"}:

        def _haz(tok: str, seen: dict[str, int]) -> str | None:
            """
            Internal helper ``_haz``.

            Parameters
            ----------
            tok : str
                Argument ``tok``.

            seen : dict[str, int]
                Argument ``seen``.

            Returns
            -------
            str | None
                Return value.
            """
            return _explain_sigmet_airmet(tok, product=product, seen=seen)

        return _haz
    if product in _ADVISORY_STRUCTURED:

        def _adv(tok: str, seen: dict[str, int]) -> str | None:
            """
            Internal helper ``_adv``.

            Parameters
            ----------
            tok : str
                Argument ``tok``.

            seen : dict[str, int]
                Argument ``seen``.

            Returns
            -------
            str | None
                Return value.
            """
            return _explain_advisory(tok, product=product, seen=seen)

        return _adv

    def _none(_tok: str, _seen: dict[str, int]) -> str | None:
        """
        Internal helper ``_none``.

        Parameters
        ----------
        _tok : str
            Argument ``_tok``.

        _seen : dict[str, int]
            Argument ``_seen``.

        Returns
        -------
        str | None
            Return value.
        """
        return None

    return _none


def _coalesce_residuals(
    tokens: list[tuple[int, int, str]],
    explained: set[int],
    tac: str,
) -> list[DecodeResidual]:
    """
    Internal helper ``_coalesce_residuals``.

    Parameters
    ----------
    tokens : list[tuple[int, int, str]]
        Argument ``tokens``.

    explained : set[int]
        Argument ``explained``.

    tac : str
        Argument ``tac``.

    Returns
    -------
    list[DecodeResidual]
        Return value.
    """
    residuals: list[DecodeResidual] = []
    i = 0
    while i < len(tokens):
        if i in explained:
            i += 1
            continue
        start = tokens[i][0]
        end = tokens[i][1]
        j = i + 1
        while j < len(tokens) and j not in explained:
            # Include intervening whitespace in residual text span.
            end = tokens[j][1]
            j += 1
        residuals.append(DecodeResidual(start=start, end=end, text=tac[start:end]))
        i = j
    return residuals


_SPARSE_PRODUCTS = frozenset({"SIGMET", "AIRMET", "VAA", "TCA", "SWXA", "VONA"})


def _sentence_from_segment(seg: DecodeSegment) -> str | None:
    """
    Internal helper ``_sentence_from_segment``.

    Parameters
    ----------
    seg : DecodeSegment
        Argument ``seg``.

    Returns
    -------
    str | None
        Return value.
    """
    if seg.code == "=" or seg.explanation.lower().startswith("report terminator"):
        return None
    text = seg.explanation.strip()
    if not text:
        return None
    lower = text.lower()
    if "station location" in lower or (
        "location indicator" in lower and "fir" not in lower and "watch office" not in lower
    ):
        for sep in (" — ", " - "):
            if sep in text:
                place = text.split(sep, 1)[1].strip().rstrip(".")
                if place and not place.startswith("("):
                    return f"station {place} ({seg.code.upper()})"
                break
        return f"station {seg.code.upper()}"
    # Prefer the value-bearing half after an em dash when present.
    if " - " in text:
        left, right = text.split(" - ", 1)
        if left.lower().startswith("report type"):
            return text.rstrip(".")
        return right.rstrip(".")
    return text.rstrip(".")


def _build_summary(
    product: str,
    segments: list[DecodeSegment],
    residuals: list[DecodeResidual],
) -> str:
    """
    Build a deterministic plain-language paragraph for the decode panel (F9).

    Parameters
    ----------
    product : str
        Uppercase product id.

    segments : list[DecodeSegment]
        Value-aware decode segments.

    residuals : list[DecodeResidual]
        Undecoded spans; named in a trailing "Not decoded: …" clause.

    Returns
    -------
    str
        One flowing paragraph. Sparse products include "partial decode" wording.
    """
    clauses: list[str] = []
    for seg in segments:
        clause = _sentence_from_segment(seg)
        if clause and (not clauses or clauses[-1] != clause):
            clauses.append(clause)

    if product in _SPARSE_PRODUCTS:
        lead = f"{product} (partial decode)"
        body = "; ".join(clauses) if clauses else "few recognizable groups"
        paragraph = f"{lead}: {body}."
    elif clauses:
        # Lead with product when the first clause is the report type.
        paragraph = "; ".join(clauses) + "."
        paragraph = paragraph[0].upper() + paragraph[1:]
    else:
        paragraph = f"{product} report with no decoded groups."

    if residuals:
        residual_bits = " ".join(r.text for r in residuals)
        # Collapse whitespace for readable "Not decoded" naming.
        residual_bits = " ".join(residual_bits.split())
        paragraph = f"{paragraph} Not decoded: {residual_bits}."

    return paragraph
