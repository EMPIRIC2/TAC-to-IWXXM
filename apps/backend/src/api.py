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
from typing import Any, List, Optional

# Add src directory to path for imports (for local uvicorn execution)
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse

try:
    # Try relative imports first (when run as module in Docker)
    from .routers import (
        conversion_meta,
        dissemination,
        evaluation,
        health,
        icao_opmet,
        mass_ingest,
        quality_metrics,
        tac_quality,
        validation,
        work_sessions,
    )
    from .schemas.conversion import (
        ConversionIssue,
        ConversionIssueSeverity,
        ConversionRequest,
        ConversionResponse,
        ConversionResult,
        ErrorDetail,
        FailedSpan,
    )
    from .schemas.icao_opmet import TranslationStatus
    from .schemas.validation import (
        BulletinMetaModel,
        BulletinReportResultModel,
        ConvertBulletinResponse,
        LintFixModel,
        LintIssueModel,
        ValidateRequest,
        ValidateResponse,
        ValidationLayer,
    )
    from .services.database import database_lifespan
    from .services.validation import ValidationError as ValidationServiceError
    from .utilities.abuse_controls import install_abuse_controls
    from .utilities.ca_exchange_wire import (
        apply_ca_eccc_collect_output,
        ca_eccc_output_spec_for_request,
    )
    from .utilities.conversion import ConversionError
    from .utilities.extension_wire import IWXXM_CA_TOKEN
    from .utilities.iwxxm_pass_through import NOT_XML_CODE, lint_iwxxm_pass_through
    from .utilities.iwxxm_readable_decode import decode_for_validate
    from .utilities.metar_normalizer import normalize_recent_weather_tokens
    from .utilities.observability import (
        install_fastapi_observability,
        set_request_log_level,
        setup_logging,
    )
    from .utilities.sentry_init import init_sentry
    from .utilities.tac_parser import extract_airport_code
except ImportError:
    # Fall back to direct imports (when sys.path is set for local development)
    from routers import (
        conversion_meta,
        dissemination,
        evaluation,
        health,
        icao_opmet,
        mass_ingest,
        quality_metrics,
        tac_quality,
        validation,
        work_sessions,
    )
    from schemas.conversion import (
        ConversionIssue,
        ConversionIssueSeverity,
        ConversionRequest,
        ConversionResponse,
        ConversionResult,
        ErrorDetail,
        FailedSpan,
    )
    from schemas.icao_opmet import TranslationStatus
    from schemas.validation import (
        BulletinMetaModel,
        BulletinReportResultModel,
        ConvertBulletinResponse,
        LintFixModel,
        LintIssueModel,
        ValidateRequest,
        ValidateResponse,
        ValidationLayer,
    )
    from services.database import database_lifespan
    from services.validation import ValidationError as ValidationServiceError
    from utilities.abuse_controls import install_abuse_controls
    from utilities.ca_exchange_wire import (
        apply_ca_eccc_collect_output,
        ca_eccc_output_spec_for_request,
    )
    from utilities.conversion import ConversionError
    from utilities.extension_wire import IWXXM_CA_TOKEN
    from utilities.iwxxm_pass_through import NOT_XML_CODE, lint_iwxxm_pass_through
    from utilities.iwxxm_readable_decode import decode_for_validate
    from utilities.metar_normalizer import normalize_recent_weather_tokens
    from utilities.observability import (
        install_fastapi_observability,
        set_request_log_level,
        setup_logging,
    )
    from utilities.sentry_init import init_sentry
    from utilities.tac_parser import extract_airport_code

# Package thin-wrapper aliases (patchable in unit tests; ADR-015 / TC-F6-033 / F13)
from dissemination.packaging import apply_exchange_packaging
from tac2iwxxm import BulletinSplitError, iwxxm_filename, parse_ahl
from tac_validate import lint as tac_lint_fn

setup_logging("backend")
logger = logging.getLogger(__name__)
init_sentry(service_name="backend")

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
    ],
)

install_fastapi_observability(app=app, service_name="backend")
install_abuse_controls(app)


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


# EV-037 TD-2: wire helpers live in api_wire; re-export for routes and tests.
try:
    from . import api_wire
except ImportError:
    import api_wire

is_dev_cors_relaxation_enabled = api_wire.is_dev_cors_relaxation_enabled
add_origin_if_missing = api_wire.add_origin_if_missing
add_loopback_origin_variants = api_wire.add_loopback_origin_variants
get_cors_origins = api_wire.get_cors_origins
get_cors_allowed_headers = api_wire.get_cors_allowed_headers
_is_named_upload = api_wire._is_named_upload
parse_files = api_wire.parse_files
normalize_api_product = api_wire.normalize_api_product
_coerce_form_list = api_wire._coerce_form_list
_coerce_form_str = api_wire._coerce_form_str
_resolve_request_extensions = api_wire._resolve_request_extensions
_package_issue_payload = api_wire._package_issue_payload
_package_stages_payload = api_wire._package_stages_payload
_resolve_request_profiles = api_wire._resolve_request_profiles
_is_multiline_template_product = api_wire._is_multiline_template_product
split_manual_entries = api_wire.split_manual_entries
manual_entries_with_offsets = api_wire.manual_entries_with_offsets
is_xml_input = api_wire.is_xml_input
normalize_code = api_wire.normalize_code
parse_optional_bulletin_id = api_wire.parse_optional_bulletin_id
parse_optional_issuing_center = api_wire.parse_optional_issuing_center
normalize_validation_level = api_wire.normalize_validation_level
_product_uses_metar_tac_layers = api_wire._product_uses_metar_tac_layers
parse_optional_files = api_wire.parse_optional_files
bulletin_split_http_error = api_wire.bulletin_split_http_error
MAX_BULLETIN_REPORTS = api_wire.MAX_BULLETIN_REPORTS

# EV-037 TD-3a: patchable collaborators; re-export on ``api`` for monkeypatch contract.
try:
    from . import api_deps
except ImportError:
    import api_deps

ValidationService = api_deps.ValidationService
_call_iwxxm_validate = api_deps._call_iwxxm_validate
classify_and_validate_upload_content = api_deps.classify_and_validate_upload_content
convert_metar_tac_with_metadata = api_deps.convert_metar_tac_with_metadata
get_icao_region = api_deps.get_icao_region
get_translation_centre_info = api_deps.get_translation_centre_info
get_validation_orchestrator = api_deps.get_validation_orchestrator
iwxxm_validate_fn = api_deps.iwxxm_validate_fn  # noqa: F401 — patch surface (TC-F6-033)
msgspec_json_response = api_deps.msgspec_json_response
read_upload_files_text = api_deps.read_upload_files_text
read_uploaded_text = api_deps.read_uploaded_text
statistics_service = api_deps.statistics_service
tac2iwxxm_split_bulletin = api_deps.tac2iwxxm_split_bulletin
webhook_service = api_deps.webhook_service

# Configure CORS with dynamic allowed origins from environment


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


# OpenAPI schema — public operator API (F21 / ADR-031); no Bearer JWT scheme.
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
    # Ensure no leftover security schemes from FastAPI defaults.
    components = openapi_schema.setdefault("components", {})
    components.pop("securitySchemes", None)
    openapi_schema.pop("security", None)

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

# Work-sessions HTTP restored (F31 / ADR-033) — JWT + DO Postgres DATABASE_URL.
try:
    app.include_router(
        work_sessions.router,
        prefix="/api/v1/work-sessions",
        tags=["Work Sessions"],
    )
    logger.info("DEBUG: included work_sessions router successfully")
except Exception as e:  # pragma: no cover - defensive
    logger.error(f"DEBUG: Failed to include work_sessions router: {e}", exc_info=True)

try:
    app.include_router(dissemination.router)
    logger.info("DEBUG: included dissemination router successfully")
except Exception as e:  # pragma: no cover - defensive
    logger.error(f"DEBUG: Failed to include dissemination router: {e}", exc_info=True)

try:
    app.include_router(mass_ingest.router)
    logger.info("DEBUG: included mass_ingest router successfully")
except Exception as e:  # pragma: no cover - defensive
    logger.error(f"DEBUG: Failed to include mass_ingest router: {e}", exc_info=True)

try:
    app.include_router(icao_opmet.router)
    logger.info("DEBUG: included ICAO OPMET router successfully")
except Exception as e:  # pragma: no cover - defensive
    logger.error(f"DEBUG: Failed to include ICAO OPMET router: {e}", exc_info=True)

try:
    app.include_router(quality_metrics.router)
    logger.info("DEBUG: included quality_metrics router successfully")
except Exception as e:  # pragma: no cover - defensive
    logger.error(f"DEBUG: Failed to include quality_metrics router: {e}", exc_info=True)

try:
    app.include_router(health.router)
    app.include_router(conversion_meta.router)
    app.include_router(tac_quality.router)
    logger.info("DEBUG: included health/conversion_meta/tac_quality routers successfully")
except Exception as e:  # pragma: no cover - defensive
    logger.error(f"DEBUG: Failed to include TD-3b routers: {e}", exc_info=True)

# Auth routers restored (F31 / ADR-033) — JWKS-only Supabase Auth; no /admin.
try:
    from metar_auth import create_auth_router
    from metar_shared.supabase_env import get_supabase_url

    # CI E2E Full has no .env; fall back to config/local.json via get_supabase_url().
    _supabase_url = get_supabase_url()
    if _supabase_url and not (os.environ.get("SUPABASE_URL") or "").strip():
        os.environ["SUPABASE_URL"] = _supabase_url

    app.include_router(create_auth_router(supabase_url=_supabase_url or None))
    logger.info("DEBUG: included metar_auth /auth router successfully")
except Exception as e:  # pragma: no cover - defensive
    logger.error(f"DEBUG: Failed to include auth router: {e}", exc_info=True)

logger.info(f"DEBUG: total routes = {len(app.routes)}")


# Custom dependency to handle optional file uploads (filters out empty strings from Swagger UI)


@app.post(
    "/api/v1/convert-bulletin",
    tags=["Conversion"],
    response_model=ConvertBulletinResponse,
    responses={
        400: {"description": "Empty bulletin — no TAC reports after the abbreviated heading"},
        415: {"description": "Unsupported Media Type — multipart/form-data required"},
        422: {
            "description": (
                "Malformed abbreviated heading (INVALID_AHL) or missing required fields. "
                "Engine split failures may include an alias of bulletin_split_failed."
            )
        },
    },
)
async def convert_bulletin(
    request: Request,
    product: str = Form(..., description="TAC product, or iwxxm for XML pass-through"),
    files: Optional[List[UploadFile]] = File(None),
    manual_text: str = Form(
        default="",
        description=(
            "Bulletin text: abbreviated heading TTAAii CCCC YYGGgg (optional BBB), "
            "then one or more TAC reports. Empty Bulletin ID / Issuing Center uses "
            "the heading TTAAii and CCCC."
        ),
    ),
    profile: str = Form(default="", description="Deprecated — use semantic_profile (legacy alias: annex3 or iwxxm_us)"),
    semantic_profile: str = Form(
        default="",
        description="Semantic profile id (e.g. ICAO_2025, US_FAA_NWS, or CA_ECCC; aliases annex3 / iwxxm_us accepted)",
    ),
    exchange_profile: str = Form(
        default="",
        description="Exchange packaging profile (e.g. GLOBAL_AFS); ignored on convert-only paths",
    ),
    iwxxm_version: str = Form(default="2025-2", description="Target IWXXM version"),
    lint: bool = Form(default=True, description="Run tac-validate before each report convert"),
    extensions: List[str] = Form(
        default=[],
        description="Optional national extension tokens (e.g. IWXXM_CA for full Canadian validate stack)",
    ),
) -> Response:
    """Split a WMO AHL bulletin and convert each TAC report.

    Partial success is allowed: HTTP 200 when split succeeds even if some reports fail.
    Per-report ``issues`` / ``fixes`` follow lint-style identity.
    """
    wire = _resolve_request_profiles(
        route="/api/v1/convert-bulletin",
        profile=profile,
        semantic_profile=semantic_profile,
        exchange_profile=exchange_profile,
        for_packaging=True,
    )
    profile = wire.emit_key
    _resolve_request_extensions(extensions, None)

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

    product = normalize_api_product(product, default=None)

    # F7.t: convert-bulletin with product=iwxxm treats the body as one XML document.
    if product == "IWXXM":
        iwxxm_lint = lint_iwxxm_pass_through(bulletin_text)
        issues = [
            LintIssueModel(
                severity=i.severity,
                code=i.code,
                message=i.message,
                location=i.location,
                start=i.start,
                end=i.end,
            )
            for i in iwxxm_lint.issues
        ]
        if not iwxxm_lint.ok:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": NOT_XML_CODE,
                    "message": issues[0].message if issues else "Expected IWXXM XML",
                    "issues": [i.model_dump() for i in issues],
                },
            )
        xml_body = bulletin_text.strip()
        return msgspec_json_response(
            ConvertBulletinResponse(
                bulletin_meta=BulletinMetaModel(
                    ahl="",
                    report_count=1,
                    tt="",
                    aa="",
                    cccc="",
                    yygggg="",
                    bbb=None,
                ),
                results=[
                    BulletinReportResultModel(
                        report_index=0,
                        ok=True,
                        tac_input="",
                        xml=xml_body,
                        issues=[],
                        fixes=[],
                    )
                ],
            )
        )

    try:
        split = tac2iwxxm_split_bulletin(bulletin_text, product=product)
    except BulletinSplitError as exc:
        raise bulletin_split_http_error(exc) from exc

    if split.meta.report_count > MAX_BULLETIN_REPORTS:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "too_many_reports",
                "message": (f"Bulletin contains {split.meta.report_count} reports; limit is {MAX_BULLETIN_REPORTS}"),
            },
        )

    bulletin_identifier: str | None = None
    try:
        ahl_parts = parse_ahl(split.meta.ahl)
        yy = int(split.meta.yygggg[:2])
        hh = int(split.meta.yygggg[2:4])
        mm = int(split.meta.yygggg[4:6])
        issued_at = datetime.datetime.now(datetime.UTC).replace(day=yy, hour=hh, minute=mm, second=0, microsecond=0)
        bulletin_identifier = iwxxm_filename(ahl_parts, issued_at=issued_at)
    except (TypeError, ValueError):
        bulletin_identifier = None

    results: list[BulletinReportResultModel] = []
    for index, tac in enumerate(split.reports):
        issues: list[LintIssueModel] = []
        fixes: list[LintFixModel] = []
        xml_out: str | None = None
        ok = True

        if lint:
            lint_report = tac_lint_fn(tac, product=product, profile=profile)
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
                    report_status=split.meta.report_status,
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

        if ok and xml_out and wire.exchange_profile:
            xml_out = apply_exchange_packaging(
                xml_out,
                exchange_profile=wire.exchange_profile,
                bulletin_identifier=bulletin_identifier,
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
                report_status=split.meta.report_status,
            ),
            exchange_profile=wire.exchange_profile,
            results=results,
        )
    )


@app.post(
    "/api/v1/ingest-collect",
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
    responses={},
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
    profile: str = Form(default="", description="Deprecated — use semantic_profile (legacy alias: annex3 or iwxxm_us)"),
    semantic_profile: str = Form(
        default="",
        description="Semantic profile id (e.g. ICAO_2025, US_FAA_NWS, or CA_ECCC; aliases annex3 / iwxxm_us accepted)",
    ),
    exchange_profile: str = Form(
        default="",
        description="Exchange packaging profile (e.g. GLOBAL_AFS); ignored on validate-only paths",
    ),
    extensions: List[str] = Form(
        default=[],
        description="Optional national extension tokens (e.g. IWXXM_CA for full Canadian validate stack)",
    ),
    product: str = Form(
        default="METAR",
        description="TAC product for Canadian extension XSD when extensions include IWXXM_CA",
    ),
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

    **Authentication**: Public (no login required)

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
        json_profile = None
        json_semantic = None
        json_exchange = None
        json_extensions = None
        json_product = None
        extensions = _coerce_form_list(extensions)
        product = _coerce_form_str(product, "METAR")
        # Handle JSON request body
        if request_body is not None:
            xml_content = request_body.iwxxm_xml
            iwxxm_version = request_body.version
            validation_level = request_body.validation_level or "comprehensive"
            json_profile = request_body.profile
            json_semantic = getattr(request_body, "semantic_profile", None)
            json_exchange = getattr(request_body, "exchange_profile", None)
            json_extensions = getattr(request_body, "extensions", None)
            json_product = getattr(request_body, "product", None)
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

        wire = _resolve_request_profiles(
            route="/api/v1/validate",
            profile=profile,
            semantic_profile=semantic_profile,
            exchange_profile=exchange_profile,
            json_profile=json_profile,
            json_semantic_profile=json_semantic,
            json_exchange_profile=json_exchange,
        )
        profile = wire.emit_key

        resolved_extensions = _resolve_request_extensions(extensions, json_extensions)
        validate_product = normalize_api_product(
            json_product if json_product is not None else product,
            default="METAR",
        )

        # Normalize version
        try:
            from .config.iwxxm_versions import get_version_config_for_emit_profile, normalize_version
        except ImportError:
            from config.iwxxm_versions import get_version_config_for_emit_profile, normalize_version

        iwxxm_version = normalize_version(iwxxm_version)

        # Validate version is supported
        try:
            get_version_config_for_emit_profile(iwxxm_version, profile)
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

        pkg_report = _call_iwxxm_validate(
            xml_content,
            iwxxm_version=iwxxm_version,
            profile=profile or "annex3",
            levels=pkg_levels,
            emit_key=profile or "annex3",
            extensions=resolved_extensions,
            product=validate_product,
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
        payload: dict[str, Any] = {
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
            "package_issues": [_package_issue_payload(issue) for issue in pkg_report.issues],
        }
        package_stages = _package_stages_payload(pkg_report)
        if package_stages is not None:
            payload["package_stages"] = package_stages
        if resolved_extensions:
            payload["extensions"] = resolved_extensions
        decoded = decode_for_validate(xml_content=xml_content, manual_text=manual_text)
        if decoded.segments:
            payload["segments"] = [
                {
                    "start": seg.start,
                    "end": seg.end,
                    "code": seg.code,
                    "explanation": seg.explanation,
                }
                for seg in decoded.segments
            ]
            if decoded.summary:
                payload["summary"] = decoded.summary
        return msgspec_json_response(payload)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@app.post(
    "/api/v1/convert",
    response_model=ConversionResponse,
    tags=["Conversion"],
    responses={},
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
    product: str = Form(
        default="METAR",
        description=("TAC product type, or iwxxm for XML pass-through (default METAR for legacy clients)"),
    ),
    profile: str = Form(default="", description="Deprecated — use semantic_profile (legacy alias: annex3 or iwxxm_us)"),
    semantic_profile: str = Form(
        default="",
        description="Semantic profile id (e.g. ICAO_2025, US_FAA_NWS, or CA_ECCC; aliases annex3 / iwxxm_us accepted)",
    ),
    exchange_profile: str = Form(
        default="",
        description="Exchange packaging profile (e.g. GLOBAL_AFS); ignored on convert-only paths",
    ),
    exchange_output: bool = Form(
        default=False,
        description=(
            "When true with semantic_profile=CA_ECCC, wrap convert output in MSC COLLECT envelope "
            "(inner product validate paths unchanged)"
        ),
    ),
    extensions: List[str] = Form(
        default=[],
        description="Optional national extension tokens (e.g. IWXXM_CA for full Canadian validate stack)",
    ),
    preview: bool = Form(
        default=False,
        description="Soft-preview: best-effort IWXXM with failure spans on partial convert",
    ),
    include_nil_reasons: bool = Form(
        default=True,
        description=("When false, prefer omitting nilReason attributes (engine may still emit NIL report shells)"),
    ),
    emit_translation_centre: bool = Form(
        default=False,
        description=(
            "When true, emit translationCentreDesignator/Name on successful convert "
            "(cross-State / Translation Centre mode; FAQ §14.5). Default omit for in-State."
        ),
    ),
    translation_centre_designator: str = Form(
        default="",
        description="Optional translationCentreDesignator when emit_translation_centre is true",
    ),
    translation_centre_name: str = Form(
        default="",
        description="Optional translationCentreName when emit_translation_centre is true",
    ),
    log_level: str = Form(
        default="INFO",
        description="Minimum severity for conversion/validation/lint process issues echoed to the client",
    ),
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

    **Authentication**: Public (no login required)

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
        body_exchange_output = getattr(request_body, "exchange_output", None)
        if body_exchange_output is not None:
            exchange_output = bool(body_exchange_output)
        body_product = getattr(request_body, "product", None)
        if body_product is not None:
            product = body_product
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

    product = normalize_api_product(product, default="METAR")
    bulletin_id = parse_optional_bulletin_id(bulletin_id)
    issuing_center = parse_optional_issuing_center(issuing_center)

    json_profile = getattr(request_body, "profile", None) if request_body is not None else None
    json_semantic = getattr(request_body, "semantic_profile", None) if request_body is not None else None
    json_exchange = getattr(request_body, "exchange_profile", None) if request_body is not None else None
    wire = _resolve_request_profiles(
        route="/api/v1/convert",
        profile=profile,
        semantic_profile=semantic_profile,
        exchange_profile=exchange_profile,
        json_profile=json_profile,
        json_semantic_profile=json_semantic,
        json_exchange_profile=json_exchange,
    )
    profile = wire.emit_key

    json_extensions = getattr(request_body, "extensions", None) if request_body is not None else None
    resolved_extensions = _resolve_request_extensions(extensions, json_extensions)

    if wire.semantic_canonical == "ca_eccc" and IWXXM_CA_TOKEN in resolved_extensions:
        try:
            from iwxxm_validate.ca_eccc_bundle import ca_eccc_bundle_available
        except ImportError:

            def ca_eccc_bundle_available(
                *,
                iwxxm_version: str = "3.0.0",
                extension_tag: str = "3.0",
            ) -> bool:
                return False

        if not ca_eccc_bundle_available():
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "missing_ca_extension_bundle",
                    "message": (
                        "Canadian national extension schemas are not available on this deployment. "
                        "Contact your administrator or choose Annex 3 / IWXXM-US."
                    ),
                },
            )

    # F7.t / EV-060 / #1003: product=iwxxm is XML pass-through (no TAC convert).
    if product == "IWXXM":
        xml_payload = (manual_text or "").strip()
        if request_body is not None and getattr(request_body, "metars", None):
            xml_payload = (request_body.metars[0] or "").strip() if request_body.metars else xml_payload
        if not xml_payload and files:
            joined, err = await read_upload_files_text(files)
            if err:
                raise HTTPException(status_code=400, detail={"code": "upload_rejected", "message": err})
            xml_payload = (joined or "").strip()
        if not xml_payload:
            raise HTTPException(
                status_code=400,
                detail=ErrorDetail(
                    message="No IWXXM XML provided",
                    errors=["Provide XML via manual_text, files, or JSON metars."],
                    issues=[
                        ConversionIssue(
                            source="request",
                            message="Expected IWXXM XML for product IWXXM",
                            severity=ConversionIssueSeverity.ERROR,
                            hint="Paste or upload IWXXM XML, or choose a TAC product to convert.",
                            code=NOT_XML_CODE,
                        )
                    ],
                    total_errors=1,
                ).model_dump(),
            )
        iwxxm_lint = lint_iwxxm_pass_through(xml_payload)
        if not iwxxm_lint.ok:
            issues = [
                ConversionIssue(
                    source="manual",
                    message=i.message,
                    severity=ConversionIssueSeverity.ERROR,
                    code=i.code,
                    location=i.location,
                )
                for i in iwxxm_lint.issues
            ]
            raise HTTPException(
                status_code=400,
                detail=ErrorDetail(
                    message="IWXXM pass-through rejected input",
                    errors=[i.message for i in issues],
                    issues=issues,
                    total_errors=len(issues),
                ).model_dump(),
            )
        pass_issues: List[ConversionIssue] = []
        want_validate = bool(validate_output) or str(validation_level or "").lower() in {
            "comprehensive",
            "schematron",
            "icao_opmet",
            "schema",
        }
        if want_validate:
            try:
                report = _call_iwxxm_validate(
                    xml_payload,
                    iwxxm_version=iwxxm_version,
                    profile=(profile or "annex3"),
                    levels=("xsd", "schematron"),
                    emit_key=(profile or "annex3"),
                    extensions=resolved_extensions,
                    product=product,
                )
                if not getattr(report, "ok", True):
                    for issue in getattr(report, "issues", []) or []:
                        pass_issues.append(
                            ConversionIssue(
                                source="manual",
                                message=str(getattr(issue, "message", "") or "IWXXM validation issue"),
                                severity=ConversionIssueSeverity.WARNING,
                                code=str(getattr(issue, "code", None) or "IWXXM_VALIDATE"),
                                location=getattr(issue, "location", None),
                            )
                        )
            except Exception as exc:  # noqa: BLE001 — pass-through must not 500 on optional F2
                logger.warning("[CONVERT] IWXXM pass-through validate_output failed: %s", exc)
                pass_issues.append(
                    ConversionIssue(
                        source="manual",
                        message=f"Optional IWXXM validation could not complete: {exc}",
                        severity=ConversionIssueSeverity.WARNING,
                        code="IWXXM_VALIDATE_ERROR",
                    )
                )
        return msgspec_json_response(
            ConversionResponse(
                results=[
                    ConversionResult(
                        name="iwxxm_pass_through.xml",
                        content=xml_payload,
                        tac_input=None,
                        source="manual",
                        size_bytes=len(xml_payload.encode("utf-8")),
                    )
                ],
                errors=[],
                issues=pass_issues,
                total_processed=1,
                successful=1,
                failed=0,
                metadata={
                    "bulletin_id": bulletin_id,
                    "issuing_center": issuing_center,
                    "validation_level": validation_level,
                    "stop_on_error": bool(stop_on_error),
                    "product": "iwxxm",
                    "pass_through": True,
                },
            )
        )

    # Q14=C: lint default on — echo tac-validate issues on the convert response (FR-L6).
    pre_convert_lint_report = None
    if lint:
        sample = manual_text.strip() if manual_text else ""
        if request_body is not None and getattr(request_body, "metars", None):
            sample = (request_body.metars[0] or "").strip() if request_body.metars else sample
        if sample:
            pre_convert_lint_report = tac_lint_fn(sample, product=product, profile=profile)

    validation_level = normalize_validation_level(validation_level)
    validate_output = bool(validate_output) or validation_level in [
        "comprehensive",
        "schematron",
        "icao_opmet",
        "schema",
    ]
    log_level_norm = set_request_log_level(request, log_level)
    logger.debug("[CONVERT] logger verbosity applied level=%s", log_level_norm)
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
        from .config.iwxxm_versions import get_version_config_for_emit_profile, normalize_version
    except ImportError:
        from config.iwxxm_versions import get_version_config_for_emit_profile, normalize_version

    try:
        iwxxm_version = normalize_version(iwxxm_version)
        get_version_config_for_emit_profile(iwxxm_version, profile)
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

    manual_with_offsets = manual_entries_with_offsets(manual_text or "", product=product)
    manual_entries = [entry for entry, _ in manual_with_offsets]

    request_metadata = {
        "bulletin_id": bulletin_id,
        "issuing_center": issuing_center,
        "validation_level": validation_level,
        "stop_on_error": bool(stop_on_error),
        "semantic_profile": wire.semantic_canonical,
    }
    if exchange_output:
        request_metadata["exchange_output"] = True
    sample_for_output_spec = manual_text.strip() if manual_text else ""
    if not sample_for_output_spec and metars_list:
        sample_for_output_spec = (metars_list[0] or "").strip()
    output_spec = ca_eccc_output_spec_for_request(
        semantic_canonical=wire.semantic_canonical,
        product=product,
        sample_text=sample_for_output_spec or None,
    )
    if output_spec:
        request_metadata["output_spec"] = output_spec

    def _finalize_exchange_xml(xml: str, tac_input: str | None) -> str:
        spec_filename = None
        meta_output_spec = request_metadata.get("output_spec")
        if isinstance(meta_output_spec, dict):
            spec_filename = meta_output_spec.get("suggested_filename")
        return apply_ca_eccc_collect_output(
            xml,
            semantic_canonical=wire.semantic_canonical,
            exchange_output=exchange_output,
            product=product,
            tac_input=tac_input,
            bulletin_identifier=spec_filename,
            bulletin_context=sample_for_output_spec or None,
        )

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
                                    user_id=None,
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
                            user_id=None,
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
                    emit_translation_centre=emit_translation_centre,
                    translation_centre_designator=translation_centre_designator,
                    translation_centre_name=translation_centre_name,
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
                    pkg_out = _call_iwxxm_validate(
                        iwxxm_content,
                        iwxxm_version=iwxxm_version,
                        profile=profile or "annex3",
                        levels=("xsd", "schematron"),
                        emit_key=profile or "annex3",
                        extensions=resolved_extensions,
                        product=product,
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
                result_xml = _finalize_exchange_xml(iwxxm_content, metar_text.strip())
                result = ConversionResult(
                    name=metar_name,
                    content=result_xml,
                    tac_input=metar_text.strip(),
                    source="json",
                    size_bytes=len(result_xml.encode("utf-8")),
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
                        user_id=None,
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
                        user_id=None,
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
                                    user_id=None,
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
                            user_id=None,
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
            xml_text, _ = convert_metar_tac_with_metadata(
                _normalized_entry,
                iwxxm_version=iwxxm_version,
                validate=False,
                lenient=False,  # normalization already applied above
                product=product,
                profile=profile,
                preview=preview,
                soft_preview_out=soft_preview_buf,
                emit_translation_centre=emit_translation_centre,
                translation_centre_designator=translation_centre_designator,
                translation_centre_name=translation_centre_name,
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

            if validate_output and validation_orchestrator:
                try:
                    pkg_out = _call_iwxxm_validate(
                        xml_text,
                        iwxxm_version=iwxxm_version,
                        profile=profile or "annex3",
                        levels=("xsd", "schematron"),
                        emit_key=profile or "annex3",
                        extensions=resolved_extensions,
                        product=product,
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
                        tac_text=manual_entry,
                        xml_content=xml_text,
                        version=iwxxm_version,
                        layers=orch_layers,
                        stop_on_error=False,
                    )
                    if pkg_out.ok and validation_result.is_valid:
                        for layer in ValidationLayer:
                            if layer.value not in layers_passed:
                                layers_passed.append(layer.value)
                    else:
                        warning_msg = (
                            f"{manual_source}: IWXXM validation issues found - "
                            f"{len(validation_result.all_issues)} issues"
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
                            "validation_issues": [str(issue) for issue in validation_result.all_issues[:10]]
                        }
                except Exception as ve:
                    logger.warning(f"{manual_source}: Output validation failed: {ve}")
                    add_issue(
                        source=manual_source,
                        message=f"Output validation failed: {ve}",
                        severity=ConversionIssueSeverity.WARNING,
                        hint="Conversion succeeded, but post-conversion validation could not complete.",
                        code="OUTPUT_VALIDATION_FAILED",
                        layer="iwxxm_output",
                    )
                    validation_errors_dict = {"validation_error": str(ve)}

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
                    user_id=None,
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

            manual_xml = _finalize_exchange_xml(xml_text, manual_entry.strip())
            results.append(
                ConversionResult(
                    name=manual_name,
                    content=manual_xml,
                    tac_input=manual_entry.strip(),
                    source=manual_source,
                    size_bytes=len(manual_xml.encode("utf-8")),
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
                                        user_id=None,
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
                                user_id=None,
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
                    emit_translation_centre=emit_translation_centre,
                    translation_centre_designator=translation_centre_designator,
                    translation_centre_name=translation_centre_name,
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
                        pkg_out = _call_iwxxm_validate(
                            xml_text,
                            iwxxm_version=iwxxm_version,
                            profile=profile or "annex3",
                            levels=("xsd", "schematron"),
                            emit_key=profile or "annex3",
                            extensions=resolved_extensions,
                            product=product,
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
                        user_id=None,
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
                file_xml = _finalize_exchange_xml(xml_text, (data or "").strip())
                results.append(
                    ConversionResult(
                        name=out_name,
                        content=file_xml,
                        tac_input=(data or "").strip(),
                        source=source_name,
                        size_bytes=len(file_xml.encode("utf-8")),
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
                        user_id=None,
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
                        user_id=None,
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

    if pre_convert_lint_report is not None:
        for lint_issue in pre_convert_lint_report.issues:
            sev_raw = str(lint_issue.severity or "info").strip().lower()
            if sev_raw == "error":
                lint_severity = ConversionIssueSeverity.ERROR
            elif sev_raw == "warning":
                lint_severity = ConversionIssueSeverity.WARNING
            else:
                lint_severity = ConversionIssueSeverity.INFO
            add_issue(
                source="lint",
                message=str(lint_issue.message or lint_issue.code or "Lint issue"),
                severity=lint_severity,
                code=str(lint_issue.code or "LINT"),
                location=getattr(lint_issue, "location", None),
            )
        if not pre_convert_lint_report.ok:
            logger.info(
                "[CONVERT] tac-validate issues (non-blocking soft path): %s",
                [i.code for i in pre_convert_lint_report.issues],
            )

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
    responses={},
)
async def convert_zip(
    request: Request,
    files: Any = Depends(parse_files),
    manual_text: str = Form(default="", description="Optional manual text input (METAR TAC format)"),
    iwxxm_version: str = Form(
        default="2025-2",
        description="Target IWXXM version: 2025-2 (latest), 2023-1 (previous), or 2025-1 (auto-remaps to 2025-2)",
    ),
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

    **Authentication**: Public (no login required)

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
                    user_id=None,
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
                    user_id=None,
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
                        user_id=None,
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
                        user_id=None,
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
                        user_id=None,
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
                            user_id=None,
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
                        user_id=None,
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
                    user_id=None,
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
                    user_id=None,
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
                    user_id=None,
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


# EV-037 TD-3b: re-export moved handlers for tests that introspect ``src.api`` by name.
health = health.health
get_supported_versions = conversion_meta.get_supported_versions
get_schema_status = conversion_meta.get_schema_status
lint_issue_catalog = tac_quality.lint_issue_catalog
lint_tac = tac_quality.lint_tac
decode_tac_endpoint = tac_quality.decode_tac_endpoint

__all__ = ["app"]
