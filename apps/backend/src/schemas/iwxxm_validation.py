"""HTTP schema adapters for iwxxm_validation (re-export from ``src.models``)."""

from src.models.iwxxm_validation import (
    SUPPORTED_IWXXM_VERSIONS,
    VALID_METEOROLOGICAL_FEATURES,
    VALID_NIL_REASONS,
    VALID_VOLCANIC_CODES,
    IWXXMVersion,
    MeteorologicalFeature,
    NilReason,
    VolcanicAviationColourCode,
    extract_iwxxm_namespace_version,
    get_namespace_version,
    is_supported_iwxxm_version,
    is_valid_meteorological_feature,
    is_valid_nil_reason,
    is_valid_volcanic_code,
)

__all__ = [
    "SUPPORTED_IWXXM_VERSIONS",
    "VALID_METEOROLOGICAL_FEATURES",
    "VALID_NIL_REASONS",
    "VALID_VOLCANIC_CODES",
    "IWXXMVersion",
    "MeteorologicalFeature",
    "NilReason",
    "VolcanicAviationColourCode",
    "extract_iwxxm_namespace_version",
    "get_namespace_version",
    "is_supported_iwxxm_version",
    "is_valid_meteorological_feature",
    "is_valid_nil_reason",
    "is_valid_volcanic_code",
]
