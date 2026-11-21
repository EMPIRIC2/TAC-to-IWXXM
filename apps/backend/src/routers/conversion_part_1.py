"""Part 1 of ``conversion.py`` (line-cap split)."""

from __future__ import annotations

import logging
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, cast

from fastapi import APIRouter, HTTPException
from tac2iwxxm.profile_registry import supported_report_variants_for_profile
from tac2iwxxm.profile_resolve import resolve_validation_policies
from tac2iwxxm.profiles.ca_eccc import CA_IWXXM_VERSION
from tac_validate.api import lint_with_profile

from src.schemas.conversion import (
    ConversionIssue,
    ConversionIssueSeverity,
    ErrorDetail,
)
from src.schemas.validation import (
    AggregatedValidationResult,
    ValidationLayer,
)

from .conversion_api_surface import api_surface

tac_lint_fn = lint_with_profile

logger = logging.getLogger(__name__)


def _convert_output_policy_id(profile: str) -> str:
    """
    Internal helper ``_convert_output_policy_id``.

    Parameters
    ----------
    profile : object
        Argument ``profile``.

    Returns
    -------
    object
        Return value.
    """
    return resolve_validation_policies(profile or "annex3").iwxxm_output_policy_id


def _output_validation_orch_layers() -> list[ValidationLayer]:
    """
    Layers for post-convert IWXXM soft validation (exclude TAC input + XSD/SCH).

    AIRPORT_ICAO / TAC_SYNTAX are METAR/SPECI input checks (already gated before
    convert). XML_SCHEMA / SCHEMATRON run via ``_call_iwxxm_validate``.


    Returns
    -------
    object
        Return value.
    """
    skip = {
        ValidationLayer.AIRPORT_ICAO,
        ValidationLayer.TAC_SYNTAX,
        ValidationLayer.XML_SCHEMA,
        ValidationLayer.SCHEMATRON,
    }
    return [layer for layer in ValidationLayer if layer not in skip]


def _initial_layers_passed(product: str | None) -> list[str]:
    """
    Layers already satisfied before post-convert soft validation.


    Parameters
    ----------
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    if api_surface._product_uses_metar_tac_layers(product):
        return [ValidationLayer.AIRPORT_ICAO.value, ValidationLayer.TAC_SYNTAX.value]
    if api_surface._product_uses_aerodrome_icao_layer(product):
        return [ValidationLayer.AIRPORT_ICAO.value]
    return []


def _pre_convert_tac_layers(product: str | None) -> list[ValidationLayer] | None:
    """
    TAC input layers to run before convert for the given product.

    METAR/SPECI run airport ICAO + TAC syntax. TAF runs airport ICAO only
    (syntax differs from METAR Layer 2). Unknown ICAO soft-warns and does not
    block convert.

    Parameters
    ----------
    product : str | None
        Wire product id.

    Returns
    -------
    list[ValidationLayer] | None
        Layers to validate, or None when the product has no aerodrome gate.
    """
    if api_surface._product_uses_metar_tac_layers(product):
        return [ValidationLayer.AIRPORT_ICAO, ValidationLayer.TAC_SYNTAX]
    if api_surface._product_uses_aerodrome_icao_layer(product):
        return [ValidationLayer.AIRPORT_ICAO]
    return None


def _run_pre_convert_validation(
    validation_service: object, tac_text: str, layers: list[ValidationLayer]
) -> AggregatedValidationResult:
    """
    Run Layer 1-2 (or ICAO-only) validation, tolerating stubs without ``layers``.

    Parameters
    ----------
    validation_service : object
        Validation service or unit-test double.
    tac_text : str
        TAC input.
    layers : list[ValidationLayer]
        Layers to request when the service supports ``layers``.

    Returns
    -------
    AggregatedValidationResult
        Aggregated validation result.
    """
    validate = cast(
        Callable[..., AggregatedValidationResult],
        validation_service.validate_all_layers,  # type: ignore[attr-defined]
    )
    try:
        return validate(tac_text, layers=layers)
    except TypeError:
        # Unit-test doubles often accept only ``tac_text``.
        return validate(tac_text)


router = APIRouter(prefix="/api/v1", tags=["Conversion"])


def _form_text(value: object) -> str:
    """
    Internal helper ``_form_text``.

    Parameters
    ----------
    value : object
        Argument ``value``.

    Returns
    -------
    object
        Return value.
    """
    return value if isinstance(value, str) else ""


def _resolve_effective_iwxxm_version(
    requested_version: str,
    *,
    semantic_canonical: str | None,
    emit_profile: str,
) -> str:
    """
    Internal helper ``_resolve_effective_iwxxm_version``.

    Parameters
    ----------
    requested_version : object
        Argument ``requested_version``.
    semantic_canonical : object
        Argument ``semantic_canonical``.
    emit_profile : object
        Argument ``emit_profile``.

    Returns
    -------
    object
        Return value.
    """
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
    """
    Internal helper ``_wire_payload_dict``.

    Parameters
    ----------
    raw_obj : object
        Argument ``raw_obj``.

    Returns
    -------
    object
        Return value.
    """
    model_dump = getattr(raw_obj, "model_dump", None)
    if callable(model_dump):
        return cast(dict[str, Any], model_dump())
    if isinstance(raw_obj, dict):
        return cast(dict[str, Any], raw_obj)
    return {}


def _resolve_report_variant(emit_profile: str, product: str, requested_variant: str | None) -> str | None:
    """
    Internal helper ``_resolve_report_variant``.

    Parameters
    ----------
    emit_profile : object
        Argument ``emit_profile``.
    product : object
        Argument ``product``.
    requested_variant : object
        Argument ``requested_variant``.

    Returns
    -------
    object
        Return value.
    """
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
    """
    Internal helper ``_infer_report_variant_from_sample``.

    Parameters
    ----------
    emit_profile : object
        Argument ``emit_profile``.
    product : object
        Argument ``product``.
    sample_text : object
        Argument ``sample_text``.

    Returns
    -------
    object
        Return value.
    """
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
class _ConvertRuntime:
    """Internal helper ``_ConvertRuntime``."""

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
    include_national_remarks: bool
    bulletin_date: str
    validation_service: Any
    validation_orchestrator: Any
    finalize_exchange_xml: Callable[[str, str | None], str]
