"""Part 3 of ``api_wire.py`` (line-cap split)."""

from __future__ import annotations

from fastapi import HTTPException, Request, UploadFile

from src.schemas.conversion import ConversionIssue, ConversionIssueSeverity, ErrorDetail
from tac2iwxxm import BulletinSplitError

from .api_wire_part_1 import (
    _AHL_HEADING_SPLIT_CODES,
    _BULLETIN_ID_RE,
    _CCCC_RE,
    _EMPTY_BULLETIN_MESSAGE,
    _INVALID_AHL_MESSAGE,
    _is_named_upload,
)


def parse_optional_bulletin_id(value: str | None) -> str:
    """
    Return uppercase bulletin id, or empty when omitted.

    Raises
    ------
    HTTPException
        400 when a non-empty value is not 4 letters + 2 digits.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (parse_optional_bulletin_id)
    2

    Parameters
    ----------
    value : object
        Argument ``value``.

    Returns
    -------
    object
        Return value.
    """
    raw = (value or "").strip().upper()
    if not raw:
        return ""
    if _BULLETIN_ID_RE.fullmatch(raw) is None:
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(
                message="Bulletin ID must be 4 letters followed by 2 digits.",
                errors=["bulletin_id"],
                issues=[
                    ConversionIssue(
                        source="request",
                        message="Bulletin ID must be 4 letters followed by 2 digits.",
                        severity=ConversionIssueSeverity.ERROR,
                        hint="Example: SAAA00. Leave blank to discover from the AHL or use defaults.",
                        code="INVALID_BULLETIN_ID",
                    )
                ],
                total_errors=1,
            ).model_dump(),
        )
    return raw


def parse_optional_issuing_center(value: str | None) -> str:
    """
    Return uppercase ICAO CCCC, or empty when omitted.

    Raises
    ------
    HTTPException
        400 when a non-empty value is not exactly 4 letters.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (parse_optional_issuing_center)
    2

    Parameters
    ----------
    value : object
        Argument ``value``.

    Returns
    -------
    object
        Return value.
    """
    raw = (value or "").strip().upper()
    if not raw:
        return ""
    if _CCCC_RE.fullmatch(raw) is None:
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(
                message="Issuing center must be a 4-letter ICAO code.",
                errors=["issuing_center"],
                issues=[
                    ConversionIssue(
                        source="request",
                        message="Issuing center must be a 4-letter ICAO code.",
                        severity=ConversionIssueSeverity.ERROR,
                        hint="Example: KWBC. Leave blank to discover from the AHL or use defaults.",
                        code="INVALID_ISSUING_CENTER",
                    )
                ],
                total_errors=1,
            ).model_dump(),
        )
    return raw


def _product_uses_aerodrome_icao_layer(product: str | None) -> bool:
    """
    True when the product carries an aerodrome ICAO designator (METAR/SPECI/TAF).

    Parameters
    ----------
    product : str | None
        Wire product id.

    Returns
    -------
    bool
        Whether Layer 1 AIRPORT_ICAO applies.
    """
    product_u = (product or "METAR").strip().upper()
    return product_u in {"METAR", "SPECI", "TAF"}


async def parse_optional_files(request: Request) -> list[UploadFile]:
    """
    Parse optional file uploads, filtering out empty strings from form data.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (parse_optional_files)
    2

    Parameters
    ----------
    request : object
        Argument ``request``.

    Returns
    -------
    object
        Return value.
    """
    form = await request.form()
    files_data = form.getlist("files")
    return [f for f in files_data if _is_named_upload(f)]


def bulletin_split_http_error(exc: BulletinSplitError) -> HTTPException:
    """
    Map a bulletin split failure to an operator-facing HTTP error.

    Malformed heading codes become ``INVALID_AHL`` with ``alias`` preserving the
    engine code. Empty body after a valid heading stays ``empty_bulletin``.

    Parameters
    ----------
    exc :
        Split failure from ``tac2iwxxm.split_bulletin``.

    Returns
    -------
    HTTPException
        400 for empty bulletins; 422 for malformed headings.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (bulletin_split_http_error)
    2
    """
    if exc.code == "empty_bulletin":
        return HTTPException(
            status_code=400,
            detail={"code": "empty_bulletin", "message": _EMPTY_BULLETIN_MESSAGE},
        )
    if exc.code in _AHL_HEADING_SPLIT_CODES:
        return HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_AHL",
                "alias": exc.code,
                "message": _INVALID_AHL_MESSAGE,
            },
        )
    return HTTPException(
        status_code=422,
        detail={"code": exc.code, "message": exc.message},
    )
