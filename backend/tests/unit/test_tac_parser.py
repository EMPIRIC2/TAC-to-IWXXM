"""
Tests for TAC message parsing utilities.
"""
from src.utilities.tac_parser import extract_airport_code


class TestExtractAirportCode:
    """Test ICAO airport code extraction from TAC messages."""

    def test_metar_standard(self):
        """Test extraction from standard METAR."""
        tac = "METAR KJFK 131051Z 18012KT 10SM FEW250 23/14 A3012"
        assert extract_airport_code(tac) == "KJFK"

    def test_speci_message(self):
        """Test extraction from SPECI."""
        tac = "SPECI EGLL 111520Z 27015KT 9999 BKN025 15/12 Q1018"
        assert extract_airport_code(tac) == "EGLL"

    def test_lowercase_input(self):
        """Test extraction with lowercase input (should normalize)."""
        tac = "metar kjfk 131051z 18012kt 10sm few250"
        assert extract_airport_code(tac) == "KJFK"

    def test_mixed_case(self):
        """Test extraction with mixed case."""
        tac = "MeTaR EgLl 111520Z 27015KT 9999"
        assert extract_airport_code(tac) == "EGLL"

    def test_extra_whitespace(self):
        """Test extraction with extra whitespace."""
        tac = "METAR  KJFK  131051Z 18012KT"
        assert extract_airport_code(tac) == "KJFK"

    def test_no_keyword(self):
        """Test extraction when METAR/SPECI keyword is missing."""
        tac = "KJFK 131051Z 18012KT 10SM FEW250"
        assert extract_airport_code(tac) is None

    def test_invalid_code_length(self):
        """Test extraction with invalid code length."""
        tac = "METAR ABC 131051Z 18012KT"
        assert extract_airport_code(tac) is None

        tac = "METAR ABCDE 131051Z 18012KT"
        assert extract_airport_code(tac) is None

    def test_empty_string(self):
        """Test extraction from empty string."""
        assert extract_airport_code("") is None

    def test_whitespace_only(self):
        """Test extraction from whitespace."""
        assert extract_airport_code("   \n\t  ") is None

    def test_african_airports(self):
        """Test extraction from African airport codes."""
        tac = "METAR FAJS 131100Z 32015KT CAVOK 15/05 Q1025"
        assert extract_airport_code(tac) == "FAJS"

        tac = "SPECI GOOY 141520Z 27020KT 9999 FEW020"
        assert extract_airport_code(tac) == "GOOY"

    def test_asian_airports(self):
        """Test extraction from Asian airport codes."""
        tac = "METAR RJAA 131630Z 36010KT 9999 FEW025 BKN100 28/21 Q1012"
        assert extract_airport_code(tac) == "RJAA"

        tac = "METAR VHHH 131630Z 22015KT 180V270 9999 FEW020 SCT100 30/24 Q1010"
        assert extract_airport_code(tac) == "VHHH"

    def test_with_cor_or_amendments(self):
        """Test extraction from corrected/amended reports."""
        tac = "METAR COR KJFK 131051Z 18012KT"
        assert extract_airport_code(tac) == "KJFK"

        tac = "SPECI COR EGLL 111520Z 27015KT 9999 BKN025"
        assert extract_airport_code(tac) == "EGLL"

        # Standard format: code comes right after keyword
        tac = "METAR KJFK 131051Z COR 18012KT"
        assert extract_airport_code(tac) == "KJFK"

    def test_with_cor_lowercase_and_whitespace(self):
        """Test extraction from corrected reports with mixed casing and spacing."""
        tac = "  metar   cor   faor 101200Z 12012KT 9999 FEW020 22/14 Q1018"
        assert extract_airport_code(tac) == "FAOR"
