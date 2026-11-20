"""Part 3 of ``conversion.py`` (line-cap split)."""

from __future__ import annotations

import time
from typing import Any

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
from src.utilities.metar_normalizer import normalize_recent_weather_tokens
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


async def _process_json_metars(
    metars_list: list[str],
    *,
    runtime: _ConvertRuntime,
    acc: _ConvertAccumulator,
) -> None:
    """
    Internal helper ``_process_json_metars``.

    Parameters
    ----------
    metars_list : object
        Argument ``metars_list``.
    runtime : object
        Argument ``runtime``.
    acc : object
        Argument ``acc``.
    """
    for metar_text in metars_list:
        if not metar_text.strip():
            continue

        normalized_metar_text, norm_warnings = normalize_recent_weather_tokens(metar_text.strip())

        acc.total_inputs += 1
        start_time: float | None = None
        translation_id: str | None = None
        metar_name = f"metar_{acc.total_inputs}.txt"
        try:
            layer12_abort = False
            try:
                pre_layers = _pre_convert_tac_layers(runtime.product)
                if pre_layers is not None:
                    validation_result = _run_pre_convert_validation(
                        runtime.validation_service, normalized_metar_text, pre_layers
                    )
                    if not validation_result.passed:
                        validation_summary = f"{validation_result.total_issues} validation issue(s) found"
                        acc.add_issue(
                            source=metar_name,
                            message=f"Validation failed: {validation_summary}",
                            severity=ConversionIssueSeverity.ERROR,
                            hint="Fix TAC format and ICAO code issues, then retry conversion.",
                            code="VALIDATION_FAILED",
                        )
                        acc.add_aggregated_validation_issues(metar_name, validation_result)
                        if runtime.preview:
                            acc.record_preview_layer12_soft_fail(validation_result, normalized_metar_text)
                        else:
                            error_msg = f"{metar_name}: Validation failed - {validation_summary}"
                            acc.errors.append(error_msg)
                            try:
                                translation_id = await api_surface.statistics_service.log_translation(
                                    tac_message=metar_text.strip(),
                                    iwxxm_output=None,
                                    iwxxm_version=runtime.iwxxm_version,
                                    translation_status=TranslationStatus.FAILED,
                                    validation_layers_passed=[],
                                    validation_errors={"validation": validation_summary},
                                    translation_duration_ms=0,
                                    icao_airport_code=extract_airport_code(metar_text.strip()),
                                    user_id=None,
                                )
                                airport_code = extract_airport_code(metar_text.strip())
                                await api_surface.webhook_service.notify_translation_failed(
                                    translation_id=translation_id,
                                    airport_code=airport_code or "UNKNOWN",
                                    error_type="validation_failed",
                                    error_message=validation_summary,
                                )
                            except Exception as log_err:
                                logger.error(f"Failed to log failed translation: {log_err}")
                            layer12_abort = True
                    else:
                        # Soft warnings (e.g. UNKNOWN_ICAO) must surface without aborting.
                        acc.add_aggregated_validation_issues(metar_name, validation_result)
            except ValidationServiceError as ve:
                acc.add_issue(
                    source=metar_name,
                    message=str(ve),
                    severity=ConversionIssueSeverity.ERROR,
                    hint="Ensure the METAR starts with METAR/SPECI and includes a valid ICAO station and timestamp.",
                    code="VALIDATION_SERVICE_ERROR",
                )
                if runtime.preview:
                    acc.record_preview_layer12_soft_fail(None, normalized_metar_text)
                else:
                    acc.errors.append(f"{metar_name}: {ve!s}")
                    try:
                        translation_id = await api_surface.statistics_service.log_translation(
                            tac_message=metar_text.strip(),
                            iwxxm_output=None,
                            iwxxm_version=runtime.iwxxm_version,
                            translation_status=TranslationStatus.FAILED,
                            validation_layers_passed=[],
                            validation_errors={"error": str(ve)},
                            translation_duration_ms=0,
                            icao_airport_code=extract_airport_code(metar_text.strip()),
                            user_id=None,
                        )
                        airport_code = extract_airport_code(metar_text.strip())
                        await api_surface.webhook_service.notify_translation_failed(
                            translation_id=translation_id,
                            airport_code=airport_code or "UNKNOWN",
                            error_type="validation_error",
                            error_message=str(ve),
                        )
                    except Exception as log_err:
                        logger.error(f"Failed to log validation error: {log_err}")
                    layer12_abort = True

            if layer12_abort:
                if runtime.stop_on_error:
                    break
                continue

            start_time = time.perf_counter()
            acc.emit_recent_wx_issues(metar_name, norm_warnings)

            try:
                soft_preview_buf: dict[str, Any] = {}
                iwxxm_content, _ = api_surface.convert_metar_tac_with_metadata(
                    normalized_metar_text,
                    iwxxm_version=runtime.iwxxm_version,
                    reference_time=runtime.bulletin_date or None,
                    validate=False,
                    lenient=False,
                    product=runtime.product,
                    profile=runtime.emit_profile,
                    report_variant=runtime.resolved_report_variant,
                    preview=runtime.preview,
                    soft_preview_out=soft_preview_buf,
                    emit_translation_centre=runtime.emit_translation_centre,
                    translation_centre_designator=runtime.translation_centre_designator,
                    translation_centre_name=runtime.translation_centre_name,
                    propagate_residuals_to_remarks=runtime.propagate_residuals_to_remarks,
                    include_national_remarks=runtime.include_national_remarks,
                )
                acc.absorb_soft_preview(soft_preview_buf, preview=runtime.preview, source=metar_name)
                if runtime.preview and soft_preview_buf.get("ok") is False:
                    acc.add_issue(
                        source=metar_name,
                        message="Soft-preview: conversion incomplete",
                        severity=ConversionIssueSeverity.ERROR,
                        hint="Fix failed TAC spans and retry hard convert before publish.",
                        code="SOFT_PREVIEW_PARTIAL",
                    )

                validation_layers_passed = [ValidationLayer(layer) for layer in _initial_layers_passed(runtime.product)]
                if runtime.validation_orchestrator:
                    pkg_out = api_surface._call_iwxxm_validate(
                        iwxxm_content,
                        iwxxm_version=runtime.iwxxm_version,
                        profile=runtime.emit_profile or "annex3",
                        levels=("xsd", "schematron"),
                        emit_key=runtime.emit_profile or "annex3",
                        extensions=runtime.resolved_extensions,
                        product=runtime.product,
                        output_policy_id=_convert_output_policy_id(runtime.emit_profile or "annex3"),
                    )
                    validation_result = runtime.validation_orchestrator.validate(
                        iwxxm_content,
                        iwxxm_version=runtime.iwxxm_version,
                        layers=_output_validation_orch_layers(),
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
                    else:
                        # Align JSON metars[] path with manual/upload soft-warn visibility (#1159).
                        acc.emit_output_validation_soft_warning(
                            source=metar_name,
                            label=metar_name,
                            pkg_out=pkg_out,
                            validation_result=validation_result,
                        )

                result_xml = runtime.finalize_exchange_xml(iwxxm_content, metar_text.strip())
                acc.results.append(
                    ConversionResult(
                        name=metar_name,
                        content=result_xml,
                        tac_input=metar_text.strip(),
                        source="json",
                        size_bytes=len(result_xml.encode("utf-8")),
                    )
                )

                try:
                    end_time = time.perf_counter()
                    duration_ms = round((end_time - start_time) * 1000)
                    soft_incomplete = bool(runtime.preview and soft_preview_buf.get("ok") is False)

                    translation_id = await api_surface.statistics_service.log_translation(
                        tac_message=metar_text.strip(),
                        iwxxm_output=iwxxm_content,
                        iwxxm_version=runtime.iwxxm_version,
                        translation_status=(TranslationStatus.FAILED if soft_incomplete else TranslationStatus.SUCCESS),
                        validation_layers_passed=validation_layers_passed,
                        translation_duration_ms=duration_ms,
                        icao_airport_code=extract_airport_code(normalized_metar_text),
                        user_id=None,
                    )

                    airport_code = extract_airport_code(normalized_metar_text)
                    if soft_incomplete:
                        await api_surface.webhook_service.notify_translation_failed(
                            translation_id=translation_id,
                            airport_code=airport_code or "UNKNOWN",
                            error_type="soft_preview_partial",
                            error_message="Soft-preview conversion incomplete",
                        )
                    else:
                        await api_surface.webhook_service.notify_translation_completed(
                            translation_id=translation_id,
                            airport_code=airport_code or "UNKNOWN",
                            iwxxm_version=runtime.iwxxm_version,
                            file_size_bytes=len(iwxxm_content.encode("utf-8")),
                            duration_ms=duration_ms,
                        )
                except Exception as log_err:
                    logger.error(f"Failed to log successful translation: {log_err}")

            except ConversionError as ce:
                error_msg = f"{metar_name}: Conversion error - {ce!s}"
                acc.errors.append(error_msg)
                acc.add_issue(
                    source=metar_name,
                    message=f"Conversion error: {ce}",
                    severity=ConversionIssueSeverity.ERROR,
                    hint="Check METAR TAC structure and required tokens (station/time/wind).",
                    code="CONVERSION_ERROR",
                )
                logger.error(error_msg)
                try:
                    end_time = time.perf_counter()
                    duration_ms = round((end_time - start_time) * 1000) if start_time else 0

                    await api_surface.statistics_service.log_translation(
                        tac_message=metar_text.strip(),
                        iwxxm_output=None,
                        iwxxm_version=runtime.iwxxm_version,
                        translation_status=TranslationStatus.FAILED,
                        validation_layers_passed=[ValidationLayer.AIRPORT_ICAO, ValidationLayer.TAC_SYNTAX],
                        validation_errors={"error": str(ce)},
                        translation_duration_ms=duration_ms,
                        icao_airport_code=extract_airport_code(normalized_metar_text),
                        user_id=None,
                    )

                    airport_code = extract_airport_code(normalized_metar_text)
                    await api_surface.webhook_service.notify_translation_failed(
                        translation_id=translation_id or "unknown",
                        airport_code=airport_code or "UNKNOWN",
                        error_type="conversion_error",
                        error_message=str(ce),
                    )
                except Exception as log_err:
                    logger.error(f"Failed to log conversion error: {log_err}")
                if runtime.stop_on_error:
                    break
            except Exception as exc:
                error_msg = f"{metar_name}: Unexpected error - {exc!s}"
                acc.errors.append(error_msg)
                acc.add_issue(
                    source=metar_name,
                    message=f"Unexpected backend error: {exc}",
                    severity=ConversionIssueSeverity.ERROR,
                    hint="Retry once. If it persists, contact support with this message.",
                    code="UNEXPECTED_BACKEND_ERROR",
                )
                logger.exception(error_msg)
                if runtime.stop_on_error:
                    break
        except Exception as exc:
            error_msg = f"{metar_name}: Unhandled error - {exc!s}"
            acc.errors.append(error_msg)
            acc.add_issue(
                source=metar_name,
                message=f"Unhandled backend error: {exc}",
                severity=ConversionIssueSeverity.ERROR,
                hint="Retry once. If it persists, contact support with this message.",
                code="UNHANDLED_BACKEND_ERROR",
            )
            logger.exception(error_msg)
            if runtime.stop_on_error:
                break
