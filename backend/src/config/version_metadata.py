"""
IWXXM Version Metadata Configuration

Centralizes version-specific configuration including namespaces, element ordering,
translation metadata requirements, and formatting rules for IWXXM versions 2016-2025-2.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class VersionMetadata:
    """Metadata for a specific IWXXM version."""
    
    version: str
    namespace: str
    schema_query_binding: str  # "xslt1" or "xslt2"
    has_runway_state: bool  # Removed in 2025-2
    has_measures: bool  # Special measures schema
    translation_metadata_optional: bool  # Can be omitted
    coordinate_precision_decimals: int  # Format precision for gml:pos
    elevation_rounding: Optional[int]  # None = no rounding, 0/1 = round to that precision
    element_order_priority: List[str] = field(default_factory=list)  # Element ordering for aerodrome
    
    def __repr__(self) -> str:
        return f"VersionMetadata(version={self.version}, ns={self.namespace.split('/')[-1]})"


# Version metadata registry - single source of truth for all versions
VERSION_METADATA: Dict[str, VersionMetadata] = {
    "2016": VersionMetadata(
        version="2016",
        namespace="http://icao.int/iwxxm/2.1",
        schema_query_binding="xslt1",
        has_runway_state=True,
        has_measures=False,
        translation_metadata_optional=True,
        coordinate_precision_decimals=2,
        elevation_rounding=1,
        element_order_priority=[
            "interpretation", "designator", "name", "locationIndicatorICAO", "ARP"
        ]
    ),
    
    "2018": VersionMetadata(
        version="2018",
        namespace="http://icao.int/iwxxm/3.0",
        schema_query_binding="xslt1",
        has_runway_state=True,
        has_measures=False,
        translation_metadata_optional=True,
        coordinate_precision_decimals=2,
        elevation_rounding=1,
        element_order_priority=[
            "interpretation", "designator", "name", "locationIndicatorICAO", "ARP"
        ]
    ),
    
    "2021-2": VersionMetadata(
        version="2021-2",
        namespace="http://icao.int/iwxxm/2021-2",
        schema_query_binding="xslt1",
        has_runway_state=True,
        has_measures=True,
        translation_metadata_optional=True,
        coordinate_precision_decimals=6,
        elevation_rounding=0,
        element_order_priority=[
            "interpretation", "name", "locationIndicatorICAO", "ARP"
        ]
    ),
    
    "2023-1": VersionMetadata(
        version="2023-1",
        namespace="http://icao.int/iwxxm/2023-1",
        schema_query_binding="xslt1",
        has_runway_state=True,
        has_measures=True,
        translation_metadata_optional=True,
        coordinate_precision_decimals=6,
        elevation_rounding=0,
        element_order_priority=[
            "interpretation", "name", "locationIndicatorICAO", "ARP"
        ]
    ),
    
    "2025-2": VersionMetadata(
        version="2025-2",
        namespace="http://icao.int/iwxxm/2025-2",
        schema_query_binding="xslt2",  # Requires Saxon (currently unsupported)
        has_runway_state=False,  # Removed in 2025-2
        has_measures=False,  # Consolidated into main schema
        translation_metadata_optional=True,
        coordinate_precision_decimals=8,  # High precision (ICAO Annex 3)
        elevation_rounding=0,
        element_order_priority=[
            "interpretation", "name", "locationIndicatorICAO", "designatorIATA", "ARP"
        ]
    ),
}


def get_version_metadata(version: str) -> Optional[VersionMetadata]:
    """Get metadata for a specific IWXXM version.
    
    Args:
        version: Version string (e.g., "2025-2")
    
    Returns:
        VersionMetadata if version exists, None otherwise
    """
    return VERSION_METADATA.get(version)


def normalize_version(version_str: str) -> str:
    """Normalize version string to canonical form.
    
    Handles aliases:
    - "2025" or "2025-1" → "2025-2"
    - "3.0" → "2018"
    - "2.1" → "2016"
    
    Args:
        version_str: Input version string
    
    Returns:
        Canonical version string
    """
    normalized = version_str.strip()
    
    # Handle namespace-style versions
    if normalized.endswith(".1"):
        # "2.1" → "2016"
        return "2016"
    elif normalized.endswith(".0") and normalized.startswith("3"):
        # "3.0" → "2018"
        return "2018"
    
    # Handle "2025" or "2025-1" → "2025-2"
    if normalized in ("2025", "2025-1"):
        return "2025-2"
    
    # Return as-is if already canonical
    if normalized in VERSION_METADATA:
        return normalized
    
    return normalized


def get_supported_versions() -> List[str]:
    """Get list of supported IWXXM versions."""
    return list(VERSION_METADATA.keys())
