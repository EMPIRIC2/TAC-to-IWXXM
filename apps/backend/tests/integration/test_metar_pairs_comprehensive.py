"""Comprehensive parametrized tests for METAR→IWXXM conversion.

Tests all .tac/.xml pairs from:
- Amd79-80-2023 (34 pairs) - IWXXM 2023-1/2025-2 compliant

Total: 34 test cases

Acceptable differences:
- UID values (gml:id, id attributes)
- Record dates (timeStamp, validTime)
- Lat/lon coordinates within 100m tolerance
- Numeric values within 0.001 precision

All other XML elements and attributes must match exactly.
Failures generate detailed JSON diff reports for root cause analysis.
"""

import re
from pathlib import Path
from typing import List, Tuple

import pytest

from src.utilities.conversion import convert_metar_tac_with_metadata


def extract_iwxxm_version(xml_content: str) -> str:
    """Extract IWXXM version from XML namespace URI.

    Args:
        xml_content: XML string containing IWXXM namespace declaration

    Returns:
        Version string like "2023-1" or "2025-2", defaults to "2025-2" if not found
    """
    # Look for xmlns:iwxxm="http://icao.int/iwxxm/{version}"
    match = re.search(r'xmlns:iwxxm="http://icao\.int/iwxxm/(\d{4}-\d+)"', xml_content)
    if match:
        return match.group(1)

    # Fallback: check xsi:schemaLocation
    match = re.search(r"http://icao\.int/iwxxm/(\d{4}-\d+)/iwxxm\.xsd", xml_content)
    if match:
        return match.group(1)

    # Default to latest version
    return "2025-2"


def _collect_metar_pairs(data_dir: Path) -> List[Tuple[Path, Path, str]]:
    """Collect all (tac_file, xml_file, version_name) tuples from test data directories.

    Returns:
        List of (tac_path, xml_path, amendment_version) tuples
    """
    pairs = []
    base = Path(data_dir)

    # Only test current supported IWXXM version data
    versions = ["Amd79-80-2023"]

    for version in versions:
        metar_dir = base / version / "metar"
        if not metar_dir.exists():
            continue

        # Find all .tac files
        tac_files = sorted(metar_dir.glob("*.tac"))
        for tac_file in tac_files:
            # Corresponding .xml file must exist
            xml_file = tac_file.with_suffix(".xml")
            if xml_file.exists():
                pairs.append((tac_file, xml_file, version))

    return pairs


# Collect test data at module load time
# Data is at repository root (4 levels up from tests/integration), not backend
DATA_ROOT = Path(__file__).parent.parent.parent.parent / "data" / "iwxxm-translation"
METAR_PAIRS = _collect_metar_pairs(DATA_ROOT)
REPORT_DIR = Path(__file__).parent.parent / "test-reports" / "local-test-failures"
LIVE_REPORT_DIR = Path(__file__).parent.parent / "test-reports" / "live-test-failures"


class TestMetarConversionComprehensive:
    """Parametrized tests for METAR→IWXXM conversion across all amendment versions."""

    @pytest.mark.parametrize(
        "tac_file,xml_file,amendment_version",
        METAR_PAIRS,
    )
    def test_metar_converts_to_matching_iwxxm(self, tac_file: Path, xml_file: Path, amendment_version: str):
        """Convert METAR TAC to IWXXM and verify output matches expected XML.

        Args:
            tac_file: Path to METAR TAC input file
            xml_file: Path to expected IWXXM XML output file
            amendment_version: Amendment version (e.g., "Amd79-80-2023")

        Acceptable differences:
        - UID/ID attributes (dynamically generated)
        - Record/issue dates (current timestamp)
        - Lat/lon within 100m of original coordinates
        - Numeric values within 0.001 precision

        All other elements must match exactly.
        Failures save detailed diff report to test-reports/local-test-failures/
        """
        import xml.etree.ElementTree as ET

        from _comparative_xml_utils import (
            compare_xml_with_tolerance,
            parse_xml,
        )

        # Read input METAR TAC
        tac_text = tac_file.read_text().strip()

        # Ensure trailing = sign for METAR parsing
        if not tac_text.endswith("="):
            tac_text += "="

        # Extract IWXXM version and observation time from reference XML
        # Version detection ensures structural compatibility (2023-1 vs 2025-2)
        # Reference time ensures trend forecast dates computed from observation, not current date
        expected_xml = xml_file.read_text()
        iwxxm_version = extract_iwxxm_version(expected_xml)

        reference_time = None
        try:
            expected_root = ET.fromstring(expected_xml)

            # Extract namespace URI dynamically instead of hardcoding
            ns_match = re.search(r'xmlns:iwxxm="([^"]+)"', expected_xml)
            iwxxm_ns = ns_match.group(1) if ns_match else "http://icao.int/iwxxm/2023-1"

            # Find iwxxm:issueTime/gml:TimeInstant/gml:timePosition
            namespaces = {"iwxxm": iwxxm_ns, "gml": "http://www.opengis.net/gml/3.2"}
            time_elem = expected_root.find(".//iwxxm:issueTime//gml:timePosition", namespaces)
            if time_elem is not None and time_elem.text:
                reference_time = time_elem.text.strip()
        except Exception:
            # If extraction fails, proceed without reference time (will use current time)
            pass

        # Convert METAR TAC to IWXXM XML with enriched aerodrome metadata
        # Use detected version for compatibility + test mode for WMO reference compliance
        converted_xml, validation_result = convert_metar_tac_with_metadata(
            tac_text,
            iwxxm_version=iwxxm_version,  # Auto-detected from reference XML
            reference_time=reference_time,
            use_test_overrides=True,  # Use WMO reference datum expectations
            validate=False,  # Disable validation to avoid overhead in these tests
        )
        assert converted_xml, f"Conversion failed for {tac_file.name}"

        # Read expected XML
        expected_xml_str = xml_file.read_text()

        # Parse both expected and converted XML
        expected_elem = parse_xml(expected_xml_str)
        actual_elem = parse_xml(converted_xml)

        # Deep comparison with tolerance for dynamic attributes and coordinates
        report = compare_xml_with_tolerance(
            expected_elem,
            actual_elem,
            test_case=tac_file.stem,
            amendment_version=amendment_version,
            lat_lon_tolerance_m=100.0,
            expected_xml_str=expected_xml_str,
            actual_xml_str=converted_xml,
        )

        # Save report for all tests (useful for analysis even on pass)
        report.save(REPORT_DIR)

        # Assert comparison passed
        if report.status == "FAIL":
            # Build detailed failure message
            msg_parts = [
                f"\nTest: {tac_file.stem} ({amendment_version})",
                f"TAC Input: {tac_text[:80]}",
            ]

            if report.field_diffs:
                msg_parts.append(f"\n{len(report.field_diffs)} Field Differences:")
                for diff in report.field_diffs[:5]:  # Show first 5
                    msg_parts.append(f"  - {diff}")
                if len(report.field_diffs) > 5:
                    msg_parts.append(f"  ... and {len(report.field_diffs) - 5} more")

            if report.lat_lon_diffs:
                msg_parts.append(f"\n{len(report.lat_lon_diffs)} Lat/Lon Differences:")
                for diff in report.lat_lon_diffs[:3]:
                    msg_parts.append(f"  - {diff}")

            msg_parts.append(f"\nFull diff report: {REPORT_DIR}/{tac_file.stem}_{amendment_version}.json")

            pytest.fail("\n".join(msg_parts))

    @pytest.mark.parametrize(
        "tac_file,xml_file,amendment_version",
        METAR_PAIRS,
    )
    def test_metar_converts_to_iwxxm_2025_2(self, tac_file: Path, xml_file: Path, amendment_version: str):
        """Convert METAR TAC to IWXXM 2025-2 and generate comparison reports.

        This test generates JSON reports for 2025-2 conversions using
        aviation-weather-service data, allowing comparison with WMO reference data.
        Reports are always generated regardless of pass/fail status for analysis.

        Args:
            tac_file: Path to METAR TAC input file
            xml_file: Path to expected IWXXM XML output file (2023-1 reference)
            amendment_version: Amendment version (e.g., "Amd79-80-2023")
        """

        from _comparative_xml_utils import (
            compare_xml_with_tolerance,
            parse_xml,
        )

        # Read input METAR TAC
        tac_text = tac_file.read_text().strip()

        # Ensure trailing = sign for METAR parsing
        if not tac_text.endswith("="):
            tac_text += "="

        # Convert to IWXXM 2025-2 (latest version)
        converted_xml, validation_result = convert_metar_tac_with_metadata(
            tac_text,
            iwxxm_version="2025-2",  # Force 2025-2 for live comparison
            use_test_overrides=True,
            validate=False,
        )
        assert converted_xml, f"Conversion failed for {tac_file.name}"

        # Read expected XML (2023-1 reference)
        expected_xml_str = xml_file.read_text()

        # Parse both expected and converted XML
        expected_elem = parse_xml(expected_xml_str)
        actual_elem = parse_xml(converted_xml)

        # Deep comparison with tolerance
        report = compare_xml_with_tolerance(
            expected_elem,
            actual_elem,
            test_case=tac_file.stem,
            amendment_version=f"{amendment_version}-2025-2",
            lat_lon_tolerance_m=100.0,
            expected_xml_str=expected_xml_str,
            actual_xml_str=converted_xml,
        )

        # Save report for analysis (not blocking)
        LIVE_REPORT_DIR.mkdir(parents=True, exist_ok=True)
        report.save(LIVE_REPORT_DIR)

        # These tests are for comparison only - don't fail on differences
        # The goal is to understand version differences, not enforce strict matching
        if report.status == "FAIL":
            print(f"\n⚠️  Version comparison report: {tac_file.stem} (2025-2)")
            print(f"    Field diffs: {len(report.field_diffs)}, Lat/Lon diffs: {len(report.lat_lon_diffs)}")
            print(f"    Report saved to: {LIVE_REPORT_DIR}/{tac_file.stem}_{amendment_version}-2025-2.json")
        else:
            print(f"\n✅ Perfect match: {tac_file.stem} (2025-2)")


class TestMetarConversionStats:
    """Test suite statistics and data validation."""

    def test_metar_pairs_discovered(self):
        """Verify that expected number of METAR pairs were discovered."""
        assert len(METAR_PAIRS) > 0, "No METAR test pairs discovered"

        # Group by version
        by_version = {}
        for _, _, version in METAR_PAIRS:
            by_version[version] = by_version.get(version, 0) + 1

        # Expected counts (from data/iwxxm-translation)
        # Only testing current supported IWXXM version
        expected_counts = {
            "Amd79-80-2023": 34,
        }

        for version, expected_count in expected_counts.items():
            actual_count = by_version.get(version, 0)
            assert actual_count == expected_count, f"{version}: expected {expected_count} pairs, got {actual_count}"

    def test_report_directory_writable(self):
        """Verify test report directory can be created and written to."""
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        assert REPORT_DIR.exists()
        assert REPORT_DIR.is_dir()

    def test_sample_tac_file_content(self):
        """Verify sample TAC files have valid content."""
        if not METAR_PAIRS:
            pytest.skip("No METAR pairs available")

        # Check first pair
        tac_file, _, _ = METAR_PAIRS[0]
        tac_text = tac_file.read_text().strip()

        # TAC should contain METAR or SPECI
        assert "METAR" in tac_text or "SPECI" in tac_text, f"TAC should contain METAR/SPECI: {tac_text}"
        # Should have station code somewhere in text
        words = tac_text.split()
        assert len(words) > 0, f"TAC file should not be empty: {tac_file.name}"
        # Station code is typically the first or second word (after METAR/SPECI)
        has_station = any(len(word) == 4 and word.isalpha() for word in words[:3])
        assert has_station, f"Should have 4-letter station code in first 3 words: {tac_text}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
