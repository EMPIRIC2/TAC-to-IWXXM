"""Core conversion routes: convert, convert-zip, convert-bulletin (EV-037 TD-3b)."""

from __future__ import annotations

import datetime
import io
import logging
import pathlib
import re
import time
import zipfile
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, cast
from uuid import UUID

from dissemination.packaging import apply_exchange_packaging
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import Response, StreamingResponse
from tac2iwxxm.profile_registry import supported_report_variants_for_profile
from tac2iwxxm.profiles.ca_eccc import CA_IWXXM_VERSION
from tac_validate import lint as tac_lint_fn
from tac_validate.models import LintReport

from src import api as api_surface
from src.schemas.conversion import (
    ConversionIssue,
    ConversionIssueSeverity,
    ConversionRequest,
    ConversionResponse,
    ConversionResult,
    ErrorDetail,
    FailedSpan,
)
from src.schemas.icao_opmet import TranslationStatus
from src.schemas.iwxxm_validation import get_namespace_version
from src.schemas.validation import (
    BulletinMetaModel,
    BulletinReportResultModel,
    ConvertBulletinResponse,
    LintFixModel,
    LintIssueModel,
    ValidationLayer,
)
from src.services.conversion_profiles_service import ConversionProfilesService
from src.services.validation import ValidationError as ValidationServiceError
from src.utilities.ca_exchange_wire import apply_ca_eccc_collect_output, ca_eccc_output_spec_for_request
from src.utilities.conversion import ConversionError
from src.utilities.extension_wire import IWXXM_CA_TOKEN
from src.utilities.iwxxm_pass_through import NOT_XML_CODE, lint_iwxxm_pass_through
from src.utilities.metar_normalizer import normalize_recent_weather_tokens
from src.utilities.observability import set_request_log_level
from src.utilities.security import verify_optional_supabase_token
from src.utilities.tac_parser import extract_airport_code
from src.utilities.version_migration import migrate_xml
from tac2iwxxm import BulletinSplitError, iwxxm_filename, parse_ahl

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Conversion"])


def _resolve_effective_iwxxm_version(
    requested_version: str,
    *,
    semantic_canonical: str | None,
    emit_profile: str,
) -> str:
    """Resolve and validate request IWXXM version for a semantic profile."""
    requested = requested_version.strip()
    if not requested:
        requested = CA_IWXXM_VERSION if semantic_canonical == "ca_eccc" else "2025-2"

    try:
        from src.config.iwxxm_versions import get_version_config_for_emit_profile, normalize_version
    except ImportError:
        from config.iwxxm_versions import get_version_config_for_emit_profile, normalize_version

    try:
        normalized = normalize_version(requested)
        get_version_config_for_emit_profile(normalized, emit_profile)
    except ValueError as e:
        logger.warning("[CONVERT] Invalid IWXXM version requested: %s", requested)
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
        ) from e
    return normalized


def _wire_payload_dict(raw_obj: object) -> dict[str, Any]:
    """Normalize tac2iwxxm issue/span payloads to plain dicts."""
    model_dump = getattr(raw_obj, "model_dump", None)
    if callable(model_dump):
        return cast(dict[str, Any], model_dump())
    if isinstance(raw_obj, dict):
        return cast(dict[str, Any], raw_obj)
    return {}


def _resolve_report_variant(emit_profile: str, product: str, requested_variant: str | None) -> str | None:
    """Validate and normalize optional report-variant request input."""
    raw = (requested_variant or "").strip()
    if not raw:
        return None
    variant = raw.upper()
    supported_variants = supported_report_variants_for_profile(emit_profile, product)
    detail = ErrorDetail(
        message="Invalid report_variant",
        errors=[f"Unsupported report_variant {variant!r} for profile {emit_profile!r} and product {product!r}"],
        issues=[
            ConversionIssue(
                source="request",
                message=(
                    f"profile {emit_profile} supports report_variant(s) {sorted(supported_variants)!r} "
                    f"for product {product!r}, got {variant!r}"
                )
                if supported_variants
                else f"profile {emit_profile} does not define report variants for product {product!r}",
                severity=ConversionIssueSeverity.ERROR,
                hint=(
                    "Choose a report_variant from the allowed profile/product set."
                    if supported_variants
                    else "Omit report_variant for profiles without variant catalogs."
                ),
                code="INVALID_REPORT_VARIANT",
            )
        ],
        total_errors=1,
    )
    if variant not in supported_variants:
        raise HTTPException(status_code=400, detail=detail.model_dump())
    return variant


def _infer_report_variant_from_sample(emit_profile: str, product: str, sample_text: str | None) -> str | None:
    """Infer the resolved report variant from TAC lead when the request omits it."""
    supported_variants = supported_report_variants_for_profile(emit_profile, product)
    if not supported_variants:
        return None
    sample = (sample_text or "").strip().upper()
    match = re.match(r"^([A-Z]+)\b", sample)
    if match:
        lead = match.group(1)
        if lead in supported_variants:
            return lead
    product_u = product.strip().upper()
    if product_u in supported_variants:
        return product_u
    return None


@dataclass(slots=True)
class _ConvertAccumulator:
    results: list[ConversionResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    issues: list[ConversionIssue] = field(default_factory=list)
    preview_failed_spans: list[FailedSpan] = field(default_factory=list)
    total_inputs: int = 0
    preview_saw_soft_fail: bool = False

    def add_issue(
        self,
        source: str,
        message: str,
        severity: ConversionIssueSeverity = ConversionIssueSeverity.ERROR,
        hint: str | None = None,
        code: str | None = None,
        layer: str | None = None,
        location: str | None = None,
    ) -> None:
        """Append a conversion/validation issue to this accumulator.

        Parameters
        ----------
        source :
            Input name or logical source label.
        message :
            Operator-facing issue text.
        severity :
            Issue severity (default ERROR).
        hint :
            Optional remediation hint.
        code :
            Optional stable issue code.
        layer :
            Optional validation layer id.
        location :
            Optional location pointer within the input.
        """
        self.issues.append(
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

    def absorb_convert_issues(self, soft: dict[str, Any], *, source: str) -> None:
        """Echo tac2iwxxm non-fatal convert issues (e.g. REMARKS_EXCLUDED) to the client."""
        for raw_obj in cast(list[object], soft.get("convert_issues") or []):
            data = _wire_payload_dict(raw_obj)
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
            self.add_issue(
                source=source,
                message=str(data.get("message") or code or "Convert issue"),
                severity=severity,
                hint=("Use profile=iwxxm_us to retain US REMARKS in IWXXM." if code == "REMARKS_EXCLUDED" else None),
                code=code,
                location=data.get("location"),
            )

    def absorb_soft_preview(
        self,
        soft: dict[str, Any],
        *,
        preview: bool,
        base_offset: int = 0,
        source: str | None = None,
    ) -> None:
        """Merge soft-preview envelope fields from convert_metar_tac_with_metadata."""
        if not soft:
            return
        if source:
            self.absorb_convert_issues(soft, source=source)
        if not preview:
            return
        if soft.get("ok") is False:
            self.preview_saw_soft_fail = True
            for span in cast(list[object], soft.get("failed_spans") or []):
                data = _wire_payload_dict(span)
                if base_offset:
                    if data.get("start") is not None:
                        data["start"] = int(data["start"]) + base_offset
                    if data.get("end") is not None:
                        data["end"] = int(data["end"]) + base_offset
                self.preview_failed_spans.append(FailedSpan(**data))

    def record_preview_layer12_soft_fail(
        self,
        aggregated_result: object,
        tac_text: str = "",
        *,
        base_offset: int = 0,
    ) -> None:
        """Mark soft-preview Layer 1-2 failure and copy spans when present (ADR-022)."""
        self.preview_saw_soft_fail = True
        before = len(self.preview_failed_spans)
        if aggregated_result:
            for layer_result in getattr(aggregated_result, "results", []):
                for validation_issue in getattr(layer_result, "issues", []):
                    start = getattr(validation_issue, "start", None)
                    end = getattr(validation_issue, "end", None)
                    if start is None or end is None:
                        continue
                    self.preview_failed_spans.append(
                        FailedSpan(
                            start=int(start) + base_offset,
                            end=int(end) + base_offset,
                            code=getattr(validation_issue, "code", None),
                            message=str(getattr(validation_issue, "message", "") or "") or None,
                        )
                    )
        if len(self.preview_failed_spans) == before and tac_text:
            self.preview_failed_spans.append(
                FailedSpan(
                    start=base_offset,
                    end=base_offset + len(tac_text),
                    code="LAYER12_SOFT_FAIL",
                    message="Input failed ICAO/TAC Layer 1-2 checks; soft-preview continuing",
                )
            )

    def add_aggregated_validation_issues(self, source: str, aggregated_result: object) -> None:
        """Flatten multi-layer validation results into conversion issues."""
        if not aggregated_result:
            return
        for layer_result in getattr(aggregated_result, "results", []):
            for validation_issue in getattr(layer_result, "issues", []):
                severity = ConversionIssueSeverity.WARNING
                level = str(getattr(validation_issue, "level", "")).lower()
                if level == "error" or level == "critical":
                    severity = ConversionIssueSeverity.ERROR
                elif level == "info":
                    severity = ConversionIssueSeverity.INFO
                self.add_issue(
                    source=source,
                    message=str(getattr(validation_issue, "message", "Validation issue")),
                    severity=severity,
                    hint=getattr(validation_issue, "suggestion", None),
                    code=getattr(validation_issue, "code", None),
                    layer=str(getattr(validation_issue, "layer", "")) or None,
                    location=getattr(validation_issue, "location", None),
                )

    def emit_recent_wx_issues(self, source: str, norm_warnings: list[dict[str, Any]]) -> None:
        """Emit structured conversion issues for recent-weather rewrites."""
        for warning in norm_warnings:
            self.add_issue(
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


@dataclass(slots=True)
class _ConvertRuntime:
    product: str
    emit_profile: str
    iwxxm_version: str
    preview: bool
    stop_on_error: bool
    validate_output: bool
    resolved_report_variant: str | None
    resolved_extensions: list[str]
    emit_translation_centre: bool
    translation_centre_designator: str
    translation_centre_name: str
    propagate_residuals_to_remarks: bool | None
    validation_service: Any
    validation_orchestrator: Any
    finalize_exchange_xml: Callable[[str, str | None], str]


async def _process_json_metars(
    metars_list: list[str],
    *,
    runtime: _ConvertRuntime,
    acc: _ConvertAccumulator,
) -> None:
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
                if api_surface._product_uses_metar_tac_layers(runtime.product):
                    validation_result = runtime.validation_service.validate_all_layers(normalized_metar_text)
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
                acc.absorb_soft_preview(soft_preview_buf, preview=runtime.preview, source=metar_name)
                if runtime.preview and soft_preview_buf.get("ok") is False:
                    acc.add_issue(
                        source=metar_name,
                        message="Soft-preview: conversion incomplete",
                        severity=ConversionIssueSeverity.ERROR,
                        hint="Fix failed TAC spans and retry hard convert before publish.",
                        code="SOFT_PREVIEW_PARTIAL",
                    )

                validation_layers_passed = [ValidationLayer.AIRPORT_ICAO, ValidationLayer.TAC_SYNTAX]
                if runtime.validation_orchestrator:
                    pkg_out = api_surface._call_iwxxm_validate(
                        iwxxm_content,
                        iwxxm_version=runtime.iwxxm_version,
                        profile=runtime.emit_profile or "annex3",
                        levels=("xsd", "schematron"),
                        emit_key=runtime.emit_profile or "annex3",
                        extensions=runtime.resolved_extensions,
                        product=runtime.product,
                    )
                    validation_result = runtime.validation_orchestrator.validate(
                        iwxxm_content,
                        iwxxm_version=runtime.iwxxm_version,
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


async def _process_manual_entries(
    manual_with_offsets: list[tuple[str, int]],
    *,
    runtime: _ConvertRuntime,
    acc: _ConvertAccumulator,
) -> None:
    for manual_index, (manual_entry, entry_offset) in enumerate(manual_with_offsets, 1):
        acc.total_inputs += 1
        manual_source = f"manual_input_{manual_index}" if len(manual_with_offsets) > 1 else "manual_input"
        manual_name = f"{manual_source}.txt"
        start_time: float | None = None
        translation_id: str | None = None
        normalized_entry, norm_warnings = normalize_recent_weather_tokens(manual_entry)

        try:
            try:
                if api_surface._product_uses_metar_tac_layers(runtime.product):
                    validation_result = runtime.validation_service.validate_all_layers(normalized_entry)
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
            layers_passed = [ValidationLayer.AIRPORT_ICAO.value, ValidationLayer.TAC_SYNTAX.value]
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
                    )
                    orch_layers = [
                        layer
                        for layer in ValidationLayer
                        if layer not in (ValidationLayer.XML_SCHEMA, ValidationLayer.SCHEMATRON)
                    ]
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
                        warning_msg = (
                            f"{manual_source}: IWXXM validation issues found - "
                            f"{len(validation_result.all_issues)} issues"
                        )
                        logger.warning(warning_msg)
                        acc.add_issue(
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


async def _process_uploaded_files(
    files: list[UploadFile] | None,
    *,
    runtime: _ConvertRuntime,
    acc: _ConvertAccumulator,
) -> None:
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
                if api_surface._product_uses_metar_tac_layers(runtime.product):
                    validation_result = runtime.validation_service.validate_all_layers(data.strip())
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
                validate=False,
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
            layers_passed = [ValidationLayer.AIRPORT_ICAO.value, ValidationLayer.TAC_SYNTAX.value]
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
                    )
                    orch_layers = [
                        layer
                        for layer in ValidationLayer
                        if layer not in (ValidationLayer.XML_SCHEMA, ValidationLayer.SCHEMATRON)
                    ]
                    validation_result = runtime.validation_orchestrator.validate_complete(
                        tac_text=data.strip(),
                        xml_content=xml_text,
                        version=runtime.iwxxm_version,
                        layers=orch_layers,
                        stop_on_error=False,
                    )
                    if pkg_out.ok and validation_result.is_valid:
                        layers_passed.extend(layer.value for layer in ValidationLayer)
                    else:
                        warning_msg = (
                            f"{upload.filename}: IWXXM validation issues found - "
                            f"{len(validation_result.all_issues)} issues"
                        )
                        logger.warning(warning_msg)
                        acc.add_issue(
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


def _append_pre_convert_lint_issues(
    pre_convert_lint_report: LintReport | None,
    *,
    acc: _ConvertAccumulator,
) -> None:
    if pre_convert_lint_report is None:
        return
    for lint_issue in pre_convert_lint_report.issues:
        sev_raw = str(lint_issue.severity or "info").strip().lower()
        if sev_raw == "error":
            lint_severity = ConversionIssueSeverity.ERROR
        elif sev_raw == "warning":
            lint_severity = ConversionIssueSeverity.WARNING
        else:
            lint_severity = ConversionIssueSeverity.INFO
        acc.add_issue(
            source="lint",
            message=str(lint_issue.message or lint_issue.code or "Lint issue"),
            severity=lint_severity,
            code=str(lint_issue.code or "LINT"),
            location=getattr(lint_issue, "location", None),
        )
    if not pre_convert_lint_report.ok:
        logger.info(
            "[CONVERT] tac-validate issues (non-blocking soft path): %s",
            [item.code for item in pre_convert_lint_report.issues],
        )


@router.post(
    "/convert-bulletin",
    tags=["Conversion"],
    response_model=ConvertBulletinResponse,
    responses={
        400: {"description": "Empty bulletin - no TAC reports after the abbreviated heading"},
        415: {"description": "Unsupported Media Type - multipart/form-data required"},
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
    files: list[UploadFile] | None = File(None),
    manual_text: str = Form(
        default="",
        description=(
            "Bulletin text: abbreviated heading TTAAii CCCC YYGGgg (optional BBB), "
            "then one or more TAC reports. Empty Bulletin ID / Issuing Center uses "
            "the heading TTAAii and CCCC."
        ),
    ),
    profile: str = Form(default="", description="Deprecated - use semantic_profile (legacy alias: annex3 or iwxxm_us)"),
    semantic_profile: str = Form(
        default="",
        description="Semantic profile id (e.g. ICAO_2025, US_FAA_NWS, CA_ECCC, AU_BOM, NZ_CAA_MET, UK_METOFFICE; aliases annex3 / iwxxm_us accepted)",
    ),
    exchange_profile: str = Form(
        default="",
        description="Exchange packaging profile (e.g. GLOBAL_AFS); ignored on convert-only paths",
    ),
    iwxxm_version: str = Form(default="", description="Target IWXXM version"),
    lint: bool = Form(default=True, description="Run tac-validate before each report convert"),
    extensions: list[str] = Form(
        default=[],
        description="Optional national extension tokens (e.g. IWXXM_CA for full Canadian validate stack)",
    ),
    propagate_residuals_to_remarks: bool | None = Form(
        default=None,
        description=(
            "When true, append decode residual token text into remarks / humanReadableText "
            "when the profile supports that path; annex3 documents no XML target. "
            "Omitted uses the profile default (annex3 / ICAO_2025 off)."
        ),
    ),
) -> Response:
    """Split a WMO AHL bulletin and convert each TAC report.

    Partial success is allowed: HTTP 200 when split succeeds even if some reports fail.
    Per-report ``issues`` / ``fixes`` follow lint-style identity.
    """
    wire = api_surface._resolve_request_profiles(
        route="/api/v1/convert-bulletin",
        profile=profile,
        semantic_profile=semantic_profile,
        exchange_profile=exchange_profile,
        for_packaging=True,
    )
    emit_profile: str = str(wire.emit_key)
    profile = emit_profile
    iwxxm_version = _resolve_effective_iwxxm_version(
        iwxxm_version,
        semantic_canonical=wire.semantic_canonical,
        emit_profile=emit_profile,
    )
    api_surface._resolve_request_extensions(extensions, None)

    content_type = (request.headers.get("content-type") or "").lower()
    if "multipart/form-data" not in content_type:
        raise HTTPException(
            status_code=415,
            detail="POST /api/v1/convert-bulletin requires multipart/form-data",
        )

    bulletin_text = manual_text or ""
    if files:
        joined, err = await api_surface.read_upload_files_text(files)
        if err:
            raise HTTPException(status_code=400, detail={"code": "upload_rejected", "message": err})
        if joined:
            bulletin_text = joined

    if not bulletin_text.strip():
        raise HTTPException(
            status_code=400,
            detail={"code": "empty_bulletin", "message": "At least one of files or manual_text is required"},
        )

    product = api_surface.normalize_api_product(product, default=None)

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
        return api_surface.msgspec_json_response(
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
        split = api_surface.tac2iwxxm_split_bulletin(bulletin_text, product=product)
    except BulletinSplitError as exc:
        raise api_surface.bulletin_split_http_error(exc) from exc

    if split.meta.report_count > api_surface.MAX_BULLETIN_REPORTS:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "too_many_reports",
                "message": (
                    f"Bulletin contains {split.meta.report_count} reports; limit is {api_surface.MAX_BULLETIN_REPORTS}"
                ),
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
                xml_out, _ = api_surface.convert_metar_tac_with_metadata(
                    tac,
                    iwxxm_version=iwxxm_version,
                    validate=False,
                    product=product,
                    profile=emit_profile,
                    report_status=split.meta.report_status,
                    propagate_residuals_to_remarks=propagate_residuals_to_remarks,
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

    return api_surface.msgspec_json_response(
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


@router.post(
    "/convert",
    response_model=ConversionResponse,
    tags=["Conversion"],
    responses={},
)
async def convert(
    request: Request,
    files: list[UploadFile] | None = Depends(api_surface.parse_files),
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
    lint: bool = Form(default=True, description="Run tac-validate before convert (Q14=C; default on)"),
    product: str = Form(
        default="METAR",
        description=("TAC product type, or iwxxm for XML pass-through (default METAR for legacy clients)"),
    ),
    profile: str = Form(default="", description="Deprecated - use semantic_profile (legacy alias: annex3 or iwxxm_us)"),
    semantic_profile: str = Form(
        default="",
        description="Semantic profile id (e.g. ICAO_2025, US_FAA_NWS, CA_ECCC, AU_BOM, NZ_CAA_MET, UK_METOFFICE; aliases annex3 / iwxxm_us accepted)",
    ),
    exchange_profile: str = Form(
        default="",
        description="Exchange packaging profile (e.g. GLOBAL_AFS); ignored on convert-only paths",
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
    overlay_id: str = Form(
        default="",
        description=(
            "Optional signed ConversionProfile overlay id. When set, requires Bearer JWT "
            "and ownership (or shared); unknown or unauthorized ids are rejected."
        ),
    ),
    preset_id: str = Form(
        default="",
        description=(
            "Optional saved semantic preset id. When set, requires Bearer JWT. "
            "Explicit request fields still win when both are supplied."
        ),
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

    applied_preset_id: str | None = None
    preset_token = (preset_id or "").strip()
    overlay_token = (overlay_id or "").strip()
    has_explicit_semantic_profile = bool((semantic_profile or "").strip() or (profile or "").strip())
    if preset_token:
        if profiles_service is None:
            raise HTTPException(
                status_code=401,
                detail="Sign in required to apply a semantic preset",
                headers={"WWW-Authenticate": "Bearer"},
            )
        try:
            preset_uuid = UUID(preset_token)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Unknown preset id") from exc
        preset = profiles_service.get_preset(preset_uuid)
        applied_preset_id = str(preset.id)
        if not has_explicit_semantic_profile:
            semantic_profile = preset.semantic_profile
        if not (iwxxm_version or "").strip():
            iwxxm_version = preset.iwxxm_version
        if not has_explicit_semantic_profile and not (report_variant or "").strip() and preset.report_variant:
            report_variant = preset.report_variant
        if not extensions and preset.extensions:
            extensions = list(preset.extensions)
        if not has_explicit_semantic_profile and not overlay_token and preset.overlay_id is not None:
            overlay_token = str(preset.overlay_id)

    applied_overlay_id: str | None = None
    overlay_base_profile: str | None = None
    if overlay_token:
        if profiles_service is None:
            raise HTTPException(
                status_code=401,
                detail="Sign in required to apply a ConversionProfile overlay",
                headers={"WWW-Authenticate": "Bearer"},
            )
        try:
            overlay_uuid = UUID(overlay_token)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Unknown overlay id") from exc
        overlay = profiles_service.get_overlay(overlay_uuid)
        applied_overlay_id = str(overlay.id)
        overlay_base_profile = overlay.base_profile_id
        if not (semantic_profile or "").strip() and not (profile or "").strip():
            semantic_profile = overlay_base_profile

    json_profile = getattr(request_body, "profile", None) if request_body is not None else None
    json_semantic = getattr(request_body, "semantic_profile", None) if request_body is not None else None
    json_exchange = getattr(request_body, "exchange_profile", None) if request_body is not None else None
    wire = api_surface._resolve_request_profiles(
        route="/api/v1/convert",
        profile=profile,
        semantic_profile=semantic_profile,
        exchange_profile=exchange_profile,
        json_profile=json_profile,
        json_semantic_profile=json_semantic,
        json_exchange_profile=json_exchange,
    )
    emit_profile: str = str(wire.emit_key)
    profile = emit_profile
    iwxxm_version = _resolve_effective_iwxxm_version(
        iwxxm_version,
        semantic_canonical=wire.semantic_canonical,
        emit_profile=emit_profile,
    )
    resolved_report_variant = _resolve_report_variant(emit_profile, product, report_variant)

    json_extensions = getattr(request_body, "extensions", None) if request_body is not None else None
    resolved_extensions = api_surface._resolve_request_extensions(extensions, json_extensions)

    if wire.semantic_canonical == "ca_eccc" and IWXXM_CA_TOKEN in resolved_extensions:
        try:
            from iwxxm_validate.ca_eccc_bundle import ca_eccc_bundle_available
        except ImportError:

            def ca_eccc_bundle_available(
                *,
                iwxxm_version: str = "3.0.0",
                extension_tag: str = "3.0",
            ) -> bool:
                """Return False when the Canadian extension bundle cannot be imported."""
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
            joined, err = await api_surface.read_upload_files_text(files)
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
        pass_issues: list[ConversionIssue] = []
        try:
            source_iwxxm_version = get_namespace_version(xml_payload)
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=ErrorDetail(
                    message="Unsupported IWXXM source version",
                    errors=[str(exc)],
                    issues=[
                        ConversionIssue(
                            source="manual",
                            message=str(exc),
                            severity=ConversionIssueSeverity.ERROR,
                            code="UNSUPPORTED_IWXXM_SOURCE_VERSION",
                        )
                    ],
                    total_errors=1,
                ).model_dump(),
            ) from exc

        migrated_iwxxm = source_iwxxm_version != iwxxm_version
        migrated_payload = xml_payload
        migration_warnings: list[dict[str, Any]] = []
        if migrated_iwxxm:
            migrated_payload, migration_warnings = migrate_xml(
                xml_payload,
                from_version=source_iwxxm_version,
                to_version=iwxxm_version,
                emit_profile=emit_profile,
            )
            pass_issues.extend(
                ConversionIssue(
                    source="manual",
                    message=str(warning.get("reason") or "IWXXM migration adjusted the document for the target line."),
                    severity=ConversionIssueSeverity.WARNING,
                    code="IWXXM_VERSION_MIGRATION",
                    layer="iwxxm_version_migration",
                    location=str(warning.get("xpath") or "") or None,
                )
                for warning in migration_warnings
            )
        want_validate = (
            migrated_iwxxm
            or bool(validate_output)
            or str(validation_level or "").lower()
            in {
                "comprehensive",
                "schematron",
                "icao_opmet",
                "schema",
            }
        )
        if want_validate:
            try:
                report = api_surface._call_iwxxm_validate(
                    migrated_payload,
                    iwxxm_version=iwxxm_version,
                    profile=(profile or "annex3"),
                    levels=("xsd", "schematron"),
                    emit_key=(profile or "annex3"),
                    extensions=resolved_extensions,
                    product=product,
                )
                if not getattr(report, "ok", True):
                    validation_issues = [
                        ConversionIssue(
                            source="manual",
                            message=str(getattr(issue, "message", "") or "IWXXM validation issue"),
                            severity=(
                                ConversionIssueSeverity.ERROR if migrated_iwxxm else ConversionIssueSeverity.WARNING
                            ),
                            code=str(getattr(issue, "code", None) or "IWXXM_VALIDATE"),
                            location=getattr(issue, "location", None),
                            layer=getattr(issue, "layer", None),
                        )
                        for issue in getattr(report, "issues", []) or []
                    ]
                    if migrated_iwxxm:
                        raise HTTPException(
                            status_code=400,
                            detail=ErrorDetail(
                                message="Migrated IWXXM did not validate for the requested target version",
                                errors=[issue.message for issue in validation_issues],
                                issues=validation_issues,
                                total_errors=len(validation_issues),
                            ).model_dump(),
                        )
                    pass_issues.extend(validation_issues)
            except Exception as exc:
                if isinstance(exc, HTTPException):
                    raise
                logger.warning("[CONVERT] IWXXM pass-through validate_output failed: %s", exc)
                if migrated_iwxxm:
                    raise HTTPException(
                        status_code=400,
                        detail=ErrorDetail(
                            message="Migrated IWXXM validation could not complete",
                            errors=[str(exc)],
                            issues=[
                                ConversionIssue(
                                    source="manual",
                                    message=f"Migrated IWXXM validation could not complete: {exc}",
                                    severity=ConversionIssueSeverity.ERROR,
                                    code="IWXXM_VALIDATE_ERROR",
                                )
                            ],
                            total_errors=1,
                        ).model_dump(),
                    ) from exc
                pass_issues.append(
                    ConversionIssue(
                        source="manual",
                        message=f"Optional IWXXM validation could not complete: {exc}",
                        severity=ConversionIssueSeverity.WARNING,
                        code="IWXXM_VALIDATE_ERROR",
                    )
                )
        return api_surface.msgspec_json_response(
            ConversionResponse(
                results=[
                    ConversionResult(
                        name="iwxxm_pass_through.xml",
                        content=migrated_payload,
                        tac_input=None,
                        source="manual",
                        size_bytes=len(migrated_payload.encode("utf-8")),
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
                    "source_iwxxm_version": source_iwxxm_version,
                    "target_iwxxm_version": iwxxm_version,
                    "migrated_iwxxm": migrated_iwxxm,
                },
            )
        )

    # Q14=C: lint default on - echo tac-validate issues on the convert response (FR-L6).
    pre_convert_lint_report = None
    if lint:
        sample = manual_text.strip() if manual_text else ""
        if request_body is not None and getattr(request_body, "metars", None):
            sample = (request_body.metars[0] or "").strip() if request_body.metars else sample
        if sample:
            pre_convert_lint_report = tac_lint_fn(sample, product=product, profile=profile)

    validation_level = api_surface.normalize_validation_level(validation_level)
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

    acc = _ConvertAccumulator()

    # Initialize validation service for input validation
    validation_service = api_surface.ValidationService()

    # Initialize validation orchestrator for output validation if requested
    validation_orchestrator = api_surface.get_validation_orchestrator() if validate_output else None

    # Handle JSON request body with metars list
    metars_list: list[Any] = []
    if request_body is not None and request_body.metars:
        metars_list = request_body.metars

    manual_with_offsets = api_surface.manual_entries_with_offsets(manual_text or "", product=product)
    manual_entries = [entry for entry, _ in manual_with_offsets]

    sample_for_output_spec = manual_text.strip() if manual_text else ""
    if not sample_for_output_spec and metars_list:
        sample_for_output_spec = (metars_list[0] or "").strip()
    response_report_variant = resolved_report_variant or _infer_report_variant_from_sample(
        emit_profile,
        product,
        sample_for_output_spec or None,
    )
    request_metadata: dict[str, Any] = {
        "bulletin_id": bulletin_id,
        "issuing_center": issuing_center,
        "validation_level": validation_level,
        "stop_on_error": bool(stop_on_error),
        "semantic_profile": wire.semantic_canonical,
    }
    if applied_preset_id:
        request_metadata["preset_id"] = applied_preset_id
    if response_report_variant:
        request_metadata["report_variant"] = response_report_variant
    if applied_overlay_id:
        request_metadata["overlay_id"] = applied_overlay_id
        if overlay_base_profile:
            request_metadata["overlay_base_profile"] = overlay_base_profile
    if exchange_output:
        request_metadata["exchange_output"] = True
    output_spec = ca_eccc_output_spec_for_request(
        semantic_canonical=wire.semantic_canonical,
        product=product,
        sample_text=sample_for_output_spec or None,
    )
    if output_spec:
        request_metadata["output_spec"] = output_spec

    def _finalize_exchange_xml(xml: str, tac_input: str | None) -> str:
        spec_filename: str | None = None
        meta_output_spec = request_metadata.get("output_spec")
        if isinstance(meta_output_spec, dict):
            raw_name = cast(dict[str, Any], meta_output_spec).get("suggested_filename")
            spec_filename = str(raw_name) if raw_name is not None else None
        return apply_ca_eccc_collect_output(
            xml,
            semantic_canonical=wire.semantic_canonical,
            exchange_output=exchange_output,
            product=product,
            tac_input=tac_input,
            bulletin_identifier=spec_filename,
            bulletin_context=sample_for_output_spec or None,
        )

    runtime = _ConvertRuntime(
        product=product,
        emit_profile=emit_profile,
        iwxxm_version=iwxxm_version,
        preview=preview,
        stop_on_error=stop_on_error,
        validate_output=validate_output,
        resolved_report_variant=resolved_report_variant,
        resolved_extensions=resolved_extensions,
        emit_translation_centre=emit_translation_centre,
        translation_centre_designator=translation_centre_designator,
        translation_centre_name=translation_centre_name,
        propagate_residuals_to_remarks=propagate_residuals_to_remarks,
        validation_service=validation_service,
        validation_orchestrator=validation_orchestrator,
        finalize_exchange_xml=_finalize_exchange_xml,
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

    await _process_json_metars(metars_list, runtime=runtime, acc=acc)
    await _process_manual_entries(manual_with_offsets, runtime=runtime, acc=acc)
    await _process_uploaded_files(files, runtime=runtime, acc=acc)

    _append_pre_convert_lint_issues(pre_convert_lint_report, acc=acc)

    if not acc.results and acc.errors:
        logger.error(
            "[CONVERT] All conversions failed total_inputs=%s total_errors=%s first_error=%s",
            acc.total_inputs,
            len(acc.errors),
            acc.errors[0] if acc.errors else "none",
        )
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(
                message="All conversions failed",
                errors=acc.errors,
                issues=acc.issues,
                total_errors=len(acc.errors),
            ).model_dump(),
        )

    envelope_ok: bool | None = None
    if preview:
        envelope_ok = not acc.preview_saw_soft_fail and len(acc.errors) == 0

    return api_surface.msgspec_json_response(
        ConversionResponse(
            results=acc.results,
            errors=acc.errors,
            issues=acc.issues,
            total_processed=acc.total_inputs,
            successful=len(acc.results),
            failed=len(acc.errors),
            metadata=request_metadata,
            ok=envelope_ok,
            failed_spans=acc.preview_failed_spans if preview else [],
        )
    )


@router.post(
    "/convert-zip",
    response_class=StreamingResponse,
    tags=["Conversion"],
    responses={},
)
async def convert_zip(
    request: Request,
    files: list[UploadFile] | None = Depends(api_surface.parse_files),
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
                propagate_residuals_to_remarks=propagate_residuals_to_remarks,
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
                    propagate_residuals_to_remarks=propagate_residuals_to_remarks,
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

    # Send bulk completion webhook if conversions were successful
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
