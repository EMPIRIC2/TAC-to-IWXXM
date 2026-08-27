"""F33 secure mass file/folder ingest — JWT-gated (EV-042 / #897).

[Corpus: product §F33] [Corpus: api]
"""

from __future__ import annotations

import logging
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse

from src import api as api_surface

from ..services.mass_ingest import (
    MassIngestCaps,
    MassIngestFileResult,
    evaluate_text_bytes,
    expand_zip_bytes,
)
from ..utilities.abuse_controls import (
    get_limiter,
    get_mass_ingest_max_file_bytes,
    get_mass_ingest_max_files,
    get_mass_ingest_max_total_bytes,
    mass_ingest_limit,
)
from ..utilities.security import verify_supabase_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["mass-ingest"])
_limiter = get_limiter()


def _caps() -> MassIngestCaps:
    return MassIngestCaps(
        max_files=get_mass_ingest_max_files(),
        max_file_bytes=get_mass_ingest_max_file_bytes(),
        max_total_bytes=get_mass_ingest_max_total_bytes(),
    )


def _result_payload(item: MassIngestFileResult) -> dict[str, Any]:
    return {
        "name": item.name,
        "accepted": item.accepted,
        "reason": item.reason,
        "size_bytes": item.size_bytes,
        "content": item.content if item.accepted else None,
    }


@router.post("/ingest/mass")
@mass_ingest_limit(_limiter)
async def mass_ingest(
    request: Request,
    files: list[UploadFile] = File(...),
    _user: dict[str, Any] = Depends(verify_supabase_token),
) -> JSONResponse:
    """
    Authenticated multi-file / zip ingest with caps, sniff, and zip-bomb guards.

    Parameters
    ----------
    request : Request
        Incoming request (slowapi).
    files : list[UploadFile] | None
        Multipart files and/or ``.zip`` archives.
    _user : dict[str, Any]
        Verified JWT claims (must include ``sub``).

    Returns
    -------
    JSONResponse
        Per-file accept/reject list and summary counts.
    """
    uploads = files
    if not uploads:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one file is required",
        )

    caps = _caps()
    results: list[MassIngestFileResult] = []
    total_bytes = 0

    for upload in uploads:
        name = upload.filename or "unnamed"
        data = await upload.read()
        lower = name.lower()
        if lower.endswith(".zip"):
            member_results = expand_zip_bytes(name, data, caps)
            results.extend(member_results)
            total_bytes += sum(r.size_bytes for r in member_results if r.accepted)
        else:
            one = evaluate_text_bytes(name, data, caps)
            results.append(one)
            if one.accepted:
                total_bytes += one.size_bytes

    if len(results) > caps.max_files:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Too many files after expansion (max {caps.max_files})",
        )
    if total_bytes > caps.max_total_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Accepted content exceeds {caps.max_total_bytes} bytes",
        )

    accepted = [r for r in results if r.accepted]
    rejected = [r for r in results if not r.accepted]
    logger.info(
        "mass_ingest user=%s accepted=%s rejected=%s",
        _user.get("sub"),
        len(accepted),
        len(rejected),
    )
    return JSONResponse(
        {
            "accepted_count": len(accepted),
            "rejected_count": len(rejected),
            "results": [_result_payload(r) for r in results],
        }
    )


@router.post(
    "/ingest-collect",
    tags=["Conversion"],
    responses={
        501: {"description": "COLLECT / FTBP ingest not implemented yet (placeholder)"},
    },
)
async def ingest_collect(
    request: Request,
    files: Optional[List[UploadFile]] = File(None),
    manual_text: str = Form(default="", description="COLLECT IWXXM XML or inflated gzip text"),
    profile: str = Form(default="annex3"),
    iwxxm_version: str = Form(default="2025-2"),
) -> dict[str, Any]:
    """Placeholder for IWXXM COLLECT / FTBP ingest.

    Accepts uploads (including ``.gz`` via ``read_upload_files_text``) so the operator UI
    can exercise the path; returns HTTP 501 until member extraction + validate is shipped.
    """
    content_type = (request.headers.get("content-type") or "").lower()
    if "multipart/form-data" not in content_type:
        raise HTTPException(
            status_code=415,
            detail="POST /api/v1/ingest-collect requires multipart/form-data",
        )

    payload = manual_text or ""
    if files:
        joined, err = await api_surface.read_upload_files_text(files)
        if err:
            raise HTTPException(status_code=400, detail={"code": "upload_rejected", "message": err})
        if joined:
            payload = joined

    if not payload.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "code": "empty_collect",
                "message": "At least one of files or manual_text is required",
            },
        )

    logger.info(
        "[INGEST-COLLECT] placeholder hit profile=%s version=%s bytes=%s",
        profile,
        iwxxm_version,
        len(payload),
    )
    raise HTTPException(
        status_code=501,
        detail={
            "code": "not_implemented",
            "message": (
                "IWXXM COLLECT / FTBP ingest is not implemented yet. "
                "Convert AHL TAC bulletins via POST /api/v1/convert-bulletin, "
                "or paste individual TAC reports into /api/v1/convert."
            ),
            "profile": profile,
            "iwxxm_version": iwxxm_version,
            "accepted_bytes": len(payload),
        },
    )
