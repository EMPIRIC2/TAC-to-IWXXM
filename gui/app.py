"""FastAPI application providing a single-page GUI for METAR -> IWXXM conversion.

Features:
 - Drag & drop multiple .tac / .txt files containing METAR/SPECI TAC.
 - Manual text input area for ad-hoc METAR entry.
 - Batch conversion via /api/convert returning JSON results.
 - Client-side download & copy-to-clipboard of each IWXXM output as .txt.
"""

from __future__ import annotations

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Header
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional
import pathlib
import os
import json
import sys
import io
import zipfile
import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Add repository root to path to enable 'from backend.conversion import ...'
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from backend.conversion import convert_metar_tac, ConversionError
except Exception as e:  # pragma: no cover
    raise RuntimeError(f"Failed to import conversion module: {e}") from e
try:
    from auth import router as auth_router
    from auth.security import decode_access_token
    from auth.database import SessionLocal
    from auth.models import User, APIKey
except Exception as e:  # pragma: no cover
    # Auth optional: continue without if failure
    auth_router = None
    decode_access_token = None


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

    name: str = Field(
        ...,
        description="Output filename (e.g., 'manual_input.txt', 'metar1.txt')",
        examples=["manual_input.txt", "KJFK.txt"]
    )
    content: str = Field(
        ...,
        description="IWXXM XML document as UTF-8 text",
        min_length=1
    )
    source: Optional[str] = Field(
        None,
        description="Source of the input: 'manual', 'file', or filename",
        examples=["manual", "metar1.tac"]
    )
    size_bytes: Optional[int] = Field(
        None,
        description="Size of the XML output in bytes",
        ge=0
    )


class ConversionResponse(BaseModel):
    """Response from /api/convert endpoint containing results and errors."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "results": [
                    {
                        "name": "manual_input.txt",
                        "content": "<?xml version='1.0' encoding='utf-8'?><iwxxm:METAR...>",
                        "source": "manual",
                        "size_bytes": 1452
                    }
                ],
                "errors": [],
                "total_processed": 1,
                "successful": 1,
                "failed": 0
            }
        }
    )

    results: List[ConversionResult] = Field(
        default_factory=list,
        description="Successfully converted METAR -> IWXXM XML documents"
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Error messages for failed conversions"
    )
    total_processed: int = Field(
        ...,
        description="Total number of inputs processed",
        ge=0
    )
    successful: int = Field(
        ...,
        description="Number of successful conversions",
        ge=0
    )
    failed: int = Field(
        ...,
        description="Number of failed conversions",
        ge=0
    )


class ErrorDetail(BaseModel):
    """Detailed error response for failed requests."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "No valid METAR inputs provided",
                "errors": ["empty.tac: empty file", "invalid.tac: Decoding/encoding error"],
                "total_errors": 2
            }
        }
    )

    message: str = Field(
        ...,
        description="High-level error message",
        examples=["No valid METAR inputs provided", "All conversions failed"]
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Detailed error messages for each failure"
    )
    total_errors: int = Field(
        ...,
        description="Total number of errors encountered",
        ge=0
    )


class HealthResponse(BaseModel):
    """Health check response."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "gifts_available": True
            }
        }
    )

    status: str = Field(
        ...,
        description="Service health status",
        examples=["healthy", "degraded"]
    )
    version: str = Field(
        ...,
        description="API version",
        examples=["0.1.0"]
    )
    gifts_available: bool = Field(
        ...,
        description="Whether GIFTs submodule is properly loaded"
    )


app = FastAPI(
    title="METAR to IWXXM Converter",
    version="0.1.0",
    description="Convert METAR/SPECI TAC messages to IWXXM XML format using the GIFTs library",
    contact={
        "name": "GitHub Repository",
        "url": "https://github.com/joseph-c-mcguire/metar-to-IWXXM"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

static_dir = ROOT / "gui" / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include auth router if available
if auth_router is not None:
    app.include_router(auth_router)

# ---------------------------------------------------------------------------
# Auth dependency for protected routes
# ---------------------------------------------------------------------------


def get_db():
    if SessionLocal is None:  # type: ignore
        raise HTTPException(status_code=500, detail="Auth DB not initialized")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def current_user(authorization: str | None = Header(default=None), db=Depends(get_db)):
    if decode_access_token is None:
        raise HTTPException(
            status_code=503, detail="Authentication not available")
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split()[1]
    username = decode_access_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.get("/", response_class=HTMLResponse)
def index(user=Depends(current_user)) -> HTMLResponse:
    """Serve the single-page GUI with injected backend URL configuration.

    The backend URL is taken from the BACKEND_URL environment variable (if set).
    It is exposed to the browser as window.METAR_API_BASE for API calls.
    Falls back to same-origin ('') when not provided.
    """
    index_path = static_dir / "index.html"
    if not index_path.exists():  # pragma: no cover
        raise HTTPException(status_code=500, detail="index.html missing")
    backend_url = os.environ.get("BACKEND_URL", "").rstrip("/")
    raw_html = index_path.read_text(encoding="utf-8")
    injection = f"<script>window.METAR_API_BASE={json.dumps(backend_url)};</script>"
    # Inject before closing body tag; if not found append at end.
    if "</body>" in raw_html:
        html = raw_html.replace("</body>", injection + "</body>")
    else:
        html = raw_html + injection
    return HTMLResponse(html)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health() -> HealthResponse:
    """Health check endpoint to verify service status and GIFTs availability."""
    try:
        # Quick test to ensure conversion works
        from backend.conversion import convert_metar_tac
        test_metar = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
        _ = convert_metar_tac(test_metar)
        gifts_available = True
        status = "healthy"
    except Exception:
        gifts_available = False
        status = "degraded"

    return HealthResponse(
        status=status,
        version="0.1.0",
        gifts_available=gifts_available
    )


@app.post(
    "/api/convert",
    response_model=ConversionResponse,
    responses={
        200: {
            "description": "Successful conversion (may include partial errors)",
            "model": ConversionResponse
        },
        400: {
            "description": "All conversions failed or no valid input",
            "model": ErrorDetail
        }
    },
    tags=["Conversion"]
)
async def convert(
    files: List[UploadFile] = File(
        default=[],
        description="One or more METAR TAC files (.tac, .txt, .metar)"
    ),
    manual_text: str = Form(
        default="",
        description="Manual METAR/SPECI TAC text input"
    ),
    user=Depends(current_user),
) -> ConversionResponse:
    """Convert uploaded METAR TAC files and/or manual text to IWXXM XML format.

    This endpoint accepts:
    - Multiple file uploads via form-data
    - Manual text input via form field
    - Combination of both

    Returns a JSON response with:
    - `results`: List of successfully converted IWXXM XML documents
    - `errors`: List of error messages for failed conversions
    - Statistics: total_processed, successful, failed counts

    Example curl command:
    ```bash
    curl -X POST http://localhost:8000/api/convert \\
         -F "files=@metar1.tac" \\
         -F "files=@metar2.tac" \\
         -F "manual_text=METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
    ```
    """
    results: List[ConversionResult] = []
    errors: List[str] = []
    total_inputs = 0

    # Process manual input if provided.
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

    # Process each uploaded file.
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
        except Exception as e:  # pragma: no cover
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


@app.post(
    "/api/convert-zip",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "ZIP archive containing IWXXM XML files",
            "content": {"application/zip": {}},
            "headers": {
                "Content-Disposition": {
                    "description": "Attachment with timestamped filename",
                    "schema": {"type": "string", "example": "attachment; filename=iwxxm_batch_20251123T143022Z.zip"}
                }
            }
        },
        400: {
            "description": "All conversions failed or no valid input",
            "model": ErrorDetail
        }
    },
    tags=["Conversion"]
)
async def convert_zip(
    files: List[UploadFile] = File(
        default=[],
        description="One or more METAR TAC files to include in the ZIP archive"
    ),
    manual_text: str = Form(
        default="",
        description="Manual METAR/SPECI TAC text to include in the ZIP archive"
    ),
    user=Depends(current_user),
) -> StreamingResponse:
    """Convert inputs and stream a ZIP archive of IWXXM XML outputs.

    This endpoint converts all provided inputs to IWXXM XML and packages them
    into a downloadable ZIP archive. The archive contains:
    - One `.xml` file per successfully converted METAR
    - An `errors.txt` file (if any conversions failed)

    The ZIP filename includes a UTC timestamp for tracking.

    Example usage:
    ```bash
    curl -X POST http://localhost:8000/api/convert-zip \\
         -F "files=@metar1.tac" \\
         -F "files=@metar2.tac" \\
         -F "manual_text=METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005" \\
         -o iwxxm_batch.zip
    ```
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
        except Exception as e:  # pragma: no cover
            errors.append(f"{uf.filename}: unexpected error {e}")

    if not results and errors:
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(
                message="No valid conversions to include in ZIP",
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
            "Content-Disposition": f"attachment; filename=iwxxm_batch_{stamp}.zip"},
    )


__all__ = ["app"]
