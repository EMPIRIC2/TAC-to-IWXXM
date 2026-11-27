"""convert_continue part 2."""

from __future__ import annotations

from typing import Any, cast

from fastapi import HTTPException
from tac2iwxxm.group_trace import trace_entries
from tac2iwxxm.heading_paste import (
    HeadingPasteError,
    http_status_for_heading_error,
    reports_for_convert,
)

from src.models.conversion import GroupTrace
from src.schemas.conversion import (
    ConversionIssue,
    ConversionIssueSeverity,
    ConversionResponse,
    ErrorDetail,
)
from src.utilities.ca_exchange_wire import (
    apply_ca_eccc_collect_output,
    ca_eccc_output_spec_for_request,
)
from src.utilities.strict_raise import (
    promote_convert_failure_severity,
)

from .conversion_api_surface import api_surface
from .conversion_part_1 import (
    _ConvertRuntime,
    _infer_report_variant_from_sample,
)
from .conversion_part_2 import (
    _append_pre_convert_lint_issues,
    _record_convert_station_health,
)
from .conversion_part_3 import _process_json_metars
from .conversion_part_4 import _process_manual_entries
from .conversion_part_5 import _process_uploaded_files


async def convert_continue_part2(_prelude: dict[str, Any]) -> Any:
    """Resume convert_continue."""
    _ = _prelude.get("_")
    _custom_engine = _prelude.get("_custom_engine")
    # Nested helper may be defined later in this function; keep prelude binding optional.
    _finalize_exchange_xml = _prelude.get("_finalize_exchange_xml")
    acc = _prelude.get("acc")
    applied_conversion_library_id = _prelude.get("applied_conversion_library_id")
    applied_conversion_template_id = _prelude.get("applied_conversion_template_id")
    asset = _prelude.get("asset")
    auth_user = _prelude.get("auth_user")
    body_conversion_library_id = _prelude.get("body_conversion_library_id")
    body_data = _prelude.get("body_data")
    body_decode = _prelude.get("body_decode")
    body_dissem = _prelude.get("body_dissem")
    body_exchange_output = _prelude.get("body_exchange_output")
    body_iwxxm_lib = _prelude.get("body_iwxxm_lib")
    body_overlay_id = _prelude.get("body_overlay_id")
    body_preset_id = _prelude.get("body_preset_id")
    body_product = _prelude.get("body_product")
    body_prop = _prelude.get("body_prop")
    body_report_variant = _prelude.get("body_report_variant")
    body_tac = _prelude.get("body_tac")
    bulletin_date = _prelude.get("bulletin_date")
    bulletin_id = _prelude.get("bulletin_id")
    ca_eccc_bundle_available = _prelude.get("ca_eccc_bundle_available")
    compute_raised_severities = _prelude.get("compute_raised_severities")
    conversion_library_id = _prelude.get("conversion_library_id")
    conversion_template_id = _prelude.get("conversion_template_id")
    conversion_template_token = _prelude.get("conversion_template_token")
    decoding_library_id = _prelude.get("decoding_library_id")
    dissemination_library_id = _prelude.get("dissemination_library_id")
    emit_profile = _prelude.get("emit_profile")
    emit_translation_centre = _prelude.get("emit_translation_centre")
    entry = _prelude.get("entry")
    envelope_ok = _prelude.get("envelope_ok")
    err = _prelude.get("err")
    exc = _prelude.get("exc")
    exchange_output = _prelude.get("exchange_output")
    exchange_profile = _prelude.get("exchange_profile")
    extensions = _prelude.get("extensions")
    files = _prelude.get("files")
    get_first_party_template = _prelude.get("get_first_party_template")
    get_namespace_version = _prelude.get("get_namespace_version")
    group_trace = _prelude.get("group_trace")
    i = _prelude.get("i")
    include_nil_reasons = _prelude.get("include_nil_reasons")
    is_first_party = _prelude.get("is_first_party")
    issue = _prelude.get("issue")
    issues = _prelude.get("issues")
    issuing_center = _prelude.get("issuing_center")
    iwxxm_lint = _prelude.get("iwxxm_lint")
    iwxxm_validation_library_id = _prelude.get("iwxxm_validation_library_id")
    iwxxm_version = _prelude.get("iwxxm_version")
    joined = _prelude.get("joined")
    json_extensions = _prelude.get("json_extensions")
    legacy_fields = _prelude.get("legacy_fields")
    lint = _prelude.get("lint")
    lint_iwxxm_pass_through = _prelude.get("lint_iwxxm_pass_through")
    log_level = _prelude.get("log_level")
    log_level_norm = _prelude.get("log_level_norm")
    logger = _prelude.get("logger")
    manual_entries = _prelude.get("manual_entries")
    manual_text = _prelude.get("manual_text")
    manual_with_offsets = _prelude.get("manual_with_offsets")
    meta_output_spec = _prelude.get("meta_output_spec")
    metars = _prelude.get("metars")
    metars_list = _prelude.get("metars_list")
    migrate_xml = _prelude.get("migrate_xml")
    migrated_iwxxm = _prelude.get("migrated_iwxxm")
    migrated_payload = _prelude.get("migrated_payload")
    migration_warnings = _prelude.get("migration_warnings")
    output_spec = _prelude.get("output_spec")
    overlay_id = _prelude.get("overlay_id")
    pass_issues = _prelude.get("pass_issues")
    pasted_heading = _prelude.get("pasted_heading")
    pre_convert_lint_report = _prelude.get("pre_convert_lint_report")
    preset_id = _prelude.get("preset_id")
    preview = _prelude.get("preview")
    product = _prelude.get("product")
    profile = _prelude.get("profile")
    profiles_service = _prelude.get("profiles_service")
    promoted = _prelude.get("promoted")
    promoted_issues = _prelude.get("promoted_issues")
    propagate_residuals_to_remarks = _prelude.get("propagate_residuals_to_remarks")
    include_national_remarks = bool(_prelude.get("include_national_remarks", True))
    raised_severities = _prelude.get("raised_severities")
    raw_name = _prelude.get("raw_name")
    report = _prelude.get("report")
    report_variant = _prelude.get("report_variant")
    request = _prelude.get("request")
    request_body = _prelude.get("request_body")
    request_metadata = _prelude.get("request_metadata")
    resolved_extensions = _prelude.get("resolved_extensions")
    resolved_report_variant = _prelude.get("resolved_report_variant")
    response_report_variant = _prelude.get("response_report_variant")
    row = _prelude.get("row")
    runtime = _prelude.get("runtime")
    sample = _prelude.get("sample")
    sample_for_output_spec = _prelude.get("sample_for_output_spec")
    semantic_profile = _prelude.get("semantic_profile")
    set_request_log_level = _prelude.get("set_request_log_level")
    source_iwxxm_version = _prelude.get("source_iwxxm_version")
    spec_filename = _prelude.get("spec_filename")
    stop_on_error = _prelude.get("stop_on_error")
    strict = _prelude.get("strict")
    strict_convert = _prelude.get("strict_convert")
    strict_lint = _prelude.get("strict_lint")
    strict_validate = _prelude.get("strict_validate")
    tac_input = _prelude.get("tac_input")
    tac_lint_fn = _prelude.get("tac_lint_fn")
    tac_validation_library_id = _prelude.get("tac_validation_library_id")
    tmpl = _prelude.get("tmpl")
    translation_centre_designator = _prelude.get("translation_centre_designator")
    translation_centre_name = _prelude.get("translation_centre_name")
    validate_output = _prelude.get("validate_output")
    validation_issues = _prelude.get("validation_issues")
    validation_level = _prelude.get("validation_level")
    validation_orchestrator = _prelude.get("validation_orchestrator")
    validation_service = _prelude.get("validation_service")
    want_validate = _prelude.get("want_validate")
    warning = _prelude.get("warning")
    wire = _prelude.get("wire")
    xml = _prelude.get("xml")
    xml_payload = _prelude.get("xml_payload")
    if request_body is not None and request_body.metars:
        metars_list = request_body.metars
    try:
        pasted_heading = reports_for_convert(manual_text or "", product)
    except HeadingPasteError as exc:
        raise HTTPException(
            status_code=http_status_for_heading_error(exc.code),
            detail={"code": exc.code, "message": exc.message},
        ) from exc
    if pasted_heading is None:
        manual_with_offsets = api_surface.manual_entries_with_offsets(manual_text or "", product=product)
    else:
        manual_with_offsets = list(pasted_heading.reports)
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
        "strict": bool(strict),
        "strict_lint": bool(strict_lint),
        "strict_convert": bool(strict_convert),
        "strict_validate": bool(strict_validate),
        "raised_severities": list(raised_severities),
    }
    if response_report_variant:
        request_metadata["report_variant"] = response_report_variant
    if applied_conversion_template_id:
        request_metadata["conversion_template_id"] = applied_conversion_template_id
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
        """Internal helper ``_finalize_exchange_xml``."""
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
        semantic_canonical=str(wire.semantic_canonical),
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
        include_national_remarks=include_national_remarks,
        bulletin_date=bulletin_date,
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
    group_trace = (
        [GroupTrace.model_validate(row) for row in trace_entries(manual_with_offsets, product)] if preview else []
    )
    promoted_issues: list[ConversionIssue] = []
    for issue in acc.issues:
        promoted = promote_convert_failure_severity(
            str(issue.severity),
            layer=issue.layer,
            code=issue.code,
        )
        if promoted == str(issue.severity):
            promoted_issues.append(issue)
        else:
            promoted_issues.append(issue.model_copy(update={"severity": ConversionIssueSeverity(promoted)}))
    _record_convert_station_health(
        acc,
        product=product,
        lint_report=pre_convert_lint_report,
    )
    return api_surface.msgspec_json_response(
        ConversionResponse(
            results=acc.results,
            errors=acc.errors,
            issues=promoted_issues,
            total_processed=acc.total_inputs,
            successful=len(acc.results),
            failed=len(acc.errors),
            metadata=request_metadata,
            ok=envelope_ok,
            failed_spans=acc.preview_failed_spans if preview else [],
            group_trace=group_trace,
            raised_severities=list(raised_severities),
        )
    )
