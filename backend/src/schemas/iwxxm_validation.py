"""
IWXXM Validation Schemas and Constants

This module defines validation constants and schemas for IWXXM XML data,
including meteorological features, volcanic codes, and nil reasons.

Reference: WMO IWXXM code tables
- http://codes.wmo.int/iwxxm/MeteorologicalFeature
- http://codes.wmo.int/iwxxm/AviationColourCode
- http://codes.wmo.int/iwxxm/nil
"""

from enum import Enum
from typing import Set


class MeteorologicalFeature(str, Enum):
    """Valid IWXXM meteorological features."""
    AIRFRAME_ICING = "AIRFRAME_ICING"
    ATMOSPHERICS = "ATMOSPHERICS"
    CLOUD = "CLOUD"
    CLOUD_CLEAR = "CLOUD_CLEAR"
    COLD_FRONT_ABOVE_THE_SURFACE = "COLD_FRONT_ABOVE_THE_SURFACE"
    COLD_FRONT_AT_THE_SURFACE = "COLD_FRONT_AT_THE_SURFACE"
    CONVERGENCE_LINE = "CONVERGENCE_LINE"
    DUSTSTORM = "DUSTSTORM"
    INSTABILITY_LINE = "INSTABILITY_LINE"
    INTERTROPICAL_FRONT = "INTERTROPICAL_FRONT"
    JETSTREAM = "JETSTREAM"
    MOUNTAIN_WAVE = "MOUNTAIN_WAVE"
    OCCLUSION = "OCCLUSION"
    PHENOMENON = "PHENOMENON"
    QUASI_STATIONARY_FRONT_ABOVE_THE_SURFACE = "QUASI-STATIONARY_FRONT_ABOVE_THE_SURFACE"
    QUASI_STATIONARY_FRONT_AT_THE_SURFACE = "QUASI-STATIONARY_FRONT_AT_THE_SURFACE"
    RADIATION = "RADIATION"
    SANDSTORM = "SANDSTORM"
    SPECIAL_CLOUDS = "SPECIAL_CLOUDS"
    STORM = "STORM"


class VolcanicAviationColourCode(str, Enum):
    """Valid IWXXM volcanic aviation colour codes."""
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    RED = "RED"
    UNASSIGNED = "UNASSIGNED"


class NilReason(str, Enum):
    """Valid IWXXM nil reasons for missing data."""
    ABOVE_DETECTION_RANGE = "AboveDetectionRange"
    BELOW_DETECTION_RANGE = "BelowDetectionRange"
    INAPPLICABLE = "inapplicable"
    MISSING = "missing"
    NO_SIGNIFICANT_CHANGE = "noSignificantChange"
    NOT_DETECTED_BY_AUTO_SYSTEM = "notDetectedByAutoSystem"
    NOTHING_OF_OPERATIONAL_SIGNIFICANCE = "nothingOfOperationalSignificance"
    NOT_OBSERVABLE = "notObservable"
    TEMPLATE = "template"
    UNKNOWN = "unknown"
    WITHHELD = "withheld"


class IWXXMVersion(str, Enum):
    """Supported IWXXM versions."""
    VERSION_2016 = "2016-1"
    VERSION_2018 = "2018-2"
    VERSION_3_0 = "3.0"  # Used in some Amd78-2018 test data
    VERSION_2021_2 = "2021-2"
    VERSION_2023_1 = "2023-1"
    VERSION_2025_2 = "2025-2"


# Set for quick lookups
VALID_METEOROLOGICAL_FEATURES: Set[str] = {
    f.value for f in MeteorologicalFeature
}

VALID_VOLCANIC_CODES: Set[str] = {
    c.value for c in VolcanicAviationColourCode
}

VALID_NIL_REASONS: Set[str] = {
    r.value for r in NilReason
}

SUPPORTED_IWXXM_VERSIONS: Set[str] = {
    v.value for v in IWXXMVersion
}


def is_valid_meteorological_feature(feature: str) -> bool:
    """Check if a meteorological feature code is valid."""
    return feature in VALID_METEOROLOGICAL_FEATURES


def is_valid_volcanic_code(code: str) -> bool:
    """Check if a volcanic aviation colour code is valid."""
    return code in VALID_VOLCANIC_CODES


def is_valid_nil_reason(reason: str) -> bool:
    """Check if a nil reason is valid."""
    return reason in VALID_NIL_REASONS


def is_supported_iwxxm_version(version: str) -> bool:
    """Check if an IWXXM version is supported."""
    return version in SUPPORTED_IWXXM_VERSIONS


def extract_iwxxm_namespace_version(namespace_uri: str) -> str:
    """
    Extract IWXXM version from namespace URI.
    
    Example:
        "http://icao.int/iwxxm/2023-1" → "2023-1"
        "http://icao.int/iwxxm/2025-2" → "2025-2"
    
    Args:
        namespace_uri: The IWXXM namespace URI
        
    Returns:
        Version string (e.g., "2023-1")
        
    Raises:
        ValueError: If namespace doesn't match expected format
    """
    if not namespace_uri.startswith("http://icao.int/iwxxm/"):
        raise ValueError(f"Invalid IWXXM namespace: {namespace_uri}")
    
    version = namespace_uri.replace("http://icao.int/iwxxm/", "")
    if not is_supported_iwxxm_version(version):
        raise ValueError(f"Unsupported IWXXM version: {version}")
    
    return version


def get_namespace_version(xml_string: str) -> str:
    """
    Extract IWXXM version from XML string namespace declaration.
    
    Args:
        xml_string: XML content containing IWXXM namespace
        
    Returns:
        Version string (e.g., "2023-1" or "3.0")
        
    Raises:
        ValueError: If IWXXM namespace not found or unsupported
    """
    import re
    # Extract namespace from first few lines - supports both YYYY-X and X.X formats
    match = re.search(r'xmlns:iwxxm="http://icao\.int/iwxxm/([0-9]+(?:\.[0-9]|-[0-9])?)"', xml_string[:500])
    if not match:
        raise ValueError("IWXXM namespace not found in XML")
    
    version = match.group(1)
    if not is_supported_iwxxm_version(version):
        raise ValueError(f"Unsupported IWXXM version: {version}")
    
    return version
