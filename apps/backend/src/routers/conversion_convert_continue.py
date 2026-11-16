"""Continuation of ``convert`` (line-cap)."""

from __future__ import annotations

import logging
import warnings
from typing import Any

from fastapi import HTTPException

from src.metar_iwxxm_api.convert_library_hard_cut import (
    resolve_engine_profile_from_conversion_library,
)
from src.models.iwxxm_validation import get_namespace_version
from src.schemas.conversion import (
    ConversionIssue,
    ConversionIssueSeverity,
    ConversionResponse,
    ConversionResult,
    ErrorDetail,
)
from src.utilities.extension_wire import IWXXM_CA_TOKEN
from src.utilities.iwxxm_pass_through import NOT_XML_CODE, lint_iwxxm_pass_through
from src.utilities.observability import set_request_log_level
from src.utilities.strict_raise import apply_strict_validate_flags, compute_raised_severities
from src.utilities.version_migration import migrate_xml

from .conversion_api_surface import api_surface
from .conversion_part_1 import (
    _convert_output_policy_id,
    _resolve_effective_iwxxm_version,
    _resolve_report_variant,
    tac_lint_fn,
)
from .conversion_part_2 import _ConvertAccumulator

logger = logging.getLogger(__name__)
warning = warnings.warn


async def convert_continue(_prelude: dict[str, Any]) -> Any:
    """Resume ``convert`` after prelude."""
    conversion_library_id = _prelude.get("conversion_library_id")
    _custom_engine = _prelude.get("_custom_engine")
    conversion_template_id = _prelude.get("conversion_template_id")
    report_variant = _prelude.get("report_variant")
    lint = _prelude.get("lint")
    applied_conversion_library_id = _prelude.get("applied_conversion_library_id")
    bulletin_id = _prelude.get("bulletin_id")
    ca_eccc_bundle_available = _prelude.get("ca_eccc_bundle_available")
    conversion_template_token = _prelude.get("conversion_template_token")
    emit_profile = _prelude.get("emit_profile")
    err = _prelude.get("err")
    exc = _prelude.get("exc")
    extensions = _prelude.get("extensions")
    files = _prelude.get("files")
    get_first_party_template = _prelude.get("get_first_party_template")
    i = _prelude.get("i")
    include_nil_reasons = _prelude.get("include_nil_reasons")
    is_first_party = _prelude.get("is_first_party")
    issue = _prelude.get("issue")
    issues = _prelude.get("issues")
    issuing_center = _prelude.get("issuing_center")
    iwxxm_lint = _prelude.get("iwxxm_lint")
    iwxxm_version = _prelude.get("iwxxm_version")
    joined = _prelude.get("joined")
    json_extensions = _prelude.get("json_extensions")
    log_level = _prelude.get("log_level")
    log_level_norm = _prelude.get("log_level_norm")
    manual_text = _prelude.get("manual_text")
    migrated_iwxxm = _prelude.get("migrated_iwxxm")
    migrated_payload = _prelude.get("migrated_payload")
    migration_warnings = _prelude.get("migration_warnings")
    pass_issues = _prelude.get("pass_issues")
    preview = _prelude.get("preview")
    product = _prelude.get("product")
    profile = _prelude.get("profile")
    profiles_service = _prelude.get("profiles_service")
    report = _prelude.get("report")
    request = _prelude.get("request")
    request_body = _prelude.get("request_body")
    resolved_extensions = _prelude.get("resolved_extensions")
    sample = _prelude.get("sample")
    semantic_profile = _prelude.get("semantic_profile")
    source_iwxxm_version = _prelude.get("source_iwxxm_version")
    stop_on_error = _prelude.get("stop_on_error")
    strict = _prelude.get("strict")
    strict_convert = _prelude.get("strict_convert")
    strict_lint = _prelude.get("strict_lint")
    strict_validate = _prelude.get("strict_validate")
    tmpl = _prelude.get("tmpl")
    validate_output = _prelude.get("validate_output")
    validation_issues = _prelude.get("validation_issues")
    validation_level = _prelude.get("validation_level")
    want_validate = _prelude.get("want_validate")
    wire = _prelude.get("wire")
    xml_payload = _prelude.get("xml_payload")
    try:
        applied_conversion_library_id, semantic_profile = resolve_engine_profile_from_conversion_library(
            conversion_library_id,
            get_custom_engine_profile_id=_custom_engine,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    profile = ""
    _ = applied_conversion_library_id
    applied_conversion_template_id: str | None = None
    conversion_template_token = (conversion_template_id or "").strip()
    if conversion_template_token:
        is_first_party = False
        try:
            from tac2iwxxm.conversion_templates import get_first_party_template

            is_first_party = get_first_party_template(conversion_template_token) is not None
        except ImportError:
            is_first_party = False
        if is_first_party:
            applied_conversion_template_id = conversion_template_token
        else:
            if profiles_service is None:
                raise HTTPException(
                    status_code=401,
                    detail="Sign in required to apply a custom conversion template",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            tmpl = profiles_service.get_conversion_template(conversion_template_token)
            applied_conversion_template_id = str(tmpl.id)
    wire = api_surface._resolve_request_profiles(
        route="/api/v1/convert",
        profile="",
        semantic_profile=semantic_profile,
        exchange_profile="",
        json_profile=None,
        json_semantic_profile=None,
        json_exchange_profile=None,
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
            try:
                migrated_payload, migration_warnings = migrate_xml(
                    xml_payload,
                    from_version=source_iwxxm_version,
                    to_version=iwxxm_version,
                    emit_profile=emit_profile,
                )
            except ValueError as exc:
                raise HTTPException(
                    status_code=400,
                    detail=ErrorDetail(
                        message="Unsupported IWXXM version migration",
                        errors=[str(exc)],
                        issues=[
                            ConversionIssue(
                                source="manual",
                                message=str(exc),
                                severity=ConversionIssueSeverity.ERROR,
                                code="UNSUPPORTED_IWXXM_MIGRATION",
                            )
                        ],
                        total_errors=1,
                    ).model_dump(),
                ) from exc
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
                    output_policy_id=_convert_output_policy_id(profile or "annex3"),
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
    pre_convert_lint_report = None
    if lint:
        sample = manual_text.strip() if manual_text else ""
        if request_body is not None and getattr(request_body, "metars", None):
            sample = (request_body.metars[0] or "").strip() if request_body.metars else sample
        if sample:
            pre_convert_lint_report = tac_lint_fn(
                sample,
                product=product,
                profile=profile,
            )
    validation_level = api_surface.normalize_validation_level(validation_level)
    validate_output, validation_level = apply_strict_validate_flags(
        strict=bool(strict),
        strict_validate=bool(strict_validate),
        preview=bool(preview),
        validate_output=bool(validate_output),
        validation_level=validation_level,
    )
    validate_output = bool(validate_output) or validation_level in [
        "comprehensive",
        "schematron",
        "icao_opmet",
        "schema",
    ]
    raised_severities = compute_raised_severities(
        strict=bool(strict),
        strict_lint=bool(strict_lint),
        strict_convert=bool(strict_convert),
        strict_validate=bool(strict_validate),
    )
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
            "nilReason on NIL reports until engine honors the flag (placeholder)",
        )
    acc = _ConvertAccumulator()
    validation_service = api_surface.ValidationService()
    validation_orchestrator = api_surface.get_validation_orchestrator() if validate_output else None
    metars_list: list[Any] = []
    from .conversion_convert_continue_part2 import convert_continue_part2

    # Keep keys from the routes_io prelude that this stage never bound locally
    # (e.g. propagate_residuals_to_remarks and other Form/JSON fields).
    return await convert_continue_part2({**_prelude, **globals(), **locals()})
