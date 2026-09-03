"""Standalone backend API module for Docker deployment."""

from __future__ import annotations

import logging
import os
import pathlib
import sys
from collections.abc import Awaitable, Callable
from typing import Any

from starlette.types import Message, Receive, Scope, Send

# Add src directory to path for imports (for local uvicorn execution)
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from dissemination.packaging import apply_exchange_packaging
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from tac_validate import lint as tac_lint_fn

from tac2iwxxm import BulletinSplitError, iwxxm_filename, parse_ahl

try:
    from .schemas.conversion import (
        ConversionIssue,
        ConversionIssueSeverity,
        ConversionRequest,
        ConversionResponse,
        ConversionResult,
        ErrorDetail,
        FailedSpan,
    )
    from .schemas.validation import ValidateRequest, ValidateResponse
    from .utilities.conversion import ConversionError
    from .utilities.tac_parser import extract_airport_code
except ImportError:
    from schemas.conversion import (
        ConversionIssue,
        ConversionIssueSeverity,
        ConversionRequest,
        ConversionResponse,
        ConversionResult,
        ErrorDetail,
        FailedSpan,
    )
    from schemas.validation import ValidateRequest, ValidateResponse
    from utilities.conversion import ConversionError
    from utilities.tac_parser import extract_airport_code

try:
    from .services.database import database_lifespan
    from .services.validation import ValidationError as ValidationServiceError
    from .utilities.abuse_controls import install_abuse_controls
    from .utilities.observability import install_fastapi_observability, setup_logging
    from .utilities.sentry_init import init_sentry
except ImportError:
    from services.database import database_lifespan
    from services.validation import ValidationError as ValidationServiceError
    from utilities.abuse_controls import install_abuse_controls
    from utilities.observability import install_fastapi_observability, setup_logging
    from utilities.sentry_init import init_sentry

setup_logging("backend")
logger = logging.getLogger(__name__)
init_sentry(service_name="backend")

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
_is_named_upload = api_wire._is_named_upload  # pyright: ignore[reportPrivateUsage]
parse_files = api_wire.parse_files
normalize_api_product = api_wire.normalize_api_product
_coerce_form_list = api_wire._coerce_form_list  # pyright: ignore[reportPrivateUsage]
_coerce_form_str = api_wire._coerce_form_str  # pyright: ignore[reportPrivateUsage]
_resolve_request_extensions = api_wire._resolve_request_extensions  # pyright: ignore[reportPrivateUsage]
_package_issue_payload = api_wire._package_issue_payload  # pyright: ignore[reportPrivateUsage]
_package_stages_payload = api_wire._package_stages_payload  # pyright: ignore[reportPrivateUsage]
_resolve_request_profiles = api_wire._resolve_request_profiles  # pyright: ignore[reportPrivateUsage]
_is_multiline_template_product = api_wire._is_multiline_template_product  # pyright: ignore[reportPrivateUsage]
split_manual_entries = api_wire.split_manual_entries
manual_entries_with_offsets = api_wire.manual_entries_with_offsets
is_xml_input = api_wire.is_xml_input
normalize_code = api_wire.normalize_code
parse_optional_bulletin_id = api_wire.parse_optional_bulletin_id
parse_optional_issuing_center = api_wire.parse_optional_issuing_center
normalize_validation_level = api_wire.normalize_validation_level
_product_uses_metar_tac_layers = api_wire._product_uses_metar_tac_layers  # pyright: ignore[reportPrivateUsage]
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
iwxxm_validate_fn = api_deps.iwxxm_validate_fn
msgspec_json_response = api_deps.msgspec_json_response
read_upload_files_text = api_deps.read_upload_files_text
read_uploaded_text = api_deps.read_uploaded_text
statistics_service = api_deps.statistics_service
tac2iwxxm_split_bulletin = api_deps.tac2iwxxm_split_bulletin
webhook_service = api_deps.webhook_service

# Routers import ``src.api`` as api_surface; load after wire/deps re-exports (TD-3b).
try:
    from .routers import (
        comprehensive_validation,
        conversion,
        conversion_meta,
        dissemination,
        dissemination_ops,
        evaluation,
        health,
        icao_opmet,
        mass_ingest,
        quality_metrics,
        tac_quality,
        validation,
        work_sessions,
    )
except ImportError:
    from routers import (
        comprehensive_validation,
        conversion,
        conversion_meta,
        dissemination,
        dissemination_ops,
        evaluation,
        health,
        icao_opmet,
        mass_ingest,
        quality_metrics,
        tac_quality,
        validation,
        work_sessions,
    )

app = FastAPI(
    title="METAR to IWXXM Backend API",
    version="0.1.0",
    description="Convert METAR/SPECI TAC messages to IWXXM XML format with comprehensive validation",
    lifespan=database_lifespan,
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

    def __init__(self, app: Callable[[Scope, Receive, Send], Awaitable[None]]) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
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

        async def send_wrapper(message: Message) -> None:
            """Log preflight response status before forwarding ASGI messages."""
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


def _warn_if_dev_cors_relaxed(enabled: bool) -> None:
    """Emit operator-facing warning when local CORS relaxation is active."""
    if enabled:
        logger.warning(
            "[CORS] ENABLE_DEV_CORS_RELAXATION is active: localhost:5173 added and preflight headers set to '*'"
        )


_warn_if_dev_cors_relaxed(dev_cors_relaxed)


@app.middleware("http")
async def add_translation_centre_headers(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Add ICAO Translation Centre identification headers to all responses."""
    response = await call_next(request)

    try:
        centre_info = get_translation_centre_info()
        if centre_info.get("translationCentreDesignator"):
            response.headers["X-Translation-Centre"] = centre_info["translationCentreDesignator"].strip()
        if centre_info.get("translationCentreName"):
            response.headers["X-Translation-Centre-Name"] = centre_info["translationCentreName"].strip()
        if centre_info.get("icaoLocationIndicator"):
            response.headers["X-ICAO-Location-Indicator"] = centre_info["icaoLocationIndicator"].strip()
    except Exception as e:
        logger.debug(f"Translation Centre headers not configured: {e}")

    return response


def custom_openapi() -> dict[str, Any]:
    """Build OpenAPI schema without security schemes for public API docs.

    Returns
    -------
    dict
        Cached OpenAPI document for the FastAPI application.
    """
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
    components = openapi_schema.setdefault("components", {})
    components.pop("securitySchemes", None)
    openapi_schema.pop("security", None)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

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
    app.include_router(dissemination_ops.router)
    logger.info("DEBUG: included dissemination_ops router successfully")
except Exception as e:  # pragma: no cover - defensive
    logger.error(f"DEBUG: Failed to include dissemination_ops router: {e}", exc_info=True)

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
    app.include_router(conversion.router)
    app.include_router(comprehensive_validation.router)
    logger.info("DEBUG: included TD-3b routers successfully")
except Exception as e:  # pragma: no cover - defensive
    logger.error(f"DEBUG: Failed to include TD-3b routers: {e}", exc_info=True)

try:
    from metar_auth import create_auth_router

    from metar_shared.supabase_env import get_supabase_url

    _supabase_url = get_supabase_url()
    if _supabase_url and not (os.environ.get("SUPABASE_URL") or "").strip():
        os.environ["SUPABASE_URL"] = _supabase_url

    app.include_router(create_auth_router(supabase_url=_supabase_url or None))
    logger.info("DEBUG: included metar_auth /auth router successfully")
except Exception as e:  # pragma: no cover - defensive
    logger.error(f"DEBUG: Failed to include auth router: {e}", exc_info=True)

logger.info(f"DEBUG: total routes = {len(app.routes)}")

# EV-037 TD-3b: re-export moved handlers for tests that introspect ``src.api`` by name.
health = health.health
get_supported_versions = conversion_meta.get_supported_versions
get_schema_status = conversion_meta.get_schema_status
lint_issue_catalog = tac_quality.lint_issue_catalog
lint_tac = tac_quality.lint_tac
decode_tac_endpoint = tac_quality.decode_tac_endpoint
convert_bulletin = conversion.convert_bulletin
ingest_collect = mass_ingest.ingest_collect
validate_comprehensive = comprehensive_validation.validate_comprehensive
convert = conversion.convert
convert_zip = conversion.convert_zip

__all__ = [
    "BulletinSplitError",
    "ConversionError",
    "ConversionIssue",
    "ConversionIssueSeverity",
    "ConversionRequest",
    "ConversionResponse",
    "ConversionResult",
    "ErrorDetail",
    "FailedSpan",
    "HTTPException",
    "ValidateRequest",
    "ValidateResponse",
    "ValidationServiceError",
    "app",
    "apply_exchange_packaging",
    "convert",
    "convert_bulletin",
    "convert_zip",
    "decode_tac_endpoint",
    "extract_airport_code",
    "get_schema_status",
    "get_supported_versions",
    "health",
    "ingest_collect",
    "iwxxm_filename",
    "lint_issue_catalog",
    "lint_tac",
    "parse_ahl",
    "tac_lint_fn",
    "validate_comprehensive",
]
