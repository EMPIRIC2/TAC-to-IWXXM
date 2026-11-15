"""Part 2 of ``tac_quality.py`` (line-cap split)."""

from __future__ import annotations

from typing import Any

from fastapi import File, Form, HTTPException, Request, UploadFile
from fastapi.responses import Response
from tac_validate.api import lint_with_profile
from tac_validate.profiles import PROFILE_ANNEX3

from src import api as api_surface
from src.schemas.airport import get_airport_validator
from src.schemas.validation import (
    LintFixModel,
    LintIssueModel,
    LintTacResponse,
)
from src.utilities.iwxxm_pass_through import lint_iwxxm_pass_through
from tac2iwxxm import decode_tac as tac2iwxxm_decode_tac


async def lint_tac(
    request: Request,
    manual_text: str = Form(default="", description="TAC or IWXXM XML to lint"),
    product: str = Form(
        default="METAR",
        description="Product type, or iwxxm for XML lint (default METAR)",
    ),
    semantic_profile: str = Form(
        default=PROFILE_ANNEX3,
        description="Semantic / lint profile id (default annex3)",
    ),
    icao: str = Form(
        default="",
        description="Optional station ICAO; TAF auto-detects when omitted",
    ),
    files: list[UploadFile] | None = File(None),
) -> Response:
    """
    Lint TAC or IWXXM XML. The body must be multipart form data.


    Examples
    --------
    >>> 1 + 1  # docstring smoke (lint_tac)
    2

    Parameters
    ----------
    request : object
        Argument ``request``.
    manual_text : object
        Argument ``manual_text``.
    product : object
        Argument ``product``.
    files : object
        Argument ``files``.

    Returns
    -------
    object
        Return value.
    """
    content_type = (request.headers.get("content-type") or "").lower()
    if "multipart/form-data" not in content_type:
        raise HTTPException(
            status_code=415,
            detail="POST /api/v1/lint-tac requires multipart/form-data",
        )

    tac_text = manual_text or ""
    if files:
        joined, err = await api_surface.read_upload_files_text(files)
        if err:
            raise HTTPException(status_code=400, detail={"code": "upload_rejected", "message": err})
        if joined:
            tac_text = joined

    product_u = api_surface.normalize_api_product(product, default="METAR")
    if product_u == "IWXXM":
        report = lint_iwxxm_pass_through(tac_text)
        return api_surface.msgspec_json_response(
            LintTacResponse(
                ok=report.ok,
                product=report.product,
                issues=[
                    LintIssueModel(
                        severity=i.severity,
                        code=i.code,
                        message=i.message,
                        location=i.location,
                        start=i.start,
                        end=i.end,
                    )
                    for i in report.issues
                ],
                fixes=[],
            )
        )
    # Direct unit calls may leave FastAPI Form defaults unbound.
    profile_raw = semantic_profile if type(semantic_profile) is str else PROFILE_ANNEX3
    icao_raw = icao if type(icao) is str else ""
    profile = (profile_raw or PROFILE_ANNEX3).strip() or PROFILE_ANNEX3
    station = (icao_raw or "").strip() or None
    try:
        from tac2iwxxm.profile_registry import resolve_semantic_profile

        resolved = resolve_semantic_profile(profile)
        profile_key = resolved.emit_key if resolved is not None else profile
    except Exception:
        profile_key = profile
    try:
        report = lint_with_profile(
            tac_text,
            product=product_u,
            profile=profile_key,
            icao=station,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "invalid_semantic_profile", "message": str(exc)},
        ) from exc
    lint_issues = [
        LintIssueModel(
            severity=i.severity,
            code=i.code,
            message=i.message,
            location=i.location,
            start=getattr(i, "start", None),
            end=getattr(i, "end", None),
        )
        for i in report.issues
    ]
    # Pipeline overlay: decode residuals → PARTIAL_DECODE warning.
    # Emit at API orchestration — not from the pack engine.
    # Skip WMO AHL bulletins: whole-blob decode treats sibling reports as
    # residuals; convert-bulletin maps residuals per contained report instead.
    from tac_validate.issue_registry import issue_from as lint_issue_from

    from tac2iwxxm import BulletinSplitError, split_bulletin

    try:
        split_bulletin(tac_text, product=product_u)
        is_ahl_bulletin = True
    except BulletinSplitError:
        is_ahl_bulletin = False

    if not is_ahl_bulletin:
        decoded = tac2iwxxm_decode_tac(tac_text, product=product_u)
        residual_spans = [r for r in decoded.residuals if getattr(r, "text", None) and str(r.text).strip()]
        if residual_spans and not any(i.code == "PARTIAL_DECODE" for i in lint_issues):
            partial = lint_issue_from(
                "PARTIAL_DECODE",
                start=residual_spans[0].start,
                end=residual_spans[-1].end,
                location="decode",
            )
            lint_issues.append(
                LintIssueModel(
                    severity=partial.severity,
                    code=partial.code,
                    message=partial.message,
                    location=partial.location,
                    start=partial.start,
                    end=partial.end,
                )
            )
    return api_surface.msgspec_json_response(
        LintTacResponse(
            ok=report.ok,
            product=report.product,
            issues=lint_issues,
            fixes=[LintFixModel(code=f.code, message=f.message, replacement=f.replacement) for f in report.fixes],
        )
    )


def station_point(icao: str) -> dict[str, Any]:
    """
    Return the map point for one station ID.

    The airport catalog is already loaded for ICAO checks. This reads that
    one record. It does not call an external map service.


    Parameters
    ----------
    icao :
        Four-character station location indicator.

    Returns
    -------
    dict[str, Any]
        ICAO code, name, and decimal degrees. Unknown codes return null
        coordinates so a map lookup is a normal miss, not an error response.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (station_point)
    2
    """
    code = icao.strip().upper()
    if len(code) != 4 or not code.isalnum() or not code[0].isalpha():
        return {"icao": code, "name": None, "latitude": None, "longitude": None}
    airport = get_airport_validator().get_airport(code)
    coordinates = None if airport is None else airport.coordinates
    if airport is None or coordinates is None:
        return {"icao": code, "name": None, "latitude": None, "longitude": None}
    return {
        "icao": airport.icao,
        "name": airport.name,
        "latitude": coordinates.latitude,
        "longitude": coordinates.longitude,
    }
