"""Standalone backend API module for Docker deployment.

This module provides the same API endpoints as gui.app but without static file serving,
suitable for containerized backend-only deployments.
"""

from __future__ import annotations

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import pathlib
import sys
import io
import zipfile
import datetime

# Add repository root to path
ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from backend.conversion import convert_metar_tac, ConversionError
except Exception as e:
    raise RuntimeError(f"Failed to import conversion module: {e}") from e


# ============================================================================
# Pydantic Models
# ============================================================================

class ConversionResult(BaseModel):
    """A single conversion result from METAR TAC to IWXXM XML."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "KJFK_231751Z.txt",
                "content": "<?xml version='1.0' encoding='utf-8'?><iwxxm:METAR ...>",
                "source": "file",
                "size_bytes": 1452
            }
        }
    )

    name: str = Field(..., description="Output filename",
                      examples=["manual_input.txt"])
    content: str = Field(...,
                         description="IWXXM XML document as UTF-8 text", min_length=1)
    source: Optional[str] = Field(
        None, description="Source of input", examples=["manual"])
    size_bytes: Optional[int] = Field(
        None, description="XML output size in bytes", ge=0)


class ConversionResponse(BaseModel):
    """Response from /api/convert endpoint."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "results": [{"name": "manual_input.txt", "content": "...", "source": "manual", "size_bytes": 1452}],
                "errors": [],
                "total_processed": 1,
                "successful": 1,
                "failed": 0
            }
        }
    )

    results: List[ConversionResult] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    total_processed: int = Field(..., ge=0)
    successful: int = Field(..., ge=0)
    failed: int = Field(..., ge=0)


class ErrorDetail(BaseModel):
    """Detailed error response."""

    message: str
    errors: List[str] = Field(default_factory=list)
    total_errors: int = Field(..., ge=0)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    gifts_available: bool


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="METAR to IWXXM Backend API",
    version="0.1.0",
    description="Convert METAR/SPECI TAC messages to IWXXM XML format (backend only)",
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health() -> HealthResponse:
    """Health check endpoint."""
    try:
        test_metar = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
        _ = convert_metar_tac(test_metar)
        gifts_available = True
        status = "healthy"
    except Exception:
        gifts_available = False
        status = "degraded"

    return HealthResponse(status=status, version="0.1.0", gifts_available=gifts_available)


@app.post("/api/convert", response_model=ConversionResponse, tags=["Conversion"])
async def convert(
    files: List[UploadFile] = File(default=[], description="METAR TAC files"),
    manual_text: str = Form(default="", description="Manual METAR text"),
) -> ConversionResponse:
    """Convert METAR TAC to IWXXM XML."""
    results: List[ConversionResult] = []
    errors: List[str] = []
    total_inputs = 0

    if manual_text.strip():
        total_inputs += 1
        try:
            xml_text = convert_metar_tac(manual_text.strip())
            results.append(ConversionResult(
                name="manual_input.txt",
                content=xml_text,
                source="manual",
                size_bytes=len(xml_text.encode("utf-8"))
            ))
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
            results.append(ConversionResult(
                name=out_name,
                content=xml_text,
                source=uf.filename,
                size_bytes=len(xml_text.encode("utf-8"))
            ))
        except ConversionError as e:
            errors.append(f"{uf.filename}: {e}")
        except Exception as e:
            errors.append(f"{uf.filename}: unexpected error {e}")

    if not results and errors:
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(
                message="All conversions failed",
                errors=errors,
                total_errors=len(errors)
            ).model_dump()
        )

    return ConversionResponse(
        results=results,
        errors=errors,
        total_processed=total_inputs,
        successful=len(results),
        failed=len(errors)
    )


@app.post("/api/convert-zip", response_class=StreamingResponse, tags=["Conversion"])
async def convert_zip(
    files: List[UploadFile] = File(default=[]),
    manual_text: str = Form(default=""),
) -> StreamingResponse:
    """Convert inputs to ZIP archive of IWXXM XML files."""
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
                message="No valid conversions",
                errors=errors,
                total_errors=len(errors)
            ).model_dump()
        )

    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname, content in results:
            zf.writestr(fname, content)
        if errors:
            zf.writestr("errors.txt", "\n".join(errors))
    mem.seek(0)

    stamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    return StreamingResponse(
        mem,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=iwxxm_batch_{stamp}.zip"}
    )


__all__ = ["app"]
