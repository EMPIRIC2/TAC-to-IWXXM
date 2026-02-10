"""Standalone backend API module for Docker deployment."""
from __future__ import annotations

import os
import io
import pathlib
import zipfile
import datetime
import sys
from typing import List

# Add src directory to path for imports (for local uvicorn execution)
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

try:
    # Try relative imports first (when run as module in Docker)
    from .utilities.conversion import convert_metar_tac, ConversionError
    from .utilities.security import verify_supabase_token
    from .schemas.conversion import (
        ConversionResult,
        ConversionResponse,
        ErrorDetail,
        HealthResponse,
    )
except ImportError:
    # Fall back to direct imports (when sys.path is set for local development)
    from utilities.conversion import convert_metar_tac, ConversionError
    from utilities.security import verify_supabase_token
    from schemas.conversion import (
        ConversionResult,
        ConversionResponse,
        ErrorDetail,
        HealthResponse,
    )

app = FastAPI(
    title="METAR to IWXXM Backend API",
    version="0.1.0",
    description="Convert METAR/SPECI TAC messages to IWXXM XML format (backend only)",
)

# Restrict CORS to specific origins
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:8000")
allowed_origins = [
    frontend_url,
    "http://localhost:3000",  # Vite dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health() -> HealthResponse:
    """Check API health and GIFTs availability."""
    try:
        test_metar = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
        _ = convert_metar_tac(test_metar)
        gifts_available = True
        status = "healthy"
    except Exception:
        gifts_available = False
        status = "degraded"
    return HealthResponse(status=status, version="0.1.0", gifts_available=gifts_available)


@app.post("/api/v1/convert", response_model=ConversionResponse, tags=["Conversion"])
async def convert(
    files: List[UploadFile] = File(default=[], description="METAR TAC files"),
    manual_text: str = Form(default="", description="Manual METAR text"),
    user: dict = Depends(verify_supabase_token),
) -> ConversionResponse:
    """Convert METAR/SPECI TAC text to IWXXM XML.

    Accepts manual text input and/or file uploads. Requires valid Supabase JWT token.
    
    **Endpoint**: `/api/v1/convert`
    """
    results: List[ConversionResult] = []
    errors: List[str] = []
    total_inputs = 0

    if manual_text.strip():
        total_inputs += 1
        try:
            xml_text = convert_metar_tac(manual_text.strip())
            results.append(
                ConversionResult(
                    name="manual_input.txt",
                    content=xml_text,
                    source="manual",
                    size_bytes=len(xml_text.encode("utf-8")),
                )
            )
        except ConversionError as e:
            errors.append(f"manual_input: {e}")

    for uf in files:
        total_inputs += 1
        try:
            data = (await uf.read()).decode("utf-8", errors="ignore")
            if not data.strip():
                errors.append(f"{uf.filename}: empty file")
                continue
            xml_text = convert_metar_tac(data)
            out_name = pathlib.Path(uf.filename or "unknown").stem + ".txt"
            results.append(
                ConversionResult(
                    name=out_name,
                    content=xml_text,
                    source=uf.filename,
                    size_bytes=len(xml_text.encode("utf-8")),
                )
            )
        except ConversionError as e:
            errors.append(f"{uf.filename}: {e}")
        except Exception as e:
            errors.append(f"{uf.filename}: unexpected error {e}")

    if not results and errors:
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(
                message="All conversions failed", errors=errors, total_errors=len(errors)
            ).model_dump(),
        )

    return ConversionResponse(
        results=results,
        errors=errors,
        total_processed=total_inputs,
        successful=len(results),
        failed=len(errors),
    )


@app.post("/api/v1/convert-zip", response_class=StreamingResponse, tags=["Conversion"])
async def convert_zip(
    files: List[UploadFile] = File(default=[]),
    manual_text: str = Form(default=""),
    user: dict = Depends(verify_supabase_token),
) -> StreamingResponse:
    """Convert METAR/SPECI TAC inputs to zipped IWXXM XML files.

    Requires valid Supabase JWT token. Returns a ZIP file containing output XML
    files and an errors.txt file if any conversions failed.
    
    **Endpoint**: `/api/v1/convert-zip`
    """
    results: List[tuple[str, str]] = []
    errors: List[str] = []

    if manual_text.strip():
        try:
            xml_text = convert_metar_tac(manual_text.strip())
            results.append(("manual_input.xml", xml_text))
        except ConversionError as e:
            errors.append(f"manual_input: {e}")

    for uf in files:
        try:
            data = (await uf.read()).decode("utf-8", errors="ignore").strip()
            if not data:
                errors.append(f"{uf.filename}: empty file")
                continue
            xml_text = convert_metar_tac(data)
            fname = pathlib.Path(uf.filename or "unknown").stem + ".xml"
            results.append((fname, xml_text))
        except ConversionError as e:
            errors.append(f"{uf.filename}: {e}")
        except Exception as e:
            errors.append(f"{uf.filename}: unexpected error {e}")

    if not results and errors:
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(
                message="No valid conversions", errors=errors, total_errors=len(errors)
            ).model_dump(),
        )

    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname, content in results:
            zf.writestr(fname, content)
        if errors:
            zf.writestr("errors.txt", "\n".join(errors))
    mem.seek(0)

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return StreamingResponse(
        mem,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=iwxxm_batch_{stamp}.zip"
        },
    )


__all__ = ["app"]
