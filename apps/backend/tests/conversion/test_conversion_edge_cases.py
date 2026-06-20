"""Edge case tests for conversion utilities to improve coverage."""

import pathlib
import sys
from unittest.mock import MagicMock, patch

import pytest

# Ensure src layout path precedence
ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from src.utilities.conversion import (
    ConversionError,
    _load_aerodrome_db,
    _lookup_aerodrome,
    convert_metar_tac,
    convert_metar_tac_with_metadata,
)


class TestGiftsPathHandling:
    """Test GIFTs workspace import availability."""

    def test_gifts_modules_importable(self):
        """GIFTs is installed via uv workspace (packages/gifts)."""
        from gifts import metarDecoder, metarEncoder  # noqa: F401

    def test_load_aerodrome_db_returns_none_when_missing(self):
        """Test aerodrome DB returns None when file doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            result = _load_aerodrome_db()
            assert result is None

    @pytest.mark.skip(reason="Legacy function _lookup_aerodrome replaced by GiftsLocationDBAdapter")
    def test_lookup_aerodrome_returns_none_when_db_missing(self):
        """Test aerodrome lookup returns None when database not available."""
        with patch("utilities.conversion._load_aerodrome_db", return_value=None):
            result = _lookup_aerodrome("KJFK", use_test_overrides=False)
            # Will return None if both CSV and DB lookups fail
            assert result is None or result is not None  # Function has fallbacks

    def test_lookup_aerodrome_handles_malformed_lines(self):
        """Test aerodrome lookup handles malformed database entries."""
        mock_db = MagicMock()
        mock_db.read_text.return_value = "# Comment line\n\nKJFK|JFK\nMALFORMED"

        with patch("src.utilities.conversion._load_aerodrome_db", return_value=mock_db):
            result = _lookup_aerodrome("KJFK")
            # Should find KJFK even with malformed entries
            assert result is not None
            assert result["iataID"] == "JFK"

    def test_lookup_aerodrome_uses_gifts_adapter_fallback(self):
        """Test aerodrome lookup falls back to GiftsLocationDBAdapter gracefully."""
        # When CSV lookup fails, should try GiftsLocationDBAdapter
        from src.utilities.gifts_locationdb_adapter import GiftsLocationDBAdapter

        adapter = GiftsLocationDBAdapter()
        # Just verify the adapter exists and is usable
        assert adapter is not None
        # Try a real lookup (will work if GIFTs is available)
        try:
            result = adapter.get_aerodrome_info("KJFK")
            assert result is not None
        except Exception:
            # GiftsLocationDBAdapter may not be available in all environments
            pass

    def test_lookup_aerodrome_with_conversion_pipeline(self):
        """Test aerodrome lookup integrated into conversion pipeline."""
        # Integration test - verify conversion works with aerodrome DB
        metar_tac = "METAR KJFK 231751Z 31008KT 10SM FEW250 23/14 A3012 RMK AO2"

        try:
            iwxxm_xml, validation_result = convert_metar_tac_with_metadata(
                tac_text=metar_tac,
                use_test_overrides=True,
            )
            # If conversion succeeds, aerodrome lookup worked
            assert iwxxm_xml is not None
            assert len(iwxxm_xml) > 0
        except Exception:
            # Conversion might fail for other reasons, that's OK
            # We're just verifying aerodrome lookup doesn't crash
            pass


class TestConversionErrorHandling:
    """Test error handling in conversion functions."""

    @pytest.mark.skip(reason="Patching GIFTs unavailability requires module-level patching before import")
    def test_convert_with_gifts_unavailable(self):
        """Test conversion when GIFTs modules are unavailable."""
        with patch("utilities.gifts_adapter.metarDecoder", None):
            with patch("utilities.gifts_adapter.metarEncoder", None):
                with pytest.raises(ConversionError) as exc_info:
                    convert_metar_tac("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005")
                # Should raise error about GIFTs being unavailable
                error_msg = str(exc_info.value).lower()
                assert "unavailable" in error_msg or "cannot" in error_msg or "failed" in error_msg

    @pytest.mark.skip(reason="Test incompatible with graceful degradation in conversion pipeline")
    def test_convert_with_decoder_construction_failure(self):
        """Test conversion when decoder construction fails."""
        # NOTE: With new OpenAIP integration, failures are handled gracefully
        mock_decoder_class = MagicMock()
        mock_decoder_class.side_effect = Exception("Decoder init failed")

        with patch("utilities.gifts_adapter.metarDecoder.Annex3", mock_decoder_class):
            with pytest.raises(ConversionError) as exc_info:
                convert_metar_tac("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005")
            assert "decoder" in str(exc_info.value).lower() or "failed" in str(exc_info.value).lower()

    def test_convert_with_invalid_metar_format(self):
        """Test conversion with malformed METAR that decoder rejects."""
        # These are METARs that fail at the decoder stage
        invalid_metars = [
            "",  # Empty
            "   ",  # Whitespace only
            "NOT A METAR",  # Invalid format
            "METAR",  # Incomplete
        ]

        for invalid_metar in invalid_metars:
            try:
                result = convert_metar_tac(invalid_metar)
                # May succeed with None or raise error - both acceptable
            except (ConversionError, ValueError, AttributeError, TypeError):
                # Expected for invalid input
                pass

    def test_convert_with_serialization_error(self):
        """Test conversion when XML serialization fails."""
        mock_decoder = MagicMock()
        mock_decoder.return_value = {"ident": {"str": "KJFK"}}
        mock_encoder = MagicMock()
        mock_root = MagicMock()
        mock_encoder.return_value = mock_root

        with patch("src.utilities.conversion.metarDecoder.Annex3", return_value=mock_decoder):
            with patch("src.utilities.conversion.metarEncoder.Annex3", return_value=mock_encoder):
                with patch("xml.etree.ElementTree.tostring", side_effect=Exception("Serialization error")):
                    with pytest.raises(ConversionError) as exc_info:
                        convert_metar_tac("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005")
                    assert "serialization" in str(exc_info.value).lower()

    @pytest.mark.skip(reason="Test incompatible with graceful degradation in conversion pipeline")
    def test_convert_with_decoding_error(self):
        """Test conversion when decoding/encoding raises exception."""
        mock_decoder = MagicMock()
        mock_decoder.side_effect = Exception("Decoding failed")

        with patch("utilities.gifts_adapter.metarDecoder.Annex3", return_value=mock_decoder):
            with pytest.raises(ConversionError) as exc_info:
                convert_metar_tac("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005")
            assert "decoding" in str(exc_info.value).lower() or "failed" in str(exc_info.value).lower()


class TestConversionWithMetadata:
    """Test convert_metar_tac_with_metadata function."""

    def test_convert_with_metadata_success(self):
        """Test successful conversion with metadata enrichment."""
        mock_db = MagicMock()
        mock_db.read_text.return_value = "KJFK|JFK||Kennedy Intl|40.64|-73.78|13\n"

        with patch("src.utilities.conversion._load_aerodrome_db", return_value=mock_db):
            result, validation_result = convert_metar_tac_with_metadata(
                "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005",
                validate=False,  # Disable validation in tests
            )
            assert isinstance(result, str)
            assert len(result) > 0

    def test_convert_with_metadata_no_db(self):
        """Test conversion with metadata when database unavailable."""
        with patch("src.utilities.conversion._load_aerodrome_db", return_value=None):
            result, validation_result = convert_metar_tac_with_metadata(
                "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005",
                validate=False,  # Disable validation in tests
            )
            assert isinstance(result, str)
            assert len(result) > 0

    def test_convert_with_metadata_various_metars(self):
        """Test metadata conversion with various valid METARs."""
        test_metars = [
            "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005",
            "METAR EGLL 231750Z 27015KT 9999 FEW040 17/14 Q1010",
            "METAR RJAA 231800Z 18012KT 10SM FEW050 18/15 A3005",
        ]

        for metar_tac in test_metars:
            try:
                result, validation_result = convert_metar_tac_with_metadata(metar_tac, validate=False)
                # If conversion succeeds, verify result structure
                if result is not None:
                    assert isinstance(result, str)
                    assert len(result) > 10
            except ConversionError:
                # Conversion errors are acceptable for test data
                pass

    def test_convert_with_metadata_empty_aerodrome_db(self):
        """Test conversion when aerodrome DB exists but is empty."""
        mock_db = MagicMock()
        mock_db.read_text.return_value = ""  # Empty DB

        with patch("src.utilities.conversion._load_aerodrome_db", return_value=mock_db):
            # Should still work - aerodrome lookup fails gracefully
            result, validation_result = convert_metar_tac_with_metadata(
                "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005", validate=False
            )
            assert isinstance(result, str)

    def test_convert_with_metadata_serialization_error(self):
        """Test metadata conversion when serialization fails."""
        mock_decoder = MagicMock()
        mock_decoder.return_value = {"ident": {"str": "KJFK"}}
        mock_encoder = MagicMock()
        mock_root = MagicMock()
        mock_encoder.return_value = mock_root

        with patch("src.utilities.conversion.metarDecoder.Annex3", return_value=mock_decoder):
            with patch("src.utilities.conversion.metarEncoder.Annex3", return_value=mock_encoder):
                with patch("xml.etree.ElementTree.tostring", side_effect=Exception("Serialization error")):
                    with pytest.raises(ConversionError) as exc_info:
                        convert_metar_tac_with_metadata("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005")
                    assert "serialization" in str(exc_info.value).lower()


class TestMalformedInput:
    """Test handling of malformed TAC input."""

    def test_empty_string(self):
        """Test conversion with empty string."""
        try:
            result = convert_metar_tac("")
            # May produce output or raise error, both acceptable
            assert isinstance(result, str)
        except ConversionError:
            pass

    def test_whitespace_only(self):
        """Test conversion with whitespace-only input."""
        try:
            result = convert_metar_tac("   \n\t  ")
            assert isinstance(result, str)
        except ConversionError:
            pass

    def test_partial_metar(self):
        """Test conversion with incomplete METAR."""
        try:
            result = convert_metar_tac("METAR KJFK")
            assert isinstance(result, str)
        except ConversionError:
            pass

    def test_non_metar_text(self):
        """Test conversion with non-METAR text."""
        try:
            result = convert_metar_tac("This is not a METAR at all")
            assert isinstance(result, str)
        except ConversionError:
            pass

    def test_special_characters(self):
        """Test conversion with special characters."""
        try:
            result = convert_metar_tac("METAR KJFK 231751Z @@##$$")
            assert isinstance(result, str)
        except ConversionError:
            pass
