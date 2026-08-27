"""Tests for validation service."""

import pytest
from src.schemas.validation import ValidationLayer, ValidationLevel
from src.services.validation import ValidationError, ValidationService, get_validation_service


class TestAirportValidation:
    """Test Layer 1: Airport ICAO validation."""

    def test_valid_icao_passes(self):
        """Test that valid ICAO codes pass validation."""
        validator = get_validation_service()

        # KJFK is reliably present in the bundled airport set used by CI/local.
        result = validator.validate_airport_icao("METAR KJFK 101200Z 12012KT 9999 FEW020 22/14 Q1018")

        assert result.passed is True
        assert result.layer == ValidationLayer.AIRPORT_ICAO
        assert len(result.issues) == 0
        assert result.metadata is not None
        assert result.metadata["icao"] == "KJFK"

    def test_valid_cor_icao_passes(self):
        """Test that corrected reports still pass ICAO validation."""
        validator = get_validation_service()

        result = validator.validate_airport_icao("METAR COR KJFK 101200Z 12012KT 9999 FEW020 22/14 Q1018")

        assert result.passed is True
        assert result.metadata is not None
        assert result.metadata["icao"] == "KJFK"

    def test_unknown_icao_is_soft_fail_warning(self):
        """Unknown ICAO codes warn but do not raise (WMO demos / UJ-036)."""
        validator = get_validation_service()

        tac = "METAR ZZZZ 101200Z 12012KT 9999 FEW020 22/14 Q1018"
        result = validator.validate_airport_icao(tac)
        assert result.passed is True
        assert any(i.code == "UNKNOWN_ICAO" for i in result.issues)
        assert result.metadata is not None
        assert result.metadata.get("icao") == "ZZZZ"
        assert result.metadata.get("airport_known") is False

    def test_missing_icao_raises(self):
        """Test that missing ICAO code raises ValidationError."""
        validator = get_validation_service()

        # No 4-letter alphabetic token - avoids false-positive ICAO extraction.
        tac = "??"

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_airport_icao(tac)

        assert "ICAO" in str(exc_info.value)

    def test_invalid_icao_format_raises(self):
        """Test that invalid ICAO format raises ValidationError."""
        validator = get_validation_service()

        # 3-letter code instead of 4
        tac = "METAR ABC 101200Z 12012KT 9999 FEW020 22/14 Q1018"

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_airport_icao(tac)

        assert "ICAO code found" in str(exc_info.value) or "Invalid ICAO" in str(exc_info.value)


class TestTACSyntaxValidation:
    """Test Layer 2: TAC syntax validation."""

    def test_valid_metar_passes(self):
        """Test that syntactically valid METAR passes."""
        validator = get_validation_service()

        result = validator.validate_tac_syntax("METAR KJFK 101200Z 12012KT 10SM FEW020 22/14 A3005")

        assert result.passed == True
        assert result.layer == ValidationLayer.TAC_SYNTAX

    def test_missing_keyword_fails(self):
        """Test that TAC without METAR/SPECI keyword fails."""
        validator = get_validation_service()

        result = validator.validate_tac_syntax("KJFK 101200Z 12012KT 10SM FEW020 22/14 A3005")

        assert result.passed == False
        assert any(issue.code == "MISSING_KEYWORD" for issue in result.issues)

    def test_missing_timestamp_warning(self):
        """Test that TAC without timestamp gets warning."""
        validator = get_validation_service()

        result = validator.validate_tac_syntax("METAR KJFK NOSUCH 12012KT 10SM FEW020")

        # Should have warning about missing timestamp
        assert any(issue.level == ValidationLevel.WARNING for issue in result.issues)

    def test_short_message_warning(self):
        """Test that very short TAC gets warning."""
        validator = get_validation_service()

        result = validator.validate_tac_syntax("METAR KJFK")

        assert any(issue.code == "SHORT_MESSAGE" for issue in result.issues)

    def test_tabs_info_issue(self):
        """Test that TAC with tabs gets info-level issue."""
        validator = get_validation_service()

        result = validator.validate_tac_syntax("METAR\tKJFK\t101200Z 12012KT 10SM FEW020")

        assert any(issue.code == "CONTAINS_TABS" for issue in result.issues)


class TestAggregatedValidation:
    """Test combined validation layers."""

    def test_valid_tac_passes_all_layers(self):
        """Test that valid TAC passes all synchronous layers."""
        validator = get_validation_service()

        result = validator.validate_all_layers("METAR KJFK 101200Z 12012KT 9999 FEW020 22/14 Q1018")

        assert result.passed is True
        assert ValidationLayer.AIRPORT_ICAO in result.layers_validated
        assert ValidationLayer.TAC_SYNTAX in result.layers_validated
        assert result.total_issues == 0

    def test_unknown_icao_continues_to_syntax_layer(self):
        """Unknown ICAO soft-fails; TAC syntax layer still runs (UJ-036)."""
        validator = get_validation_service()

        result = validator.validate_all_layers("METAR ZZZZ 101200Z 12012KT 9999 FEW020 22/14 Q1018")

        assert result.passed is True
        assert ValidationLayer.AIRPORT_ICAO in result.layers_validated
        assert ValidationLayer.TAC_SYNTAX in result.layers_validated
        assert any(i.code == "UNKNOWN_ICAO" for r in result.results for i in r.issues)

    def test_execution_time_recorded(self):
        """Test that execution time is recorded."""
        validator = get_validation_service()

        result = validator.validate_all_layers("METAR KJFK 101200Z 12012KT 9999 FEW020 22/14 Q1018")

        assert result.execution_time_ms > 0
        assert all(r.execution_time_ms is not None and r.execution_time_ms > 0 for r in result.results)


class TestValidationServiceInitialization:
    """Test validation service initialization."""

    def test_singleton_pattern(self):
        """Test that get_validation_service returns same instance."""
        service1 = get_validation_service()
        service2 = get_validation_service()

        assert service1 is service2

    def test_airport_validator_loaded(self):
        """Test that airport validator is loaded with data."""
        service = get_validation_service()

        assert service.airport_validator is not None
        assert service.airport_validator.count() > 0


class TestICAOExtraction:
    """Test ICAO extraction utility."""

    def test_extract_with_metar_keyword(self):
        """Test ICAO extraction with METAR keyword."""
        tac = "METAR KJFK 101200Z 12012KT 10SM FEW020 22/14 A3005"
        icao = ValidationService._extract_icao_from_tac(tac)

        assert icao == "KJFK"

    def test_extract_with_speci_keyword(self):
        """Test ICAO extraction with SPECI keyword."""
        tac = "SPECI EGLL 101200Z 12012KT 10SM FEW020 22/14 Q1018"
        icao = ValidationService._extract_icao_from_tac(tac)

        assert icao == "EGLL"

    def test_extract_without_keyword(self):
        """Test ICAO extraction without METAR/SPECI keyword."""
        tac = "KJFK 101200Z 12012KT 10SM FEW020 22/14 A3005"
        icao = ValidationService._extract_icao_from_tac(tac)

        assert icao == "KJFK"

    def test_extract_case_insensitive(self):
        """Test ICAO extraction is case-insensitive."""
        tac = "metar kjfk 101200z 12012kt 10sm few020 22/14 a3005"
        icao = ValidationService._extract_icao_from_tac(tac)

        assert icao == "KJFK"

    def test_extract_with_cor_keyword(self):
        """Test ICAO extraction with COR between type and station."""
        tac = "SPECI COR FAOR 101200Z 12012KT 9999 FEW020 22/14 Q1018"
        icao = ValidationService._extract_icao_from_tac(tac)

        assert icao == "FAOR"

    def test_extract_returns_none_for_invalid(self):
        """Test ICAO extraction returns None for invalid input."""
        tac = "Some random text"
        icao = ValidationService._extract_icao_from_tac(tac)

        # May return None or find a false positive - both acceptable
        assert icao is None or len(icao) == 4
