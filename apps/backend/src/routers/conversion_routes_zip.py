"""Convert route handlers (line-cap split from conversion.py)."""

from __future__ import annotations

import pathlib
import time
from typing import Any

from fastapi import Depends, Form, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse

from src.schemas.conversion import (
    ConversionIssue,
    ConversionIssueSeverity,
    ConversionRequest,
    ErrorDetail,
)
from src.schemas.icao_opmet import TranslationStatus
from src.utilities.conversion import ConversionError
from src.utilities.tac_parser import extract_airport_code

from .conversion_api_surface import api_surface, parse_files
from .conversion_part_1 import (
    logger,
    router,
)


@router.post(
    "/convert-zip",
    response_class=StreamingResponse,
    tags=["Conversion"],
    summary="Convert TAC to a ZIP of IWXXM files",
    responses={},
)
async def convert_zip(
    request: Request,
    files: list[UploadFile] | None = Depends(parse_files),
    manual_text: str = Form(default="", description="Optional manual text input (METAR TAC format)"),
    iwxxm_version: str = Form(
        default="2025-2",
        description="Target IWXXM version: 2025-2 (latest), 2023-1 (previous), or 2025-1 (auto-remaps to 2025-2)",
    ),
    propagate_residuals_to_remarks: bool | None = Form(
        default=None,
        description=(
            "When true, append decode residual token text into remarks / humanReadableText "
            "when the profile supports that path; annex3 documents no XML target. "
            "Omitted uses the profile default (annex3 / ICAO_2025 off)."
        ),
    ),
    include_national_remarks: bool = Form(
        default=True,
        description=(
            "When false, omit national remarks after RMK from IWXXM output even for "
            "profiles that normally keep remarks."
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
) -> StreamingResponse:
    """Convert METAR/SPECI TAC inputs to a ZIP of IWXXM XML files."""
    # Try to parse JSON body if Content-Type is application/json
    request_body = None
    if request.headers.get("content-type", "").startswith("application/json"):
        try:
            body_data = await request.json()
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Invalid JSON in request body: {e!s}") from e

        try:
            request_body = ConversionRequest(**body_data)
        except Exception as e:
            # Pydantic validation error - return 422
            raise HTTPException(status_code=422, detail=f"Validation error: {e!s}") from e
    # Handle JSON request body (for metars list)
    if request_body is not None:
        metars_list = request_body.metars or []
        iwxxm_version = request_body.version
        manual_text = ""  # Override form input
        files = None  # Override file input
    else:
        metars_list: list[Any] = []

    manual_entries = api_surface.split_manual_entries(manual_text)

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
        from src.config.iwxxm_versions import get_version_config, normalize_version
    except ImportError:
        from config.iwxxm_versions import get_version_config, normalize_version

    try:
        iwxxm_version = normalize_version(iwxxm_version)
        get_version_config(iwxxm_version)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(message=f"Invalid IWXXM version: {e}", errors=[str(e)], total_errors=1).model_dump(),
        ) from e

    results: list[tuple[str, str]] = []
    errors: list[str] = []
    translation_ids: list[str] = []  # Track for bulk notification
    validation_service = api_surface.ValidationService()
    validation_orchestrator = api_surface.get_validation_orchestrator()

    for manual_index, manual_entry in enumerate(manual_entries, 1):
        start_time = None
        translation_id = None
        manual_name = f"manual_input_{manual_index}.xml" if len(manual_entries) > 1 else "manual_input.xml"
        try:
            start_time = time.perf_counter()

            xml_text, _ = api_surface.convert_metar_tac_with_metadata(
                manual_entry,
                iwxxm_version=iwxxm_version,
                reference_time=bulletin_date or None,
                propagate_residuals_to_remarks=propagate_residuals_to_remarks,
                include_national_remarks=include_national_remarks,
            )
            duration_ms = int((time.perf_counter() - start_time) * 1000)

            results.append((manual_name, xml_text))

            try:
                translation_id = await api_surface.statistics_service.log_translation(
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
                translation_id = await api_surface.statistics_service.log_translation(
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
                await api_surface.webhook_service.notify_translation_failed(
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
                data, read_error = await api_surface.read_uploaded_text(uf)
                if read_error:
                    errors.append(f"{source_name}: {read_error}")
                    continue

                xml_rejection = api_surface.classify_and_validate_upload_content(
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

                xml_text, _ = api_surface.convert_metar_tac_with_metadata(
                    data or "",
                    iwxxm_version=iwxxm_version,
                    reference_time=bulletin_date or None,
                    propagate_residuals_to_remarks=propagate_residuals_to_remarks,
                    include_national_remarks=include_national_remarks,
                )

                # Calculate duration
                duration_ms = int((time.perf_counter() - start_time) * 1000)

                fname = pathlib.Path(source_name).stem + ".xml"
                results.append((fname, xml_text))

                # Log successful translation
                try:
                    translation_id = await api_surface.statistics_service.log_translation(
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
                    translation_id = await api_surface.statistics_service.log_translation(
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
                    await api_surface.webhook_service.notify_translation_failed(
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
                    translation_id = await api_surface.statistics_service.log_translation(
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
                    await api_surface.webhook_service.notify_translation_failed(
                        translation_id=translation_id,
                        airport_code=airport_code or "UNKNOWN",
                        error_type="unexpected_error",
                        error_message=str(e),
                    )
                except Exception as log_err:
                    logger.error(f"Failed to log unexpected error: {log_err}")

    from .conversion_zip_continue import convert_zip_continue

    return await convert_zip_continue({**globals(), **locals()})
