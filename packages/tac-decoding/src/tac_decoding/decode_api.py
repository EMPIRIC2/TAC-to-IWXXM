"""Public decode entrypoints and bulletin orchestration.

[Corpus: product §F9]
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import cast

from tac_decoding.decode_advisory_fields import (
    _iter_advisory_fields,
    _token_indices_covering,
)
from tac_decoding.decode_classify import (
    _build_summary,
    _classify,
    _coalesce_residuals,
)
from tac_decoding.decode_explain_advisory import (
    _AHL_LINE,
    _iter_advisory_ahl,
    _iter_ahl_heading,
)
from tac_decoding.decode_fir import _extend_fir_name_span
from tac_decoding.decode_patterns import *
from tac_decoding.decode_tokens import _iter_tokens, _spaced_cavok_span, _whole_miles
from tac_decoding.models.bulletin import _BulletinSplit
from tac_decoding.models.decode_result import DecodeResidual, DecodeResult, DecodeSegment

_bulletin_splitter: Callable[[str, str], object] | None = None


def _looks_like_ahl_bulletin(text: str) -> bool:
    """
    Internal helper ``_looks_like_ahl_bulletin``.

    Parameters
    ----------
    text : str
        Argument ``text``.

    Returns
    -------
    bool
        Return value.
    """
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        return _AHL_LINE.match(stripped) is not None
    return False


def _shift_decode(result: DecodeResult, offset: int) -> DecodeResult:
    """
    Internal helper ``_shift_decode``.

    Parameters
    ----------
    result : DecodeResult
        Argument ``result``.

    offset : int
        Argument ``offset``.

    Returns
    -------
    DecodeResult
        Return value.
    """
    return DecodeResult(
        product=result.product,
        segments=[
            DecodeSegment(
                start=s.start + offset,
                end=s.end + offset,
                code=s.code,
                explanation=s.explanation,
            )
            for s in result.segments
        ],
        residuals=[
            DecodeResidual(
                start=r.start + offset,
                end=r.end + offset,
                text=r.text,
            )
            for r in result.residuals
            if r.text.strip()
        ],
        summary=result.summary,
    )


def set_bulletin_splitter(splitter: Callable[[str, str], object] | None) -> None:
    """
    Inject WMO bulletin splitting. Unset means bulletins are not split.

    Parameters
    ----------
    splitter : Callable[[str, str], object] | None
        Callable that splits a bulletin into TAC reports.
    """
    global _bulletin_splitter
    _bulletin_splitter = splitter


def _decode_bulletin(tac: str, *, product: str) -> DecodeResult | None:
    """
    Internal helper ``_decode_bulletin``.

    Parameters
    ----------
    tac : str
        Argument ``tac``.

    product : str
        Argument ``product``.

    Returns
    -------
    DecodeResult | None
        Return value.
    """
    if not _looks_like_ahl_bulletin(tac):
        return None
    if _bulletin_splitter is None:
        return None
    split_obj = _bulletin_splitter(tac, product)
    if split_obj is None:
        return None
    split = cast(_BulletinSplit, split_obj)

    segments: list[DecodeSegment] = []
    for start, end, code, explanation in _iter_ahl_heading(tac):
        segments.append(DecodeSegment(start=start, end=end, code=code, explanation=explanation))

    residuals: list[DecodeResidual] = []
    summaries: list[str] = []
    search_from = 0
    for report in split.reports:
        pos = tac.find(report, search_from)
        if pos < 0:
            pos = tac.find(report)
        if pos < 0:
            pos = 0
        inner = _shift_decode(_decode_single_report(report, product=product), pos)
        segments.extend(inner.segments)
        residuals.extend(inner.residuals)
        if inner.summary:
            summaries.append(inner.summary.rstrip("."))
        search_from = pos + len(report)

    segments.sort(key=lambda s: (s.start, s.end))
    n = split.meta.report_count
    numbered = " ".join(f"{i + 1}) {clause}." for i, clause in enumerate(summaries))
    summary = f"Bulletin {split.meta.ahl} ({n} report{'s' if n != 1 else ''}). {numbered}".strip()
    return DecodeResult(product=product, segments=segments, residuals=residuals, summary=summary)


def _decode_single_report(tac: str, *, product: str) -> DecodeResult:
    """
    Internal helper ``_decode_single_report``.

    Parameters
    ----------
    tac : str
        Argument ``tac``.

    product : str
        Argument ``product``.

    Returns
    -------
    DecodeResult
        Return value.
    """
    tokens = _iter_tokens(tac)
    classify = _classify(product)
    seen: dict[str, int] = {}
    segments: list[DecodeSegment] = []
    explained: set[int] = set()

    if product in {"SIGMET", "AIRMET"}:
        heading = _LOOSE_AHL.match(tac.lstrip("\ufeff"))
        if heading is not None:
            lead = len(tac) - len(tac.lstrip("\ufeff"))
            start = lead + heading.start()
            end = lead + heading.end()
            segments.append(
                DecodeSegment(
                    start=start,
                    end=end,
                    code=tac[start:end],
                    explanation=(
                        f"Abbreviated heading {heading.group('ahl')} from "
                        f"{heading.group('cccc')} at {heading.group('yygggg')}"
                    ),
                )
            )
            for idx, (token_start, token_end, _token) in enumerate(tokens):
                if token_start >= start and token_end <= end:
                    explained.add(idx)

    # Advisory products: structured LABEL: value fields first (EV-030 / EV-099).
    if product in _ADVISORY_STRUCTURED:
        field_spans: list[tuple[int, int]] = []
        for start, end, code, explanation in _iter_advisory_ahl(tac, product=product):
            segments.append(DecodeSegment(start=start, end=end, code=code, explanation=explanation))
            field_spans.append((start, end))
        label_starts: list[int] = []
        for mark_start, mark_end, code, explanation, label_start in _iter_advisory_fields(tac, product=product):
            segments.append(DecodeSegment(start=mark_start, end=mark_end, code=code, explanation=explanation))
            field_spans.append((label_start, mark_end))
            label_starts.append(label_start)
        explained |= _token_indices_covering(tokens, field_spans)
        if label_starts:
            first_label = min(label_starts)
            for idx, (_token_start, token_end, _token) in enumerate(tokens):
                if token_end <= first_label:
                    explained.add(idx)

    for idx, (start, end, token) in enumerate(tokens):
        if idx in explained:
            continue
        # Spaced CAVOK (TAF live typo) — consume five single-letter tokens.
        if product == "TAF":
            cavok_span = _spaced_cavok_span(tokens, idx)
            if cavok_span is not None:
                cavok_start, cavok_end = cavok_span
                segments.append(
                    DecodeSegment(
                        start=cavok_start,
                        end=cavok_end,
                        code=tac[cavok_start:cavok_end],
                        explanation="Ceiling and visibility OK",
                    )
                )
                explained.update(range(idx, idx + 5))
                continue
        # Annex 3 runway wind shear: WS + bare R{nn}[LCR]?
        if product in {"METAR", "SPECI"} and token.upper() == "WS" and idx + 1 < len(tokens):
            _next_start, next_end, next_tok = tokens[idx + 1]
            if _WS_RUNWAY.fullmatch(next_tok.upper()) and (idx + 1) not in explained:
                rw = next_tok.upper()[1:]
                segments.append(
                    DecodeSegment(
                        start=start,
                        end=next_end,
                        code=f"{token} {next_tok}",
                        explanation=f"Wind shear on runway {rw}",
                    )
                )
                explained.add(idx)
                explained.add(idx + 1)
                continue
        # US convective SIGMET: ``1 IN...WIND`` / ``2 IN...WIND`` — digit precedes
        # the ellipsis token, so arm hail-size before single-token classify.
        if (
            product in {"SIGMET", "AIRMET"}
            and token.isdigit()
            and len(token) <= 2
            and idx + 1 < len(tokens)
            and (idx + 1) not in explained
        ):
            next_tok = tokens[idx + 1][2]
            next_u = next_tok.upper().rstrip(":")
            if re.search(r"(?<!\.)\.$", next_u):
                next_u = next_u[:-1]
            if _IN_WIND_ELLIPSIS.match(next_u):
                seen["hail_size"] = 1
        explanation = classify(token, seen)
        if explanation is None and product in {"METAR", "SPECI", "TAF"}:
            following = tokens[idx + 1][2] if idx + 1 < len(tokens) else ""
            explanation = _whole_miles(token, following)
        if explanation is None:
            continue
        # Multi-word FIR proper names (NEW YORK, LA PAZ, KOTA KINABALU).
        if (
            product in {"SIGMET", "AIRMET"}
            and explanation.startswith("FIR name (")
            and (span := _extend_fir_name_span(tokens, idx, tac=tac)) is not None
        ):
            span_start, span_end, span_code, span_expl, span_n = span
            segments.append(
                DecodeSegment(
                    start=span_start,
                    end=span_end,
                    code=span_code,
                    explanation=span_expl,
                )
            )
            explained.update(range(idx, idx + span_n))
            continue
        segments.append(
            DecodeSegment(
                start=start,
                end=end,
                code=token,
                explanation=explanation,
            )
        )
        explained.add(idx)

    segments.sort(key=lambda s: (s.start, s.end))
    residuals = _coalesce_residuals(tokens, explained, tac)
    summary = _build_summary(product, segments, residuals)
    return DecodeResult(product=product, segments=segments, residuals=residuals, summary=summary)


def decode_single_report(tac: str, *, product: str) -> DecodeResult:
    """
    Decode one TAC report without bulletin or COLLECT dispatch.

    Parameters
    ----------
    tac : str
        TAC text.

    product : str
        Product name.

    Returns
    -------
    DecodeResult
        Decode one TAC report without bulletin or COLLECT dispatch.
    """
    return _decode_single_report(tac, product=product)


def shift_decode(result: DecodeResult, offset: int) -> DecodeResult:
    """
    Translate segment offsets into a parent document string.

    Parameters
    ----------
    result : DecodeResult
        Decode result whose spans are shifted.

    offset : int
        Character offset added to spans.

    Returns
    -------
    DecodeResult
        Translate segment offsets into a parent document string.
    """
    return _shift_decode(result, offset)


def _leading_report_product(tac: str) -> str | None:
    """
    Return the product keyword when the report itself starts with one.

    Parameters
    ----------
    tac : str
        Raw TAC text.

    Returns
    -------
    str | None
        Supported product id, or None when the first word is not one.
    """
    for line in tac.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        first = stripped.split(None, 1)[0].upper().rstrip(":")
        if first in _SUPPORTED:
            return first
        return None
    return None


def decode_tac(tac: str, *, product: str) -> DecodeResult:
    """
    Decode TAC text into ordered explanation segments and residuals.

    Parameters
    ----------
    tac : str
        Raw TAC report text, a WMO AHL bulletin, or COLLECT / IWXXM XML with
        contained TAC or leaf fields.

    product : str
        One of the F6 product ids or ``SWXA`` (case-insensitive).

    Returns
    -------
    DecodeResult
        ``segments`` for recognized groups; ``residuals`` for undecoded spans;
        ``summary`` plain-language paragraph (F9).
        METAR/SPECI/TAF aim for rich segments; VAA/TCA/SWXA/VONA use structured
        LABEL fields (EV-030 / EV-099) with explicit residuals for leftovers (G4).
        Multi-report AHL bulletins are split so each report is decoded independently
        (heading is a bulletin-framing segment, not a product residual).
        COLLECT documents decode contained TAC when present, otherwise walk XML
        fields.
    """
    product_u = product.upper()
    if product_u in _SUPPORTED:
        leading = _leading_report_product(tac)
        if leading is not None:
            product_u = leading
    if product_u not in _SUPPORTED:
        # Entire body residual - unknown product still returns a well-formed shape.
        text = tac
        residuals = [DecodeResidual(start=0, end=len(text), text=text)] if text else []
        summary = _build_summary(product_u, [], residuals)
        return DecodeResult(product=product_u, segments=[], residuals=residuals, summary=summary)

    from tac_decoding.collect import try_decode_collect

    collected = try_decode_collect(tac, product=product_u)
    if collected is not None:
        return collected

    bulletin = _decode_bulletin(tac, product=product_u)
    if bulletin is not None:
        return bulletin
    return _decode_single_report(tac, product=product_u)


__all__ = [
    "DecodeResidual",
    "DecodeResult",
    "DecodeSegment",
    "decode_tac",
]
