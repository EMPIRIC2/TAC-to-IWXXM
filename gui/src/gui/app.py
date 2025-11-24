"""FastAPI GUI application (src layout).

Relocated from top-level to src/gui for standard packaging.
"""
from __future__ import annotations
from fastapi import HTTPException

import pathlib
import sys
import os
import json
import io
import zipfile
import datetime
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict

# Repository and GUI roots (robust across src layout or installed package)
_FILE_PATH = pathlib.Path(__file__).resolve()

# Attempt to identify repo root (dev layout) else fall back to ancestors.
_CANDIDATE_REPO_ROOTS = []
for depth in range(2, 6):  # parents[2] in dev gives <repo>/gui
    try:
        parent = _FILE_PATH.parents[depth]
    except IndexError:
        break
    _CANDIDATE_REPO_ROOTS.append(parent)
# Explicit Docker workdir
_CANDIDATE_REPO_ROOTS.append(pathlib.Path('/app'))

for _root in _CANDIDATE_REPO_ROOTS:
    if (_root / 'GIFTs').exists() or (_root / 'gui' / 'static').exists():
        REPO_ROOT = _root
        break
else:  # Fallback to deepest ancestor
    REPO_ROOT = _FILE_PATH.parents[-1]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Resolve static directory from multiple candidates.
_STATIC_CANDIDATES = []
for depth in range(0, 6):
    try:
        parent = _FILE_PATH.parents[depth]
    except IndexError:
        break
    _STATIC_CANDIDATES.append(parent / 'static')
    # If this parent looks like a 'gui' directory, also try its parent/static
    if parent.name == 'gui':
        _STATIC_CANDIDATES.append(parent.parent / 'static')
_STATIC_CANDIDATES.extend([
    pathlib.Path('/app/gui/static'),
    pathlib.Path('/app/static'),
])

for cand in _STATIC_CANDIDATES:
    if cand.exists():
        static_dir = cand
        break
else:
    raise RuntimeError('Static directory not found. Tried: ' +
                       ', '.join(str(c) for c in _STATIC_CANDIDATES))

try:
    from backend.conversion import convert_metar_tac, ConversionError  # type: ignore
except Exception as e:  # pragma: no cover
    raise RuntimeError(f"Failed to import conversion module: {e}") from e

# Auth (real or mock fallback)
try:
    from auth.api import router as auth_router  # type: ignore
    from auth.security import decode_access_token  # type: ignore
    from auth.database import SessionLocal  # type: ignore
    from auth.models import User  # type: ignore
    _mock_mode = False
except Exception:  # pragma: no cover - fallback for isolated GUI tests
    from fastapi import APIRouter
    auth_router = APIRouter(prefix="/auth", tags=["Auth-Mock"])
    _mock_users: dict[str, dict] = {}
    _mock_mode = True

    def _make_token(username: str) -> str: return f"mock-{username}"

    @auth_router.post("/register")
    def mock_register(user_in: dict):
        username = user_in.get("username")
        if not username:
            raise HTTPException(status_code=400, detail="Username required")
        if username in _mock_users:
            raise HTTPException(status_code=400, detail="Username exists")
        _mock_users[username] = user_in
        return {"id": len(_mock_users), "name": user_in.get("name", "Test User"), "email": user_in.get("email", "test@example.com"), "address": user_in.get("address", ""), "username": username}

    @auth_router.post("/login")
    def mock_login(payload: dict):
        username = payload.get("username")
        password = payload.get("password")
        if username not in _mock_users or not password:
            raise HTTPException(status_code=400, detail="Invalid credentials")
        token = _make_token(username)
        return {"access_token": token, "token_type": "bearer", "user": {"id": 1, "name": _mock_users[username].get("name", "Test User"), "email": _mock_users[username].get("email", "test@example.com"), "address": _mock_users[username].get("address", ""), "username": username}, "api_keys": []}

    def decode_access_token(
        token: str) -> str | None: return token[5:] if token.startswith("mock-") else None
    SessionLocal = None  # type: ignore

    class User:  # type: ignore
        def __init__(self, username: str): self.username = username

# Models


class ConversionResult(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {
                              "name": "KJFK_231751Z.txt", "content": "<?xml version='1.0' encoding='utf-8'?><iwxxm:METAR ...>", "source": "file", "size_bytes": 1452}})
    name: str = Field(..., description="Output filename")
    content: str = Field(..., description="IWXXM XML document", min_length=1)
    source: Optional[str] = Field(None, description="Input source")
    size_bytes: Optional[int] = Field(
        None, ge=0, description="Size of XML output")


class ConversionResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"results": [
                              {"name": "manual_input.txt", "content": "...", "source": "manual", "size_bytes": 1452}], "errors": [], "total_processed": 1, "successful": 1, "failed": 0}})
    results: List[ConversionResult] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    total_processed: int = Field(..., ge=0)
    successful: int = Field(..., ge=0)
    failed: int = Field(..., ge=0)


class ErrorDetail(BaseModel):
    message: str
    errors: List[str] = Field(default_factory=list)
    total_errors: int = Field(..., ge=0)


class HealthResponse(BaseModel):
    status: str
    version: str
    gifts_available: bool


app = FastAPI(title="METAR to IWXXM Converter", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
if auth_router is not None:
    app.include_router(auth_router)

# Auth helpers


def get_db():
    if _mock_mode:
        yield None
        return
    if SessionLocal is None:
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
    if _mock_mode:
        return User(username)  # type: ignore
    user = db.query(User).filter(User.username ==
                                 username).first()  # type: ignore
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    """Serve the main page (auth handled client-side)."""
    index_path = static_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=500, detail="index.html missing")
    backend_url = os.environ.get("BACKEND_URL", "").rstrip("/")
    raw_html = index_path.read_text(encoding="utf-8")
    injection = f"<script>window.METAR_API_BASE={json.dumps(backend_url)};</script>"
    html = raw_html.replace(
        "</body>", injection + "</body>") if "</body>" in raw_html else raw_html + injection
    return HTMLResponse(html)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    try:
        from backend.conversion import convert_metar_tac  # type: ignore
        _ = convert_metar_tac(
            "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005")
        return HealthResponse(status="healthy", version="0.1.0", gifts_available=True)
    except Exception:
        return HealthResponse(status="degraded", version="0.1.0", gifts_available=False)


@app.post("/api/convert", response_model=ConversionResponse)
async def convert(files: List[UploadFile] = File(default=[]), manual_text: str = Form(default=""), user=Depends(current_user)) -> ConversionResponse:
    results: List[ConversionResult] = []
    errors: List[str] = []
    total_inputs = 0
    if manual_text.strip():
        total_inputs += 1
        try:
            xml_text = convert_metar_tac(manual_text.strip())
            results.append(ConversionResult(name="manual_input.txt", content=xml_text,
                           source="manual", size_bytes=len(xml_text.encode())))
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
            results.append(ConversionResult(name=out_name, content=xml_text,
                           source=uf.filename, size_bytes=len(xml_text.encode())))
        except ConversionError as e:
            errors.append(f"{uf.filename}: {e}")
        except Exception as e:
            errors.append(f"{uf.filename}: unexpected error {e}")
    if not results and errors:
        raise HTTPException(status_code=400, detail=ErrorDetail(
            message="All conversions failed", errors=errors, total_errors=len(errors)).model_dump())
    return ConversionResponse(results=results, errors=errors, total_processed=total_inputs, successful=len(results), failed=len(errors))


@app.post("/api/convert-zip", response_class=StreamingResponse)
async def convert_zip(files: List[UploadFile] = File(default=[]), manual_text: str = Form(default=""), user=Depends(current_user)) -> StreamingResponse:
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
        raise HTTPException(status_code=400, detail=ErrorDetail(
            message="No valid conversions to include in ZIP", errors=errors, total_errors=len(errors)).model_dump())
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname, content in results:
            zf.writestr(fname, content)
        if errors:
            zf.writestr("errors.txt", "\n".join(errors))
    mem.seek(0)
    stamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    return StreamingResponse(mem, media_type="application/zip", headers={"Content-Disposition": f"attachment; filename=iwxxm_batch_{stamp}.zip"})

__all__ = ["app"]
