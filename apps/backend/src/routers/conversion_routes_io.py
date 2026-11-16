"""Convert route handlers (line-cap split from conversion.py)."""

from __future__ import annotations

from typing import Any

from fastapi import Depends, Form, HTTPException, Request, UploadFile
from fastapi.responses import Response

from src.metar_iwxxm_api.convert_library_hard_cut import (
    resolve_engine_profile_from_conversion_library,
)
from src.routers.conversion_api_surface import api_surface, parse_files
from src.routers.conversion_part_1 import (
    _convert_output_policy_id,
    _resolve_effective_iwxxm_version,
    _resolve_report_variant,
    logger,
    router,
)
from src.routers.conversion_part_2 import (
    _append_pre_convert_lint_issues,
    _ConvertAccumulator,
    _record_convert_station_health,
)
from src.routers.conversion_part_3 import _process_json_metars
from src.routers.conversion_part_4 import _process_manual_entries
from src.routers.conversion_part_5 import _process_uploaded_files
from src.schemas.conversion import (
    ConversionIssue,
    ConversionIssueSeverity,
    ConversionRequest,
    ConversionResponse,
    ErrorDetail,
)
from src.services.conversion_profiles_service import ConversionProfilesService
from src.utilities.security import verify_optional_supabase_token

# Kept alive for convert_continue({**globals(), **locals()}) handoff.
_CONVERT_HANDOFF_HELPERS = (
    resolve_engine_profile_from_conversion_library,
    _convert_output_policy_id,
    _resolve_effective_iwxxm_version,
    _resolve_report_variant,
    _ConvertAccumulator,
    _append_pre_convert_lint_issues,
    _record_convert_station_health,
    _process_json_metars,
    _process_manual_entries,
    _process_uploaded_files,
    api_surface,
)


@router.post(
    "/convert",
    response_model=ConversionResponse,
    tags=["Conversion"],
    summary="Convert TAC to IWXXM",
    responses={},
)
async def convert(
    request: Request,
    files: list[UploadFile] | None = Depends(parse_files),
    manual_text: str = Form(default="", description="Optional manual text input (METAR TAC format)"),
    iwxxm_version: str = Form(
        default="",
        description="Target IWXXM version: 2025-2 (latest), 2023-1 (previous), or 2025-1 (auto-remaps to 2025-2)",
    ),
    validate_output: bool = Form(default=False, description="Enable full 7-layer IWXXM validation after conversion"),
    validation_level: str = Form(
        default="basic", description="Validation depth: basic, schema, schematron, icao_opmet, comprehensive"
    ),
    stop_on_error: bool = Form(default=False, description="Stop processing remaining inputs after first error"),
    bulletin_id: str = Form(default="", description="Optional bulletin identifier"),
    issuing_center: str = Form(default="", description="Optional issuing centre ICAO code"),
    lint: bool = Form(default=True, description="Run TAC validation before conversion. On by default."),
    product: str = Form(
        default="METAR",
        description=("TAC product type, or iwxxm for XML pass-through (default METAR for legacy clients)"),
    ),
    profile: str = Form(
        default="",
        description="Rejected. Use conversion_library_id.",
        include_in_schema=False,
    ),
    semantic_profile: str = Form(
        default="",
        description="Rejected. Use conversion_library_id.",
        include_in_schema=False,
    ),
    exchange_profile: str = Form(
        default="",
        description="Rejected. Use dissemination_library_id for packaging transforms.",
        include_in_schema=False,
    ),
    report_variant: str = Form(
        default="",
        description="Optional profile-scoped report variant within the selected product family (for example LWIS under CA_ECCC + METAR)",
    ),
    exchange_output: bool = Form(
        default=False,
        description=(
            "When true with semantic_profile=CA_ECCC, wrap convert output in MSC COLLECT envelope "
            "(inner product validate paths unchanged)"
        ),
    ),
    extensions: list[str] = Form(
        default=[],
        description="Optional national extension tokens (e.g. IWXXM_CA for full Canadian validate stack)",
    ),
    preview: bool = Form(
        default=False,
        description="Soft-preview: best-effort IWXXM with failure spans on partial convert",
    ),
    strict: bool = Form(
        default=False,
        description=(
            "When false, only critical and error findings are raised in the client. "
            "When true, the full severity set applies subject to step flags, and IWXXM "
            "output validation runs when the validate step is on."
        ),
    ),
    strict_lint: bool = Form(
        default=True,
        description="When strict is true, include TAC lint findings in the raised set.",
    ),
    strict_convert: bool = Form(
        default=True,
        description="When strict is true, include convert findings in the raised set.",
    ),
    strict_validate: bool = Form(
        default=True,
        description=(
            "When strict is true, include IWXXM validation findings in the raised set "
            "and run post-convert validation on convert routes."
        ),
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
    propagate_residuals_to_remarks: bool | None = Form(
        default=None,
        description=(
            "When true, append decode residual token text into remarks / humanReadableText "
            "when the profile supports that path; annex3 documents no XML target. "
            "Omitted uses the profile default (annex3 / ICAO_2025 off)."
        ),
    ),
    bulletin_date: str = Form(
        default="",
        description=(
            "Optional calendar date (YYYY-MM-DD) used as the year and month for TAC day stamps. "
            "When omitted, the current UTC date is used. A day that cannot fall in that month "
            "fails conversion, and the message names the day and the month."
        ),
    ),
    overlay_id: str = Form(
        default="",
        description="Rejected. Overlays are not accepted on convert. Use conversion_library_id.",
        include_in_schema=False,
    ),
    preset_id: str = Form(
        default="",
        description="Rejected. Presets are not accepted on convert. Use conversion_library_id.",
        include_in_schema=False,
    ),
    conversion_template_id: str = Form(
        default="",
        description=(
            "Optional conversion template id (first-party or custom). When set for a "
            "custom template, requires Bearer JWT and ownership (or shared); unknown "
            "ids are rejected."
        ),
    ),
    conversion_library_id: str = Form(
        default="",
        description="Conversion library asset id (resolves engine profile).",
    ),
    tac_validation_library_id: str = Form(
        default="",
        description="TAC validation library asset id.",
    ),
    iwxxm_validation_library_id: str = Form(
        default="",
        description="IWXXM validation library asset id.",
    ),
    dissemination_library_id: str = Form(
        default="",
        description="Dissemination library asset id.",
    ),
    decoding_library_id: str = Form(
        default="",
        description="Decoding library asset id.",
    ),
    auth_user: dict[str, Any] | None = Depends(verify_optional_supabase_token),
) -> Response:
    """Convert METAR/SPECI TAC text to IWXXM XML."""
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
            ) from e

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
            ) from e
    # Handle JSON request body (for metars list)
    if request_body is not None:
        metars = request_body.metars
        iwxxm_version = request_body.version
        validation_level = request_body.validation_level or "basic"
        stop_on_error = request_body.stop_on_error
        bulletin_id = request_body.bulletin_id or ""
        issuing_center = request_body.issuing_center or ""
        preview = bool(getattr(request_body, "preview", False))
        body_prop = getattr(request_body, "propagate_residuals_to_remarks", None)
        if body_prop is not None:
            propagate_residuals_to_remarks = body_prop
        body_exchange_output = getattr(request_body, "exchange_output", None)
        if body_exchange_output is not None:
            exchange_output = bool(body_exchange_output)
        body_product = getattr(request_body, "product", None)
        if body_product is not None:
            product = body_product
        body_report_variant = getattr(request_body, "report_variant", None)
        if body_report_variant is not None:
            report_variant = body_report_variant
        body_preset_id = getattr(request_body, "preset_id", None)
        if body_preset_id is not None:
            preset_id = body_preset_id
        body_overlay_id = getattr(request_body, "overlay_id", None)
        if body_overlay_id is not None:
            overlay_id = str(body_overlay_id)
        body_conversion_library_id = getattr(request_body, "conversion_library_id", None)
        if body_conversion_library_id is not None:
            conversion_library_id = str(body_conversion_library_id)
        body_tac = getattr(request_body, "tac_validation_library_id", None)
        if body_tac is not None:
            tac_validation_library_id = str(body_tac)
        body_iwxxm_lib = getattr(request_body, "iwxxm_validation_library_id", None)
        if body_iwxxm_lib is not None:
            iwxxm_validation_library_id = str(body_iwxxm_lib)
        body_dissem = getattr(request_body, "dissemination_library_id", None)
        if body_dissem is not None:
            dissemination_library_id = str(body_dissem)
        body_decode = getattr(request_body, "decoding_library_id", None)
        if body_decode is not None:
            decoding_library_id = str(body_decode)
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

    product = api_surface.normalize_api_product(product, default="METAR")
    bulletin_id = api_surface.parse_optional_bulletin_id(bulletin_id)
    issuing_center = api_surface.parse_optional_issuing_center(issuing_center)

    profiles_service: ConversionProfilesService | None = None
    if auth_user is not None:
        profiles_service = ConversionProfilesService(str(auth_user.get("sub") or auth_user.get("user_id")))

    # Reserved for Convert bar pickers (validation/dissem/decode applied in later milestones).
    _ = (
        tac_validation_library_id,
        iwxxm_validation_library_id,
        dissemination_library_id,
        decoding_library_id,
    )

    from metar_iwxxm_api.convert_library_hard_cut import (
        legacy_convert_fields_present,
        legacy_convert_reject_detail,
    )

    legacy_fields = legacy_convert_fields_present(
        semantic_profile=semantic_profile,
        profile=profile,
        preset_id=preset_id,
        overlay_id=overlay_id,
        exchange_profile=exchange_profile,
    )
    if request_body is not None:
        legacy_fields.extend(
            legacy_convert_fields_present(
                semantic_profile=str(getattr(request_body, "semantic_profile", None) or ""),
                profile=str(getattr(request_body, "profile", None) or ""),
                preset_id=str(getattr(request_body, "preset_id", None) or ""),
                overlay_id=str(getattr(request_body, "overlay_id", None) or ""),
                exchange_profile=str(getattr(request_body, "exchange_profile", None) or ""),
            )
        )
        # Dedupe while preserving order
        legacy_fields = list(dict.fromkeys(legacy_fields))
    if legacy_fields:
        raise HTTPException(
            status_code=422,
            detail=legacy_convert_reject_detail(legacy_fields),
        )

    def _custom_engine(asset_id: str) -> str | None:
        """Internal helper ``_custom_engine``."""
        if profiles_service is None:
            return None
        try:
            asset = profiles_service.get_library_asset(asset_id)
        except ValueError:
            raise
        except Exception:
            return None
        from metar_iwxxm_api.convert_library_hard_cut import assert_library_usable_on_convert

        assert_library_usable_on_convert(
            kind=asset.kind,
            expected_kind="conversion",
            access=asset.access,
            status=asset.status,
        )
        return asset.engine_profile_id

    from src.routers.conversion_convert_continue import convert_continue

    # Module-level imports live in globals(), not locals(); merge so continue
    # modules receive helpers (_resolve_*, api_surface, schemas, etc.).
    return await convert_continue({**globals(), **locals()})
