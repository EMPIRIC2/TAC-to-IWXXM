"""METAR TAC → IWXXM conversion utilities (tac2iwxxm cutover — ADR-014 / T4.7)."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:
    from ..services.validation_orchestrator import ComprehensiveValidationResult

try:
    from .tac_parser import extract_airport_code
except (ImportError, ModuleNotFoundError):  # pragma: no cover - flat layout fallback
    from utilities.tac_parser import extract_airport_code  # type: ignore

logger = logging.getLogger(__name__)
try:
    from ..schemas.validation import ValidationLayer
except ImportError:  # pragma: no cover - flat layout fallback
    from schemas.validation import ValidationLayer


def _load_service_validation_error() -> type[Exception]:
    try:
        from ..services.validation import ValidationError

        return ValidationError
    except (ImportError, ModuleNotFoundError):  # pragma: no cover - flat layout fallback
        try:  # pragma: no cover
            from services.validation import ValidationError

            return ValidationError
        except (ImportError, ModuleNotFoundError):  # pragma: no cover

            class _FallbackValidationError(Exception):
                """Fallback validation error."""

                pass

            return _FallbackValidationError


ServiceValidationError = _load_service_validation_error()


class ConversionError(Exception):
    """Raised when METAR to IWXXM conversion fails."""

    pass


def _extract_icao_from_tac(tac_text: str) -> Optional[str]:
    """Extract ICAO code from METAR/SPECI TAC text."""
    icao = extract_airport_code(tac_text)
    if icao:
        return icao
    match = re.search(r"\b([A-Z][A-Z0-9]{3})\b", tac_text.upper())
    if match:
        return match.group(1)
    return None


def _detect_product(tac_text: str, default: str = "METAR") -> str:
    """Detect METAR vs SPECI from TAC text."""
    match = re.search(r"\b(METAR|SPECI)\b", tac_text.upper())
    if match:
        return match.group(1)
    return default.upper()


try:
    from .metar_normalizer import (  # noqa: E402
        normalize_recent_weather_for_tac,
        normalize_recent_weather_tokens,
    )
except ImportError:  # pragma: no cover - flat layout fallback
    from metar_normalizer import (  # type: ignore  # noqa: E402
        normalize_recent_weather_for_tac,
        normalize_recent_weather_tokens,
    )

__all__ = [
    "convert_metar_tac",
    "ConversionError",
    "convert_metar_tac_with_metadata",
    "normalize_recent_weather_tokens",
]


def convert_metar_tac(tac_text: str, iwxxm_version: Optional[str] = None) -> str:
    """
    Convert METAR/SPECI TAC text to IWXXM XML.

    Deprecated: prefer ``convert_metar_tac_with_metadata``.
    """
    import warnings

    warnings.warn(
        "convert_metar_tac() is deprecated, use convert_metar_tac_with_metadata() instead",
        DeprecationWarning,
        stacklevel=2,
    )
    xml, _ = convert_metar_tac_with_metadata(
        tac_text,
        iwxxm_version=iwxxm_version,
        validate=False,
    )
    return xml


def _apply_recent_weather_normalization(
    tac_text: str,
    *,
    lenient: bool,
) -> str:
    """Optionally normalize recent-weather tokens and log rewrites."""
    if not lenient:
        return tac_text

    normalized_tac, norm_warnings = normalize_recent_weather_for_tac(tac_text)
    for warning in norm_warnings:
        logger.info(
            "METAR recent-weather pre-normalization: '%s' at token index %d rewritten to '%s' (rule: %s)",
            warning["original"],
            warning["index"],
            warning["replacement"],
            warning["rule"],
        )

    return normalized_tac


def convert_metar_tac_with_metadata(
    tac_text: str,
    iwxxm_version: Optional[str] = None,
    reference_time: Optional[str] = None,
    use_test_overrides: bool = False,
    validate: bool = True,
    validation_layers: Optional[List[str]] = None,
    raise_on_validation_error: bool = False,
    lenient: bool = True,
    product: Optional[str] = None,
    profile: str = "annex3",
    preview: bool = False,
    soft_preview_out: Optional[dict] = None,
) -> Tuple[str, Optional[ComprehensiveValidationResult]]:
    """
    Convert TAC to IWXXM via ``tac2iwxxm`` and optionally validate.

    Parameters
    ----------
    tac_text :
        METAR or SPECI TAC.
    iwxxm_version :
        Target IWXXM release line (default ``2025-2``).
    reference_time :
        Reserved (historical date patching was gifts-specific); ignored.
    use_test_overrides :
        Reserved; ignored after gifts cutover.
    validate :
        Run validation orchestrator after conversion.
    validation_layers :
        Layer names for the orchestrator.
    raise_on_validation_error :
        Raise ``ConversionError`` when validation fails.
    lenient :
        Pre-normalize truncated recent-weather tokens before convert.
    product :
        ``METAR`` or ``SPECI``; auto-detected when omitted.
    profile :
        ``annex3`` or ``iwxxm_us``.
    preview :
        Soft-preview mode (ADR-022): return best-effort XML instead of raising on
        parse/convert failure.
    soft_preview_out :
        Optional mutable dict filled when ``preview=True`` with ``ok`` and
        ``failed_spans`` for the API response envelope.

    Returns
    -------
    tuple
        ``(xml_string, validation_result)``; validation_result is None when validate=False.

    Raises
    ------
    ConversionError
        When conversion (or requested validation) fails and ``preview`` is False.
    """
    _ = (reference_time, use_test_overrides)  # gifts-era knobs; no-op after cutover

    try:
        from tac2iwxxm import convert as tac2iwxxm_convert
    except ImportError as exc:
        raise ConversionError(f"tac2iwxxm unavailable: {exc}") from exc

    version = iwxxm_version or "2025-2"
    product_u = (product or _detect_product(tac_text)).upper()
    profile_l = (profile or "annex3").lower()

    tac_text = _apply_recent_weather_normalization(tac_text, lenient=lenient)

    result = tac2iwxxm_convert(
        tac_text,
        product=product_u,
        profile=profile_l,
        iwxxm_version=version,
        preview=preview,
    )
    if not result.ok or not result.xml:
        msgs = "; ".join(f"{i.code}: {i.message}" for i in result.issues) or "unknown convert failure"
        if preview and result.xml:
            failed_spans = [
                {
                    "start": int(i.start),
                    "end": int(i.end),
                    "code": i.code,
                    "message": i.message,
                }
                for i in result.issues
                if i.start is not None and i.end is not None
            ]
            if soft_preview_out is not None:
                soft_preview_out.clear()
                soft_preview_out["ok"] = False
                soft_preview_out["failed_spans"] = failed_spans
            xml_string = result.xml
            if not xml_string.lstrip().startswith("<?xml"):
                xml_string = '<?xml version="1.0"?>\n' + xml_string
            return xml_string, None
        raise ConversionError(f"Conversion failed: {msgs}")

    if soft_preview_out is not None and preview:
        soft_preview_out.clear()
        soft_preview_out["ok"] = True
        soft_preview_out["failed_spans"] = []

    xml_string = result.xml
    if not xml_string.lstrip().startswith("<?xml"):
        xml_string = '<?xml version="1.0"?>\n' + xml_string

    validation_result = None
    if validate:
        try:
            try:
                from ..services.validation_orchestrator import get_validation_orchestrator
            except (ImportError, ValueError):  # pragma: no cover - flat layout fallback
                from services.validation_orchestrator import get_validation_orchestrator

            orchestrator = get_validation_orchestrator()

            if validation_layers is None:
                validation_layers = [
                    "XML_WELLFORMED",
                    "XML_SCHEMA",
                    "SCHEMATRON",
                    "WMO_CODELISTS",
                ]

            layer_values = validation_layers or []
            mapped_layers: List[ValidationLayer] | None = None
            if layer_values:
                mapped_layers = []
                for layer_name in layer_values:
                    if isinstance(layer_name, ValidationLayer):
                        mapped_layers.append(layer_name)
                    else:
                        mapped_layers.append(ValidationLayer(str(layer_name).lower()))

            validation_result = orchestrator.validate_complete(
                tac_text=tac_text,
                xml_content=xml_string,
                version=version,
                layers=mapped_layers,
                stop_on_error=raise_on_validation_error,
            )

            if validation_result.is_valid:
                logger.info(
                    "Validation passed: %s layers, %s total issues",
                    len(validation_result.layers_passed),
                    len(validation_result.all_issues),
                )
            else:
                logger.warning(
                    "Validation failed: %s failed layers",
                    len(validation_result.layers_failed),
                )

            if raise_on_validation_error and not validation_result.is_valid:
                error_msgs = [
                    f"{i.code}: {i.message}"
                    for i in validation_result.all_issues
                    if i.level.value in ["ERROR", "CRITICAL"]
                ]
                raise ConversionError(
                    f"Validation failed with {len(error_msgs)} error(s):\n" + "\n".join(error_msgs[:5])
                )

        except ConversionError:
            raise
        except Exception as e:
            if raise_on_validation_error:
                raise ConversionError(f"Validation error: {e}") from e
            logger.error("Validation failed but continuing: %s", e)
            validation_result = None

    return xml_string, validation_result
