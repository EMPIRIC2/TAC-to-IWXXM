"""Continuation of ``convert_zip`` (line-cap)."""

from __future__ import annotations

import datetime
import io
import time
import zipfile
from typing import Any

from fastapi.responses import StreamingResponse

from src.schemas.icao_opmet import TranslationStatus
from src.services.validation import ValidationError as ValidationServiceError
from src.utilities.conversion import ConversionError
from src.utilities.tac_parser import extract_airport_code

from .conversion_api_surface import api_surface


async def convert_zip_continue(_prelude: dict[str, Any]) -> Any:
    """Resume ``convert_zip`` after prelude."""
    _ = _prelude.get("_")
    airport_code = _prelude.get("airport_code")
    body_data = _prelude.get("body_data")
    bulletin_date = _prelude.get("bulletin_date")
    content = _prelude.get("content")
    data = _prelude.get("data")
    duration_ms = _prelude.get("duration_ms")
    e = _prelude.get("e")
    error_msg = _prelude.get("error_msg")
    errors = _prelude.get("errors")
    files = _prelude.get("files")
    fname = _prelude.get("fname")
    idx = _prelude.get("idx")
    iwxxm_version = _prelude.get("iwxxm_version")
    log_err = _prelude.get("log_err")
    logger = _prelude.get("logger")
    manual_entries = _prelude.get("manual_entries")
    manual_entry = _prelude.get("manual_entry")
    manual_index = _prelude.get("manual_index")
    manual_name = _prelude.get("manual_name")
    manual_text = _prelude.get("manual_text")
    mem = _prelude.get("mem")
    metar_name = _prelude.get("metar_name")
    metar_text = _prelude.get("metar_text")
    metars_list = _prelude.get("metars_list")
    propagate_residuals_to_remarks = _prelude.get("propagate_residuals_to_remarks")
    read_error = _prelude.get("read_error")
    request = _prelude.get("request")
    request_body = _prelude.get("request_body")
    results = _prelude.get("results")
    source_name = _prelude.get("source_name")
    stamp = _prelude.get("stamp")
    start_time = _prelude.get("start_time")
    translation_id = _prelude.get("translation_id")
    translation_ids = _prelude.get("translation_ids")
    uf = _prelude.get("uf")
    validation_orchestrator = _prelude.get("validation_orchestrator")
    validation_result = _prelude.get("validation_result")
    validation_service = _prelude.get("validation_service")
    validation_summary = _prelude.get("validation_summary")
    ve = _prelude.get("ve")
    webhook_err = _prelude.get("webhook_err")
    xml_rejection = _prelude.get("xml_rejection")
    xml_text = _prelude.get("xml_text")
    zf = _prelude.get("zf")
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
                        translation_id = await api_surface.statistics_service.log_translation(
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
                        await api_surface.webhook_service.notify_translation_failed(
                            translation_id=translation_id,
                            airport_code=airport_code or "UNKNOWN",
                            error_type="validation_failed",
                            error_message=validation_summary,
                        )
                    except Exception as log_err:
                        logger.error(f"Failed to log failed translation: {log_err}")
                    continue  # Skip to next METAR
            except ValidationServiceError as ve:
                errors.append(f"{metar_name}: {ve!s}")
                # Log validation error
                try:
                    translation_id = await api_surface.statistics_service.log_translation(
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
                    await api_surface.webhook_service.notify_translation_failed(
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

            xml_text, _ = api_surface.convert_metar_tac_with_metadata(
                metar_text.strip(),
                iwxxm_version=iwxxm_version,
                reference_time=bulletin_date or None,
                propagate_residuals_to_remarks=propagate_residuals_to_remarks,
            )

            # Calculate duration
            duration_ms = int((time.perf_counter() - start_time) * 1000)

            fname = f"metar_{idx}.xml"
            results.append((fname, xml_text))

            # Log successful translation
            try:
                translation_id = await api_surface.statistics_service.log_translation(
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
                translation_id = await api_surface.statistics_service.log_translation(
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
                await api_surface.webhook_service.notify_translation_failed(
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
                translation_id = await api_surface.statistics_service.log_translation(
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
                await api_surface.webhook_service.notify_translation_failed(
                    translation_id=translation_id,
                    airport_code=airport_code or "UNKNOWN",
                    error_type="unexpected_error",
                    error_message=str(e),
                )
            except Exception as log_err:
                logger.error(f"Failed to log unexpected error: {log_err}")
    if translation_ids:
        try:
            await api_surface.webhook_service.notify_bulk_completed(
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
    stamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    return StreamingResponse(
        mem,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=iwxxm_batch_{stamp}.zip"},
    )
