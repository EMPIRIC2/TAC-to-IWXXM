"""Maintainable TAC lint issue registry (F15 / ADR-028).

Rules import ``IssueSpec`` rows via ``by_code`` / ``issue_from`` instead of inventing
severity or code string literals. Catalog export (``make catalog-regen``) iterates
``ISSUES``.
"""

from __future__ import annotations

import msgspec

from tac_validate.models import Issue


class IssueSpec(msgspec.Struct, frozen=True):
    """
    One registered lint issue definition.

    Parameters
    ----------
    code :
        Stable SCREAMING_SNAKE public id.
    severity :
        Default ``error``, ``warning``, or ``info``.
    message_template :
        Human message; may include ``str.format`` placeholders (e.g. ``{product}``).
    product :
        Optional product tag for catalog filtering (``None`` = shared / multi-product).
    tags :
        Optional catalog / FE tags (not part of the public code string).
    """

    code: str
    severity: str
    message_template: str
    product: str | None = None
    tags: tuple[str, ...] = ()


def _row(
    code: str,
    severity: str,
    message_template: str,
    *,
    product: str | None = None,
    tags: tuple[str, ...] = (),
) -> IssueSpec:
    return IssueSpec(
        code=code,
        severity=severity,
        message_template=message_template,
        product=product,
        tags=tags,
    )


# Seed: every code currently emitted by rules.py / product_rules.py (T1.2).
ISSUES: tuple[IssueSpec, ...] = (
    _row(
        "UNKNOWN_PRODUCT",
        "error",
        "Unknown product {product!r}; expected one of {expected}",
        tags=("parse_gate",),
    ),
    _row(
        "EMPTY_TAC",
        "error",
        "TAC text is empty",
        tags=("parse_gate", "body"),
    ),
    _row(
        "MISSING_PRODUCT_KEYWORD",
        "error",
        "{product} TAC must contain one of {keywords}",
        tags=("parse_gate", "header"),
    ),
    _row(
        "MISSING_TERMINATOR",
        "info",
        "Reports in bulletins end with '=' — add it before publishing",
        tags=("terminator", "metar", "speci", "taf"),
    ),
    _row(
        "MISSING_CCCC",
        "error",
        "{product} missing ICAO location (CCCC)",
        tags=("station", "metar", "speci", "taf"),
    ),
    _row(
        "MISSING_OBS_TIME",
        "error",
        "{product} missing observation time ddhhmmZ — A3-2 #3",
        tags=("time", "metar", "speci"),
    ),
    _row(
        "ODD_FIELD_ORDER",
        "warning",
        "{product} groups out of A3-2 order (CCCC → ddhhmmZ → wind)",
        tags=("order", "station", "time", "metar", "speci", "r1"),
    ),
    _row(
        "MISSING_WIND",
        "error",
        "{product} missing surface wind group — A3-2 #5",
        tags=("wind", "metar", "speci"),
    ),
    _row(
        "MISSING_VISIBILITY",
        "error",
        "{product} missing visibility or CAVOK — A3-2 #6",
        tags=("visibility", "metar", "speci"),
    ),
    _row(
        "INVALID_VISIBILITY",
        "error",
        "{product} invalid visibility token (use SM, meters, or CAVOK)",
        tags=("visibility", "metar", "speci", "r2"),
    ),
    _row(
        "INVALID_WEATHER",
        "error",
        "{product} invalid present weather token {token!r} — A3-2 #8",
        tags=("weather", "metar", "speci", "r3"),
    ),
    _row(
        "MISSING_TEMP_DEWPOINT",
        "error",
        "{product} missing temperature/dewpoint tt/td — A3-2 #10",
        tags=("temperature", "metar", "speci"),
    ),
    _row(
        "MISSING_QNH",
        "error",
        "{product} missing QNH/altimeter (Qnnnn/Annnn) — A3-2 #11",
        tags=("pressure", "metar", "speci"),
    ),
    _row(
        "INVALID_CLOUD_TOKEN",
        "error",
        "{product} invalid cloud/VV token {token!r} — A3-2 #9",
        tags=("cloud", "metar", "speci", "r4"),
    ),
    _row(
        "CLOUD_CB_OR_TCU",
        "info",
        "{product} cloud group includes convective type CB/TCU",
        tags=("cloud", "metar", "speci", "r4", "cb", "tcu"),
    ),
    _row(
        "REMARK_US_EXTENSION",
        "info",
        "{product} US remarks present — iwxxm_us profile awareness",
        tags=("remark", "metar", "speci", "r5", "iwxxm_us"),
    ),
    _row(
        "INVALID_REMARK",
        "error",
        "{product} malformed remark group {token!r}",
        tags=("remark", "metar", "speci", "r5", "iwxxm_us"),
    ),
    _row(
        "AUTO_PRESENT",
        "info",
        "{product} AUTO modifier present — research R8",
        tags=("modifier", "metar", "speci", "r8"),
    ),
    _row(
        "COR_PRESENT",
        "info",
        "{product} COR modifier present — research R8",
        tags=("modifier", "metar", "speci", "r8"),
    ),
    _row(
        "NIL_REPORT",
        "info",
        "{product} NIL report — research R8",
        tags=("nil", "metar", "speci", "r8"),
    ),
    _row(
        "INVALID_NIL",
        "error",
        "{product} NIL must not include body groups — research R8",
        tags=("nil", "metar", "speci", "r8"),
    ),
    _row(
        "NOSIG_PRESENT",
        "info",
        "{product} NOSIG trend present — research R8",
        tags=("trend", "metar", "speci", "r8"),
    ),
    _row(
        "TEMPO_PRESENT",
        "info",
        "{product} TEMPO trend present — research R8",
        tags=("trend", "metar", "speci", "r8"),
    ),
    _row(
        "RVR_PRESENT",
        "info",
        "{product} RVR group present — research R8",
        tags=("rvr", "metar", "speci", "r8"),
    ),
    _row(
        "INVALID_RVR",
        "error",
        "{product} invalid RVR token {token!r} — research R8",
        tags=("rvr", "metar", "speci", "r8"),
    ),
    _row(
        "WIND_VRB_OR_GUST",
        "info",
        "{product} wind uses VRB and/or gust — research R8",
        tags=("wind", "metar", "speci", "r8"),
    ),
    _row(
        "INVALID_WIND",
        "error",
        "{product} invalid wind token {token!r} — research R8",
        tags=("wind", "metar", "speci", "r8"),
    ),
    _row(
        "MISSING_ISSUE_TIME",
        "error",
        "TAF missing issue time ddhhmmZ — A5-1 #3",
        product="taf",
        tags=("time", "taf"),
    ),
    _row(
        "MISSING_VALIDITY",
        "error",
        "TAF missing validity period ddhh/ddhh — A5-1 #5",
        product="taf",
        tags=("validity", "taf"),
    ),
    _row(
        "INVALID_CNL_SHAPE",
        "error",
        "TAF CNL must end the message — A5-1 #6",
        product="taf",
        tags=("cnl", "taf"),
    ),
    _row(
        "MISSING_VALID",
        "error",
        "{product} missing VALID ddhhmm/ddhhmm period — A6 identity",
        tags=("valid", "sigmet", "airmet"),
    ),
    _row(
        "MULTIPLE_PHENOMENA",
        "error",
        "{product} encodes multiple phenomenon families {hit} — A6 one-phenomenon gate",
        tags=("phenomenon", "sigmet", "airmet"),
    ),
    _row(
        "MISSING_DTG",
        "error",
        "{product} missing DTG: template field",
        tags=("dtg", "vaa", "tca"),
    ),
    _row(
        "MISSING_VAAC",
        "error",
        "VAA missing VAAC: template field — A2-1",
        product="vaa",
        tags=("vaac", "vaa"),
    ),
    _row(
        "MISSING_MAX_WIND",
        "error",
        "TCA missing MAX WIND: template field — A2-2",
        product="tca",
        tags=("max_wind", "tca"),
    ),
)

_BY_CODE: dict[str, IssueSpec] = {spec.code: spec for spec in ISSUES}


def by_code(code: str) -> IssueSpec:
    """
    Return the registered ``IssueSpec`` for ``code``.

    Parameters
    ----------
    code :
        Public issue code.

    Returns
    -------
    IssueSpec
        Registry row.

    Raises
    ------
    KeyError
        If ``code`` is not registered.
    """
    try:
        return _BY_CODE[code]
    except KeyError:
        raise KeyError(f"unknown lint issue code: {code!r}") from None


def issue_from(
    code: str,
    *,
    message: str | None = None,
    location: str | None = None,
    start: int | None = None,
    end: int | None = None,
    **kwargs: object,
) -> Issue:
    """
    Build an ``Issue`` from a registry row.

    Parameters
    ----------
    code :
        Registered public code.
    message :
        Optional full message override (skips template formatting).
    location :
        Optional token / field hint.
    start, end :
        Optional character offsets into the TAC string.
    **kwargs :
        Passed to ``message_template.format`` when ``message`` is omitted.

    Returns
    -------
    Issue
        Structured finding using the registry default severity.

    Raises
    ------
    KeyError
        If ``code`` is not registered.
    """
    spec = by_code(code)
    if message is not None:
        text = message
    elif kwargs:
        text = spec.message_template.format(**kwargs)
    else:
        text = spec.message_template
    return Issue(
        severity=spec.severity,
        code=spec.code,
        message=text,
        location=location,
        start=start,
        end=end,
    )


__all__ = ["ISSUES", "IssueSpec", "by_code", "issue_from"]
