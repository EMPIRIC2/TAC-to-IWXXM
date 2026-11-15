"""Part 4 of ``conversion.py`` (line-cap split)."""

from __future__ import annotations

import time
from typing import Any

from src.routers.conversion_api_surface import api_surface
from src.routers.conversion_part_1 import (
    _convert_output_policy_id,
    _ConvertRuntime,
    _initial_layers_passed,
    _output_validation_orch_layers,
    _pre_convert_tac_layers,
    _run_pre_convert_validation,
    logger,
)
from src.routers.conversion_part_2 import _ConvertAccumulator
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


async def _process_manual_entries(
    manual_with_offsets: list[tuple[str, int]],
    *,
    runtime: _ConvertRuntime,
    acc: _ConvertAccumulator,
) -> None:
    """
    Internal helper ``_process_manual_entries``.

    Parameters
    ----------
    manual_with_offsets : object
        Argument ``manual_with_offsets``.
    runtime : object
        Argument ``runtime``.
    acc : object
        Argument ``acc``.
    """
    for manual_index, (manual_entry, entry_offset) in enumerate(manual_with_offsets, 1):
        acc.total_inputs += 1
        manual_source = f"manual_input_{manual_index}" if len(manual_with_offsets) > 1 else "manual_input"
        manual_name = f"{manual_source}.txt"
        start_time: float | None = None
        translation_id: str | None = None
        normalized_entry, norm_warnings = normalize_recent_weather_tokens(manual_entry)

        try:
            try:
                pre_layers = _pre_convert_tac_layers(runtime.product)
                if pre_layers is not None:
                    validation_result = _run_pre_convert_validation(
                        runtime.validation_service, normalized_entry, pre_layers
                    )
                    if not validation_result.passed:
                        validation_summary = f"{validation_result.total_issues} validation issue(s) found"
                        acc.add_issue(
                            source=manual_source,
                            message=f"Validation failed: {validation_summary}",
                            severity=ConversionIssueSeverity.ERROR,
                            hint="Fix TAC format and ICAO code issues, then retry conversion.",
                            code="VALIDATION_FAILED",
                        )
                        acc.add_aggregated_validation_issues(manual_source, validation_result)
                        if runtime.preview:
                            acc.record_preview_layer12_soft_fail(
                                validation_result, normalized_entry, base_offset=entry_offset
                            )
                        else:
                            acc.errors.append(f"{manual_source}: Validation failed - {validation_summary}")
                            try:
                                translation_id = await api_surface.statistics_service.log_translation(
                                    tac_message=manual_entry,
                                    iwxxm_output=None,
                                    iwxxm_version=runtime.iwxxm_version,
                                    translation_status=TranslationStatus.FAILED,
                                    validation_layers_passed=[],
                                    validation_errors={"validation": validation_summary},
                                    translation_duration_ms=0,
                                    icao_airport_code=extract_airport_code(manual_entry),
                                    user_id=None,
                                )
                                airport_code = extract_airport_code(manual_entry)
                                await api_surface.webhook_service.notify_translation_failed(
                                    translation_id=translation_id,
                                    airport_code=airport_code or "UNKNOWN",
                                    error_type="validation_failed",
                                    error_message=validation_summary,
                                )
                            except Exception as log_err:
                                logger.error(f"Failed to log failed translation: {log_err}")
                            if runtime.stop_on_error:
                                break
                            continue
                    else:
                        # Soft warnings (e.g. UNKNOWN_ICAO) must surface without aborting.
                        acc.add_aggregated_validation_issues(manual_source, validation_result)
            except ValidationServiceError as ve:
                acc.add_issue(
                    source=manual_source,
                    message=str(ve),
                    severity=ConversionIssueSeverity.ERROR,
                    hint="Ensure the METAR starts with METAR/SPECI and includes a valid ICAO station and timestamp.",
                    code="VALIDATION_SERVICE_ERROR",
                )
                if runtime.preview:
                    acc.record_preview_layer12_soft_fail(None, normalized_entry, base_offset=entry_offset)
                else:
                    acc.errors.append(f"{manual_source}: {ve!s}")
                    try:
                        translation_id = await api_surface.statistics_service.log_translation(
                            tac_message=manual_entry,
                            iwxxm_output=None,
                            iwxxm_version=runtime.iwxxm_version,
                            translation_status=TranslationStatus.FAILED,
                            validation_layers_passed=[],
                            validation_errors={"error": str(ve)},
                            translation_duration_ms=0,
                            icao_airport_code=extract_airport_code(manual_entry),
                            user_id=None,
                        )
                        airport_code = extract_airport_code(manual_entry)
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
            acc.emit_recent_wx_issues(manual_source, norm_warnings)

            soft_preview_buf: dict[str, Any] = {}
            xml_text, _ = api_surface.convert_metar_tac_with_metadata(
                normalized_entry,
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
            )
            acc.absorb_soft_preview(
                soft_preview_buf,
                preview=runtime.preview,
                base_offset=entry_offset,
                source=manual_source,
            )
            if runtime.preview and soft_preview_buf.get("ok") is False:
                acc.add_issue(
                    source=manual_source,
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
                        tac_text=manual_entry,
                        xml_content=xml_text,
                        version=runtime.iwxxm_version,
                        layers=orch_layers,
                        stop_on_error=False,
                    )
                    if pkg_out.ok and validation_result.is_valid:
                        for layer in ValidationLayer:
                            if layer.value not in layers_passed:
                                layers_passed.append(layer.value)
                    else:
                        validation_errors_dict = acc.emit_output_validation_soft_warning(
                            source=manual_source,
                            label=manual_source,
                            pkg_out=pkg_out,
                            validation_result=validation_result,
                        )
                except Exception as ve:
                    logger.warning(f"{manual_source}: Output validation failed: {ve}")
                    acc.add_issue(
                        source=manual_source,
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
                    tac_message=manual_entry,
                    iwxxm_output=xml_text,
                    iwxxm_version=runtime.iwxxm_version,
                    translation_status=(TranslationStatus.FAILED if soft_incomplete else TranslationStatus.SUCCESS),
                    validation_layers_passed=layers_passed,
                    validation_errors=validation_errors_dict if validation_errors_dict else None,
                    translation_duration_ms=duration_ms,
                    icao_airport_code=extract_airport_code(manual_entry),
                    user_id=None,
                )
                airport_code = extract_airport_code(manual_entry)
                icao_region = api_surface.get_icao_region(airport_code) if airport_code else "UNKNOWN"
                if soft_incomplete:
                    await api_surface.webhook_service.notify_translation_failed(
                        translation_id=translation_id,
                        airport_code=airport_code or "UNKNOWN",
                        error_type="soft_preview_partial",
                        error_message="Soft-preview conversion incomplete",
                    )
                else:
                    await api_surface.webhook_service.notify_translation_success(
                        translation_id=translation_id,
                        airport_code=airport_code or "UNKNOWN",
                        icao_region=icao_region,
                        iwxxm_version=runtime.iwxxm_version,
                        duration_ms=duration_ms,
                    )
            except Exception as log_err:
                logger.error(f"Failed to log successful translation: {log_err}")

            manual_xml = runtime.finalize_exchange_xml(xml_text, manual_entry.strip())
            acc.results.append(
                ConversionResult(
                    name=manual_name,
                    content=manual_xml,
                    tac_input=manual_entry.strip(),
                    source=manual_source,
                    size_bytes=len(manual_xml.encode("utf-8")),
                )
            )
        except ConversionError as exc:
            acc.errors.append(f"{manual_source}: {exc}")
            acc.add_issue(
                source=manual_source,
                message=str(exc),
                severity=ConversionIssueSeverity.ERROR,
                hint="Check METAR TAC structure and required tokens (station/time/wind).",
                code="CONVERSION_ERROR",
            )
            if runtime.stop_on_error:
                break
