"""Standalone backend API module for Docker deployment."""

from __future__ import annotations

import datetime
import io
import logging
import os
import pathlib
import sys
import time
import zipfile
from typing import Any, Dict, List, Optional, Tuple, TypeGuard

# Add src directory to path for imports (for local uvicorn execution)
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse

try:
    # Try relative imports first (when run as module in Docker)
    from .config.icao_opmet import get_icao_region, get_translation_centre_info
    from .msgspec_http import msgspec_json_response
    from .routers import dissemination, evaluation, icao_opmet, validation, work_sessions
    from .schemas.conversion import (
        ConversionIssue,
        ConversionIssueSeverity,
        ConversionRequest,
        ConversionResponse,
        ConversionResult,
        ErrorDetail,
        FailedSpan,
        HealthResponse,
    )
    from .schemas.icao_opmet import TranslationStatus
    from .schemas.validation import (
        BulletinMetaModel,
        BulletinReportResultModel,
        ConvertBulletinResponse,
        DecodeResidualModel,
        DecodeSegmentModel,
        DecodeTacResponse,
        LintFixModel,
        LintIssueCatalogEntryModel,
        LintIssueCatalogResponse,
        LintIssueModel,
        LintTacResponse,
        ValidateRequest,
        ValidateResponse,
        ValidationLayer,
    )
    from .services.database import database_lifespan
    from .services.statistics import statistics_service
    from .services.validation import ValidationError as ValidationServiceError
    from .services.validation import ValidationService
    from .services.validation_orchestrator import get_validation_orchestrator
    from .services.webhooks import webhook_service
    from .utilities.conversion import ConversionError, convert_metar_tac_with_metadata
    from .utilities.metar_normalizer import normalize_recent_weather_tokens
    from .utilities.observability import install_fastapi_observability, setup_logging
    from .utilities.security import verify_supabase_token
    from .utilities.tac_parser import extract_airport_code
except ImportError:
    # Fall back to direct imports (when sys.path is set for local development)
    from config.icao_opmet import get_icao_region, get_translation_centre_info
    from msgspec_http import msgspec_json_response
    from routers import dissemination, evaluation, icao_opmet, validation, work_sessions
    from schemas.conversion import (
        ConversionIssue,
        ConversionIssueSeverity,
        ConversionRequest,
        ConversionResponse,
        ConversionResult,
        ErrorDetail,
        FailedSpan,
        HealthResponse,
    )
    from schemas.icao_opmet import TranslationStatus
    from schemas.validation import (
        BulletinMetaModel,
        BulletinReportResultModel,
        ConvertBulletinResponse,
        DecodeResidualModel,
        DecodeSegmentModel,
        DecodeTacResponse,
        LintFixModel,
        LintIssueCatalogEntryModel,
        LintIssueCatalogResponse,
        LintIssueModel,
        LintTacResponse,
        ValidateRequest,
        ValidateResponse,
        ValidationLayer,
    )
    from services.database import database_lifespan
    from services.statistics import statistics_service
    from services.validation import ValidationError as ValidationServiceError
    from services.validation import ValidationService
    from services.validation_orchestrator import get_validation_orchestrator
    from services.webhooks import webhook_service
    from utilities.conversion import ConversionError, convert_metar_tac_with_metadata
    from utilities.metar_normalizer import normalize_recent_weather_tokens
    from utilities.observability import install_fastapi_observability, setup_logging
    from utilities.security import verify_supabase_token
    from utilities.tac_parser import extract_airport_code

# Package thin-wrapper aliases (patchable in unit tests; ADR-015 / TC-F6-033 / F13)
# Prefer validate_iwxxm (Rust hot path + lxml fallback) over legacy lxml-only validate.
from iwxxm_validate import validate_iwxxm as iwxxm_validate_fn
from tac2iwxxm import BulletinSplitError
from tac2iwxxm import decode_tac as tac2iwxxm_decode_tac
from tac2iwxxm import split_bulletin as tac2iwxxm_split_bulletin
from tac_validate import lint as tac_lint_fn
from tac_validate.issue_registry import catalog_entries as tac_catalog_entries

setup_logging("backend")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="METAR to IWXXM Backend API",
    version="0.1.0",
    description="Convert METAR/SPECI TAC messages to IWXXM XML format with comprehensive validation",
    lifespan=database_lifespan,  # Initialize database pool on startup
    openapi_tags=[
        {
            "name": "Health",
            "description": "API health and status checks",
        },
        {
            "name": "Conversion",
            "description": "Convert METAR TAC to IWXXM XML format",
        },
        {
            "name": "Validation",
            "description": "Validate METAR TAC and IWXXM XML content through multiple validation layers",
        },
        {
            "name": "Evaluation",
            "description": "Run evaluation jobs to compare conversion results with reference data",
        },
        {
            "name": "ICAO OPMET Statistics",
            "description": "Translation Centre statistics and ICAO OPMET Data Exchange compliance",
        },
        {
            "name": "Auth",
            "description": "Authentication endpoints (Supabase proxy) — merged from packages/auth",
        },
    ],
    swagger_ui_parameters={
        "persistAuthorization": True,
    },
)

install_fastapi_observability(app=app, service_name="backend")


class ConvertRequestLoggingMiddleware:
    """Log request/response details for convert flow, including OPTIONS preflight."""

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        method = scope.get("method", "")

        if path != "/api/v1/convert":
            await self.app(scope, receive, send)
            return

        headers = {key.decode("latin1").lower(): value.decode("latin1") for key, value in scope.get("headers", [])}

        logger.info(
            "[PREFLIGHT] %s %s origin=%s acr_method=%s acr_headers=%s content_type=%s",
            method,
            path,
            headers.get("origin", "none"),
            headers.get("access-control-request-method", "none"),
            headers.get("access-control-request-headers", "none"),
            headers.get("content-type", "none"),
        )

        async def send_wrapper(message):
            if message.get("type") == "http.response.start":
                status_code = message.get("status")
                logger.info(
                    "[PREFLIGHT] %s %s -> status=%s",
                    method,
                    path,
                    status_code,
                )
            await send(message)

        await self.app(scope, receive, send_wrapper)


# Configure CORS with dynamic allowed origins from environment
def is_dev_cors_relaxation_enabled() -> bool:
    """Enable relaxed CORS behavior for local debugging when explicitly requested."""
    return os.getenv("ENABLE_DEV_CORS_RELAXATION", "").lower() in (
        "true",
        "1",
        "yes",
        "on",
    )


def add_origin_if_missing(origins: list, origin: str) -> list:
    """Append origin if not present."""
    if origin and origin not in origins:
        origins.append(origin)
    return origins


def add_loopback_origin_variants(origins: list) -> list:
    """Ensure localhost and 127.0.0.1 variants are both allowed for local dev."""
    expanded_origins = list(origins)
    for origin in origins:
        if "localhost" in origin:
            loopback_variant = origin.replace("localhost", "127.0.0.1")
            add_origin_if_missing(expanded_origins, loopback_variant)
        if "127.0.0.1" in origin:
            localhost_variant = origin.replace("127.0.0.1", "localhost")
            add_origin_if_missing(expanded_origins, localhost_variant)
    return expanded_origins


def get_cors_origins() -> list:
    """Get allowed CORS origins from config with deprecated env fallbacks."""
    import warnings

    from metar_shared import METAR_CORS_ORIGINS_ENV, parse_comma_separated_origins
    from metar_shared.config_loader import get_cors_origins_from_config, get_frontend_url_from_config

    relaxed_cors = is_dev_cors_relaxation_enabled()
    origins = get_cors_origins_from_config()

    allowed_origins_env = os.getenv(METAR_CORS_ORIGINS_ENV, "").strip()
    if allowed_origins_env:
        env_origins = list(parse_comma_separated_origins(allowed_origins_env))
        if origins:
            warnings.warn(
                f"{METAR_CORS_ORIGINS_ENV} supplements config.*.api.corsOrigins (deprecated env)",
                DeprecationWarning,
                stacklevel=2,
            )
            for origin in env_origins:
                add_origin_if_missing(origins, origin)
        else:
            warnings.warn(
                f"{METAR_CORS_ORIGINS_ENV} is deprecated; use config.*.api.corsOrigins",
                DeprecationWarning,
                stacklevel=2,
            )
            origins = env_origins

    if not origins:
        frontend_url = os.getenv("FRONTEND_URL", "").strip() or get_frontend_url_from_config()
        if not frontend_url:
            frontend_url = "http://localhost:18000"
        origins = [frontend_url, "http://localhost:3000"]

    if relaxed_cors:
        add_origin_if_missing(origins, "http://localhost:5173")
        add_origin_if_missing(origins, "http://localhost:18000")
    return add_loopback_origin_variants(origins)


def get_cors_allowed_headers() -> list:
    """Get allowed CORS request headers."""
    if is_dev_cors_relaxation_enabled():
        return ["*"]
    return ["Authorization", "Content-Type"]


allowed_origins = get_cors_origins()
allowed_headers = get_cors_allowed_headers()
dev_cors_relaxed = is_dev_cors_relaxation_enabled()

_CORS_METHODS = ["GET", "POST", "PATCH", "DELETE", "OPTIONS"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=_CORS_METHODS,
    allow_headers=allowed_headers,
)

app.add_middleware(ConvertRequestLoggingMiddleware)

logger.info(
    "[CORS] Configured relaxed_mode=%s allow_origins=%s allow_methods=%s allow_headers=%s allow_credentials=%s",
    dev_cors_relaxed,
    allowed_origins,
    _CORS_METHODS,
    allowed_headers,
    True,
)

if dev_cors_relaxed:
    logger.warning("[CORS] ENABLE_DEV_CORS_RELAXATION is active: localhost:5173 added and preflight headers set to '*'")


# Add Translation Centre identification headers (ICAO OPMET compliance)
@app.middleware("http")
async def add_translation_centre_headers(request: Request, call_next):
    """
    Add ICAO Translation Centre identification headers to all responses.

    Implements ICAO OPMET Data Exchange Guidelines Section 7 requirements
    for Translation Centre identification in HTTP responses.
    """
    response = await call_next(request)

    # Add Translation Centre metadata headers
    try:
        centre_info = get_translation_centre_info()
        # Only add headers with non-None values.
        # .strip() guards against CRLF line-endings in env vars read from
        # Windows-format .env files (b'TEST\r' is rejected by h11 as illegal).
        if centre_info.get("translationCentreDesignator"):
            response.headers["X-Translation-Centre"] = centre_info["translationCentreDesignator"].strip()
        if centre_info.get("translationCentreName"):
            response.headers["X-Translation-Centre-Name"] = centre_info["translationCentreName"].strip()
        if centre_info.get("icaoLocationIndicator"):
            response.headers["X-ICAO-Location-Indicator"] = centre_info["icaoLocationIndicator"].strip()
    except Exception as e:
        logger.debug(f"Translation Centre headers not configured: {e}")

    return response


# Dependency to handle optional file uploads (including empty strings from Swagger UI)
def _is_named_upload(value: object) -> TypeGuard[UploadFile]:
    """Return True for Starlette/FastAPI uploads and duck-typed upload objects."""
    if isinstance(value, str) or not value:
        return False
    return bool(getattr(value, "filename", None))


async def parse_files(request: Request) -> List[UploadFile]:
    """
    Parse files parameter from request, handling edge cases:
    - Swagger UI 'Send empty value' sends empty string which FastAPI can't parse
    - This manually extracts files from the form, filtering out empty strings
    """
    try:
        form = await request.form()
        files = []
        for key, value in form.multi_items():
            if key == "files" and _is_named_upload(value):
                files.append(value)
        return files
    except Exception as e:
        logger.warning(f"Error parsing files from request: {e}")
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(
                message="Invalid file upload payload",
                errors=[str(e)],
                issues=[
                    ConversionIssue(
                        source="request",
                        message="Unable to parse multipart file upload payload.",
                        severity=ConversionIssueSeverity.ERROR,
                        hint="Ensure the request uses multipart/form-data and each file field is named 'files'.",
                        code="INVALID_MULTIPART_PAYLOAD",
                    )
                ],
                total_errors=1,
            ).model_dump(),
        )


def split_manual_entries(manual_text: str) -> List[str]:
    """Split manual text input into one TAC entry per non-empty line."""
    if not manual_text:
        return []
    return [line.strip() for line in manual_text.splitlines() if line.strip()]


def manual_entries_with_offsets(manual_text: str) -> List[Tuple[str, int]]:
    """Split like ``split_manual_entries`` with start offsets into the original buffer.

    Offsets point at the first non-whitespace character of each kept line so
    soft-preview ``failed_spans`` can be remapped onto the full editor document.
    """
    if not manual_text:
        return []
    out: List[Tuple[str, int]] = []
    offset = 0
    for line in manual_text.splitlines(keepends=True):
        raw = line[:-1] if line.endswith("\n") else line
        if raw.endswith("\r"):
            raw = raw[:-1]
        stripped = raw.strip()
        if stripped:
            lead = len(raw) - len(raw.lstrip())
            out.append((stripped, offset + lead))
        offset += len(line)
    return out


async def read_uploaded_text(upload_file: UploadFile) -> Tuple[Optional[str], Optional[str]]:
    """Read uploaded text file using strict UTF-8 decoding with a size limit.

    Gzip payloads (``.gz`` / magic ``1f 8b``) are inflated before decode.
    """
    import gzip

    max_upload_bytes = 10 * 1024 * 1024  # 10 MiB
    raw_bytes = await upload_file.read(max_upload_bytes + 1)
    if not raw_bytes or not raw_bytes.strip():
        return None, "empty file"

    if len(raw_bytes) > max_upload_bytes:
        return None, f"file too large (limit {max_upload_bytes} bytes)"

    name = (upload_file.filename or "").lower()
    if name.endswith(".gz") or name.endswith(".gzip") or raw_bytes[:2] == b"\x1f\x8b":
        try:
            import io

            # Cap inflate size during decompression (avoid gzip bombs).
            inflated = bytearray()
            with gzip.GzipFile(fileobj=io.BytesIO(raw_bytes), mode="rb") as gz:
                while True:
                    chunk = gz.read(64 * 1024)
                    if not chunk:
                        break
                    inflated.extend(chunk)
                    if len(inflated) > max_upload_bytes:
                        return None, f"decompressed file too large (limit {max_upload_bytes} bytes)"
            raw_bytes = bytes(inflated)
        except OSError as exc:
            return None, f"gzip decompress failed ({exc})"

    try:
        decoded = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        return None, f"file must be UTF-8 encoded ({exc})"

    content = decoded.strip()
    if not content:
        return None, "empty file"

    return content, None


# Cap per-request bulletin fan-out (lint + convert per report).
MAX_BULLETIN_REPORTS = 100


async def read_upload_files_text(files: Optional[List[UploadFile]]) -> Tuple[str, Optional[str]]:
    """Join multipart uploads via ``read_uploaded_text`` (10 MiB each).

    Returns
    -------
    tuple[str, str | None]
        Joined text and an error message when a non-empty upload fails limits/encoding.
    """
    if not files:
        return "", None
    chunks: list[str] = []
    for upload in files:
        content, err = await read_uploaded_text(upload)
        if err == "empty file":
            continue
        if err:
            return "", err
        if content:
            chunks.append(content)
    return "\n".join(chunks), None


def is_xml_input(filename: Optional[str], content: str) -> bool:
    """Determine if uploaded content looks like XML input."""
    lowered_name = (filename or "").lower()
    if lowered_name.endswith(".xml"):
        return True
    return content.lstrip().startswith("<")


def classify_and_validate_upload_content(
    *,
    filename: Optional[str],
    content: str | None,
    iwxxm_version: str,
    endpoint_path: str,
    validation_orchestrator: Optional[Any],
) -> Optional[Dict[str, str]]:
    """Return a standardized XML rejection payload for TAC-only conversion endpoints."""
    if not content or not is_xml_input(filename, content):
        return None

    if not validation_orchestrator:
        return {
            "message": "XML validation is unavailable in this environment.",
            "hint": "Retry later or use TAC input for conversion.",
            "code": "XML_VALIDATION_UNAVAILABLE",
            "layer": "xml_input",
        }

    xml_wellformed_result = validation_orchestrator.validate_wellformed(content)
    if not xml_wellformed_result.passed:
        issue_message = (
            xml_wellformed_result.issues[0].message if xml_wellformed_result.issues else "XML is not well-formed"
        )
        return {
            "message": issue_message,
            "hint": "Fix XML syntax before upload.",
            "code": "XML_NOT_WELLFORMED",
            "layer": "xml_input",
        }

    xml_schema_result = validation_orchestrator.validate_xml_schema(content, iwxxm_version)
    blocking_schema_issues = [
        issue
        for issue in xml_schema_result.issues
        if getattr(issue, "level", None) and str(issue.level).lower().endswith("error")
    ]
    if not xml_schema_result.is_valid or blocking_schema_issues:
        schema_message = blocking_schema_issues[0].message if blocking_schema_issues else "XML schema validation failed"
        return {
            "message": schema_message,
            "hint": "Use an IWXXM XML file matching the selected IWXXM schema version.",
            "code": "XML_SCHEMA_VALIDATION_FAILED",
            "layer": "xml_input",
        }

    return {
        "message": f"XML input is valid, but {endpoint_path} is TAC only.",
        "hint": "Use TAC files for conversion. Use XML validation endpoints for XML-only checks.",
        "code": "XML_INPUT_NOT_CONVERTIBLE",
        "layer": "xml_input",
    }


def normalize_code(value: Optional[str], max_length: int) -> Optional[str]:
    """Normalize optional alphanumeric code-like fields."""
    if not value:
        return None
    normalized = value.strip().upper()
    if not normalized:
        return None
    return normalized[:max_length]


def normalize_validation_level(value: Optional[str]) -> str:
    """Normalize validation level to one of the supported API values."""
    allowed_levels = {"basic", "schema", "schematron", "icao_opmet", "comprehensive"}
    level = (value or "basic").strip().lower().replace("-", "_")
    return level if level in allowed_levels else "basic"


def _product_uses_metar_tac_layers(product: Optional[str]) -> bool:
    """Return True when legacy METAR/SPECI TAC keyword layers apply.

    F6.e non-METAR products (TAF, SIGMET, ...) must not be rejected by
    ``ValidationService.validate_all_layers`` which requires METAR/SPECI keywords.
    """
    product_u = (product or "METAR").strip().upper()
    return product_u in {"METAR", "SPECI"}


# Customize OpenAPI schema to add Bearer token authentication
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )

    # Add Bearer token security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token from the auth service (login at auth service or use DISABLE_AUTH=true for dev)",
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Include routers
logger.info(f"DEBUG: validation module = {validation}")
logger.info(f"DEBUG: validation.router = {validation.router}")
logger.info(f"DEBUG: evaluation module = {evaluation}")
logger.info(f"DEBUG: evaluation.router = {evaluation.router}")

try:
    app.include_router(validation.router, prefix="/api/v1/validation", tags=["Validation"])
    logger.info("DEBUG: included validation router successfully")
except Exception as e:  # pragma: no cover - defensive
    logger.error(f"DEBUG: Failed to include validation router: {e}", exc_info=True)

try:
    app.include_router(evaluation.router, prefix="/api/v1/eval", tags=["Evaluation"])
    logger.info("DEBUG: included evaluation router successfully")
except Exception as e:  # pragma: no cover - defensive
    logger.error(f"DEBUG: Failed to include evaluation router: {e}", exc_info=True)

try:
    app.include_router(work_sessions.router, prefix="/api/v1/work-sessions", tags=["Work Sessions"])
    # Admin work-sessions list removed (S011 / ADR-021 / #697).
    logger.info("DEBUG: included work sessions routers successfully")
except Exception as e:  # pragma: no cover - defensive
    logger.error(f"DEBUG: Failed to include work sessions routers: {e}", exc_info=True)

try:
    app.include_router(dissemination.router)
    logger.info("DEBUG: included dissemination router successfully")
except Exception as e:  # pragma: no cover - defensive
    logger.error(f"DEBUG: Failed to include dissemination router: {e}", exc_info=True)

try:
    app.include_router(icao_opmet.router)
    logger.info("DEBUG: included ICAO OPMET router successfully")
except Exception as e:  # pragma: no cover - defensive
    logger.error(f"DEBUG: Failed to include ICAO OPMET router: {e}", exc_info=True)

try:
    from auth.api_supabase import legacy_router as auth_legacy_router
    from auth.api_supabase import router as auth_router

    app.include_router(auth_router)
    app.include_router(auth_legacy_router)
    # Product /admin/* routers not mounted (S011 / ADR-021 / #697).
    logger.info("DEBUG: included auth routers at /auth/* successfully (admin product routes removed)")
except Exception as e:
    logger.error(f"DEBUG: Failed to include auth routers: {e}", exc_info=True)

logger.info(f"DEBUG: total routes = {len(app.routes)}")


# Custom dependency to handle optional file uploads (filters out empty strings from Swagger UI)
async def parse_optional_files(request: Request) -> List[UploadFile]:
    """Parse optional file uploads, filtering out empty strings from form data."""
    form = await request.form()
    files_data = form.getlist("files")
    return [f for f in files_data if _is_named_upload(f)]


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health() -> HealthResponse:
    """Check API health and conversion availability.

    Verifies that the API is running and tac2iwxxm can convert a sample METAR.
    Returns overall status and version information.

    ## Response
    - **status** (string): "healthy" or "degraded"
    - **version** (string): API version
    - **tac2iwxxm_available** (boolean): Whether tac2iwxxm convert works
    """
    try:
        test_metar = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="
        _ = convert_metar_tac_with_metadata(test_metar, validate=False)
        tac2iwxxm_available = True
        status = "healthy"
    except Exception:
        tac2iwxxm_available = False
        status = "degraded"
    return HealthResponse(status=status, version="0.1.0", tac2iwxxm_available=tac2iwxxm_available)


@app.get("/api/v1/versions", tags=["Conversion"])
def get_supported_versions():
    """Get list of supported IWXXM versions.

    Returns information about all supported IWXXM versions including
    version strings, release dates, and status (latest, previous, legacy).

    ## Response
    ```json
    {
      "default_version": "2025-2",
      "supported_versions": [
        {
          "version": "2025-2",
          "name": "IWXXM 2025-2",
          "status": "latest",
          "release_date": "2025-11-25",
          "wmo_amendment": 82
        },
        {
          "version": "2023-1",
          "name": "IWXXM 2023-1",
          "status": "previous",
          "release_date": "2023-06-02",
          "wmo_amendment": 78
        }
      ],
      "notes": {
        "2025-1": "Version 2025-1 does not exist; requests are remapped to 2025-2"
      },
      "deprecated_versions": [
        "2021-2",
        "2018",
        "2016",
        "3.0",
        "2.1",
        "2.0",
        "1.1"
      ]
    }
    ```
    """
    try:
        from .config.iwxxm_versions import DEFAULT_VERSION, DEPRECATED_VERSIONS, SUPPORTED_VERSIONS
    except ImportError:
        from config.iwxxm_versions import DEFAULT_VERSION, DEPRECATED_VERSIONS, SUPPORTED_VERSIONS

    versions_list = []
    for version, config in SUPPORTED_VERSIONS.items():
        versions_list.append(
            {
                "version": version,
                "name": config.get("name", ""),
                "status": config.get("status", ""),
                "release_date": config.get("release_date", ""),
                "wmo_amendment": config.get("wmo_amendment", 0),
            }
        )

    return {
        "default_version": DEFAULT_VERSION,
        "supported_versions": sorted(versions_list, key=lambda x: x["release_date"], reverse=True),
        "notes": {"2025-1": "Version 2025-1 does not exist; requests are auto-remapped to 2025-2"},
        "deprecated_versions": list(DEPRECATED_VERSIONS.keys()),
    }


@app.get("/api/v1/schema-status", tags=["Conversion"])
def get_schema_status():
    """Get comprehensive schema status including RC versions and mirroring info.

    Returns detailed information about all IWXXM schema versions including:
    - Stable releases and Release Candidates (RC)
    - Discovery dates and source URLs
    - Mirroring status
    - Channel classification

    ## Response
    ```json
    {
      "stable": ["2025-2", "2023-1"],
      "rc": ["2025-2RC1"],
      "all": ["2025-2", "2025-2RC1", "2023-1"],
      "default": "2025-2",
      "metadata": {
        "2025-2": {
          "name": "IWXXM 2025-2",
          "channel": "stable",
          "status": "latest",
          "discovered": "2025-11-25T00:00:00Z",
          "source_url": "https://github.com/wmo-im/iwxxm/tree/v2025-2",
          "mirrored": true
        },
        "2025-2RC1": {
          "name": "IWXXM 2025-2 RC1",
          "channel": "rc",
          "status": "rc",
          "discovered": "2026-02-10T00:00:00Z",
          "source_url": "https://schemas.wmo.int/iwxxm/2025-2RC1/",
          "mirrored": false,
          "promoted_to_stable": null
        }
      }
    }
    ```
    """
    try:
        from .config.iwxxm_versions import DEFAULT_VERSION, get_all_versions_with_metadata, get_versions_by_channel
    except ImportError:
        from config.iwxxm_versions import DEFAULT_VERSION, get_all_versions_with_metadata, get_versions_by_channel

    stable_versions = get_versions_by_channel("stable")
    rc_versions = get_versions_by_channel("rc")
    all_versions = get_versions_by_channel("all")
    all_metadata = get_all_versions_with_metadata()

    # Build metadata summary
    metadata_summary = {}
    for version, data in all_metadata.items():
        discovery_meta = data.get("discovery_metadata", {})
        metadata_summary[version] = {
            "name": data.get("name", f"IWXXM {version}"),
            "channel": discovery_meta.get("channel", "stable"),
            "status": data.get("status", "unknown"),
            "discovered": discovery_meta.get("discovered", ""),
            "source_url": discovery_meta.get("source_url", ""),
            "mirrored": discovery_meta.get("mirrored", False),
        }

        # Add RC-specific fields
        if "RC" in version.upper():
            metadata_summary[version]["promoted_to_stable"] = data.get("promoted_to_stable")

    return {
        "stable": stable_versions,
        "rc": rc_versions,
        "all": all_versions,
        "default": DEFAULT_VERSION,
        "metadata": metadata_summary,
    }


@app.get(
    "/api/v1/lint-issue-catalog",
    tags=["Validation"],
    response_model=LintIssueCatalogResponse,
    responses={
        401: {"description": "Unauthorized - Invalid or missing authentication token"},
    },
)
async def lint_issue_catalog(
    product: Optional[str] = None,
    user: dict = Depends(verify_supabase_token),
) -> Response:
    """Export the tac-validate issue registry for FE tooltips / catalog panel (E11-31)."""
    _ = user
    entries = tac_catalog_entries(product=product)
    return msgspec_json_response(
        LintIssueCatalogResponse(
            issues=[
                LintIssueCatalogEntryModel(
                    code=spec.code,
                    severity=spec.severity,
                    message_template=spec.message_template,
                    product=spec.product,
                    tags=list(spec.tags),
                )
                for spec in entries
            ]
        )
    )


@app.post(
    "/api/v1/lint-tac",
    tags=["Validation"],
    response_model=LintTacResponse,
    responses={
        401: {"description": "Unauthorized - Invalid or missing authentication token"},
        415: {"description": "Unsupported Media Type — multipart/form-data required"},
    },
)
async def lint_tac(
    request: Request,
    manual_text: str = Form(default="", description="TAC text to lint"),
    product: str = Form(default="METAR", description="Product hint when known"),
    files: Optional[List[UploadFile]] = File(None),
    user: dict = Depends(verify_supabase_token),
) -> Response:
    """Thin wrapper over ``packages/tac-validate`` (multipart/form-data only — Q8=A)."""
    content_type = (request.headers.get("content-type") or "").lower()
    if "multipart/form-data" not in content_type:
        raise HTTPException(
            status_code=415,
            detail="POST /api/v1/lint-tac requires multipart/form-data",
        )

    tac_text = manual_text or ""
    if files:
        joined, err = await read_upload_files_text(files)
        if err:
            raise HTTPException(status_code=400, detail={"code": "upload_rejected", "message": err})
        if joined:
            tac_text = joined

    report = tac_lint_fn(tac_text, product=product or "METAR")
    return msgspec_json_response(
        LintTacResponse(
            ok=report.ok,
            product=report.product,
            issues=[
                LintIssueModel(
                    severity=i.severity,
                    code=i.code,
                    message=i.message,
                    location=i.location,
                    start=getattr(i, "start", None),
                    end=getattr(i, "end", None),
                )
                for i in report.issues
            ],
            fixes=[LintFixModel(code=f.code, message=f.message, replacement=f.replacement) for f in report.fixes],
        )
    )


@app.post(
    "/api/v1/decode-tac",
    tags=["Conversion"],
    response_model=DecodeTacResponse,
    responses={
        401: {"description": "Unauthorized - Invalid or missing authentication token"},
        415: {"description": "Unsupported Media Type — multipart/form-data required"},
        422: {"description": "Missing required product field"},
    },
)
async def decode_tac_endpoint(
    request: Request,
    product: str = Form(..., description="TAC product (required)"),
    manual_text: str = Form(default="", description="TAC text to decode"),
    files: Optional[List[UploadFile]] = File(None),
    user: dict = Depends(verify_supabase_token),
) -> Response:
    """Thin wrapper over ``tac2iwxxm.decode_tac`` (S011 / #702 / TC-F7-002)."""
    _ = user
    content_type = (request.headers.get("content-type") or "").lower()
    if "multipart/form-data" not in content_type:
        raise HTTPException(
            status_code=415,
            detail="POST /api/v1/decode-tac requires multipart/form-data",
        )

    tac_text = manual_text or ""
    if files:
        joined, err = await read_upload_files_text(files)
        if err:
            raise HTTPException(status_code=400, detail={"code": "upload_rejected", "message": err})
        if joined:
            tac_text = joined

    result = tac2iwxxm_decode_tac(tac_text, product=product)
    return msgspec_json_response(
        DecodeTacResponse(
            product=result.product,
            segments=[
                DecodeSegmentModel(
                    start=s.start,
                    end=s.end,
                    code=s.code,
                    explanation=s.explanation,
                )
                for s in result.segments
            ],
            residuals=[DecodeResidualModel(start=r.start, end=r.end, text=r.text) for r in result.residuals],
            summary=result.summary,
        )
    )


@app.post(
    "/api/v1/convert-bulletin",
    tags=["Conversion"],
    response_model=ConvertBulletinResponse,
    responses={
        400: {"description": "Empty bulletin (no reports after split)"},
        401: {"description": "Unauthorized - Invalid or missing authentication token"},
        415: {"description": "Unsupported Media Type — multipart/form-data required"},
        422: {"description": "AHL split failed or missing required fields"},
    },
)
async def convert_bulletin(
    request: Request,
    product: str = Form(..., description="TAC product (required)"),
    files: Optional[List[UploadFile]] = File(None),
    manual_text: str = Form(default="", description="Bulletin string"),
    profile: str = Form(default="annex3", description="Schema profile: annex3 or iwxxm_us"),
    iwxxm_version: str = Form(default="2025-2", description="Target IWXXM version"),
    lint: bool = Form(default=True, description="Run tac-validate before each report convert"),
    user: dict = Depends(verify_supabase_token),
) -> Response:
    """Split a WMO AHL bulletin and convert each TAC report (F6.bulletin / TC-F6-030).

    Partial success is allowed: HTTP 200 when split succeeds even if some reports fail
    (Q6=A). Per-report ``issues`` / ``fixes`` follow lint-style identity (Q7=C).
    """
    content_type = (request.headers.get("content-type") or "").lower()
    if "multipart/form-data" not in content_type:
        raise HTTPException(
            status_code=415,
            detail="POST /api/v1/convert-bulletin requires multipart/form-data",
        )

    bulletin_text = manual_text or ""
    if files:
        joined, err = await read_upload_files_text(files)
        if err:
            raise HTTPException(status_code=400, detail={"code": "upload_rejected", "message": err})
        if joined:
            bulletin_text = joined

    if not bulletin_text.strip():
        raise HTTPException(
            status_code=400,
            detail={"code": "empty_bulletin", "message": "At least one of files or manual_text is required"},
        )

    try:
        split = tac2iwxxm_split_bulletin(bulletin_text, product=product)
    except BulletinSplitError as exc:
        status = 400 if exc.code == "empty_bulletin" else 422
        raise HTTPException(status_code=status, detail={"code": exc.code, "message": exc.message}) from exc

    if split.meta.report_count > MAX_BULLETIN_REPORTS:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "too_many_reports",
                "message": (f"Bulletin contains {split.meta.report_count} reports; limit is {MAX_BULLETIN_REPORTS}"),
            },
        )

    results: list[BulletinReportResultModel] = []
    for index, tac in enumerate(split.reports):
        issues: list[LintIssueModel] = []
        fixes: list[LintFixModel] = []
        xml_out: str | None = None
        ok = True

        if lint:
            lint_report = tac_lint_fn(tac, product=product)
            issues.extend(
                LintIssueModel(
                    severity=i.severity,
                    code=i.code,
                    message=i.message,
                    location=i.location,
                    start=getattr(i, "start", None),
                    end=getattr(i, "end", None),
                )
                for i in lint_report.issues
            )
            fixes.extend(
                LintFixModel(code=f.code, message=f.message, replacement=f.replacement) for f in lint_report.fixes
            )
            if not lint_report.ok:
                ok = False

        if ok:
            try:
                xml_out, _ = convert_metar_tac_with_metadata(
                    tac,
                    iwxxm_version=iwxxm_version,
                    validate=False,
                    product=product,
                    profile=profile,
                )
            except ConversionError as exc:
                ok = False
                xml_out = None
                issues.append(
                    LintIssueModel(
                        severity="error",
                        code="parse_failed",
                        message=str(exc),
                        location=None,
                    )
                )

        results.append(
            BulletinReportResultModel(
                report_index=index,
                ok=ok and xml_out is not None,
                tac_input=tac,
                xml=xml_out if ok else None,
                issues=issues,
                fixes=fixes,
            )
        )

    return msgspec_json_response(
        ConvertBulletinResponse(
            bulletin_meta=BulletinMetaModel(
                ahl=split.meta.ahl,
                report_count=split.meta.report_count,
                tt=split.meta.tt,
                aa=split.meta.aa,
                cccc=split.meta.cccc,
                yygggg=split.meta.yygggg,
                bbb=split.meta.bbb,
            ),
            results=results,
        )
    )


@app.post(
    "/api/v1/ingest-collect",
    tags=["Conversion"],
    responses={
        401: {"description": "Unauthorized"},
        501: {"description": "COLLECT / FTBP ingest not implemented yet (placeholder)"},
    },
)
async def ingest_collect(
    request: Request,
    files: Optional[List[UploadFile]] = File(None),
    manual_text: str = Form(default="", description="COLLECT IWXXM XML or inflated gzip text"),
    profile: str = Form(default="annex3"),
    iwxxm_version: str = Form(default="2025-2"),
    user: dict = Depends(verify_supabase_token),
) -> dict[str, Any]:
    """Placeholder for IWXXM COLLECT / FTBP ingest (ADR-024).

    Accepts uploads (including ``.gz`` via ``read_upload_files_text``) so the operator UI
    can exercise the path; returns HTTP 501 until member extraction + validate is shipped.
    """
    _ = user
    content_type = (request.headers.get("content-type") or "").lower()
    if "multipart/form-data" not in content_type:
        raise HTTPException(
            status_code=415,
            detail="POST /api/v1/ingest-collect requires multipart/form-data",
        )

    payload = manual_text or ""
    if files:
        joined, err = await read_upload_files_text(files)
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


@app.post(
    "/api/v1/validate",
    tags=["Validation"],
    response_model=ValidateResponse,
    responses={
        401: {"description": "Unauthorized - Invalid or missing authentication token"},
    },
)
async def validate_comprehensive(
    request_body: Optional[ValidateRequest] = None,
    manual_text: str = Form(default="", description="METAR TAC text to validate"),
    xml_content: str = Form(
        default="", description="Optional XML to validate (if omitted, TAC will be converted first)"
    ),
    iwxxm_version: str = Form(default="2025-2", description="Target IWXXM version"),
    layers: List[str] = Form(
        default=["ALL"],
        description="Validation layers to run (ALL, or specific: AIRPORT_ICAO, TAC_SYNTAX, XML_WELLFORMED, XML_SCHEMA, SCHEMATRON, GML_REFERENCES, WMO_CODELISTS)",
    ),
    stop_on_error: bool = Form(default=True, description="Stop at first blocking layer failure"),
    profile: str = Form(default="annex3", description="Schema profile: annex3 or iwxxm_us"),
    user: dict = Depends(verify_supabase_token),
):
    """Perform comprehensive 7-layer IWXXM validation.

    Validates METAR TAC input through all 7 validation layers:

    1. **Layer 1 (AIRPORT_ICAO)**: Validates ICAO airport code against database
    2. **Layer 2 (TAC_SYNTAX)**: Validates TAC/METAR syntax basics
    3. **Layer 3 (XML_WELLFORMED)**: Checks XML is well-formed
    4. **Layer 4 (XML_SCHEMA)**: Validates against official IWXXM XSD schemas
    5. **Layer 5 (SCHEMATRON)**: Validates business rules from official Schematron
    6. **Layer 6 (GML_REFERENCES)**: Validates GML internal references
    7. **Layer 7 (WMO_CODELISTS)**: Validates against official WMO RDF codelists

    **Authentication**: Requires valid Supabase JWT token

    **Request Parameters**:
    - **manual_text** (required): METAR TAC text to validate
    - **xml_content** (optional): Pre-converted XML to validate (if omitted, TAC will be converted)
    - **iwxxm_version**: Target IWXXM version (default: "2025-2")
    - **layers**: Validation layers to run (default: ["ALL"])
      - "ALL": Run all 7 layers
      - Or specify: ["AIRPORT_ICAO", "TAC_SYNTAX", "XML_SCHEMA", "SCHEMATRON", ...]
    - **stop_on_error**: Stop at first blocking layer failure (default: true)

    **Response**:
    ```json
    {
      "is_valid": true,
      "version": "2025-2",
      "layers_run": ["AIRPORT_ICAO", "TAC_SYNTAX", "XML_WELLFORMED", "XML_SCHEMA", "SCHEMATRON", "GML_REFERENCES", "WMO_CODELISTS"],
      "layers_passed": ["AIRPORT_ICAO", "TAC_SYNTAX", "XML_WELLFORMED", "XML_SCHEMA", "SCHEMATRON", "GML_REFERENCES", "WMO_CODELISTS"],
      "layers_failed": [],
      "total_issues": 0,
      "issues_by_layer": {},
      "stopped_at_layer": null
    }
    ```
    """
    try:
        # Handle JSON request body
        if request_body is not None:
            xml_content = request_body.iwxxm_xml
            iwxxm_version = request_body.version
            validation_level = request_body.validation_level or "comprehensive"
            profile = request_body.profile or profile
            manual_text = ""  # Don't use form input

            # Map validation_level to layers
            if validation_level == "comprehensive":
                layers = ["ALL"]
            elif validation_level == "schema":
                layers = ["XML_WELLFORMED", "XML_SCHEMA"]
            elif validation_level == "schematron":
                layers = ["SCHEMATRON"]
            elif validation_level == "icao_opmet":
                layers = ["WMO_CODELISTS", "GML_REFERENCES"]
            else:
                layers = ["AIRPORT_ICAO", "TAC_SYNTAX"]

        # Normalize version
        try:
            from .config.iwxxm_versions import get_version_config, normalize_version
        except ImportError:
            from config.iwxxm_versions import get_version_config, normalize_version

        iwxxm_version = normalize_version(iwxxm_version)

        # Validate version is supported
        try:
            get_version_config(iwxxm_version)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Convert TAC to XML if not provided (forward profile; validate afterward)
        if not xml_content:
            try:
                xml_content, _ = convert_metar_tac_with_metadata(
                    manual_text,
                    iwxxm_version=iwxxm_version,
                    validate=False,
                    profile=profile or "annex3",
                )
            except ConversionError as e:
                raise HTTPException(status_code=400, detail=f"Failed to convert TAC to XML: {str(e)}")

        # Thin wrapper: always invoke packages/iwxxm-validate (TC-F6-033 / ADR-015)
        validation_level_name = ""
        if request_body is not None:
            validation_level_name = request_body.validation_level or "comprehensive"
        if validation_level_name == "schematron" or layers == ["SCHEMATRON"]:
            pkg_levels: tuple[str, ...] = ("schematron",)
        elif validation_level_name == "schema" or layers == ["XML_WELLFORMED", "XML_SCHEMA"]:
            pkg_levels = ("xsd",)
        else:
            pkg_levels = ("xsd", "schematron")

        pkg_report = iwxxm_validate_fn(
            xml_content,
            iwxxm_version=iwxxm_version,
            profile=profile or "annex3",
            levels=pkg_levels,
        )

        # Parse layer selection
        selected_layers = []
        if "ALL" in layers:
            selected_layers = list(ValidationLayer)
        else:
            # Convert string names to enum values
            for layer_name in layers:
                try:
                    selected_layers.append(ValidationLayer[layer_name])
                except KeyError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid validation layer: {layer_name}. "
                        f"Valid options: {[l.name for l in ValidationLayer]}",
                    )

        # F11.4 / T3.8: skip orchestrator XSD+Schematron when the package SDK already ran them.
        skip_heavy: set[ValidationLayer] = set()
        if "xsd" in pkg_levels:
            skip_heavy.add(ValidationLayer.XML_SCHEMA)
        if "schematron" in pkg_levels:
            skip_heavy.add(ValidationLayer.SCHEMATRON)
        orch_layers = [layer for layer in selected_layers if layer not in skip_heavy]

        # Run remaining (non-duplicated) orchestrator layers
        orchestrator = get_validation_orchestrator()
        result = orchestrator.validate_complete(
            tac_text=manual_text,
            xml_content=xml_content,
            version=iwxxm_version,
            layers=orch_layers,
            stop_on_error=stop_on_error,
        )

        # Format response (HTTP shape unchanged; package metadata additive)
        return msgspec_json_response(
            {
                "is_valid": result.is_valid,
                "version": result.version,
                "profile": profile or "annex3",
                "layers_run": [layer.name for layer in result.layers_run],
                "layers_passed": [layer.name for layer in result.layers_passed],
                "layers_failed": [layer.name for layer in result.layers_failed],
                "total_issues": len(result.all_issues),
                "issues": [
                    {
                        "layer": issue.layer.name,
                        "level": issue.level.name,
                        "message": issue.message,
                        "location": issue.location,
                        "code": issue.code,
                    }
                    for issue in result.all_issues
                ],
                "issues_by_layer": {
                    layer.name: [
                        {
                            "level": issue.level.name,
                            "message": issue.message,
                            "location": issue.location,
                            "code": issue.code,
                        }
                        for issue in issues
                    ]
                    for layer, issues in result.issues_by_layer.items()
                },
                "stopped_at_layer": result.stopped_at_layer.name if result.stopped_at_layer else None,
                "package_ok": pkg_report.ok,
                "package_issues": [
                    {
                        "layer": issue.layer,
                        "severity": issue.severity,
                        "message": issue.message,
                        "location": issue.location,
                        "code": issue.code,
                    }
                    for issue in pkg_report.issues
                ],
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@app.post(
    "/api/v1/convert",
    response_model=ConversionResponse,
    tags=["Conversion"],
    responses={
        401: {"description": "Unauthorized - Invalid or missing authentication token"},
    },
)
async def convert(
    request: Request,
    files: Any = Depends(parse_files),
    manual_text: str = Form(default="", description="Optional manual text input (METAR TAC format)"),
    iwxxm_version: str = Form(
        default="2025-2",
        description="Target IWXXM version: 2025-2 (latest), 2023-1 (previous), or 2025-1 (auto-remaps to 2025-2)",
    ),
    validate_output: bool = Form(default=False, description="Enable full 7-layer IWXXM validation after conversion"),
    validation_level: str = Form(
        default="basic", description="Validation depth: basic, schema, schematron, icao_opmet, comprehensive"
    ),
    stop_on_error: bool = Form(default=False, description="Stop processing remaining inputs after first error"),
    bulletin_id: str = Form(default="", description="Optional bulletin identifier"),
    issuing_center: str = Form(default="", description="Optional issuing centre ICAO code"),
    lint: bool = Form(default=True, description="Run tac-validate before convert (Q14=C; default on)"),
    product: str = Form(default="METAR", description="TAC product (required for F6; default METAR for legacy)"),
    profile: str = Form(default="annex3", description="Schema profile: annex3 or iwxxm_us"),
    preview: bool = Form(
        default=False,
        description="Soft-preview mode (ADR-022): best-effort IWXXM + failed_spans on partial failure",
    ),
    include_nil_reasons: bool = Form(
        default=True,
        description="When false, prefer omitting nilReason attributes (engine may still emit NIL report shells; ADR-024)",
    ),
    log_level: str = Form(
        default="INFO",
        description="Minimum severity for conversion/validation/lint process issues echoed to the client",
    ),
    user: dict = Depends(verify_supabase_token),
) -> Response:
    logger.info(
        "[CONVERT] Request received method=%s path=%s origin=%s content_type=%s has_auth_header=%s",
        request.method,
        request.url.path,
        request.headers.get("origin", "none"),
        request.headers.get("content-type", "none"),
        bool(request.headers.get("authorization")),
    )

    # Try to parse JSON body if Content-Type is application/json
    request_body = None
    if request.headers.get("content-type", "").startswith("application/json"):
        logger.info("[CONVERT] Processing JSON body payload")
        try:
            body_data = await request.json()
        except Exception as e:
            logger.warning("[CONVERT] Invalid JSON body: %s", str(e))
            raise HTTPException(
                status_code=422,
                detail=ErrorDetail(
                    message="Invalid JSON in request body",
                    errors=[str(e)],
                    issues=[
                        ConversionIssue(
                            source="request",
                            message=str(e),
                            severity=ConversionIssueSeverity.ERROR,
                            hint="Send a valid JSON payload with a 'metars' array.",
                            code="INVALID_JSON_BODY",
                        )
                    ],
                    total_errors=1,
                ).model_dump(),
            )

        try:
            request_body = ConversionRequest(**body_data)
        except Exception as e:
            # Pydantic validation error - return 422
            logger.warning("[CONVERT] JSON validation error: %s", str(e))
            raise HTTPException(
                status_code=422,
                detail=ErrorDetail(
                    message="Validation error in request body",
                    errors=[str(e)],
                    issues=[
                        ConversionIssue(
                            source="request",
                            message=str(e),
                            severity=ConversionIssueSeverity.ERROR,
                            hint="Provide valid JSON fields (for example: 'metars', 'version').",
                            code="REQUEST_VALIDATION_ERROR",
                        )
                    ],
                    total_errors=1,
                ).model_dump(),
            )
    """Convert METAR/SPECI TAC text to IWXXM XML format.

    Converts one or more METAR TAC messages to IWXXM XML format. Supports:
    - Manual text input via form field
    - File uploads (text files)
    - Batch processing (multiple files)
    - Dynamic IWXXM version selection
    - Input validation (ICAO code and TAC syntax)
    - Optional output validation (full 7-layer IWXXM validation)

    **Authentication**: Requires valid Supabase JWT token in Authorization header

    **Request Parameters**:
    - **files** (array): Optional uploaded text files containing METAR TAC
    - **manual_text** (string): Optional manual text input
    - **iwxxm_version** (string): Target IWXXM version (default: "2025-2")
      - "2025-2": Latest IWXXM version (recommended)
      - "2023-1": Previous stable release
      - "2025-1": Auto-remaps to 2025-2
      - Pre-2023 versions (2021-2, 2018, 2016, etc.) are deprecated and will be rejected
    - **validate_output** (boolean): Enable full IWXXM validation after conversion (default: false)
      - When true, runs layers 3-7 (XML wellformed, XSD schema, Schematron, GML, codelists)
      - Validation issues are logged but don't prevent conversion results

    **Validation**:
    - **Input Validation (Always On)**:
      - Layer 1: ICAO airport code validation
      - Layer 2: TAC syntax validation
    - **Output Validation (Optional)**:
      - Layer 3: XML well-formedness
      - Layer 4: XSD schema validation
      - Layer 5: Schematron business rules
      - Layer 6: GML reference validation
      - Layer 7: WMO codelist validation

    **Response**:
    - **results** (array): Successfully converted IWXXM XML documents
    - **errors** (array): Error messages for failed conversions
    - **total_processed** (integer): Total inputs processed
    - **successful** (integer): Number of successful conversions
    - **failed** (integer): Number of failed conversions

    **Example Success Response**:
    ```json
    {
      "results": [
        {
          "name": "manual_input.txt",
          "content": "<?xml version='1.0'?>...",
          "source": "manual",
          "size_bytes": 1452,
          "iwxxm_version": "2025-2"
        }
      ],
      "errors": [],
      "total_processed": 1,
      "successful": 1,
      "failed": 0
    }
    ```

    **Example Failure Response**:
    ```json
    {
      "results": [
        {
          "name": "valid_file.txt",
          "content": "<?xml version='1.0'?>...",
          "source": "valid_file.txt",
          "size_bytes": 1200,
          "iwxxm_version": "2025-2"
        }
      ],
      "errors": [
        "invalid_file.txt: Unknown airport code: ZZZZ"
      ],
      "total_processed": 2,
      "successful": 1,
      "failed": 1
    }
    ```
    """
    # Handle JSON request body (for metars list)
    if request_body is not None:
        metars = request_body.metars
        iwxxm_version = request_body.version
        validation_level = request_body.validation_level or "basic"
        stop_on_error = request_body.stop_on_error
        bulletin_id = request_body.bulletin_id or ""
        issuing_center = request_body.issuing_center or ""
        preview = bool(getattr(request_body, "preview", False))
        body_product = getattr(request_body, "product", None)
        if body_product is not None:
            product = body_product
        body_profile = getattr(request_body, "profile", None)
        if body_profile is not None:
            profile = body_profile
        manual_text = ""  # Override form input
        files = None  # Override file input

        logger.info(
            "[CONVERT] JSON mode metars=%s version=%s validation_level=%s preview=%s",
            len(metars or []),
            iwxxm_version,
            validation_level,
            preview,
        )

        # Map validation_level to validate_output
        validate_output = validation_level in ["comprehensive", "schematron", "icao_opmet", "schema"]

    # Q14=C: lint default on — soft-wire tac-validate (hard fails use POST /lint-tac)
    if lint:
        sample = manual_text.strip() if manual_text else ""
        if request_body is not None and getattr(request_body, "metars", None):
            sample = (request_body.metars[0] or "").strip() if request_body.metars else sample
        if sample:
            lint_report = tac_lint_fn(sample, product=product or "METAR")
            if not lint_report.ok:
                logger.info(
                    "[CONVERT] tac-validate issues (non-blocking soft path): %s",
                    [i.code for i in lint_report.issues],
                )

    validation_level = normalize_validation_level(validation_level)
    validate_output = bool(validate_output) or validation_level in [
        "comprehensive",
        "schematron",
        "icao_opmet",
        "schema",
    ]
    bulletin_id = normalize_code(bulletin_id, 6) or ""
    issuing_center = normalize_code(issuing_center, 4) or ""
    log_level_norm = (log_level or "INFO").strip().upper()
    logger.info(
        "[CONVERT] include_nil_reasons=%s log_level=%s",
        include_nil_reasons,
        log_level_norm,
    )
    if not include_nil_reasons:
        logger.info(
            "[CONVERT] include_nil_reasons=false accepted; tac2iwxxm may still emit "
            "nilReason on NIL reports until engine honors the flag (ADR-024 placeholder)",
        )

    # Validate and normalize IWXXM version
    try:
        from .config.iwxxm_versions import get_version_config, normalize_version
    except ImportError:
        from config.iwxxm_versions import get_version_config, normalize_version

    try:
        iwxxm_version = normalize_version(iwxxm_version)
        get_version_config(iwxxm_version)
    except ValueError as e:
        logger.warning("[CONVERT] Invalid IWXXM version requested: %s", iwxxm_version)
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(
                message=f"Invalid IWXXM version: {e}",
                errors=[str(e)],
                issues=[
                    ConversionIssue(
                        source="request",
                        message=str(e),
                        severity=ConversionIssueSeverity.ERROR,
                        hint="Use a supported IWXXM version such as 2025-2 or 2023-1.",
                        code="INVALID_IWXXM_VERSION",
                    )
                ],
                total_errors=1,
            ).model_dump(),
        )

    results: List[ConversionResult] = []
    errors: List[str] = []
    issues: List[ConversionIssue] = []
    total_inputs = 0
    preview_failed_spans: List[FailedSpan] = []
    preview_saw_soft_fail = False

    def absorb_convert_issues(soft: dict, *, source: str) -> None:
        """Echo tac2iwxxm non-fatal convert issues (e.g. REMARKS_EXCLUDED) to the client."""
        for raw in soft.get("convert_issues") or []:
            data = raw.model_dump() if hasattr(raw, "model_dump") else dict(raw)
            sev_raw = str(data.get("severity") or "info").strip().lower()
            if "." in sev_raw:
                sev_raw = sev_raw.rsplit(".", 1)[-1]
            if sev_raw == "error":
                severity = ConversionIssueSeverity.ERROR
            elif sev_raw == "warning":
                severity = ConversionIssueSeverity.WARNING
            else:
                severity = ConversionIssueSeverity.INFO
            code = data.get("code") or None
            add_issue(
                source=source,
                message=str(data.get("message") or code or "Convert issue"),
                severity=severity,
                hint=("Use profile=iwxxm_us to retain US REMARKS in IWXXM." if code == "REMARKS_EXCLUDED" else None),
                code=code,
                location=data.get("location"),
            )

    def absorb_soft_preview(soft: dict, *, base_offset: int = 0, source: str | None = None) -> None:
        """Merge soft-preview envelope fields from convert_metar_tac_with_metadata.

        ``base_offset`` shifts entry-local span offsets into the original
        ``manual_text`` buffer (multi-line editor documents).
        Always absorbs ``convert_issues`` when ``source`` is provided (EV-013 / #667).
        """
        nonlocal preview_saw_soft_fail
        if not soft:
            return
        if source:
            absorb_convert_issues(soft, source=source)
        if not preview:
            return
        if soft.get("ok") is False:
            preview_saw_soft_fail = True
            for span in soft.get("failed_spans") or []:
                data = span.model_dump() if hasattr(span, "model_dump") else dict(span)
                if base_offset:
                    if data.get("start") is not None:
                        data["start"] = int(data["start"]) + base_offset
                    if data.get("end") is not None:
                        data["end"] = int(data["end"]) + base_offset
                preview_failed_spans.append(FailedSpan(**data))

    def record_preview_layer12_soft_fail(aggregated_result, tac_text: str = "", *, base_offset: int = 0) -> None:
        """Mark soft-preview Layer 1–2 failure and copy spans when present (ADR-022)."""
        nonlocal preview_saw_soft_fail
        preview_saw_soft_fail = True
        before = len(preview_failed_spans)
        if aggregated_result:
            for layer_result in getattr(aggregated_result, "results", []):
                for validation_issue in getattr(layer_result, "issues", []):
                    start = getattr(validation_issue, "start", None)
                    end = getattr(validation_issue, "end", None)
                    if start is None or end is None:
                        continue
                    preview_failed_spans.append(
                        FailedSpan(
                            start=int(start) + base_offset,
                            end=int(end) + base_offset,
                            code=getattr(validation_issue, "code", None),
                            message=str(getattr(validation_issue, "message", "") or "") or None,
                        )
                    )
        if len(preview_failed_spans) == before and tac_text:
            preview_failed_spans.append(
                FailedSpan(
                    start=base_offset,
                    end=base_offset + len(tac_text),
                    code="LAYER12_SOFT_FAIL",
                    message="Input failed ICAO/TAC Layer 1–2 checks; soft-preview continuing",
                )
            )

    def add_issue(
        source: str,
        message: str,
        severity: ConversionIssueSeverity = ConversionIssueSeverity.ERROR,
        hint: Optional[str] = None,
        code: Optional[str] = None,
        layer: Optional[str] = None,
        location: Optional[str] = None,
    ) -> None:
        issues.append(
            ConversionIssue(
                source=source,
                message=message,
                severity=severity,
                hint=hint,
                code=code,
                layer=layer,
                location=location,
            )
        )

    def add_aggregated_validation_issues(source: str, aggregated_result) -> None:
        if not aggregated_result:  # pragma: no cover - defensive guard
            return
        for layer_result in getattr(aggregated_result, "results", []):
            for validation_issue in getattr(layer_result, "issues", []):
                severity = ConversionIssueSeverity.WARNING
                level = str(getattr(validation_issue, "level", "")).lower()
                if level == "error" or level == "critical":
                    severity = ConversionIssueSeverity.ERROR
                elif level == "info":
                    severity = ConversionIssueSeverity.INFO
                add_issue(
                    source=source,
                    message=str(getattr(validation_issue, "message", "Validation issue")),
                    severity=severity,
                    hint=getattr(validation_issue, "suggestion", None),
                    code=getattr(validation_issue, "code", None),
                    layer=str(getattr(validation_issue, "layer", "")) or None,
                    location=getattr(validation_issue, "location", None),
                )

    def emit_recent_wx_issues(source: str, norm_warnings: List[dict]) -> None:
        """Emit structured conversion issues for recent-weather rewrites."""
        for warning in norm_warnings:
            add_issue(
                source=source,
                message=(
                    f"Recent weather token '{warning['original']}' rewritten to "
                    f"'{warning['replacement']}' for WMO D-6 compliance "
                    f"(truncated descriptor-only code; UP phenomenon added)."
                ),
                severity=ConversionIssueSeverity.INFO,
                hint=(
                    f"'{warning['original']}' is not a valid Annex 3 recent weather code. "
                    f"Using '{warning['replacement']}' (unidentified precipitation) instead."
                ),
                code="RECENT_WX_NORMALIZED",
                layer="tac_normalization",
            )

    # Initialize validation service for input validation
    validation_service = ValidationService()

    # Initialize validation orchestrator for output validation if requested
    validation_orchestrator = get_validation_orchestrator() if validate_output else None

    # Handle JSON request body with metars list
    metars_list = []
    if request_body is not None and request_body.metars:
        metars_list = request_body.metars

    manual_with_offsets = manual_entries_with_offsets(manual_text or "")
    manual_entries = [entry for entry, _ in manual_with_offsets]

    request_metadata = {
        "bulletin_id": bulletin_id,
        "issuing_center": issuing_center,
        "validation_level": validation_level,
        "stop_on_error": bool(stop_on_error),
    }

    logger.info(
        "[CONVERT] Input summary files=%s manual_entries=%s json_metars=%s validate_output=%s validation_level=%s stop_on_error=%s iwxxm_version=%s bulletin_id=%s issuing_center=%s",
        len(files or []),
        len(manual_entries),
        len(metars_list),
        validate_output,
        validation_level,
        bool(stop_on_error),
        iwxxm_version,
        bulletin_id,
        issuing_center,
    )

    if not (metars_list or manual_entries or (files and len(files) > 0)):
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(
                message="No conversion input provided",
                errors=["Provide at least one METAR TAC input via manual_text, files, or JSON metars."],
                issues=[
                    ConversionIssue(
                        source="request",
                        message="Empty conversion request",
                        severity=ConversionIssueSeverity.ERROR,
                        hint="Send manual_text, files, or JSON metars in the request body.",
                        code="NO_INPUT",
                    )
                ],
                total_errors=1,
            ).model_dump(),
        )

    # Process metars from JSON request body
    for metar_text in metars_list:
        if not metar_text.strip():
            continue

        normalized_metar_text, norm_warnings = normalize_recent_weather_tokens(metar_text.strip())

        total_inputs += 1
        start_time = None
        translation_id = None
        metar_name = f"metar_{total_inputs}.txt"
        try:
            # Validate METAR input (Layers 1-2: ICAO and TAC syntax)
            layer12_abort = False
            try:
                if _product_uses_metar_tac_layers(product):
                    validation_result = validation_service.validate_all_layers(normalized_metar_text)
                    if not validation_result.passed:
                        # Build summary from validation result
                        validation_summary = f"{validation_result.total_issues} validation issue(s) found"
                        add_issue(
                            source=metar_name,
                            message=f"Validation failed: {validation_summary}",
                            severity=ConversionIssueSeverity.ERROR,
                            hint="Fix TAC format and ICAO code issues, then retry conversion.",
                            code="VALIDATION_FAILED",
                        )
                        add_aggregated_validation_issues(metar_name, validation_result)
                        if preview:
                            # ADR-022: do not hard-abort; continue to best-effort convert.
                            record_preview_layer12_soft_fail(validation_result, normalized_metar_text)
                        else:
                            error_msg = f"{metar_name}: Validation failed - {validation_summary}"
                            errors.append(error_msg)
                            # Log failed validation
                            try:
                                translation_id = await statistics_service.log_translation(
                                    tac_message=metar_text.strip(),
                                    iwxxm_output=None,
                                    iwxxm_version=iwxxm_version,
                                    translation_status=TranslationStatus.FAILED,
                                    validation_layers_passed=[],
                                    validation_errors={"validation": validation_summary},
                                    translation_duration_ms=0,
                                    icao_airport_code=extract_airport_code(metar_text.strip()),
                                    user_id=user.get("sub"),
                                )
                                airport_code = extract_airport_code(metar_text.strip())
                                await webhook_service.notify_translation_failed(
                                    translation_id=translation_id,
                                    airport_code=airport_code or "UNKNOWN",
                                    error_type="validation_failed",
                                    error_message=validation_summary,
                                )
                            except Exception as log_err:
                                logger.error(f"Failed to log failed translation: {log_err}")
                            layer12_abort = True
            except ValidationServiceError as ve:
                add_issue(
                    source=metar_name,
                    message=str(ve),
                    severity=ConversionIssueSeverity.ERROR,
                    hint="Ensure the METAR starts with METAR/SPECI and includes a valid ICAO station and timestamp.",
                    code="VALIDATION_SERVICE_ERROR",
                )
                if preview:
                    record_preview_layer12_soft_fail(None, normalized_metar_text)
                else:
                    errors.append(f"{metar_name}: {str(ve)}")
                    # Log validation error
                    try:
                        translation_id = await statistics_service.log_translation(
                            tac_message=metar_text.strip(),
                            iwxxm_output=None,
                            iwxxm_version=iwxxm_version,
                            translation_status=TranslationStatus.FAILED,
                            validation_layers_passed=[],
                            validation_errors={"error": str(ve)},
                            translation_duration_ms=0,
                            icao_airport_code=extract_airport_code(metar_text.strip()),
                            user_id=user.get("sub"),
                        )
                        airport_code = extract_airport_code(metar_text.strip())
                        await webhook_service.notify_translation_failed(
                            translation_id=translation_id,
                            airport_code=airport_code or "UNKNOWN",
                            error_type="validation_error",
                            error_message=str(ve),
                        )
                    except Exception as log_err:
                        logger.error(f"Failed to log validation error: {log_err}")
                    layer12_abort = True

            if layer12_abort:
                if stop_on_error:
                    break
                continue

            # Start timing for successful conversion
            start_time = time.perf_counter()

            emit_recent_wx_issues(metar_name, norm_warnings)

            # Convert METAR to IWXXM
            try:
                soft_preview_buf = {}
                iwxxm_content, _ = convert_metar_tac_with_metadata(
                    normalized_metar_text,
                    iwxxm_version=iwxxm_version,
                    lenient=False,
                    product=product,
                    profile=profile,
                    preview=preview,
                    soft_preview_out=soft_preview_buf,
                )
                absorb_soft_preview(soft_preview_buf, source=metar_name)
                if preview and soft_preview_buf.get("ok") is False:
                    add_issue(
                        source=metar_name,
                        message="Soft-preview: conversion incomplete",
                        severity=ConversionIssueSeverity.ERROR,
                        hint="Fix failed TAC spans and retry hard convert before publish.",
                        code="SOFT_PREVIEW_PARTIAL",
                    )

                # Optional output validation (Layers 3-7); F11.4: SDK owns XSD+Schematron
                validation_layers_passed = [ValidationLayer.AIRPORT_ICAO, ValidationLayer.TAC_SYNTAX]

                if validation_orchestrator:
                    pkg_out = iwxxm_validate_fn(
                        iwxxm_content,
                        iwxxm_version=iwxxm_version,
                        profile=profile or "annex3",
                        levels=("xsd", "schematron"),
                    )
                    validation_result = validation_orchestrator.validate(
                        iwxxm_content,
                        iwxxm_version=iwxxm_version,
                        layers=[
                            ValidationLayer.XML_WELLFORMED,
                            ValidationLayer.GML_REFERENCES,
                            ValidationLayer.WMO_CODELISTS,
                        ],
                    )
                    if pkg_out.ok and validation_result.passed:
                        validation_layers_passed.extend(
                            [
                                ValidationLayer.XML_WELLFORMED,
                                ValidationLayer.XML_SCHEMA,
                                ValidationLayer.SCHEMATRON,
                                ValidationLayer.GML_REFERENCES,
                                ValidationLayer.WMO_CODELISTS,
                            ]
                        )

                # Add to results
                result = ConversionResult(
                    name=metar_name,
                    content=iwxxm_content,
                    tac_input=metar_text.strip(),
                    source="json",
                    size_bytes=len(iwxxm_content.encode("utf-8")),
                )
                results.append(result)

                # Log successful (or soft-preview partial) translation
                try:
                    end_time = time.perf_counter()
                    duration_ms = int(round((end_time - start_time) * 1000))
                    soft_incomplete = bool(preview and soft_preview_buf.get("ok") is False)

                    translation_id = await statistics_service.log_translation(
                        tac_message=metar_text.strip(),
                        iwxxm_output=iwxxm_content,
                        iwxxm_version=iwxxm_version,
                        translation_status=(TranslationStatus.FAILED if soft_incomplete else TranslationStatus.SUCCESS),
                        validation_layers_passed=validation_layers_passed,
                        translation_duration_ms=duration_ms,
                        icao_airport_code=extract_airport_code(normalized_metar_text),
                        user_id=user.get("sub"),
                    )

                    airport_code = extract_airport_code(normalized_metar_text)
                    if soft_incomplete:
                        await webhook_service.notify_translation_failed(
                            translation_id=translation_id,
                            airport_code=airport_code or "UNKNOWN",
                            error_type="soft_preview_partial",
                            error_message="Soft-preview conversion incomplete",
                        )
                    else:
                        await webhook_service.notify_translation_completed(
                            translation_id=translation_id,
                            airport_code=airport_code or "UNKNOWN",
                            iwxxm_version=iwxxm_version,
                            file_size_bytes=len(iwxxm_content.encode("utf-8")),
                            duration_ms=duration_ms,
                        )
                except Exception as log_err:
                    logger.error(f"Failed to log successful translation: {log_err}")

            except ConversionError as ce:
                error_msg = f"{metar_name}: Conversion error - {str(ce)}"
                errors.append(error_msg)
                add_issue(
                    source=metar_name,
                    message=f"Conversion error: {ce}",
                    severity=ConversionIssueSeverity.ERROR,
                    hint="Check METAR TAC structure and required tokens (station/time/wind).",
                    code="CONVERSION_ERROR",
                )
                logger.error(error_msg)
                try:
                    end_time = time.perf_counter()
                    duration_ms = int(round((end_time - start_time) * 1000)) if start_time else 0

                    await statistics_service.log_translation(
                        tac_message=metar_text.strip(),
                        iwxxm_output=None,
                        iwxxm_version=iwxxm_version,
                        translation_status=TranslationStatus.FAILED,
                        validation_layers_passed=[ValidationLayer.AIRPORT_ICAO, ValidationLayer.TAC_SYNTAX],
                        validation_errors={"error": str(ce)},
                        translation_duration_ms=duration_ms,
                        icao_airport_code=extract_airport_code(normalized_metar_text),
                        user_id=user.get("sub"),
                    )

                    airport_code = extract_airport_code(normalized_metar_text)
                    await webhook_service.notify_translation_failed(
                        translation_id=translation_id or "unknown",
                        airport_code=airport_code or "UNKNOWN",
                        error_type="conversion_error",
                        error_message=str(ce),
                    )
                except Exception as log_err:
                    logger.error(f"Failed to log conversion error: {log_err}")
                if stop_on_error:
                    break
            except Exception as e:
                error_msg = f"{metar_name}: Unexpected error - {str(e)}"
                errors.append(error_msg)
                add_issue(
                    source=metar_name,
                    message=f"Unexpected backend error: {e}",
                    severity=ConversionIssueSeverity.ERROR,
                    hint="Retry once. If it persists, contact support with this message.",
                    code="UNEXPECTED_BACKEND_ERROR",
                )
                logger.exception(error_msg)
                if stop_on_error:
                    break
        except Exception as e:
            error_msg = f"{metar_name}: Unhandled error - {str(e)}"
            errors.append(error_msg)
            add_issue(
                source=metar_name,
                message=f"Unhandled backend error: {e}",
                severity=ConversionIssueSeverity.ERROR,
                hint="Retry once. If it persists, contact support with this message.",
                code="UNHANDLED_BACKEND_ERROR",
            )
            logger.exception(error_msg)
            if stop_on_error:
                break

    for manual_index, (manual_entry, entry_offset) in enumerate(manual_with_offsets, 1):
        total_inputs += 1
        manual_source = f"manual_input_{manual_index}" if len(manual_with_offsets) > 1 else "manual_input"
        manual_name = f"{manual_source}.txt"
        start_time = None
        translation_id = None
        # Normalize once and share this result across validation and conversion.
        _normalized_entry, _norm_warnings = normalize_recent_weather_tokens(manual_entry)

        try:
            try:
                if _product_uses_metar_tac_layers(product):
                    validation_result = validation_service.validate_all_layers(_normalized_entry)
                    if not validation_result.passed:
                        validation_summary = f"{validation_result.total_issues} validation issue(s) found"
                        add_issue(
                            source=manual_source,
                            message=f"Validation failed: {validation_summary}",
                            severity=ConversionIssueSeverity.ERROR,
                            hint="Fix TAC format and ICAO code issues, then retry conversion.",
                            code="VALIDATION_FAILED",
                        )
                        add_aggregated_validation_issues(manual_source, validation_result)
                        if preview:
                            # ADR-022: soft-preview continues to best-effort convert.
                            record_preview_layer12_soft_fail(
                                validation_result, _normalized_entry, base_offset=entry_offset
                            )
                        else:
                            errors.append(f"{manual_source}: Validation failed - {validation_summary}")
                            try:
                                translation_id = await statistics_service.log_translation(
                                    tac_message=manual_entry,
                                    iwxxm_output=None,
                                    iwxxm_version=iwxxm_version,
                                    translation_status=TranslationStatus.FAILED,
                                    validation_layers_passed=[],
                                    validation_errors={"validation": validation_summary},
                                    translation_duration_ms=0,
                                    icao_airport_code=extract_airport_code(manual_entry),
                                    user_id=user.get("sub"),
                                )
                                airport_code = extract_airport_code(manual_entry)
                                await webhook_service.notify_translation_failed(
                                    translation_id=translation_id,
                                    airport_code=airport_code or "UNKNOWN",
                                    error_type="validation_failed",
                                    error_message=validation_summary,
                                )
                            except Exception as log_err:
                                logger.error(f"Failed to log failed translation: {log_err}")
                            if stop_on_error:
                                break
                            continue
            except ValidationServiceError as ve:
                add_issue(
                    source=manual_source,
                    message=str(ve),
                    severity=ConversionIssueSeverity.ERROR,
                    hint="Ensure the METAR starts with METAR/SPECI and includes a valid ICAO station and timestamp.",
                    code="VALIDATION_SERVICE_ERROR",
                )
                if preview:
                    record_preview_layer12_soft_fail(None, _normalized_entry, base_offset=entry_offset)
                else:
                    errors.append(f"{manual_source}: {str(ve)}")
                    try:
                        translation_id = await statistics_service.log_translation(
                            tac_message=manual_entry,
                            iwxxm_output=None,
                            iwxxm_version=iwxxm_version,
                            translation_status=TranslationStatus.FAILED,
                            validation_layers_passed=[],
                            validation_errors={"error": str(ve)},
                            translation_duration_ms=0,
                            icao_airport_code=extract_airport_code(manual_entry),
                            user_id=user.get("sub"),
                        )
                        airport_code = extract_airport_code(manual_entry)
                        await webhook_service.notify_translation_failed(
                            translation_id=translation_id,
                            airport_code=airport_code or "UNKNOWN",
                            error_type="validation_error",
                            error_message=str(ve),
                        )
                    except Exception as log_err:
                        logger.error(f"Failed to log validation error: {log_err}")
                    if stop_on_error:
                        break
                    continue

            start_time = time.perf_counter()

            emit_recent_wx_issues(manual_source, _norm_warnings)

            soft_preview_buf = {}
            xml_text, validation_result_from_conversion = convert_metar_tac_with_metadata(
                _normalized_entry,
                iwxxm_version=iwxxm_version,
                validate=validate_output,
                lenient=False,  # normalization already applied above
                product=product,
                profile=profile,
                preview=preview,
                soft_preview_out=soft_preview_buf,
            )
            absorb_soft_preview(soft_preview_buf, base_offset=entry_offset, source=manual_source)
            if preview and soft_preview_buf.get("ok") is False:
                add_issue(
                    source=manual_source,
                    message="Soft-preview: conversion incomplete",
                    severity=ConversionIssueSeverity.ERROR,
                    hint="Fix failed TAC spans and retry hard convert before publish.",
                    code="SOFT_PREVIEW_PARTIAL",
                )

            duration_ms = int((time.perf_counter() - start_time) * 1000)
            layers_passed = [ValidationLayer.AIRPORT_ICAO.value, ValidationLayer.TAC_SYNTAX.value]
            validation_errors_dict = {}

            if validate_output and validation_result_from_conversion:
                if validation_result_from_conversion.is_valid:
                    for layer in ValidationLayer:
                        if layer.value not in layers_passed:
                            layers_passed.append(layer.value)
                else:
                    warning_msg = (
                        f"{manual_source}: IWXXM validation issues found - "
                        f"{len(validation_result_from_conversion.all_issues)} issues"
                    )
                    logger.warning(warning_msg)
                    add_issue(
                        source=manual_source,
                        message=warning_msg,
                        severity=ConversionIssueSeverity.WARNING,
                        hint="Output converted, but IWXXM validation reported issues.",
                        code="OUTPUT_VALIDATION_WARNING",
                        layer="iwxxm_output",
                    )
                    validation_errors_dict = {
                        "validation_issues": [str(issue) for issue in validation_result_from_conversion.all_issues[:10]]
                    }

            try:
                soft_incomplete = bool(preview and soft_preview_buf.get("ok") is False)
                translation_id = await statistics_service.log_translation(
                    tac_message=manual_entry,
                    iwxxm_output=xml_text,
                    iwxxm_version=iwxxm_version,
                    translation_status=(TranslationStatus.FAILED if soft_incomplete else TranslationStatus.SUCCESS),
                    validation_layers_passed=layers_passed,
                    validation_errors=validation_errors_dict if validation_errors_dict else None,
                    translation_duration_ms=duration_ms,
                    icao_airport_code=extract_airport_code(manual_entry),
                    user_id=user.get("sub"),
                )
                airport_code = extract_airport_code(manual_entry)
                icao_region = get_icao_region(airport_code) if airport_code else "UNKNOWN"
                if soft_incomplete:
                    await webhook_service.notify_translation_failed(
                        translation_id=translation_id,
                        airport_code=airport_code or "UNKNOWN",
                        error_type="soft_preview_partial",
                        error_message="Soft-preview conversion incomplete",
                    )
                else:
                    await webhook_service.notify_translation_success(
                        translation_id=translation_id,
                        airport_code=airport_code or "UNKNOWN",
                        icao_region=icao_region,
                        iwxxm_version=iwxxm_version,
                        duration_ms=duration_ms,
                    )
            except Exception as log_err:
                logger.error(f"Failed to log successful translation: {log_err}")

            results.append(
                ConversionResult(
                    name=manual_name,
                    content=xml_text,
                    tac_input=manual_entry.strip(),
                    source=manual_source,
                    size_bytes=len(xml_text.encode("utf-8")),
                )
            )
        except ConversionError as e:
            errors.append(f"{manual_source}: {e}")
            add_issue(
                source=manual_source,
                message=str(e),
                severity=ConversionIssueSeverity.ERROR,
                hint="Check METAR TAC structure and required tokens (station/time/wind).",
                code="CONVERSION_ERROR",
            )
            if stop_on_error:
                break

    # Process uploaded files (if any)
    if files:
        for uf in files:
            total_inputs += 1
            start_time = None
            translation_id = None
            data = ""
            try:
                data, read_error = await read_uploaded_text(uf)
                source_name = uf.filename or "unknown_file"

                if read_error:
                    errors.append(f"{source_name}: {read_error}")
                    add_issue(
                        source=source_name,
                        message=f"Invalid input file: {read_error}",
                        severity=ConversionIssueSeverity.ERROR,
                        hint="Upload a UTF-8 file containing a METAR/SPECI TAC message.",
                        code="INVALID_INPUT_FILE",
                    )
                    if stop_on_error:
                        break
                    continue

                xml_rejection = classify_and_validate_upload_content(
                    filename=uf.filename,
                    content=data,
                    iwxxm_version=iwxxm_version,
                    endpoint_path="/api/v1/convert",
                    validation_orchestrator=validation_orchestrator,
                )
                if xml_rejection:
                    errors.append(f"{source_name}: {xml_rejection['message']}")
                    add_issue(
                        source=source_name,
                        message=xml_rejection["message"],
                        severity=ConversionIssueSeverity.ERROR,
                        hint=xml_rejection["hint"],
                        code=xml_rejection["code"],
                        layer=xml_rejection["layer"],
                    )
                    if stop_on_error:
                        break
                    continue

                # Validate METAR input (Layers 1-2: ICAO and TAC syntax)
                try:
                    if _product_uses_metar_tac_layers(product):
                        validation_result = validation_service.validate_all_layers((data or "").strip())
                        if not validation_result.passed:
                            validation_summary = f"{validation_result.total_issues} validation issue(s) found"
                            add_issue(
                                source=source_name,
                                message=f"Validation failed: {validation_summary}",
                                severity=ConversionIssueSeverity.ERROR,
                                hint="Fix TAC format and ICAO code issues, then retry conversion.",
                                code="VALIDATION_FAILED",
                            )
                            add_aggregated_validation_issues(source_name, validation_result)
                            if preview:
                                record_preview_layer12_soft_fail(validation_result, (data or "").strip())
                            else:
                                error_msg = f"{source_name}: Validation failed - {validation_summary}"
                                errors.append(error_msg)
                                try:
                                    translation_id = await statistics_service.log_translation(
                                        tac_message=(data or "").strip(),
                                        iwxxm_output=None,
                                        iwxxm_version=iwxxm_version,
                                        translation_status=TranslationStatus.FAILED,
                                        validation_layers_passed=[],
                                        validation_errors={"validation": validation_summary},
                                        translation_duration_ms=0,
                                        icao_airport_code=extract_airport_code((data or "").strip()),
                                        user_id=user.get("sub"),
                                    )
                                    airport_code = extract_airport_code((data or "").strip())
                                    await webhook_service.notify_translation_failed(
                                        translation_id=translation_id,
                                        airport_code=airport_code or "UNKNOWN",
                                        error_type="validation_failed",
                                        error_message=validation_summary,
                                    )
                                except Exception as log_err:
                                    logger.error(f"Failed to log failed translation: {log_err}")
                                continue
                except ValidationServiceError as ve:
                    add_issue(
                        source=source_name,
                        message=str(ve),
                        severity=ConversionIssueSeverity.ERROR,
                        hint="Ensure the METAR starts with METAR/SPECI and includes a valid ICAO station and timestamp.",
                        code="VALIDATION_SERVICE_ERROR",
                    )
                    if preview:
                        record_preview_layer12_soft_fail(None, (data or "").strip())
                    else:
                        errors.append(f"{uf.filename}: {str(ve)}")
                        try:
                            translation_id = await statistics_service.log_translation(
                                tac_message=(data or "").strip(),
                                iwxxm_output=None,
                                iwxxm_version=iwxxm_version,
                                translation_status=TranslationStatus.FAILED,
                                validation_layers_passed=[],
                                validation_errors={"error": str(ve)},
                                translation_duration_ms=0,
                                icao_airport_code=extract_airport_code((data or "").strip()),
                                user_id=user.get("sub"),
                            )
                            airport_code = extract_airport_code((data or "").strip())
                            await webhook_service.notify_translation_failed(
                                translation_id=translation_id,
                                airport_code=airport_code or "UNKNOWN",
                                error_type="validation_error",
                                error_message=str(ve),
                            )
                        except Exception as log_err:
                            logger.error(f"Failed to log validation error: {log_err}")
                        if stop_on_error:
                            break
                        continue

                # Start timing for successful conversion

                start_time = time.perf_counter()

                # Only convert if validation passed
                soft_preview_buf = {}
                xml_text, _ = convert_metar_tac_with_metadata(
                    data or "",
                    iwxxm_version=iwxxm_version,
                    validate=False,
                    product=product,
                    profile=profile,
                    preview=preview,
                    soft_preview_out=soft_preview_buf,
                )
                absorb_soft_preview(soft_preview_buf, source=source_name)
                if preview and soft_preview_buf.get("ok") is False:
                    add_issue(
                        source=source_name,
                        message="Soft-preview: conversion incomplete",
                        severity=ConversionIssueSeverity.ERROR,
                        hint="Fix failed TAC spans and retry hard convert before publish.",
                        code="SOFT_PREVIEW_PARTIAL",
                    )

                # Calculate duration
                duration_ms = int((time.perf_counter() - start_time) * 1000)

                # Track validation layers passed
                layers_passed = [ValidationLayer.AIRPORT_ICAO.value, ValidationLayer.TAC_SYNTAX.value]
                validation_errors_dict = {}

                # Optionally validate output IWXXM XML (Layers 3-7); F11.4: SDK owns XSD+SCH
                if validate_output and validation_orchestrator:
                    try:
                        pkg_out = iwxxm_validate_fn(
                            xml_text,
                            iwxxm_version=iwxxm_version,
                            profile=profile or "annex3",
                            levels=("xsd", "schematron"),
                        )
                        orch_layers = [
                            layer
                            for layer in ValidationLayer
                            if layer
                            not in (
                                ValidationLayer.XML_SCHEMA,
                                ValidationLayer.SCHEMATRON,
                            )
                        ]
                        validation_result = validation_orchestrator.validate_complete(
                            tac_text=(data or "").strip(),
                            xml_content=xml_text,
                            version=iwxxm_version,
                            layers=orch_layers,
                            stop_on_error=False,  # Collect all issues
                        )
                        if pkg_out.ok and validation_result.is_valid:
                            # Add all passed validation layers
                            for layer in ValidationLayer:
                                layers_passed.append(layer.value)
                        else:
                            warning_msg = f"{uf.filename}: IWXXM validation issues found - {len(validation_result.all_issues)} issues"
                            logger.warning(warning_msg)
                            add_issue(
                                source=source_name,
                                message=warning_msg,
                                severity=ConversionIssueSeverity.WARNING,
                                hint="Output converted, but IWXXM validation reported issues.",
                                code="OUTPUT_VALIDATION_WARNING",
                                layer="iwxxm_output",
                            )
                            validation_errors_dict = {
                                "validation_issues": [str(issue) for issue in validation_result.all_issues[:10]]
                            }
                            # Add validation issues as warnings but still include the result
                    except Exception as ve:
                        logger.warning(f"{uf.filename}: Output validation failed: {ve}")
                        add_issue(
                            source=source_name,
                            message=f"Output validation failed: {ve}",
                            severity=ConversionIssueSeverity.WARNING,
                            hint="Conversion succeeded, but post-conversion validation could not complete.",
                            code="OUTPUT_VALIDATION_FAILED",
                            layer="iwxxm_output",
                        )
                        validation_errors_dict = {"validation_error": str(ve)}

                # Log successful (or soft-preview partial) translation
                try:
                    soft_incomplete = bool(preview and soft_preview_buf.get("ok") is False)
                    translation_id = await statistics_service.log_translation(
                        tac_message=(data or "").strip(),
                        iwxxm_output=xml_text,
                        iwxxm_version=iwxxm_version,
                        translation_status=(TranslationStatus.FAILED if soft_incomplete else TranslationStatus.SUCCESS),
                        validation_layers_passed=layers_passed,
                        validation_errors=validation_errors_dict if validation_errors_dict else None,
                        translation_duration_ms=duration_ms,
                        icao_airport_code=extract_airport_code((data or "").strip()),
                        user_id=user.get("sub"),
                    )
                    if soft_incomplete:
                        await webhook_service.notify_translation_failed(
                            translation_id=translation_id,
                            airport_code=extract_airport_code((data or "").strip()) or "UNKNOWN",
                            error_type="soft_preview_partial",
                            error_message="Soft-preview conversion incomplete",
                        )
                    else:
                        await webhook_service.notify_translation_success(
                            translation_id=translation_id,
                            airport_code=extract_airport_code((data or "").strip()) or "UNKNOWN",
                            icao_region=get_icao_region(extract_airport_code((data or "").strip()) or "ZZZZ"),
                            iwxxm_version=iwxxm_version,
                            duration_ms=duration_ms,
                        )
                except Exception as log_err:
                    logger.error(f"Failed to log successful translation: {log_err}")

                out_name = pathlib.Path(uf.filename or "unknown").stem + ".txt"
                results.append(
                    ConversionResult(
                        name=out_name,
                        content=xml_text,
                        tac_input=(data or "").strip(),
                        source=source_name,
                        size_bytes=len(xml_text.encode("utf-8")),
                    )
                )
            except ConversionError as e:
                errors.append(f"{uf.filename}: {e}")
                add_issue(
                    source=uf.filename or "unknown_file",
                    message=str(e),
                    severity=ConversionIssueSeverity.ERROR,
                    hint="Check METAR TAC structure and required tokens (station/time/wind).",
                    code="CONVERSION_ERROR",
                )
                # Log conversion error
                try:
                    translation_id = await statistics_service.log_translation(
                        tac_message=(data or "").strip(),
                        iwxxm_output=None,
                        iwxxm_version=iwxxm_version,
                        translation_status=TranslationStatus.FAILED,
                        validation_layers_passed=[],
                        validation_errors={"conversion_error": str(e)},
                        translation_duration_ms=int((time.perf_counter() - start_time) * 1000) if start_time else 0,
                        icao_airport_code=extract_airport_code((data or "").strip()) or None,
                        user_id=user.get("sub"),
                    )
                    airport_code = extract_airport_code((data or "").strip()) or None
                    await webhook_service.notify_translation_failed(
                        translation_id=translation_id,
                        airport_code=airport_code or "UNKNOWN",
                        error_type="conversion_error",
                        error_message=str(e),
                    )
                except Exception as log_err:
                    logger.error(f"Failed to log conversion error: {log_err}")
                if stop_on_error:
                    break
            except Exception as e:
                errors.append(f"{uf.filename}: unexpected error {e}")
                add_issue(
                    source=uf.filename or "unknown_file",
                    message=f"Unexpected backend error: {e}",
                    severity=ConversionIssueSeverity.ERROR,
                    hint="Retry once. If it persists, contact support with this message.",
                    code="UNEXPECTED_BACKEND_ERROR",
                )
                # Log unexpected error
                try:
                    translation_id = await statistics_service.log_translation(
                        tac_message=(data or "").strip(),
                        iwxxm_output=None,
                        iwxxm_version=iwxxm_version,
                        translation_status=TranslationStatus.FAILED,
                        validation_layers_passed=[],
                        validation_errors={"unexpected_error": str(e)},
                        translation_duration_ms=int((time.perf_counter() - start_time) * 1000) if start_time else 0,
                        icao_airport_code=extract_airport_code((data or "").strip()) or None,
                        user_id=user.get("sub"),
                    )
                    airport_code = extract_airport_code((data or "").strip()) or None
                    await webhook_service.notify_translation_failed(
                        translation_id=translation_id,
                        airport_code=airport_code or "UNKNOWN",
                        error_type="unexpected_error",
                        error_message=str(e),
                    )
                except Exception as log_err:
                    logger.error(f"Failed to log unexpected error: {log_err}")
                if stop_on_error:
                    break

    if not results and errors:
        logger.error(
            "[CONVERT] All conversions failed total_inputs=%s total_errors=%s first_error=%s",
            total_inputs,
            len(errors),
            errors[0] if errors else "none",
        )
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(
                message="All conversions failed", errors=errors, issues=issues, total_errors=len(errors)
            ).model_dump(),
        )

    envelope_ok: Optional[bool] = None
    if preview:
        envelope_ok = not preview_saw_soft_fail and len(errors) == 0

    return msgspec_json_response(
        ConversionResponse(
            results=results,
            errors=errors,
            issues=issues,
            total_processed=total_inputs,
            successful=len(results),
            failed=len(errors),
            metadata=request_metadata,
            ok=envelope_ok,
            failed_spans=preview_failed_spans if preview else [],
        )
    )


@app.post(
    "/api/v1/convert-zip",
    response_class=StreamingResponse,
    tags=["Conversion"],
    responses={
        401: {"description": "Unauthorized - Invalid or missing authentication token"},
    },
)
async def convert_zip(
    request: Request,
    files: Any = Depends(parse_files),
    manual_text: str = Form(default="", description="Optional manual text input (METAR TAC format)"),
    iwxxm_version: str = Form(
        default="2025-2",
        description="Target IWXXM version: 2025-2 (latest), 2023-1 (previous), or 2025-1 (auto-remaps to 2025-2)",
    ),
    user: dict = Depends(verify_supabase_token),
) -> StreamingResponse:
    # Try to parse JSON body if Content-Type is application/json
    request_body = None
    if request.headers.get("content-type", "").startswith("application/json"):
        try:
            body_data = await request.json()
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Invalid JSON in request body: {str(e)}")

        try:
            request_body = ConversionRequest(**body_data)
        except Exception as e:
            # Pydantic validation error - return 422
            raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
    """Convert METAR/SPECI TAC inputs to a zipped archive of IWXXM XML files.

    Similar to `/api/v1/convert` but returns results as a ZIP archive instead of JSON.
    Useful for batch processing or downloading multiple converted files.

    **Authentication**: Requires valid Supabase JWT token in Authorization header

    **Request Parameters**:
    - **files** (array): Optional uploaded text files containing METAR TAC
    - **manual_text** (string): Optional manual text input
    - **iwxxm_version** (string): Target IWXXM version (default: "2025-2")

    **Response**:
    - **Content Type**: `application/zip`
    - **Content**: ZIP archive containing:
      - One `.xml` file per successfully converted METAR
      - `errors.txt` file (if any conversions failed)

    **Example ZIP Contents**:
    ```
    iwxxm_batch_20260210T143000Z.zip
    ├── manual_input.xml
    ├── KJFK_231751Z.xml
    ├── EGLL_231750Z.xml
    └── errors.txt (if any failures)
    ```

    **Use Cases**:
    - Batch conversion with file export
    - Integration with external processing pipelines
    - Offline processing and storage
    """
    # Handle JSON request body (for metars list)
    if request_body is not None:
        metars_list = request_body.metars or []
        iwxxm_version = request_body.version
        manual_text = ""  # Override form input
        files = None  # Override file input
    else:
        metars_list = []

    manual_entries = split_manual_entries(manual_text)

    if not (metars_list or manual_entries or (files and len(files) > 0)):
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(
                message="No conversion input provided",
                errors=["Provide at least one METAR TAC input via manual_text, files, or JSON metars."],
                issues=[
                    ConversionIssue(
                        source="request",
                        message="Empty conversion request",
                        severity=ConversionIssueSeverity.ERROR,
                        hint="Send manual_text, files, or JSON metars in the request body.",
                        code="NO_INPUT",
                    )
                ],
                total_errors=1,
            ).model_dump(),
        )

    # Validate and normalize IWXXM version
    try:
        from .config.iwxxm_versions import get_version_config, normalize_version
    except ImportError:
        from config.iwxxm_versions import get_version_config, normalize_version

    try:
        iwxxm_version = normalize_version(iwxxm_version)
        get_version_config(iwxxm_version)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(message=f"Invalid IWXXM version: {e}", errors=[str(e)], total_errors=1).model_dump(),
        )

    results: List[tuple[str, str]] = []
    errors: List[str] = []
    translation_ids: List[str] = []  # Track for bulk notification
    validation_service = ValidationService()
    validation_orchestrator = get_validation_orchestrator()

    for manual_index, manual_entry in enumerate(manual_entries, 1):
        start_time = None
        translation_id = None
        manual_name = f"manual_input_{manual_index}.xml" if len(manual_entries) > 1 else "manual_input.xml"
        try:
            start_time = time.perf_counter()

            xml_text, _ = convert_metar_tac_with_metadata(manual_entry, iwxxm_version=iwxxm_version)
            duration_ms = int((time.perf_counter() - start_time) * 1000)

            results.append((manual_name, xml_text))

            try:
                translation_id = await statistics_service.log_translation(
                    tac_message=manual_entry,
                    iwxxm_output=xml_text,
                    iwxxm_version=iwxxm_version,
                    translation_status=TranslationStatus.SUCCESS,
                    validation_layers_passed=[],
                    validation_errors=None,
                    translation_duration_ms=duration_ms,
                    icao_airport_code=extract_airport_code(manual_entry),
                    user_id=user.get("sub"),
                )
                if translation_id:
                    translation_ids.append(translation_id)
            except Exception as log_err:
                logger.error(f"Failed to log successful translation: {log_err}")
        except ConversionError as e:
            errors.append(f"manual_input_{manual_index}: {e}" if len(manual_entries) > 1 else f"manual_input: {e}")
            try:
                translation_id = await statistics_service.log_translation(
                    tac_message=manual_entry,
                    iwxxm_output=None,
                    iwxxm_version=iwxxm_version,
                    translation_status=TranslationStatus.FAILED,
                    validation_layers_passed=[],
                    validation_errors={"conversion_error": str(e)},
                    translation_duration_ms=int((time.perf_counter() - start_time) * 1000) if start_time else 0,
                    icao_airport_code=extract_airport_code(manual_entry),
                    user_id=user.get("sub"),
                )
                airport_code = extract_airport_code(manual_entry)
                await webhook_service.notify_translation_failed(
                    translation_id=translation_id,
                    airport_code=airport_code or "UNKNOWN",
                    error_type="conversion_error",
                    error_message=str(e),
                )
            except Exception as log_err:
                logger.error(f"Failed to log failed translation: {log_err}")

    # Process uploaded files (if any)
    if files:
        for uf in files:
            start_time = None
            translation_id = None
            data = ""
            try:
                source_name = uf.filename or "unknown_file"
                data, read_error = await read_uploaded_text(uf)
                if read_error:
                    errors.append(f"{source_name}: {read_error}")
                    continue

                xml_rejection = classify_and_validate_upload_content(
                    filename=uf.filename,
                    content=data,
                    iwxxm_version=iwxxm_version,
                    endpoint_path="/api/v1/convert-zip",
                    validation_orchestrator=validation_orchestrator,
                )
                if xml_rejection:
                    errors.append(f"{source_name}: {xml_rejection['message']}")
                    continue

                # Start timing

                start_time = time.perf_counter()

                xml_text, _ = convert_metar_tac_with_metadata(data or "", iwxxm_version=iwxxm_version)

                # Calculate duration
                duration_ms = int((time.perf_counter() - start_time) * 1000)

                fname = pathlib.Path(source_name).stem + ".xml"
                results.append((fname, xml_text))

                # Log successful translation
                try:
                    translation_id = await statistics_service.log_translation(
                        tac_message=data or "",
                        iwxxm_output=xml_text,
                        iwxxm_version=iwxxm_version,
                        translation_status=TranslationStatus.SUCCESS,
                        validation_layers_passed=[],  # Zip endpoint doesn't validate
                        validation_errors=None,
                        translation_duration_ms=duration_ms,
                        icao_airport_code=extract_airport_code(data or ""),
                        user_id=user.get("sub"),
                    )
                    if translation_id:
                        translation_ids.append(translation_id)
                except Exception as log_err:
                    logger.error(f"Failed to log successful translation: {log_err}")
            except ConversionError as e:
                errors.append(f"{uf.filename}: {e}")
                # Log failed translation
                try:
                    translation_id = await statistics_service.log_translation(
                        tac_message=data or "",
                        iwxxm_output=None,
                        iwxxm_version=iwxxm_version,
                        translation_status=TranslationStatus.FAILED,
                        validation_layers_passed=[],
                        validation_errors={"conversion_error": str(e)},
                        translation_duration_ms=int((time.perf_counter() - start_time) * 1000) if start_time else 0,
                        icao_airport_code=extract_airport_code(data or "") or None,
                        user_id=user.get("sub"),
                    )
                    airport_code = extract_airport_code(data or "") or None
                    await webhook_service.notify_translation_failed(
                        translation_id=translation_id,
                        airport_code=airport_code or "UNKNOWN",
                        error_type="conversion_error",
                        error_message=str(e),
                    )
                except Exception as log_err:
                    logger.error(f"Failed to log failed translation: {log_err}")
            except Exception as e:
                errors.append(f"{uf.filename}: unexpected error {e}")
                # Log unexpected error
                try:
                    translation_id = await statistics_service.log_translation(
                        tac_message=data or "",
                        iwxxm_output=None,
                        iwxxm_version=iwxxm_version,
                        translation_status=TranslationStatus.FAILED,
                        validation_layers_passed=[],
                        validation_errors={"unexpected_error": str(e)},
                        translation_duration_ms=int((time.perf_counter() - start_time) * 1000) if start_time else 0,
                        icao_airport_code=extract_airport_code(data or "") or None,
                        user_id=user.get("sub"),
                    )
                    airport_code = extract_airport_code(data or "") or None
                    await webhook_service.notify_translation_failed(
                        translation_id=translation_id,
                        airport_code=airport_code or "UNKNOWN",
                        error_type="unexpected_error",
                        error_message=str(e),
                    )
                except Exception as log_err:
                    logger.error(f"Failed to log unexpected error: {log_err}")

    # Process metars from JSON request body
    for idx, metar_text in enumerate(metars_list, 1):
        if not metar_text.strip():
            continue

        start_time = None
        translation_id = None
        try:
            metar_name = f"metar_{idx}.txt"

            # Validate METAR input (Layers 1-2: ICAO and TAC syntax)
            try:
                validation_result = validation_service.validate_all_layers(metar_text.strip())
                if not validation_result.passed:
                    # Build summary from validation result
                    validation_summary = f"{validation_result.total_issues} validation issue(s) found"
                    error_msg = f"{metar_name}: Validation failed - {validation_summary}"
                    errors.append(error_msg)
                    # Log failed validation
                    try:
                        translation_id = await statistics_service.log_translation(
                            tac_message=metar_text.strip(),
                            iwxxm_output=None,
                            iwxxm_version=iwxxm_version,
                            translation_status=TranslationStatus.FAILED,
                            validation_layers_passed=[],
                            validation_errors={"validation": validation_summary},
                            translation_duration_ms=0,
                            icao_airport_code=extract_airport_code(metar_text.strip()),
                            user_id=user.get("sub"),
                        )
                        airport_code = extract_airport_code(metar_text.strip())
                        await webhook_service.notify_translation_failed(
                            translation_id=translation_id,
                            airport_code=airport_code or "UNKNOWN",
                            error_type="validation_failed",
                            error_message=validation_summary,
                        )
                    except Exception as log_err:
                        logger.error(f"Failed to log failed translation: {log_err}")
                    continue  # Skip to next METAR
            except ValidationServiceError as ve:
                errors.append(f"{metar_name}: {str(ve)}")
                # Log validation error
                try:
                    translation_id = await statistics_service.log_translation(
                        tac_message=metar_text.strip(),
                        iwxxm_output=None,
                        iwxxm_version=iwxxm_version,
                        translation_status=TranslationStatus.FAILED,
                        validation_layers_passed=[],
                        validation_errors={"validation_service_error": str(ve)},
                        translation_duration_ms=0,
                        icao_airport_code=extract_airport_code(metar_text.strip()),
                        user_id=user.get("sub"),
                    )
                    airport_code = extract_airport_code(metar_text.strip())
                    await webhook_service.notify_translation_failed(
                        translation_id=translation_id,
                        airport_code=airport_code or "UNKNOWN",
                        error_type="validation_error",
                        error_message=str(ve),
                    )
                except Exception as log_err:
                    logger.error(f"Failed to log validation error: {log_err}")
                continue  # Skip to next METAR

            # Start timing

            start_time = time.perf_counter()

            xml_text, _ = convert_metar_tac_with_metadata(metar_text.strip(), iwxxm_version=iwxxm_version)

            # Calculate duration
            duration_ms = int((time.perf_counter() - start_time) * 1000)

            fname = f"metar_{idx}.xml"
            results.append((fname, xml_text))

            # Log successful translation
            try:
                translation_id = await statistics_service.log_translation(
                    tac_message=metar_text.strip(),
                    iwxxm_output=xml_text,
                    iwxxm_version=iwxxm_version,
                    translation_status=TranslationStatus.SUCCESS,
                    validation_layers_passed=[],
                    translation_duration_ms=duration_ms,
                    icao_airport_code=extract_airport_code(metar_text.strip()),
                    user_id=user.get("sub"),
                )
                if translation_id:
                    translation_ids.append(translation_id)
            except Exception as log_err:
                logger.error(f"Failed to log successful translation: {log_err}")
        except ConversionError as e:
            errors.append(f"metar_{idx}: {e}")
            # Log failed translation
            try:
                translation_id = await statistics_service.log_translation(
                    tac_message=metar_text.strip(),
                    iwxxm_output=None,
                    iwxxm_version=iwxxm_version,
                    translation_status=TranslationStatus.FAILED,
                    validation_layers_passed=[],
                    validation_errors={"conversion_error": str(e)},
                    translation_duration_ms=int((time.perf_counter() - start_time) * 1000) if start_time else 0,
                    icao_airport_code=extract_airport_code(metar_text.strip()),
                    user_id=user.get("sub"),
                )
                airport_code = extract_airport_code(metar_text.strip())
                await webhook_service.notify_translation_failed(
                    translation_id=translation_id,
                    airport_code=airport_code or "UNKNOWN",
                    error_type="conversion_error",
                    error_message=str(e),
                )
            except Exception as log_err:
                logger.error(f"Failed to log failed translation: {log_err}")
        except Exception as e:
            errors.append(f"metar_{idx}: unexpected error {e}")
            # Log unexpected error
            try:
                translation_id = await statistics_service.log_translation(
                    tac_message=metar_text.strip(),
                    iwxxm_output=None,
                    iwxxm_version=iwxxm_version,
                    translation_status=TranslationStatus.FAILED,
                    validation_layers_passed=[],
                    validation_errors={"unexpected_error": str(e)},
                    translation_duration_ms=int((time.perf_counter() - start_time) * 1000) if start_time else 0,
                    icao_airport_code=extract_airport_code(metar_text.strip()),
                    user_id=user.get("sub"),
                )
                airport_code = extract_airport_code(metar_text.strip())
                await webhook_service.notify_translation_failed(
                    translation_id=translation_id,
                    airport_code=airport_code or "UNKNOWN",
                    error_type="unexpected_error",
                    error_message=str(e),
                )
            except Exception as log_err:
                logger.error(f"Failed to log unexpected error: {log_err}")

    # Send bulk completion webhook if conversions were successful
    if translation_ids:
        try:
            await webhook_service.notify_bulk_completed(
                total_files=len(translation_ids),
                successful=len(results),
                failed=len(errors),
                duration_ms=0,
            )
        except Exception as webhook_err:
            logger.error(f"Failed to send bulk completion webhook: {webhook_err}")

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
        headers={"Content-Disposition": f"attachment; filename=iwxxm_batch_{stamp}.zip"},
    )


__all__ = ["app"]
