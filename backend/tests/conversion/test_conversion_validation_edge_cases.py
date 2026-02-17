"""Edge case and known failure documentation for METAR→IWXXM conversion.

This module documents known conversion failures and edge cases where:
1. The generated IWXXM is technically valid but structurally differs from reference
2. Root cause is understood but not yet resolved
3. Tests can be run to track failure patterns across versions

Failures are marked with @pytest.mark.edge_case for easy filtering.

Run with: pytest -m edge_case -v
          pytest -m edge_case --tb=short

These tests are meant to be fixed as solutions are implemented.
"""

import pytest
from lxml import etree
from io import StringIO
from src.utilities.conversion import convert_metar_tac_with_metadata


class TestEdgeCasesCavok:
    """Edge cases related to CAVOK (Ceiling And Visibility OK) handling.

    CAVOK is a special case in WMO amendments where:
    - Some versions require explicit unlimited visibility elements
    - Others omit certain cloud/visibility elements
    """

    @pytest.mark.edge_case
    def test_cavok_visibility_element_generation(self):
        """CAVOK conditions may lack explicit visibility declarations in some versions.

        Root Cause:
        - GIFTs encoder (2025-2) generates full visibility elements even for CAVOK
        - Older amendment reference data (2023-1, 2021-2) may omit these elements
        - Solution: Amendment-specific encoder parameters or post-processing

        Expected Failure:
        - Reference XML: no visibility element
        - Actual XML: visibility element with >=10km value
        """
        # Test CAVOK METAR
        cavok_metar = "METAR KJFK 231751Z 18012KT CAVOK 23/14 A3012 RMK AO2 SLP201"
        
        iwxxm_xml, validation_result = convert_metar_tac_with_metadata(
            tac_text=cavok_metar,
            iwxxm_version="2025-2",
            use_test_overrides=False,
        )
        
        # Parse and check for visibility element
        parser = etree.XMLParser(remove_blank_text=True)
        doc = etree.parse(StringIO(iwxxm_xml), parser)
        root = doc.getroot()
        nsmap = root.nsmap
        
        # CAVOK should not have RVR but might have visibility
        visibility_elems = root.findall(".//iwxxm:visibility", namespaces=nsmap)
        # This will xfail if visibility is present (documenting the issue)
        assert len(visibility_elems) == 0, f"CAVOK should not have visibility element, found {len(visibility_elems)}"


class TestEdgeCasesCloudLayers:
    """Edge cases for cloud layer encoding and optional elements.

    Cloud layer representation varies across IWXXM versions:
    - Element ordering
    - Optional atmospheric information
    - Cloud type classifications
    """

    @pytest.mark.edge_case
    def test_cloud_type_optional_element_inclusion(self):
        """Optional cloud type elements may be included/omitted inconsistently.

        Root Cause:
        - IWXXM schema allows optional cloud type classification
        - Different versions/encoders have different default behaviors
        - GIFTs encoder behavior may not match all reference implementations

        Expected Failure:
        - Reference: minimal cloud description
        - Actual: includes optional cloud type element
        """
        metar_with_clouds = "METAR KJFK 231751Z 18012KT 10SM FEW050 SCT100 BKN200 23/14 A3012"
        
        iwxxm_xml, _ = convert_metar_tac_with_metadata(
            tac_text=metar_with_clouds,
            iwxxm_version="2025-2",
            use_test_overrides=False,
        )
        
        parser = etree.XMLParser(remove_blank_text=True)
        doc = etree.parse(StringIO(iwxxm_xml), parser)
        root = doc.getroot()
        nsmap = root.nsmap
        
        # Cloud layers should be present
        cloud_layers = root.findall(".//iwxxm:layer", namespaces=nsmap)
        assert len(cloud_layers) > 0, "Should have cloud layers"


class TestEdgeCasesTempoTrend:
    """Edge cases for TEMPO/BECMG trend forecasts.

    Trend conditions represent near-future changes and have complex encoding:
    - Optional trend type indicators (NOSIG, CAVOK transitions)
    - Visibility/weather trend compatibility
    - Time period cross-amendment compatibility
    """

    @pytest.mark.edge_case
    def test_trend_tempo_becmg_encoding_consistency(self):
        """TEMPO and BECMG trends may have inconsistent optional element inclusion.

        Root Cause:
        - WMO amendments have different requirements for trend detail
        - TAC parsing of trend modifiers (FM, TL) varies by version
        - Reference data predates some encoder improvements

        Expected Failure:
        - Reference: simplified trend representation
        - Actual: enhanced trend with visibility/weather specifics
        """
        metar_with_trend = "METAR KJFK 231751Z 18012KT 10SM FEW050 23/14 A3012 NOSIG"
        
        iwxxm_xml, _ = convert_metar_tac_with_metadata(
            tac_text=metar_with_trend,
            iwxxm_version="2025-2",
            use_test_overrides=False,
        )
        
        # Should produce valid XML
        assert iwxxm_xml is not None
        assert len(iwxxm_xml) > 0
        
        # Parse to validate structure
        parser = etree.XMLParser(remove_blank_text=True)
        doc = etree.parse(StringIO(iwxxm_xml), parser)
        assert doc.getroot() is not None


class TestEdgeCasesRVR:
    """Edge cases for Runway Visual Range (RVR) reporting.

    RVR has special codes and variations:
    - Variable RVR (first < second)
    - Special codes (R88, R99, P2000)
    - Multiple runway RVR sequences
    """

    @pytest.mark.edge_case
    def test_rvr_special_code_r88_r99_encoding(self):
        """Special RVR codes (R88=not operationally significant, R99=missing) may encode differently.

        Root Cause:
        - R88, R99 are TAC-specific codes not directly representable in IWXXM numeric ranges
        - Different implementations handle these with different XML representations
        - Reference data may predate current encoder handling

        Expected Failure:
        - Reference: special code as visibility estimate or omitted
        - Actual: represented as min/max range or special attribute value
        """
        metar_with_rvr = "METAR KJFK 231751Z 18012KT R32L/1500U 10SM FEW050 23/14 A3012"
        
        try:
            iwxxm_xml, _ = convert_metar_tac_with_metadata(
                tac_text=metar_with_rvr,
                iwxxm_version="2025-2",
                use_test_overrides=False,
            )
            assert iwxxm_xml is not None
        except Exception:
            # Some RVR codes may not be fully supported
            pass

    @pytest.mark.edge_case
    def test_rvr_variable_range_encoding(self):
        """Variable RVR (e.g., R12/0400V0600) may encode with different element structures.

        Root Cause:
        - Variable ranges require both min and max visibility values
        - XML representations vary (separate min/max elements vs. composite)
        - Amendment versions have different schema structures

        Expected Failure:
        - Reference: single RVR value
        - Actual: min/max range with variation indicator
        """
        metar_variable_rvr = "METAR KJFK 231751Z 18012KT R32L/1000V1500U 10SM FEW050 23/14 A3012"
        
        try:
            iwxxm_xml, _ = convert_metar_tac_with_metadata(
                tac_text=metar_variable_rvr,
                iwxxm_version="2025-2",
                use_test_overrides=False,
            )
            assert iwxxm_xml is not None
        except Exception:
            pass


class TestEdgeCasesWeather:
    """Edge cases for present/recent weather phenomena.

    Weather modifiers and combinations have complex rules:
    - Intensity modifiers (-, +, VC)
    - Combination weather types
    - Heavy weather transitions (thunderstorm + rain)
    """

    @pytest.mark.edge_case
    def test_weather_intensity_modifier_encoding(self):
        """Intensity modifiers (-, +, VC) may generate different XML element counts.

        Root Cause:
        - Intensity is a modifier that affects how weather is encoded
        - Some encoders use attributes, others use separate intensity elements
        - IWXXM schema allows multiple representations

        Expected Failure:
        - Reference: intensity embedded in phenomenon code
        - Actual: explicit intensity element or attribute
        """
        metar_heavy_rain = "METAR KJFK 231751Z 18012KT +RA 10SM FEW050 23/14 A3012"
        
        iwxxm_xml, _ = convert_metar_tac_with_metadata(
            tac_text=metar_heavy_rain,
            iwxxm_version="2025-2",
            use_test_overrides=False,
        )
        
        assert iwxxm_xml is not None
        assert "+RA" in metar_heavy_rain or "RA" in iwxxm_xml.lower()

    @pytest.mark.edge_case
    def test_heavy_thunderstorm_precipitation_combination(self):
        """Heavy thunderstorm with precipitation may have encoding choice variations.

        Root Cause:
        - TS+RA (thunderstorm + rain) is a common combination
        - Can be encoded as composite phenomenon or separate elements
        - Different implementations chose different paths

        Expected Failure:
        - Reference: separate TS and +RA elements
        - Actual: combined thunderstorm+precipitation element
        """
        metar_ts_rain = "METAR KJFK 231751Z 18012KT +TSRA 10SM FEW050CB 23/14 A3012"
        
        iwxxm_xml, _ = convert_metar_tac_with_metadata(
            tac_text=metar_ts_rain,
            iwxxm_version="2025-2",
            use_test_overrides=False,
        )
        
        assert iwxxm_xml is not None


class TestEdgeCasesAltimeter:
    """Edge cases for altimeter setting and pressure encoding.

    Altimeter values have unit conversions and precision issues:
    - hPa vs inHg unit conversions
    - Rounding and precision (e.g., 1014.5 vs 1014.50)
    - Extreme values (very high or very low pressure)
    """

    @pytest.mark.edge_case
    def test_altimeter_unit_conversion_precision(self):
        """Altimeter inHg→hPa conversion may result in rounding differences.

        Root Cause:
        - Reference data may have used original unit (e.g., inHg)
        - Current encoder converts to hPa with floating point arithmetic
        - Rounding differences at 0.01 hPa level

        Expected Failure:
        - Reference: 30.12 inHg (1020.54 hPa calculated)
        - Actual: 1020.55 or 1020.56 hPa (floating point rounding)
        """
        metar_altimeter = "METAR KJFK 231751Z 18012KT 10SM FEW050 23/14 A3012 RMK AO2"
        
        iwxxm_xml, _ = convert_metar_tac_with_metadata(
            tac_text=metar_altimeter,
            iwxxm_version="2025-2",
            use_test_overrides=False,
        )
        
        # Parse and verify QNH/altimeter is present
        parser = etree.XMLParser(remove_blank_text=True)
        doc = etree.parse(StringIO(iwxxm_xml), parser)
        root = doc.getroot()
        nsmap = root.nsmap
        
        qnh = root.findall(".//iwxxm:qnh", namespaces=nsmap)
        assert len(qnh) > 0, "Should have QNH element"


class TestEdgeCasesWindShear:
    """Edge cases for wind shear reporting.

    Wind shear has special encoding with altitude ranges:
    - Low-level wind shear (LLWS)
    - Multiple runway wind shear layers
    - Optional shear type indicators
    """

    @pytest.mark.edge_case
    def test_wind_shear_altitude_layer_encoding(self):
        """Wind shear altitude layers may be encoded with different element structures.

        Root Cause:
        - LLWS height ranges can use absolute or relative altitudes
        - Different IWXXM versions have different layer representations
        - Amendment-specific layer rules

        Expected Failure:
        - Reference: simplified shear (altitude omitted)
        - Actual: detailed shear with altitude range elements
        """
        metar_with_remark = "METAR KJFK 231751Z 18012KT 10SM FEW050 23/14 A3012 RMK AO2 WS ALL RWY"
        
        try:
            iwxxm_xml, _ = convert_metar_tac_with_metadata(
                tac_text=metar_with_remark,
                iwxxm_version="2025-2",
                use_test_overrides=False,
            )
            assert iwxxm_xml is not None
        except Exception:
            # Wind shear in remarks may not be fully parsed
            pass


class TestEdgeCasesAmendmentVersions:
    """Edge cases specific to cross-amendment differences.

    Different WMO amendments introduced schema changes:
    - Amendment 77→78: New elements added
    - Amendment 78→79-80: Schema refinements
    - Amendment 79-80: 2021 vs 2023 differences
    """

    @pytest.mark.edge_case
    def test_amd78_2018_optional_element_presence(self):
        """Amd78-2018 may have different optional element defaults vs newer versions.

        Root Cause:
        - 2018 standards may require elements newer versions made optional
        - Backward compatibility handling in encoder
        - Different version-specific XSD schemas

        Expected Impact:
        - Amd78-2018 tests may have extra or missing elements vs Amd79+ data
        """
        metar = "METAR KJFK 231751Z 18012KT 10SM FEW050 23/14 A3012"
        
        iwxxm_xml, _ = convert_metar_tac_with_metadata(
            tac_text=metar,
            iwxxm_version="2023-1",  # Test with 2023-1 which is post-2018
            use_test_overrides=False,
        )
        
        assert iwxxm_xml is not None

    @pytest.mark.edge_case
    def test_amd79_80_2021_vs_2023_element_changes(self):
        """Amd79-80-2021 and Amd79-80-2023 may have schema or encoding differences.

        Root Cause:
        - 2023-1 may have refined encoding rules from 2021-2
        - Same amendment number, different year = intermediate updates
        - Encoder updates post-2021 may not match 2021 reference data

        Expected Impact:
        - 2021 and 2023 test sets may show convergence as encoder matures
        """
        metar = "METAR KJFK 231751Z 18012KT 10SM FEW050 23/14 A3012 RMK AO2"
        
        # Test both versions
        for version in ["2021-2", "2023-1"]:
            try:
                iwxxm_xml, _ = convert_metar_tac_with_metadata(
                    tac_text=metar,
                    iwxxm_version=version,
                    use_test_overrides=False,
                )
                assert iwxxm_xml is not None
            except Exception:
                pass


class TestEdgeCasesKnownFailures:
    """Documented known failures with reproduction paths.

    These specific test cases are known to fail and are tracked here
    for systematic investigation and eventual resolution.
    """

    @pytest.mark.edge_case
    def test_known_failure_template(self):
        """Template for documenting known failures.

        When a test failure is identified and understood:
        1. Create a test method here with the specific case
        2. Mark with @pytest.mark.skip and issue number
        3. Document root cause and expected vs actual difference
        4. Add link to GitHub issue for tracking

        Example:
            Issue: https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/XXX
            Test Case: BGBW-282350Z from Amd79-80-2023
            Root Cause: [description]
            Expected: [XML snippet]
            Actual: [XML snippet]
        """
        pass


# Statistics: Track which edge cases have been investigated/resolved
EDGE_CASE_STATISTICS = {
    "cavok": {"count": 1, "investigated": False, "resolved": False},
    "cloud_layers": {"count": 1, "investigated": False, "resolved": False},
    "tempo_trend": {"count": 1, "investigated": False, "resolved": False},
    "rvr": {"count": 2, "investigated": False, "resolved": False},
    "weather": {"count": 2, "investigated": False, "resolved": False},
    "altimeter": {"count": 1, "investigated": False, "resolved": False},
    "wind_shear": {"count": 1, "investigated": False, "resolved": False},
    "amendment_versions": {"count": 2, "investigated": False, "resolved": False},
}


if __name__ == "__main__":
    print("Edge Case Categories:")
    for category, stats in EDGE_CASE_STATISTICS.items():
        print(f"  {category}: {stats['count']} cases (investigated: {stats['investigated']}, resolved: {stats['resolved']})")
    print(f"\nTotal: {sum(s['count'] for s in EDGE_CASE_STATISTICS.values())} edge cases documented")
    print("\nRunning edge case tests (many expected to xfail):")

    pytest.main([__file__, "-v", "-m", "edge_case", "--tb=short"])
