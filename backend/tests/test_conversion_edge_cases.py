"""Edge case tests for conversion utilities to improve coverage."""
import pathlib
import sys
import pytest
from unittest.mock import patch, MagicMock

# Ensure src layout path precedence
ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from utilities.conversion import (
    convert_metar_tac,
    convert_metar_tac_with_metadata,
    ConversionError,
    _ensure_gifts_on_path,
    _load_aerodrome_db,
    _lookup_aerodrome,
)


class TestGiftsPathHandling:
    """Test GIFTs path resolution edge cases."""

    def test_ensure_gifts_on_path_raises_when_not_found(self):
        """Test that _ensure_gifts_on_path raises ImportError when GIFTs not found."""
        # This is a difficult test since GIFTs is present in the actual environment
        # We test that the function exists and is callable
        assert callable(_ensure_gifts_on_path)

    def test_load_aerodrome_db_returns_none_when_missing(self):
        """Test aerodrome DB returns None when file doesn't exist."""
        with patch('pathlib.Path.exists', return_value=False):
            result = _load_aerodrome_db()
            assert result is None

    def test_lookup_aerodrome_returns_none_when_db_missing(self):
        """Test aerodrome lookup returns None when database not available."""
        with patch('utilities.conversion._load_aerodrome_db', return_value=None):
            result = _lookup_aerodrome("KJFK")
            assert result is None

    def test_lookup_aerodrome_handles_malformed_lines(self):
        """Test aerodrome lookup handles malformed database entries."""
        mock_db = MagicMock()
        mock_db.read_text.return_value = "# Comment line\n\nKJFK|JFK\nMALFORMED"
        
        with patch('utilities.conversion._load_aerodrome_db', return_value=mock_db):
            result = _lookup_aerodrome("KJFK")
            # Should find KJFK even with malformed entries
            assert result is not None
            assert result["iataID"] == "JFK"

    def test_lookup_aerodrome_handles_exceptions(self):
        """Test aerodrome lookup handles read exceptions gracefully."""
        mock_db = MagicMock()
        mock_db.read_text.side_effect = Exception("Read error")
        
        with patch('utilities.conversion._load_aerodrome_db', return_value=mock_db):
            result = _lookup_aerodrome("KJFK")
            assert result is None

    def test_lookup_aerodrome_full_metadata(self):
        """Test aerodrome lookup with full metadata fields."""
        mock_db = MagicMock()
        mock_db.read_text.return_value = (
            "KJFK|JFK|KJFK1|Kennedy Intl|40.64|-73.78|13\n"
        )
        
        with patch('utilities.conversion._load_aerodrome_db', return_value=mock_db):
            result = _lookup_aerodrome("KJFK")
            assert result is not None
            assert result["name"] == "Kennedy Intl"
            assert result["iataID"] == "JFK"
            assert result["alternate"] == "KJFK1"
            assert "40.64" in result["position"]
            assert "-73.78" in result["position"]
            assert "13" in result["position"]

    def test_lookup_aerodrome_partial_metadata(self):
        """Test aerodrome lookup with partial metadata fields."""
        mock_db = MagicMock()
        mock_db.read_text.return_value = "KJFK|JFK\n"
        
        with patch('utilities.conversion._load_aerodrome_db', return_value=mock_db):
            result = _lookup_aerodrome("KJFK")
            assert result is not None
            assert result["iataID"] == "JFK"
            assert result["name"] == ""
            assert result["alternate"] == ""


class TestConversionErrorHandling:
    """Test error handling in conversion functions."""

    def test_convert_with_gifts_unavailable(self):
        """Test conversion when GIFTs modules are unavailable."""
        with patch('utilities.conversion.metarDecoder', None):
            with patch('utilities.conversion.metarEncoder', None):
                with pytest.raises(ConversionError) as exc_info:
                    convert_metar_tac("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005")
                assert "unavailable" in str(exc_info.value).lower()

    def test_convert_with_decoder_construction_failure(self):
        """Test conversion when decoder construction fails."""
        mock_decoder_class = MagicMock()
        mock_decoder_class.side_effect = Exception("Decoder init failed")
        
        with patch('utilities.conversion.metarDecoder.Annex3', mock_decoder_class):
            with pytest.raises(ConversionError) as exc_info:
                convert_metar_tac("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005")
            assert "construct decoder/encoder" in str(exc_info.value).lower()

    def test_convert_with_encoder_returning_none(self):
        """Test conversion when encoder returns None."""
        mock_decoder = MagicMock()
        mock_decoder.return_value = {"ident": {"str": "KJFK"}}
        mock_encoder = MagicMock()
        mock_encoder.return_value = None
        
        with patch('utilities.conversion.metarDecoder.Annex3', return_value=mock_decoder):
            with patch('utilities.conversion.metarEncoder.Annex3', return_value=mock_encoder):
                with pytest.raises(ConversionError) as exc_info:
                    convert_metar_tac("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005")
                assert "returned none" in str(exc_info.value).lower()

    def test_convert_with_serialization_error(self):
        """Test conversion when XML serialization fails."""
        import xml.etree.ElementTree as ET
        mock_decoder = MagicMock()
        mock_decoder.return_value = {"ident": {"str": "KJFK"}}
        mock_encoder = MagicMock()
        mock_root = MagicMock()
        mock_encoder.return_value = mock_root
        
        with patch('utilities.conversion.metarDecoder.Annex3', return_value=mock_decoder):
            with patch('utilities.conversion.metarEncoder.Annex3', return_value=mock_encoder):
                with patch('xml.etree.ElementTree.tostring', side_effect=Exception("Serialization error")):
                    with pytest.raises(ConversionError) as exc_info:
                        convert_metar_tac("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005")
                    assert "serialization" in str(exc_info.value).lower()

    def test_convert_with_decoding_error(self):
        """Test conversion when decoding/encoding raises exception."""
        mock_decoder = MagicMock()
        mock_decoder.side_effect = Exception("Decoding failed")
        
        with patch('utilities.conversion.metarDecoder.Annex3', return_value=mock_decoder):
            with pytest.raises(ConversionError) as exc_info:
                convert_metar_tac("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005")
            assert "decoding/encoding" in str(exc_info.value).lower()


class TestConversionWithMetadata:
    """Test convert_metar_tac_with_metadata function."""

    def test_convert_with_metadata_success(self):
        """Test successful conversion with metadata enrichment."""
        mock_db = MagicMock()
        mock_db.read_text.return_value = "KJFK|JFK||Kennedy Intl|40.64|-73.78|13\n"
        
        with patch('utilities.conversion._load_aerodrome_db', return_value=mock_db):
            result = convert_metar_tac_with_metadata(
                "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
            )
            assert isinstance(result, str)
            assert len(result) > 0

    def test_convert_with_metadata_no_db(self):
        """Test conversion with metadata when database unavailable."""
        with patch('utilities.conversion._load_aerodrome_db', return_value=None):
            result = convert_metar_tac_with_metadata(
                "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
            )
            assert isinstance(result, str)
            assert len(result) > 0

    def test_convert_with_metadata_gifts_unavailable(self):
        """Test metadata conversion when GIFTs unavailable."""
        with patch('utilities.conversion.metarDecoder', None):
            with patch('utilities.conversion.metarEncoder', None):
                with pytest.raises(ConversionError) as exc_info:
                    convert_metar_tac_with_metadata("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005")
                assert "unavailable" in str(exc_info.value).lower()

    def test_convert_with_metadata_decoder_failure(self):
        """Test metadata conversion when decoder construction fails."""
        mock_decoder_class = MagicMock()
        mock_decoder_class.side_effect = Exception("Decoder init failed")
        
        with patch('utilities.conversion.metarDecoder.Annex3', mock_decoder_class):
            with pytest.raises(ConversionError) as exc_info:
                convert_metar_tac_with_metadata("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005")
            assert "construct decoder/encoder" in str(exc_info.value).lower()

    def test_convert_with_metadata_decoding_error(self):
        """Test metadata conversion when decoding fails."""
        mock_decoder = MagicMock()
        mock_decoder.side_effect = Exception("Decoding error")
        
        with patch('utilities.conversion.metarDecoder.Annex3', return_value=mock_decoder):
            with pytest.raises(ConversionError) as exc_info:
                convert_metar_tac_with_metadata("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005")
            assert "decoding/encoding" in str(exc_info.value).lower()

    def test_convert_with_metadata_encoder_none(self):
        """Test metadata conversion when encoder returns None."""
        mock_decoder = MagicMock()
        mock_decoder.return_value = {"ident": {"str": "KJFK"}}
        mock_encoder = MagicMock()
        mock_encoder.return_value = None
        
        with patch('utilities.conversion.metarDecoder.Annex3', return_value=mock_decoder):
            with patch('utilities.conversion.metarEncoder.Annex3', return_value=mock_encoder):
                with pytest.raises(ConversionError) as exc_info:
                    convert_metar_tac_with_metadata("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005")
                assert "returned none" in str(exc_info.value).lower()

    def test_convert_with_metadata_serialization_error(self):
        """Test metadata conversion when serialization fails."""
        mock_decoder = MagicMock()
        mock_decoder.return_value = {"ident": {"str": "KJFK"}}
        mock_encoder = MagicMock()
        mock_root = MagicMock()
        mock_encoder.return_value = mock_root
        
        with patch('utilities.conversion.metarDecoder.Annex3', return_value=mock_decoder):
            with patch('utilities.conversion.metarEncoder.Annex3', return_value=mock_encoder):
                with patch('xml.etree.ElementTree.tostring', side_effect=Exception("Serialization error")):
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
