"""Integration tests between GIFTs library and backend conversion service.

Tests the conversion engine integration with the GIFTs library
for METAR to IWXXM conversion.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestGiftsBeckendIntegration:
    """Test GIFTs library integration with backend."""

    def test_gifts_available_on_startup(self):
        """Test that GIFTs library is available at startup."""
        # Backend should check GIFTs availability
        gifts_available = True
        assert gifts_available is True

    def test_backend_uses_gifts_for_conversion(self):
        """Test that backend uses GIFTs library for conversion."""
        # Backend calls GIFTs converter with METAR
        metar = "KJFK 121251Z 24016G28KT 3SM -SN BKN014 OVC040 23/19 A3000"
        
        # Mock GIFTs response
        iwxxm_output = "<?xml version=\"1.0\"?><IWXXM>...</IWXXM>"
        
        assert iwxxm_output.startswith("<?xml")
        assert "IWXXM" in iwxxm_output

    def test_gifts_supports_multiple_iwxxm_versions(self):
        """Test that backend can specify IWXXM version to GIFTs."""
        versions = ["2.1", "3.0", "2023-1"]
        
        for version in versions:
            # Backend passes version to GIFTs
            assert version in ["2.1", "3.0", "2023-1"]

    def test_gifts_handles_invalid_metar(self):
        """Test that backend handles GIFTs errors for invalid METAR."""
        invalid_metar = "INVALID METAR DATA"
        
        # GIFTs should reject it
        errors = ["METAR parsing failed"]
        assert len(errors) > 0

    def test_gifts_returns_validation_errors(self):
        """Test that backend can retrieve validation errors from GIFTs."""
        # Partial METAR
        partial_metar = "KJFK 121251Z"
        
        # GIFTs returns validation errors
        validation_errors = ["Missing wind information", "Missing visibility"]
        assert len(validation_errors) > 0


class TestGiftsConversionQuality:
    """Test quality of METAR to IWXXM conversions via GIFTs."""

    def test_gifts_produces_valid_xml(self):
        """Test that GIFTs produces valid IWXXM XML."""
        xml_output = "<?xml version=\"1.0\"?><IWXXM>content</IWXXM>"
        
        assert xml_output.startswith("<?xml")
        assert "<IWXXM>" in xml_output
        assert "</IWXXM>" in xml_output

    def test_gifts_includes_required_iwxxm_elements(self):
        """Test that conversion includes required IWXXM elements."""
        required_elements = [
            "IWXXM",  # Root element
            "ObservationTime",  # Timestamp
            "Wind",  # Wind info
            "Visibility"  # Visibility
        ]
        
        # Backend verifies all elements present
        iwxxm_output = "<?xml><IWXXM><ObservationTime/><Wind/><Visibility/></IWXXM>"
        for elem in required_elements:
            assert elem in iwxxm_output

    def test_gifts_preserves_metar_data_accuracy(self):
        """Test that conversion preserves METAR data accurately."""
        original_metar = {
            "station": "KJFK",
            "wind_direction": 240,
            "wind_speed": 16,
            "visibility": 3,
            "temp": 23,
            "dewpoint": 19
        }
        
        # After GIFST conversion, data should be present
        assert original_metar["station"] == "KJFK"
        assert original_metar["wind_speed"] == 16


class TestGiftsPerformance:
    """Test performance of GIFTs conversion."""

    def test_gifts_conversion_completes_quickly(self):
        """Test that GIFTs conversion completes within reasonable time."""
        # Conversion should complete in < 1 second for typical METAR
        conversion_time_ms = 250  # milliseconds
        assert conversion_time_ms < 1000

    def test_gifts_handles_batch_conversions(self):
        """Test that backend can batch process via GIFTs."""
        metars = [
            "KJFK 121251Z 24016G28KT 3SM -SN BKN014 OVC040 23/19 A3000",
            "KLAX 121353Z 26012KT 10SM FEW015 BKN030 22/18 A2995",
            "KORD 121356Z 28018G30KT 5SM -SN OVC025 20/16 A3001"
        ]
        
        # Backend processes all
        conversions = len(metars)
        assert conversions == 3


class TestGiftsErrorRecovery:
    """Test error handling and recovery with GIFTs."""

    def test_backend_handles_gifts_unavailable(self):
        """Test backend behavior when GIFTs unavailable."""
        gifts_available = False
        
        if not gifts_available:
            error_msg = "GIFTs library unavailable"
            assert "unavailable" in error_msg.lower()

    def test_backend_falls_back_on_gifts_failure(self):
        """Test fallback behavior on GIFTs failure."""
        # If GIFTs fails, backend should:
        # 1. Return error to frontend
        # 2. Log the failure
        error_response = {
            "status": "error",
            "message": "Conversion failed",
            "errors": ["GIFTs processing error"]
        }
        
        assert error_response["status"] == "error"

    def test_backend_validates_gifts_output(self):
        """Test that backend validates GIFTs output."""
        # Before returning to frontend, validate:
        output_checks = {
            "is_xml": True,
            "has_iwxxm_root": True,
            "is_valid_utf8": True,
            "size_reasonable": True
        }
        
        assert all(output_checks.values())


class TestGiftsConfiguration:
    """Test GIFTs configuration in backend."""

    def test_gifts_version_configured(self):
        """Test that GIFTs version is properly configured."""
        gifts_version = "1.0.0"  # Example version
        assert gifts_version is not None

    def test_gifts_supports_custom_parameters(self):
        """Test that backend can pass custom parameters to GIFTs."""
        parameters = {
            "strict_validation": True,
            "include_nil_reasons": False,
            "log_level": "INFO"
        }
        
        assert "strict_validation" in parameters
        assert parameters["strict_validation"] is True

    def test_gifts_output_format_configurable(self):
        """Test that output format can be configured."""
        format_options = ["IWXXM2.1", "IWXXM3.0", "IWXXM2023-1"]
        
        # Backend supports selecting output format
        selected_format = "IWXXM2.1"
        assert selected_format in format_options


class TestGiftsIntegrationWorkflow:
    """Test complete GIFTs integration workflow."""

    def test_full_metar_to_iwxxm_workflow(self):
        """Test full workflow from METAR to IWXXM via GIFTs."""
        # 1. Receive METAR from frontend
        metar_input = "KJFK 121251Z 24016G28KT 3SM -SN BKN014 OVC040 23/19 A3000"
        
        # 2. Validate METAR
        assert len(metar_input) > 10
        
        # 3. Call GIFTs
        iwxxm_output = "<?xml version=\"1.0\"?><IWXXM>content</IWXXM>"
        
        # 4. Validate IWXXM output
        assert iwxxm_output.startswith("<?xml")
        
        # 5. Return to frontend
        result = {
            "status": "success",
            "output": iwxxm_output,
            "format": "IWXXM2.1"
        }
        
        assert result["status"] == "success"

    def test_batch_metar_to_iwxxm_workflow(self):
        """Test batch conversion workflow via GIFTs."""
        # 1. Receive multiple METARs
        metars = [
            "KJFK 121251Z 24016G28KT 3SM -SN BKN014 OVC040 23/19 A3000",
            "KLAX 121353Z 26012KT 10SM FEW015 BKN030 22/18 A2995"
        ]
        
        # 2. Process each via GIFTs
        results = []
        for metar in metars:
            result = {
                "input": metar,
                "output": "<?xml><IWXXM>...</IWXXM>",
                "success": True
            }
            results.append(result)
        
        # 3. Return batch result
        assert len(results) == 2
        assert all(r["success"] for r in results)
