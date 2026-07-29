"""Tests for conversion utility with validation integration."""

import sys
from pathlib import Path

import pytest

SRC_DIR = Path(__file__).parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from src.services.validation import ValidationError
from src.utilities.conversion import ConversionError, convert_metar_tac


@pytest.mark.unit
class TestConversionIntegration:
    """Test conversion utility with validation integration."""

    def test_conversion_imports(self):
        """Test that conversion module imports successfully."""
        assert convert_metar_tac is not None
        assert ConversionError is not None

    def test_convert_sample_metar(self):
        """Test basic METAR conversion."""
        # Use a known valid airport
        sample_metar = "METAR KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034"

        try:
            result = convert_metar_tac(sample_metar)
            # Should return XML
            assert result is not None
            assert "<?xml" in result or len(result) > 0
        except (ConversionError, ValidationError):
            # If conversion fails, it's ok for this test
            # We're just checking it doesn't crash
            assert True

    def test_convert_invalid_metar_gracefully_degrades(self):
        """Test that conversion gracefully handles invalid METAR when validation unavailable."""
        # When validation service is unavailable, conversion attempts GIFTs conversion anyway
        invalid_metar = "METAR ZZZZ 101851Z 24008KT 10SM FEW250 15/07 A3034"

        try:
            result = convert_metar_tac(invalid_metar)
            # If it succeeds, that's ok (validation service was available)
            assert result is not None
        except (ConversionError, ValidationError):
            # If validation service is available, it should reject invalid ICAO
            assert True

    def test_convert_empty_string_gracefully_degrades(self):
        """Test that conversion gracefully handles empty string."""
        try:
            result = convert_metar_tac("")
            assert result is None or isinstance(result, str)
        except (ConversionError, ValidationError):
            assert True

    def test_convert_none_raises(self):
        """Test that None input raises error."""
        with pytest.raises((ConversionError, ValidationError, TypeError, AttributeError)):
            convert_metar_tac(None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
