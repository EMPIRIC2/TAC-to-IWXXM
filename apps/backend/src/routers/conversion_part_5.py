"""Part 5 of ``conversion.py`` (line-cap split)."""

from __future__ import annotations

import pathlib
import time
from typing import Any

from fastapi import UploadFile

from src.schemas.conversion import (
    ConversionIssueSeverity,
    ConversionResult,
)
from src.schemas.icao_opmet import TranslationStatus
from src.schemas.validation import (
    ValidationLayer,
)
from src.services.validation import ValidationError as ValidationServiceError
from src.utilities.conversion import ConversionError
from src.utilities.tac_parser import extract_airport_code

from .conversion_api_surface import api_surface
from .conversion_part_1 import (
    _convert_output_policy_id,
    _ConvertRuntime,
    _initial_layers_passed,
    _output_validation_orch_layers,
    _pre_convert_tac_layers,
    _run_pre_convert_validation,
    logger,
)
from .conversion_part_2 import _ConvertAccumulator


async def _process_uploaded_files(
    files: list[UploadFile] | None,
    *,
    runtime: _ConvertRuntime,
    acc: _ConvertAccumulator,
) -> None:
    """
    Internal helper ``_process_uploaded_files``.

    Parameters
    ----------
    files : object
        Argument ``files``.
    runtime : object
        Argument ``runtime``.
    acc : object
        Argument ``acc``.
    """
    if not files:
        return

    for upload in files:
        acc.total_inputs += 1
        start_time: float | None = None
        translation_id: str | None = None
        data = ""
        source_name = upload.filename or "unknown_file"
        try:
            raw_data, read_error = await api_surface.read_uploaded_text(upload)
            data = raw_data or ""
            if read_error:
                acc.errors.append(f"{source_name}: {read_error}")
                acc.add_issue(
                    source=source_name,
                    message=f"Invalid input file: {read_error}",
                    severity=ConversionIssueSeverity.ERROR,
                    hint="Upload a UTF-8 file containing a METAR/SPECI TAC message.",
                    code="INVALID_INPUT_FILE",
                )
                if runtime.stop_on_error:
                    break
                continue

            xml_rejection = api_surface.classify_and_validate_upload_content(
                filename=upload.filename,
                content=data,
                iwxxm_version=runtime.iwxxm_version,
                endpoint_path="/api/v1/convert",
                validation_orchestrator=runtime.validation_orchestrator,
            )
            if xml_rejection:
                acc.errors.append(f"{source_name}: {xml_rejection['message']}")
                acc.add_issue(
                    source=source_name,
                    message=xml_rejection["message"],
                    severity=ConversionIssueSeverity.ERROR,
                    hint=xml_rejection["hint"],
                    code=xml_rejection["code"],
                    layer=xml_rejection["layer"],
                )
                if runtime.stop_on_error:
                    break
                continue

            try:
                pre_layers = _pre_convert_tac_layers(runtime.product)
                if pre_layers is not None:
                    validation_result = _run_pre_convert_validation(
                        runtime.validation_service, data.strip(), pre_layers
                    )
                    if not validation_result.passed:
                        validation_summary = f"{validation_result.total_issues} validation issue(s) found"
                        acc.add_issue(
                            source=source_name,
                            message=f"Validation failed: {validation_summary}",
                            severity=ConversionIssueSeverity.ERROR,
                            hint="Fix TAC format and ICAO code issues, then retry conversion.",
                            code="VALIDATION_FAILED",
                        )
                        acc.add_aggregated_validation_issues(source_name, validation_result)
                        if runtime.preview:
                            acc.record_preview_layer12_soft_fail(validation_result, data.strip())
                        else:
                            error_msg = f"{source_name}: Validation failed - {validation_summary}"
                            acc.errors.append(error_msg)
                            try:
                                translation_id = await api_surface.statistics_service.log_translation(
                                    tac_message=data.strip(),
                                    iwxxm_output=None,
                                    iwxxm_version=runtime.iwxxm_version,
                                    translation_status=TranslationStatus.FAILED,
                                    validation_layers_passed=[],
                                    validation_errors={"validation": validation_summary},
                                    translation_duration_ms=0,
                                    icao_airport_code=extract_airport_code(data.strip()),
                                    user_id=None,
                                )
                                airport_code = extract_airport_code(data.strip())
                                await api_surface.webhook_service.notify_translation_failed(
                                    translation_id=translation_id,
                                    airport_code=airport_code or "UNKNOWN",
                                    error_type="validation_failed",
                                    error_message=validation_summary,
                                )
                            except Exception as log_err:
                                logger.error(f"Failed to log failed translation: {log_err}")
                            continue
                    else:
                        # Soft warnings (e.g. UNKNOWN_ICAO) must surface without aborting.
                        acc.add_aggregated_validation_issues(source_name, validation_result)
            except ValidationServiceError as ve:
                acc.add_issue(
                    source=source_name,
                    message=str(ve),
                    severity=ConversionIssueSeverity.ERROR,
                    hint="Ensure the METAR starts with METAR/SPECI and includes a valid ICAO station and timestamp.",
                    code="VALIDATION_SERVICE_ERROR",
                )
                if runtime.preview:
                    acc.record_preview_layer12_soft_fail(None, data.strip())
                else:
                    acc.errors.append(f"{upload.filename}: {ve!s}")
                    try:
                        translation_id = await api_surface.statistics_service.log_translation(
                            tac_message=data.strip(),
                            iwxxm_output=None,
                            iwxxm_version=runtime.iwxxm_version,
                            translation_status=TranslationStatus.FAILED,
                            validation_layers_passed=[],
                            validation_errors={"error": str(ve)},
                            translation_duration_ms=0,
                            icao_airport_code=extract_airport_code(data.strip()),
                            user_id=None,
                        )
                        airport_code = extract_airport_code(data.strip())
                        await api_surface.webhook_service.notify_translation_failed(
                            translation_id=translation_id,
                            airport_code=airport_code or "UNKNOWN",
                            error_type="validation_error",
                            error_message=str(ve),
                        )
                    except Exception as log_err:
                        logger.error(f"Failed to log validation error: {log_err}")
                    if runtime.stop_on_error:
                        break
                    continue

            start_time = time.perf_counter()
            soft_preview_buf: dict[str, Any] = {}
            xml_text, _ = api_surface.convert_metar_tac_with_metadata(
                data,
                iwxxm_version=runtime.iwxxm_version,
                reference_time=runtime.bulletin_date or None,
                validate=False,
                product=runtime.product,
                profile=runtime.semantic_canonical,
                report_variant=runtime.resolved_report_variant,
                preview=runtime.preview,
                soft_preview_out=soft_preview_buf,
                emit_translation_centre=runtime.emit_translation_centre,
                translation_centre_designator=runtime.translation_centre_designator,
                translation_centre_name=runtime.translation_centre_name,
                propagate_residuals_to_remarks=runtime.propagate_residuals_to_remarks,
                include_national_remarks=runtime.include_national_remarks,
            )
            acc.absorb_soft_preview(soft_preview_buf, preview=runtime.preview, source=source_name)
            if runtime.preview and soft_preview_buf.get("ok") is False:
                acc.add_issue(
                    source=source_name,
                    message="Soft-preview: conversion incomplete",
                    severity=ConversionIssueSeverity.ERROR,
                    hint="Fix failed TAC spans and retry hard convert before publish.",
                    code="SOFT_PREVIEW_PARTIAL",
                )

            duration_ms = int((time.perf_counter() - start_time) * 1000)
            layers_passed = _initial_layers_passed(runtime.product)
            validation_errors_dict: dict[str, Any] = {}

            if runtime.validate_output and runtime.validation_orchestrator:
                try:
                    pkg_out = api_surface._call_iwxxm_validate(
                        xml_text,
                        iwxxm_version=runtime.iwxxm_version,
                        profile=runtime.emit_profile or "annex3",
                        levels=("xsd", "schematron"),
                        emit_key=runtime.emit_profile or "annex3",
                        extensions=runtime.resolved_extensions,
                        product=runtime.product,
                        output_policy_id=_convert_output_policy_id(runtime.emit_profile or "annex3"),
                    )
                    orch_layers = _output_validation_orch_layers()
                    validation_result = runtime.validation_orchestrator.validate_complete(
                        tac_text=data.strip(),
                        xml_content=xml_text,
                        version=runtime.iwxxm_version,
                        layers=orch_layers,
                        stop_on_error=False,
                    )
                    if pkg_out.ok and validation_result.is_valid:
                        layers_passed.extend(
                            layer.value for layer in ValidationLayer if layer.value not in layers_passed
                        )
                    else:
                        validation_errors_dict = acc.emit_output_validation_soft_warning(
                            source=source_name,
                            label=upload.filename or source_name,
                            pkg_out=pkg_out,
                            validation_result=validation_result,
                        )
                except Exception as ve:
                    logger.warning(f"{upload.filename}: Output validation failed: {ve}")
                    acc.add_issue(
                        source=source_name,
                        message=f"Output validation failed: {ve}",
                        severity=ConversionIssueSeverity.WARNING,
                        hint="Conversion succeeded, but post-conversion validation could not complete.",
                        code="OUTPUT_VALIDATION_FAILED",
                        layer="iwxxm_output",
                    )
                    validation_errors_dict = {"validation_error": str(ve)}

            try:
                soft_incomplete = bool(runtime.preview and soft_preview_buf.get("ok") is False)
                translation_id = await api_surface.statistics_service.log_translation(
                    tac_message=data.strip(),
                    iwxxm_output=xml_text,
                    iwxxm_version=runtime.iwxxm_version,
                    translation_status=(TranslationStatus.FAILED if soft_incomplete else TranslationStatus.SUCCESS),
                    validation_layers_passed=layers_passed,
                    validation_errors=validation_errors_dict if validation_errors_dict else None,
                    translation_duration_ms=duration_ms,
                    icao_airport_code=extract_airport_code(data.strip()),
                    user_id=None,
                )
                if soft_incomplete:
                    await api_surface.webhook_service.notify_translation_failed(
                        translation_id=translation_id,
                        airport_code=extract_airport_code(data.strip()) or "UNKNOWN",
                        error_type="soft_preview_partial",
                        error_message="Soft-preview conversion incomplete",
                    )
                else:
                    await api_surface.webhook_service.notify_translation_success(
                        translation_id=translation_id,
                        airport_code=extract_airport_code(data.strip()) or "UNKNOWN",
                        icao_region=api_surface.get_icao_region(extract_airport_code(data.strip()) or "ZZZZ"),
                        iwxxm_version=runtime.iwxxm_version,
                        duration_ms=duration_ms,
                    )
            except Exception as log_err:
                logger.error(f"Failed to log successful translation: {log_err}")

            out_name = pathlib.Path(upload.filename or "unknown").stem + ".txt"
            file_xml = runtime.finalize_exchange_xml(xml_text, data.strip())
            acc.results.append(
                ConversionResult(
                    name=out_name,
                    content=file_xml,
                    tac_input=data.strip(),
                    source=source_name,
                    size_bytes=len(file_xml.encode("utf-8")),
                )
            )
        except ConversionError as exc:
            acc.errors.append(f"{upload.filename}: {exc}")
            acc.add_issue(
                source=upload.filename or "unknown_file",
                message=str(exc),
                severity=ConversionIssueSeverity.ERROR,
                hint="Check METAR TAC structure and required tokens (station/time/wind).",
                code="CONVERSION_ERROR",
            )
            try:
                translation_id = await api_surface.statistics_service.log_translation(
                    tac_message=data.strip(),
                    iwxxm_output=None,
                    iwxxm_version=runtime.iwxxm_version,
                    translation_status=TranslationStatus.FAILED,
                    validation_layers_passed=[],
                    validation_errors={"conversion_error": str(exc)},
                    translation_duration_ms=int((time.perf_counter() - start_time) * 1000) if start_time else 0,
                    icao_airport_code=extract_airport_code(data.strip()) or None,
                    user_id=None,
                )
                airport_code = extract_airport_code(data.strip()) or None
                await api_surface.webhook_service.notify_translation_failed(
                    translation_id=translation_id,
                    airport_code=airport_code or "UNKNOWN",
                    error_type="conversion_error",
                    error_message=str(exc),
                )
            except Exception as log_err:
                logger.error(f"Failed to log conversion error: {log_err}")
            if runtime.stop_on_error:
                break
        except Exception as exc:
            acc.errors.append(f"{upload.filename}: unexpected error {exc}")
            acc.add_issue(
                source=upload.filename or "unknown_file",
                message=f"Unexpected backend error: {exc}",
                severity=ConversionIssueSeverity.ERROR,
                hint="Retry once. If it persists, contact support with this message.",
                code="UNEXPECTED_BACKEND_ERROR",
            )
            try:
                translation_id = await api_surface.statistics_service.log_translation(
                    tac_message=data.strip(),
                    iwxxm_output=None,
                    iwxxm_version=runtime.iwxxm_version,
                    translation_status=TranslationStatus.FAILED,
                    validation_layers_passed=[],
                    validation_errors={"unexpected_error": str(exc)},
                    translation_duration_ms=int((time.perf_counter() - start_time) * 1000) if start_time else 0,
                    icao_airport_code=extract_airport_code(data.strip()) or None,
                    user_id=None,
                )
                airport_code = extract_airport_code(data.strip()) or None
                await api_surface.webhook_service.notify_translation_failed(
                    translation_id=translation_id,
                    airport_code=airport_code or "UNKNOWN",
                    error_type="unexpected_error",
                    error_message=str(exc),
                )
            except Exception as log_err:
                logger.error(f"Failed to log unexpected error: {log_err}")
            if runtime.stop_on_error:
                break
