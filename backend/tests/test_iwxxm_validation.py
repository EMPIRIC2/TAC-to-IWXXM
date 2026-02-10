"""
Tests for IWXXM validation schemas and metadata.

This module tests the validation of IWXXM metadata including:
- Meteorological features
- Volcanic aviation color codes  
- Nil reasons
- IWXXM version compatibility
"""

import pytest
import sys
import pathlib

# Setup path
ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from schemas.iwxxm_validation import (
    MeteorologicalFeature,
    VolcanicAviationColourCode,
    NilReason,
    IWXXMVersion,
    is_valid_meteorological_feature,
    is_valid_volcanic_code,
    is_valid_nil_reason,
    is_supported_iwxxm_version,
    get_namespace_version,
)


class TestMeteorologicalFeatures:
    """Test meteorological feature validation."""
    
    def test_valid_features_exist(self) -> None:
        """Verify all meteorological features are defined."""
        assert len(MeteorologicalFeature) >= 20, \
            "Expected at least 20 meteorological features"
        
        # Verify specific features
        assert MeteorologicalFeature.AIRFRAME_ICING.value == "AIRFRAME_ICING"
        assert MeteorologicalFeature.STORM.value == "STORM"
        assert MeteorologicalFeature.JETSTREAM.value == "JETSTREAM"
    
    def test_validate_meteorological_feature(self) -> None:
        """Test meteorological feature validation."""
        assert is_valid_meteorological_feature("AIRFRAME_ICING")
        assert is_valid_meteorological_feature("CLOUD")
        assert is_valid_meteorological_feature("JETSTREAM")
        assert not is_valid_meteorological_feature("INVALID_FEATURE")
        assert not is_valid_meteorological_feature("")
    
    def test_meteorological_feature_enum_values(self) -> None:
        """Verify meteorological feature enum has expected values."""
        features = [f.value for f in MeteorologicalFeature]
        assert "AIRFRAME_ICING" in features
        assert "ATMOSPHERICS" in features
        assert "COLD_FRONT_AT_THE_SURFACE" in features
        assert "DUSTSTORM" in features
        assert "SANDSTORM" in features


class TestVolcanicAviationCodes:
    """Test volcanic aviation colour code validation."""
    
    def test_valid_codes_exist(self) -> None:
        """Verify all volcanic codes are defined."""
        assert len(VolcanicAviationColourCode) == 5, \
            "Expected 5 volcanic aviation colour codes"
    
    def test_validate_volcanic_code(self) -> None:
        """Test volcanic code validation."""
        assert is_valid_volcanic_code("GREEN")
        assert is_valid_volcanic_code("YELLOW")
        assert is_valid_volcanic_code("ORANGE")
        assert is_valid_volcanic_code("RED")
        assert is_valid_volcanic_code("UNASSIGNED")
        assert not is_valid_volcanic_code("INVALID_CODE")
        assert not is_valid_volcanic_code("PURPLE")
    
    def test_volcanic_code_enum_values(self) -> None:
        """Verify volcanic code enum has expected values."""
        codes = [c.value for c in VolcanicAviationColourCode]
        assert "GREEN" in codes
        assert "YELLOW" in codes
        assert "ORANGE" in codes
        assert "RED" in codes
        assert "UNASSIGNED" in codes
        assert len(codes) == 5


class TestNilReasons:
    """Test nil reason validation."""
    
    def test_valid_nil_reasons_exist(self) -> None:
        """Verify all nil reasons are defined."""
        assert len(NilReason) >= 10, \
            "Expected at least 10 nil reasons"
    
    def test_validate_nil_reason(self) -> None:
        """Test nil reason validation."""
        assert is_valid_nil_reason("missing")
        assert is_valid_nil_reason("unknown")
        assert is_valid_nil_reason("noSignificantChange")
        assert is_valid_nil_reason("notObservable")
        assert not is_valid_nil_reason("INVALID_REASON")
        assert not is_valid_nil_reason("")
    
    def test_nil_reason_enum_values(self) -> None:
        """Verify nil reason enum has expected values."""
        reasons = [r.value for r in NilReason]
        assert "missing" in reasons
        assert "unknown" in reasons
        assert "inapplicable" in reasons
        assert "noSignificantChange" in reasons
        assert "notObservable" in reasons
        assert "AboveDetectionRange" in reasons
        assert "BelowDetectionRange" in reasons


class TestIWXXMVersions:
    """Test IWXXM version validation."""
    
    def test_supported_versions_exist(self) -> None:
        """Verify supported IWXXM versions are defined."""
        assert len(IWXXMVersion) >= 4, \
            "Expected at least 4 supported IWXXM versions"
    
    def test_version_validation(self) -> None:
        """Test IWXXM version validation."""
        assert is_supported_iwxxm_version("2016-1")
        assert is_supported_iwxxm_version("2018-2")
        assert is_supported_iwxxm_version("2021-2")
        assert is_supported_iwxxm_version("2023-1")
        assert is_supported_iwxxm_version("2025-2")
        assert not is_supported_iwxxm_version("2020-1")
        assert not is_supported_iwxxm_version("2030-0")
    
    def test_version_enum_values(self) -> None:
        """Verify version enum has expected values."""
        versions = [v.value for v in IWXXMVersion]
        assert "2016-1" in versions
        assert "2018-2" in versions
        assert "2021-2" in versions
        assert "2023-1" in versions
        assert "2025-2" in versions


class TestNamespaceVersionExtraction:
    """Test IWXXM namespace version extraction."""
    
    def test_extract_version_2023_1(self) -> None:
        """Test extracting 2023-1 version from XML."""
        xml = '''<?xml version="1.0"?>
<iwxxm:SPECI xmlns:iwxxm="http://icao.int/iwxxm/2023-1">
</iwxxm:SPECI>'''
        version = get_namespace_version(xml)
        assert version == "2023-1"
    
    def test_extract_version_2025_2(self) -> None:
        """Test extracting 2025-2 version from XML."""
        xml = '''<?xml version="1.0"?>
<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2">
</iwxxm:METAR>'''
        version = get_namespace_version(xml)
        assert version == "2025-2"
    
    def test_extract_version_2021_2(self) -> None:
        """Test extracting 2021-2 version from XML."""
        xml = '''<iwxxm:SPECI xmlns:iwxxm="http://icao.int/iwxxm/2021-2">
</iwxxm:SPECI>'''
        version = get_namespace_version(xml)
        assert version == "2021-2"
    
    def test_missing_namespace_raises_error(self) -> None:
        """Test that missing IWXXM namespace raises error."""
        xml = '''<?xml version="1.0"?>
<iwxxm:SPECI>
</iwxxm:SPECI>'''
        with pytest.raises(ValueError):
            get_namespace_version(xml)
    
    def test_invalid_namespace_raises_error(self) -> None:
        """Test that invalid namespace raises error."""
        xml = '''<?xml version="1.0"?>
<iwxxm:SPECI xmlns:iwxxm="http://example.com/invalid">
</iwxxm:SPECI>'''
        with pytest.raises(ValueError):
            get_namespace_version(xml)
    
    def test_unsupported_version_raises_error(self) -> None:
        """Test that unsupported version raises error."""
        xml = '''<?xml version="1.0"?>
<iwxxm:SPECI xmlns:iwxxm="http://icao.int/iwxxm/9999-9">
</iwxxm:SPECI>'''
        with pytest.raises(ValueError):
            get_namespace_version(xml)


class TestMetadataValidation:
    """Integration tests for metadata validation."""
    
    def test_meteorological_features_are_stable(self) -> None:
        """Verify all meteorological features are marked stable."""
        # This test documents that GIFTs should validate these
        features_to_expect = [
            "AIRFRAME_ICING",
            "CLOUD",
            "DUSTSTORM",
            "JETSTREAM",
            "STORM",
        ]
        for feature in features_to_expect:
            assert is_valid_meteorological_feature(feature), \
                f"Expected {feature} to be valid"
    
    def test_nil_reasons_cover_common_cases(self) -> None:
        """Verify nil reasons cover common no-data scenarios."""
        common_reasons = [
            "missing",           # No data provided
            "unknown",           # Can't determine value
            "inapplicable",      # Feature not relevant
            "notObservable",     # Can't measure
            "noSignificantChange",  # NOSIG
        ]
        for reason in common_reasons:
            assert is_valid_nil_reason(reason), \
                f"Expected {reason} to be valid nil reason"
    
    def test_volcanic_codes_match_icao_doc9766(self) -> None:
        """Verify volcanic codes match ICAO Doc 9766."""
        # As per ICAO Doc 9766
        expected_codes = ["GREEN", "YELLOW", "ORANGE", "RED", "UNASSIGNED"]
        for code in expected_codes:
            assert is_valid_volcanic_code(code), \
                f"Expected {code} to match ICAO Doc 9766"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
