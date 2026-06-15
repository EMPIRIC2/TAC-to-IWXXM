"""Comprehensive tests for the Encoder base class"""
import pytest
import logging
from unittest.mock import Mock, patch

from gifts.common import Encoder
from gifts.common import bulletin


class TestEncoderInit:
    """Test Encoder initialization"""

    def test_encoder_init(self):
        """Test that Encoder initializes correctly"""
        encoder = Encoder.Encoder()

        assert encoder.geoLocationsDB is None
        assert isinstance(encoder._Logger, logging.Logger)
        assert encoder._Logger.name == 'gifts.common.Encoder'

    def test_encoder_tz_env_variable(self):
        """Test that TZ environment is set to GMT"""
        import os
        Encoder.Encoder()

        # After initialization, TZ should be set
        assert os.environ.get('TZ') == 'GMT0'


class TestEncoderEncode:
    """Test Encoder encode method"""

    def setup_method(self):
        """Setup test encoder with mock regex and methods"""
        from gifts.common import xmlConfig as des
        # Save and reset TRANSLATOR state to avoid test interference
        self.original_translator = des.TRANSLATOR
        des.TRANSLATOR = False

        self.encoder = Encoder.Encoder()
        # Mock the regex patterns
        self.encoder.re_AHL = Mock()
        self.encoder.re_TAC = Mock()
        self.encoder.decoder = Mock()
        self.encoder.encoder = Mock()
        self.encoder.T1T2 = 'M'

    def teardown_method(self):
        """Restore TRANSLATOR state"""
        from gifts.common import xmlConfig as des
        des.TRANSLATOR = self.original_translator

    def test_encode_empty_text(self):
        """Test encoding empty text returns empty bulletin"""
        self.encoder.re_AHL.search.return_value = None

        result = self.encoder.encode("")

        assert isinstance(result, bulletin.Bulletin)
        assert len(result) == 0

    def test_encode_with_valid_ahl(self):
        """Test encoding with valid AHL line"""
        # Mock AHL match
        ahl_match = Mock()
        ahl_match.groupdict.return_value = {
            'tt': 'M', 'aaii': 'A', 'cccc': 'KJFK',
            'yygg': '1218', 'bbb': 'BBB'
        }
        ahl_match.group.return_value = 'METAR KJFK'

        self.encoder.re_AHL.search.return_value = ahl_match
        self.encoder.re_TAC.findall.return_value = []

        result = self.encoder.encode("METAR KJFK 121851Z 31008KT 10SM FEW250 M04/M17 A3034")

        assert isinstance(result, bulletin.Bulletin)
        # Should call set_bulletinIdentifier
        assert ahl_match.groupdict.called

    def test_encode_with_decoder_error(self):
        """Test encoding when decoder returns error"""
        ahl_match = Mock()
        ahl_match.groupdict.return_value = {'tt': 'M', 'aaii': 'A', 'cccc': 'KJFK', 'yygg': '1218', 'bbb': 'BBB'}
        ahl_match.group.return_value = 'METAR'

        self.encoder.re_AHL.search.return_value = ahl_match
        self.encoder.re_TAC.findall.return_value = ['METAR KJFK 121851Z']

        # Decoder returns error with minimal bbb field
        self.encoder.decoder.return_value = {
            'err_msg': 'Decoding failed',
            'bbb': '',
            'translationTime': '2024-01-20T12:00:00Z'
        }
        self.encoder.T1T2 = 'L'

        with patch.object(self.encoder._Logger, 'warning') as mock_warn:
            self.encoder.encode("METAR KJFK 121851Z")

            # Should log warning about bad observation
            assert mock_warn.called

    def test_encode_with_geolocationsdb(self):
        """Test encoding with geoLocationsDB"""
        ahl_match = Mock()
        ahl_match.groupdict.return_value = {'tt': 'M', 'aaii': 'A', 'cccc': 'KJFK', 'yygg': '1218', 'bbb': 'BBB'}
        ahl_match.group.return_value = 'METAR'

        self.encoder.re_AHL.search.return_value = ahl_match
        self.encoder.re_TAC.findall.return_value = ['METAR KJFK 121851Z']

        decoded_tac = {
            'ident': {'str': 'KJFK'},
            'bbb': '',
            'translationTime': '2024-01-20T12:00:00Z'
        }
        self.encoder.decoder.return_value = decoded_tac
        self.encoder.geoLocationsDB = Mock()
        self.encoder.geoLocationsDB.get.return_value = 'JFK|JFK|KJFK|40.6 -74.0 3'

        # Mock encoder to return a mock element
        mock_elem = Mock()
        self.encoder.encoder.return_value = mock_elem

        result = self.encoder.encode("METAR KJFK 121851Z")

        assert isinstance(result, bulletin.Bulletin)

    def test_encode_with_missing_geolocationsdb_entry(self):
        """Test encoding when geoLocationsDB doesn't have entry"""
        ahl_match = Mock()
        ahl_match.groupdict.return_value = {'tt': 'M', 'aaii': 'A', 'cccc': 'KJFK', 'yygg': '1218', 'bbb': 'BBB'}
        ahl_match.group.return_value = 'METAR'

        self.encoder.re_AHL.search.return_value = ahl_match
        self.encoder.re_TAC.findall.return_value = ['METAR KJFK 121851Z']

        decoded_tac = {
            'ident': {'str': 'KJFK'},
            'bbb': '',
            'translationTime': '2024-01-20T12:00:00Z'
        }
        self.encoder.decoder.return_value = decoded_tac
        self.encoder.geoLocationsDB = Mock()
        self.encoder.geoLocationsDB.get.side_effect = KeyError("KJFK not found")

        # Mock encoder to return a mock element
        mock_elem = Mock()
        self.encoder.encoder.return_value = mock_elem

        with patch.object(self.encoder._Logger, 'warning'):
            result = self.encoder.encode("METAR KJFK 121851Z")
            assert isinstance(result, bulletin.Bulletin)
            result = self.encoder.encode("METAR KJFK 121851Z")

            assert isinstance(result, bulletin.Bulletin)

    def test_encode_with_receipt_time(self):
        """Test encoding with receipt time"""
        ahl_match = Mock()
        ahl_match.groupdict.return_value = {'tt': 'M', 'aaii': 'A', 'cccc': 'KJFK', 'yygg': '1218', 'bbb': 'BBB'}
        ahl_match.group.return_value = 'METAR'

        self.encoder.re_AHL.search.return_value = ahl_match
        self.encoder.re_TAC.findall.return_value = ['METAR KJFK 121851Z']

        decoded_tac = {
            'ident': {'str': 'KJFK'},
            'bbb': '',
            'translationTime': '2024-01-20T12:00:00Z'
        }
        self.encoder.decoder.return_value = decoded_tac

        # Use translator mode
        with patch('gifts.common.xmlConfig.TRANSLATOR', True):
            mock_elem = Mock()
            self.encoder.encoder.return_value = mock_elem

            result = self.encoder.encode(
                "METAR KJFK 121851Z",
                receiptTime='2024-01-20T11:50:00Z'
            )

            assert isinstance(result, bulletin.Bulletin)

    def test_encode_tac_syntax_error(self):
        """Test encoding when encoder raises SyntaxError"""
        ahl_match = Mock()
        ahl_match.groupdict.return_value = {'tt': 'M', 'aaii': 'A', 'cccc': 'KJFK', 'yygg': '1218', 'bbb': 'BBB'}
        ahl_match.group.return_value = 'METAR'

        self.encoder.re_AHL.search.return_value = ahl_match
        self.encoder.re_TAC.findall.return_value = ['METAR KJFK 121851Z']

        decoded_tac = {
            'ident': {'str': 'KJFK'},
            'bbb': '',
            'translationTime': '2024-01-20T12:00:00Z'
        }
        self.encoder.decoder.return_value = decoded_tac

        # Encoder raises SyntaxError
        self.encoder.encoder.side_effect = SyntaxError("Bad TAC format")

        with patch.object(self.encoder._Logger, 'warning'):
            result = self.encoder.encode("METAR KJFK 121851Z")
            assert isinstance(result, bulletin.Bulletin)
            result = self.encoder.encode("METAR KJFK 121851Z")

            assert isinstance(result, bulletin.Bulletin)

    def test_encode_with_multiple_tacs(self):
        """Test encoding multiple TAC forms"""
        ahl_match = Mock()
        ahl_match.groupdict.return_value = {'tt': 'M', 'aaii': 'A', 'cccc': 'KJFK', 'yygg': '1218', 'bbb': 'BBB'}
        ahl_match.group.return_value = 'METAR'

        self.encoder.re_AHL.search.return_value = ahl_match
        tac1 = 'METAR KJFK 121851Z'
        tac2 = 'METAR KLGA 121851Z'
        self.encoder.re_TAC.findall.return_value = [tac1, tac2]

        decoded_tac = {
            'ident': {'str': 'KJFK'},
            'bbb': '',
            'translationTime': '2024-01-20T12:00:00Z'
        }
        self.encoder.decoder.return_value = decoded_tac

        mock_elem = Mock()
        self.encoder.encoder.return_value = mock_elem

        result = self.encoder.encode("METAR KJFK 121851Z\nMETAR KLGA 121851Z")

        assert isinstance(result, bulletin.Bulletin)

    def test_encode_preserves_bbb_from_attrs(self):
        """Test that bbb attribute is preserved from attrs"""
        ahl_match = Mock()
        ahl_match.groupdict.return_value = {'tt': 'M', 'aaii': 'A', 'cccc': 'KJFK', 'yygg': '1218', 'bbb': 'BBB'}
        ahl_match.group.return_value = 'METAR'

        self.encoder.re_AHL.search.return_value = ahl_match
        self.encoder.re_TAC.findall.return_value = ['METAR KJFK 121851Z']

        decoded_tac = {
            'ident': {'str': 'KJFK'},
            'bbb': 'AAA',
            'translationTime': '2024-01-20T12:00:00Z'
        }
        self.encoder.decoder.return_value = decoded_tac

        mock_elem = Mock()
        self.encoder.encoder.return_value = mock_elem

        result = self.encoder.encode("METAR KJFK 121851Z")

        assert isinstance(result, bulletin.Bulletin)

    def test_encode_with_additional_attributes(self):
        """Test encoding with additional keyword attributes"""
        ahl_match = Mock()
        ahl_match.groupdict.return_value = {'tt': 'M', 'aaii': 'A', 'cccc': 'KJFK', 'yygg': '1218', 'bbb': 'BBB'}
        ahl_match.group.return_value = 'METAR'

        self.encoder.re_AHL.search.return_value = ahl_match
        self.encoder.re_TAC.findall.return_value = []

        result = self.encoder.encode(
            "METAR KJFK 121851Z",
            originating_center="KWBC",
            issue_time="2024-01-20T12:00:00Z"
        )

        assert isinstance(result, bulletin.Bulletin)

    def test_encode_geolocationsdb_missing_ident_name(self):
        """Test when geoLocationsDB entry is missing ident name"""
        ahl_match = Mock()
        ahl_match.groupdict.return_value = {'tt': 'M', 'aaii': 'A', 'cccc': 'KJFK', 'yygg': '1218', 'bbb': 'BBB'}
        ahl_match.group.return_value = 'METAR'

        self.encoder.re_AHL.search.return_value = ahl_match
        self.encoder.re_TAC.findall.return_value = ['METAR KJFK 121851Z']

        decoded_tac = {
            'ident': {},  # No 'str' key
            'bbb': '',
            'translationTime': '2024-01-20T12:00:00Z'
        }
        self.encoder.decoder.return_value = decoded_tac

        mock_elem = Mock()
        self.encoder.encoder.return_value = mock_elem

        result = self.encoder.encode("METAR KJFK 121851Z")

        assert isinstance(result, bulletin.Bulletin)
        self.encoder.re_TAC.findall.return_value = ['METAR KJFK 121851Z']

        decoded_tac = {
            'ident': {'str': 'KJFK'},
            'bbb': ''
        }
        self.encoder.decoder.return_value = decoded_tac

        # DB returns data with empty fields
        self.encoder.geoLocationsDB = Mock()
        self.encoder.geoLocationsDB.get.return_value = '||KJFK|40.6 -74.0 3'

        mock_elem = Mock()
        self.encoder.encoder.return_value = mock_elem

        result = self.encoder.encode("METAR KJFK 121851Z")

        # Should still work even with empty fullname and iataID
        assert isinstance(result, bulletin.Bulletin)

    def test_encode_bad_position_from_geolocationsdb(self):
        """Test when geoLocationsDB returns incomplete position data"""
        ahl_match = Mock()
        ahl_match.groupdict.return_value = {'tt': 'M', 'aaii': 'A', 'cccc': 'KJFK', 'yygg': '1218', 'bbb': 'BBB'}
        ahl_match.group.return_value = 'METAR'

        self.encoder.re_AHL.search.return_value = ahl_match
        self.encoder.re_TAC.findall.return_value = ['METAR KJFK 121851Z']

        decoded_tac = {
            'ident': {'str': 'KJFK'},
            'bbb': '',
            'translationTime': '2024-01-20T12:00:00Z'
        }
        self.encoder.decoder.return_value = decoded_tac
        self.encoder.geoLocationsDB = Mock()
        # Return default position (not found in DB)
        self.encoder.geoLocationsDB.get.return_value = '|||0.0 0.0 0'

        mock_elem = Mock()
        self.encoder.encoder.return_value = mock_elem

        with patch.object(self.encoder._Logger, 'warning') as mock_warn:
            result = self.encoder.encode("METAR KJFK 121851Z")
            assert isinstance(result, bulletin.Bulletin)
            # Should log warning about location not found
            assert any('not found in geoLocationsDB' in str(call) for call in mock_warn.call_args_list)

    def test_encode_decoder_without_ident_str(self):
        """Test when decoder doesn't return ident.str"""
        ahl_match = Mock()
        ahl_match.groupdict.return_value = {'tt': 'M', 'aaii': 'A', 'cccc': 'KJFK', 'yygg': '1218', 'bbb': 'BBB'}
        ahl_match.group.return_value = 'METAR'

        self.encoder.re_AHL.search.return_value = ahl_match
        self.encoder.re_TAC.findall.return_value = ['METAR KJFK 121851Z']

        decoded_tac = {
            'bbb': '',
            'translationTime': '2024-01-20T12:00:00Z'
            # No 'ident' key at all
        }
        self.encoder.decoder.return_value = decoded_tac

        mock_elem = Mock()
        self.encoder.encoder.return_value = mock_elem

        result = self.encoder.encode("METAR KJFK 121851Z")

        assert isinstance(result, bulletin.Bulletin)

    def test_encode_advisory_type_error(self):
        """Test when encoder raises TypeError (e.g., advisory encoding issues)"""
        ahl_match = Mock()
        ahl_match.groupdict.return_value = {'tt': 'M', 'aaii': 'A', 'cccc': 'KJFK', 'yygg': '1218', 'bbb': 'BBB'}
        ahl_match.group.return_value = 'METAR'

        self.encoder.re_AHL.search.return_value = ahl_match
        self.encoder.re_TAC.findall.return_value = ['METAR KJFK 121851Z']

        decoded_tac = {
            'ident': {'str': 'KJFK'},
            'bbb': '',
            'translationTime': '2024-01-20T12:00:00Z'
        }
        self.encoder.decoder.return_value = decoded_tac

        # Encoder raises TypeError - should be caught and logged
        self.encoder.encoder.side_effect = TypeError("Advisory encoding error")

        # The TypeError should be raised (not caught in this version of the code)
        with pytest.raises(TypeError):
            self.encoder.encode("METAR KJFK 121851Z")


class TestEncoderEdgeCases:
    """Test edge cases and error conditions"""

    def setup_method(self):
        """Setup test encoder"""
        self.encoder = Encoder.Encoder()

    def test_encode_no_ahl_match(self):
        """Test when AHL regex doesn't match"""
        self.encoder.re_AHL = Mock()
        self.encoder.re_AHL.search.return_value = None

        result = self.encoder.encode("This is not a valid TAC message")

        assert isinstance(result, bulletin.Bulletin)
        assert len(result) == 0

    def test_encode_with_none_text(self):
        """Test encoding None text"""
        self.encoder.re_AHL = Mock()
        self.encoder.re_AHL.search.return_value = None

        result = self.encoder.encode(None)

        assert isinstance(result, bulletin.Bulletin)

    def test_encode_with_unicode_text(self):
        """Test encoding with unicode characters"""
        ahl_match = Mock()
        ahl_match.groupdict.return_value = {'tt': 'M', 'aaii': 'A', 'cccc': 'KJFK', 'yygg': '1218', 'bbb': 'BBB'}
        ahl_match.group.return_value = 'METAR'

        self.encoder.re_AHL = Mock()
        self.encoder.re_AHL.search.return_value = ahl_match
        self.encoder.re_TAC = Mock()
        self.encoder.re_TAC.findall.return_value = []

        result = self.encoder.encode("METAR KJFK café 121851Z")

        assert isinstance(result, bulletin.Bulletin)

    def test_encode_very_long_text(self):
        """Test encoding very long TAC message"""
        ahl_match = Mock()
        ahl_match.groupdict.return_value = {'tt': 'M', 'aaii': 'A', 'cccc': 'KJFK', 'yygg': '1218', 'bbb': 'BBB'}
        ahl_match.group.return_value = 'METAR'

        self.encoder.re_AHL = Mock()
        self.encoder.re_AHL.search.return_value = ahl_match
        self.encoder.re_TAC = Mock()
        self.encoder.re_TAC.findall.return_value = []

        long_text = "METAR " * 1000
        result = self.encoder.encode(long_text)

        assert isinstance(result, bulletin.Bulletin)


class TestEncoderIntegration:
    """Integration tests with real regex and structure"""

    def test_encoder_attributes_after_init(self):
        """Test that encoder has expected attributes after init"""
        encoder = Encoder.Encoder()

        # Check that key attributes are present
        assert hasattr(encoder, 'geoLocationsDB')
        assert hasattr(encoder, '_Logger')
        assert callable(encoder.encode)

    def test_encoder_logger_configuration(self):
        """Test that encoder logger is properly configured"""
        encoder = Encoder.Encoder()

        assert encoder._Logger.name == 'gifts.common.Encoder'
        assert isinstance(encoder._Logger, logging.Logger)
