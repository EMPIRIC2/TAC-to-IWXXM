"""
Version-Aware XML Comparison Utilities

Provides functions for comparing IWXXM XML across different schema versions.
Handles namespace differences and version-specific validation.
"""

import pathlib
import re
import sys
from typing import Optional
from xml.etree import ElementTree as ET

# Add src to path for imports
ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from schemas.iwxxm_validation import get_namespace_version, is_supported_iwxxm_version


def normalize_namespace_for_comparison(xml_string: str, target_version: str) -> str:
    """
    Normalize XML namespace to a specific version for comparison.

    Replaces namespace URIs while preserving document structure.
    Only use for comparison purposes, not for production XML.

    Args:
        xml_string: Original XML content
        target_version: Target version (e.g., "2025-2")

    Returns:
        XML with normalized namespace

    Raises:
        ValueError: If target_version is not supported
    """
    if not is_supported_iwxxm_version(target_version):
        raise ValueError(f"Unsupported target version: {target_version}")

    # Replace iwxxm namespace in schemaLocation
    normalized = re.sub(r"http://icao\.int/iwxxm/[0-9]{4}-[0-9]", f"http://icao.int/iwxxm/{target_version}", xml_string)

    # Replace schema URLs to match version
    normalized = re.sub(
        r"https://schemas\.wmo\.int/iwxxm/[0-9]{4}-[0-9][^/]*/iwxxm\.xsd",
        f"https://schemas.wmo.int/iwxxm/{target_version}/iwxxm.xsd",
        normalized,
    )

    return normalized


def compare_xml_ignoring_namespace_version(
    xml1: str, xml2: str, strip_dynamic_attrs: bool = True
) -> tuple[bool, str | None]:
    """
    Compare two IWXXM XML documents, ignoring namespace version differences.

    Useful for comparing expected XML (2023-1) with produced XML (2025-2)
    when only structural comparison is needed.

    Args:
        xml1: First XML document
        xml2: Second XML document
        strip_dynamic_attrs: Whether to remove dynamic attributes (UUIDs, timestamps)

    Returns: tuple of (is_equal, error_message)
        - is_equal: True if documents are structurally equivalent
        - error_message: Description of first difference found, or None if equal
    """
    try:
        # Get versions
        version1 = get_namespace_version(xml1)
        version2 = get_namespace_version(xml2)

        # Normalize both to common version for comparison
        target = version1  # Use first version as target
        normalized1 = normalize_namespace_for_comparison(xml1, target)
        normalized2 = normalize_namespace_for_comparison(xml2, target)

        # Parse normalized documents
        root1 = ET.fromstring(normalized1)
        root2 = ET.fromstring(normalized2)

        # Compare structure
        is_equal = _compare_elements(root1, root2)
        if not is_equal:
            return False, f"XML structure differs (version {version1} vs {version2})"

        return True, None

    except Exception as e:
        return False, f"Comparison error: {e!s}"


def get_version_compatibility(version1: str, version2: str) -> str:
    """
    Describe compatibility between two IWXXM versions.

    Args:
        version1: First version
        version2: Second version

    Returns:
        Compatibility description
    """
    if version1 == version2:
        return "exact_match"

    if version1 == "2023-1" and version2 == "2025-2":
        return "2023-1_to_2025-2_upgrade"

    if version1 == "2025-2" and version2 == "2023-1":
        return "2025-2_to_2023-1_downgrade"

    return "incompatible"


def _compare_elements(elem1: ET.Element, elem2: ET.Element) -> bool:
    """Recursively compare two XML elements, ignoring namespace versions."""
    # Extract tag without namespace for comparison
    tag1 = _extract_tag_name(elem1.tag)
    tag2 = _extract_tag_name(elem2.tag)

    if tag1 != tag2:
        return False

    if elem1.text and elem2.text and elem1.text.strip() != elem2.text.strip():
        return False

    if elem1.tail and elem2.tail and elem1.tail.strip() != elem2.tail.strip():
        return False

    # Compare non-dynamic attributes
    attrs1 = {k: v for k, v in elem1.attrib.items() if not _is_dynamic_attr(k, v)}
    attrs2 = {k: v for k, v in elem2.attrib.items() if not _is_dynamic_attr(k, v)}

    # Normalize attribute keys/values to ignore namespace versions
    attrs1 = _normalize_attributes(attrs1)
    attrs2 = _normalize_attributes(attrs2)

    if attrs1 != attrs2:
        return False

    if len(elem1) != len(elem2):
        return False

    return all(_compare_elements(c1, c2) for c1, c2 in zip(elem1, elem2, strict=False))


def _extract_tag_name(tag: str) -> str:
    """Extract tag name without namespace."""
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _normalize_attributes(attrs: dict) -> dict:
    """Normalize attributes to ignore namespace versions."""
    normalized = {}
    for key, value in attrs.items():
        # Normalize key (remove namespace version differences)
        norm_key = _normalize_attribute_key(key)
        # Normalize value (remove namespace version differences)
        norm_value = _normalize_attribute_value(value)
        normalized[norm_key] = norm_value
    return normalized


def _normalize_attribute_key(key: str) -> str:
    """Normalize attribute key to remove namespace version info."""
    # Remove namespace version from schemaLocation attributes
    if "}schemaLocation" in key:
        return "schemaLocation"
    # Remove namespace prefix for other attributes
    if "}" in key:
        return key.split("}", 1)[1]
    return key


def _normalize_attribute_value(value: str) -> str:
    """Normalize attribute value to remove namespace version info."""
    # Normalize IWXXM namespace versions in schemaLocation
    normalized = re.sub(r"http://icao\.int/iwxxm/[0-9]{4}-[0-9]", "http://icao.int/iwxxm/VERSION", value)
    # Normalize schema URLs
    normalized = re.sub(
        r"https://schemas\.wmo\.int/iwxxm/[0-9]{4}-[0-9][^/]*/iwxxm\.xsd",
        "https://schemas.wmo.int/iwxxm/VERSION/iwxxm.xsd",
        normalized,
    )
    return normalized


def _is_dynamic_attr(name: str, value: str) -> bool:
    """Check if attribute is dynamic (UUID, timestamp, etc)."""
    if name == "gml:id":
        return True
    if "uuid" in value.lower():
        return True
    return bool(re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", value))
