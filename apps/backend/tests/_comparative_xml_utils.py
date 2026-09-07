"""Enhanced XML comparison utilities for METAR→IWXXM conversion testing.

Provides:
- Lat/lon distance validation (within 100m tolerance)
- Deep XML diff reporting (field-level differences)
- Tolerance matching for numeric values
- JSON diff report generation for failure analysis
- XML normalization for minified/prettified XML handling
"""

import json
import logging
import math
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
from xml.dom import minidom

from _xml_utils import _local, _norm_text

logger = logging.getLogger(__name__)


def normalize_xml_string(xml_content: str) -> str:
    """Normalize XML string by prettifying to handle minified/formatted equivalently.

    Args:
        xml_content: XML string (minified or prettified)

    Returns:
        Normalized (prettified) XML string
    """
    try:
        # Parse with minidom
        doc = minidom.parseString(xml_content)
        # Prettify to normalize whitespace
        normalized = doc.toprettyxml(indent="  ")
        # Remove XML declaration if present (re-add at start if needed)
        if normalized.startswith("<?xml"):
            lines = normalized.split("\n")
            normalized = "\n".join(lines[1:])
        return normalized.strip()
    except Exception as e:
        logger.warning(f"Failed to normalize XML: {e}, returning original")
        return xml_content


def filter_whitespace_text_nodes(elem: ET.Element) -> None:
    """Remove whitespace-only text nodes from an element tree (in-place).

    Args:
        elem: Root element to process
    """
    # Remove text/tail that is only whitespace
    if elem.text and not elem.text.strip():
        elem.text = None
    if elem.tail and not elem.tail.strip():
        elem.tail = None

    # Recurse to children
    for child in elem:
        filter_whitespace_text_nodes(child)


def parse_xml_normalized(xml_content: str) -> ET.Element:
    """Parse XML content, normalizing first to handle minified/prettified equivalently.

    Args:
        xml_content: Raw XML string

    Returns:
        Parsed ElementTree Element with whitespace-only nodes filtered
    """
    # Normalize first
    normalized = normalize_xml_string(xml_content)
    # Parse normalized XML
    root = ET.fromstring(normalized.encode("utf-8"))
    # Filter whitespace text nodes
    filter_whitespace_text_nodes(root)
    return root


@dataclass
class DiffReport:
    """Structured difference report between expected and actual XML."""

    test_case: str  # e.g., "BGBW-282350Z"
    amendment_version: str  # e.g., "Amd79-80-2023"
    status: str = "UNKNOWN"  # "PASS" or "FAIL"
    field_diffs: list[dict] = None  # [{path, expected, actual, reason}, ...]
    lat_lon_diffs: list[dict] = None  # [{element_id, distance_meters}, ...]
    metadata_diffs: list[dict] = None  # [{attr, expected, actual}, ...]
    expected_xml: str | None = None  # Full expected XML for comparison
    actual_xml: str | None = None  # Full actual XML for comparison
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        if self.field_diffs is None:
            self.field_diffs = []
        if self.lat_lon_diffs is None:
            self.lat_lon_diffs = []
        if self.metadata_diffs is None:
            self.metadata_diffs = []

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def save(self, report_dir: Path) -> Path:
        """Save report to JSON file."""
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"{self.test_case}_{self.amendment_version}.json"
        with open(report_path, "w") as f:
            f.write(self.to_json())
        return report_path


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in meters between two lat/lon points using Haversine formula.

    Args:
        lat1, lon1: First point latitude/longitude in decimal degrees
        lat2, lon2: Second point latitude/longitude in decimal degrees

    Returns:
        Distance in meters
    """
    R = 6371000  # Earth's radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def extract_lat_lon(elem: ET.Element, tolerance_m: float = 100.0) -> dict[str, tuple[float, float]]:
    """Extract all lat/lon value pairs from XML element.

    Returns dict: {element_id_or_path: (lat, lon), ...}
    Handles various IWXXM coordinate formats.
    """
    coords = {}

    # Search for position/location elements that might contain coordinates
    for elem_iter in elem.iter():
        tag = _local(elem_iter.tag)

        # IWXXM common coordinate element patterns
        if tag in ("AirportPosition", "Location", "Position", "pos", "posList"):
            attrs_iter = elem_iter.attrib
            elem_id = attrs_iter.get("gml:id") or attrs_iter.get("id", "unknown")

            # Single pos: "lat lon" format
            if tag in ("pos", "Position"):
                text = _norm_text(elem_iter.text)
                if text:
                    try:
                        parts = text.split()
                        if len(parts) >= 2:
                            lat, lon = float(parts[0]), float(parts[1])
                            coords[elem_id] = (lat, lon)
                    except (ValueError, IndexError):
                        pass

            # Multiple positions in posList: "lat lon lat lon ..." format
            elif tag == "posList":
                text = _norm_text(elem_iter.text)
                if text:
                    try:
                        parts = text.split()
                        for i in range(0, len(parts) - 1, 2):
                            lat, lon = float(parts[i]), float(parts[i + 1])
                            coords[f"{elem_id}[{i // 2}]"] = (lat, lon)
                    except (ValueError, IndexError):
                        pass

    return coords


def validate_lat_lon_tolerance(
    expected_coords: dict[str, tuple[float, float]],
    actual_coords: dict[str, tuple[float, float]],
    tolerance_m: float = 100.0,
) -> tuple[bool, list[dict]]:
    """Validate that all lat/lon coordinates are within tolerance.

    Args:
        expected_coords: Expected coordinate dict from reference XML
        actual_coords: Actual coordinate dict from converted XML
        tolerance_m: Maximum allowed distance in meters

    Returns:
        (all_within_tolerance, diffs_list)
        diffs_list: [{element_id, distance_meters, lat_expected, lon_expected, ...}, ...]
    """
    diffs = []

    # Check each expected coordinate
    for elem_id, (lat_exp, lon_exp) in expected_coords.items():
        if elem_id not in actual_coords:
            diffs.append(
                {
                    "element_id": elem_id,
                    "status": "MISSING_IN_ACTUAL",
                    "expected_lat": lat_exp,
                    "expected_lon": lon_exp,
                }
            )
            continue

        lat_act, lon_act = actual_coords[elem_id]
        distance = haversine_distance(lat_exp, lon_exp, lat_act, lon_act)

        if distance > tolerance_m:
            diffs.append(
                {
                    "element_id": elem_id,
                    "distance_meters": round(distance, 2),
                    "expected_lat": lat_exp,
                    "expected_lon": lon_exp,
                    "actual_lat": lat_act,
                    "actual_lon": lon_act,
                    "status": "OUT_OF_TOLERANCE",
                }
            )

    # Check for coordinates in actual but not in expected
    diffs.extend(
        {
            "element_id": elem_id,
            "status": "EXTRA_IN_ACTUAL",
        }
        for elem_id in actual_coords
        if elem_id not in expected_coords
    )

    return len(diffs) == 0, diffs


def compare_xml_with_tolerance(
    expected_elem: ET.Element,
    actual_elem: ET.Element,
    test_case: str = "unknown",
    amendment_version: str = "unknown",
    lat_lon_tolerance_m: float = 100.0,
    ignore_attrs: set[str] | None = None,
    expected_xml_str: str | None = None,
    actual_xml_str: str | None = None,
) -> DiffReport:
    """Deep compare two XML elements with tolerance for numeric, UID, and lat/lon values.

    Args:
        expected_elem: Expected XML root element
        actual_elem: Actual converted XML root element
        test_case: Test case identifier (e.g., "BGBW-282350Z")
        amendment_version: Amendment version (e.g., "Amd79-80-2023")
        lat_lon_tolerance_m: Tolerance for lat/lon in meters
        ignore_attrs: Additional attributes to ignore besides id/schemaLocation

    Returns:
        DiffReport with structured comparison results
    """
    if ignore_attrs is None:
        ignore_attrs = set()

    # Normalize both elements to remove whitespace text node ambiguity
    logger.debug("Normalizing elements for comparison")

    # Convert to strings for normalization
    exp_str = ET.tostring(expected_elem, encoding="unicode")
    act_str = ET.tostring(actual_elem, encoding="unicode")

    # Re-parse with normalization
    expected_elem = parse_xml_normalized(exp_str)
    actual_elem = parse_xml_normalized(act_str)

    # Add dynamic attrs that should be ignored
    ignore_attrs.update(
        {
            "id",
            "gml:id",
            "schemaLocation",
            "translatedBulletinID",
            "translationCentreName",
            "translationCentreDesignator",
            "translationTime",
            "translatedBulletinReceptionTime",
            "translationFailedTAC",
            "permissibleUsage",
            "permissibleUsageReason",
            "permissibleUsageSupplementary",
        }
    )

    report = DiffReport(
        test_case=test_case,
        amendment_version=amendment_version,
        expected_xml=expected_xml_str,
        actual_xml=actual_xml_str,
    )

    # Extract and validate lat/lon coordinates
    expected_coords = extract_lat_lon(expected_elem)
    actual_coords = extract_lat_lon(actual_elem)
    _lat_lon_ok, lat_lon_diffs = validate_lat_lon_tolerance(expected_coords, actual_coords, lat_lon_tolerance_m)
    report.lat_lon_diffs = lat_lon_diffs

    # Strip dynamic attributes and do structural comparison
    _deep_diff(expected_elem, actual_elem, "", report, ignore_attrs)

    # Determine overall status
    has_field_diffs = len(report.field_diffs) > 0
    has_lat_lon_issues = len(report.lat_lon_diffs) > 0
    has_metadata_diffs = len(report.metadata_diffs) > 0

    report.status = "FAIL" if (has_field_diffs or has_lat_lon_issues) else "PASS"

    return report


def _deep_diff(
    expected: ET.Element,
    actual: ET.Element,
    path: str,
    report: DiffReport,
    ignore_attrs: set[str],
) -> None:
    """Recursively compare two elements and record differences."""

    tag = _local(expected.tag)
    current_path = f"{path}/{tag}" if path else tag

    # Compare tag names
    if _local(actual.tag) != tag:
        report.field_diffs.append(
            {
                "path": current_path,
                "type": "TAG_MISMATCH",
                "expected": tag,
                "actual": _local(actual.tag),
            }
        )
        return

    # Compare attributes
    def filter_attrs(attrs: dict) -> dict:
        out = {}
        for k, v in attrs.items():
            lk = _local(k)
            if lk in ignore_attrs:
                continue
            out[lk] = _norm_text(v)
        return out

    exp_attrs = filter_attrs(expected.attrib)
    act_attrs = filter_attrs(actual.attrib)

    # Check for missing attributes
    for k in exp_attrs:
        if k not in act_attrs:
            report.field_diffs.append(
                {
                    "path": current_path,
                    "type": "MISSING_ATTRIBUTE",
                    "attribute": k,
                    "expected": exp_attrs[k],
                }
            )
        elif exp_attrs[k] != act_attrs[k]:
            # Skip href attributes with UUID references (dynamic internal links)
            if k == "href" and "#uuid" in exp_attrs[k] and "#uuid" in act_attrs[k]:
                continue

            # Try numeric tolerance comparison
            try:
                exp_val = float(exp_attrs[k])
                act_val = float(act_attrs[k])
                if abs(exp_val - act_val) > 0.001:  # Small numeric tolerance
                    report.field_diffs.append(
                        {
                            "path": current_path,
                            "type": "ATTRIBUTE_MISMATCH",
                            "attribute": k,
                            "expected": str(exp_val),
                            "actual": str(act_val),
                            "difference": round(abs(exp_val - act_val), 6),
                        }
                    )
            except ValueError:
                # Non-numeric attribute difference
                if exp_attrs[k] != act_attrs[k]:
                    report.field_diffs.append(
                        {
                            "path": current_path,
                            "type": "ATTRIBUTE_MISMATCH",
                            "attribute": k,
                            "expected": exp_attrs[k],
                            "actual": act_attrs[k],
                        }
                    )

    # Check for extra attributes in actual
    for k in act_attrs:
        if k not in exp_attrs:
            report.field_diffs.append(
                {
                    "path": current_path,
                    "type": "EXTRA_ATTRIBUTE",
                    "attribute": k,
                    "actual": act_attrs[k],
                }
            )

    # Compare text content (normalized)
    # Skip timestamp elements and coordinate position elements (handled separately)
    timestamp_tags = {"timePosition", "issueTime", "validTime", "phenomenonTime", "resultTime"}
    coordinate_tags = {"pos", "posList", "Position", "AirportPosition", "Location"}
    # Airport name variations are acceptable (database vs official names)
    name_tags = {"name"}

    if tag not in timestamp_tags and tag not in coordinate_tags:
        exp_text = _norm_text(expected.text)
        act_text = _norm_text(actual.text)
        if exp_text != act_text:
            # Try numeric tolerance
            try:
                exp_val = float(exp_text)
                act_val = float(act_text)
                if abs(exp_val - act_val) > 0.001:
                    report.field_diffs.append(
                        {
                            "path": current_path,
                            "type": "TEXT_MISMATCH",
                            "expected": str(exp_val),
                            "actual": str(act_val),
                            "difference": round(abs(exp_val - act_val), 6),
                        }
                    )
            except ValueError:
                if exp_text and act_text and tag not in name_tags:  # Both non-empty; skip name tags
                    report.field_diffs.append(
                        {
                            "path": current_path,
                            "type": "TEXT_MISMATCH",
                            "expected": exp_text[:100],  # Truncate long text
                            "actual": act_text[:100],
                        }
                    )

    # Compare children recursively
    exp_children = list(expected)
    act_children = list(actual)

    if len(exp_children) != len(act_children):
        report.field_diffs.append(
            {
                "path": current_path,
                "type": "CHILD_COUNT_MISMATCH",
                "expected_count": len(exp_children),
                "actual_count": len(act_children),
            }
        )

    # Compare each child pair
    for i in range(min(len(exp_children), len(act_children))):
        _deep_diff(exp_children[i], act_children[i], current_path, report, ignore_attrs)

    # Report extra children in actual
    for i in range(len(exp_children), len(act_children)):
        child_tag = _local(act_children[i].tag)
        report.field_diffs.append(
            {
                "path": current_path,
                "type": "EXTRA_CHILD",
                "child_tag": child_tag,
                "index": i,
            }
        )

    # Report missing children in actual
    for i in range(len(act_children), len(exp_children)):
        child_tag = _local(exp_children[i].tag)
        report.field_diffs.append(
            {
                "path": current_path,
                "type": "MISSING_CHILD",
                "child_tag": child_tag,
                "index": i,
            }
        )
