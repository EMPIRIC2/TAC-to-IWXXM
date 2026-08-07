"""F33 secure mass file/folder ingest — JWT-gated (EV-042 / #897).

[Corpus: product §F33] [Corpus: api]
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse

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
