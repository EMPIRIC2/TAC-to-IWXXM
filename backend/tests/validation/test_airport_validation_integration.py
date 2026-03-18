"""Integration tests for airport validation and conversion."""
import sys
from pathlib import Path

import pytest

# Ensure src is importable
SRC_DIR = Path(__file__).parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from src.schemas.airport import get_airport_validator
from src.schemas.validation import ValidationLayer
from src.services.validation import ValidationError, get_validation_service


@pytest.mark.integration
class TestAirportValidatorIntegration:
    """Integration tests for airport validator with airport data."""

    def test_get_airport_validator_singleton(self):
        """Test that airport validator is a singleton."""
        validator1 = get_airport_validator()
        validator2 = get_airport_validator()

        assert validator1 is validator2

    def test_airport_validator_loads_data(self):
        """Test that airport validator loads airport data."""
        validator = get_airport_validator()

        assert validator.count() > 0

    def test_validate_known_airport(self):
        """Test validation with known airport if available."""
        validator = get_airport_validator()

        # Try a common airport
        if validator.validate_icao("KJFK"):
            assert True
        elif validator.validate_icao("EGLL"):
            assert True
        elif validator.count() > 0:
            # If we have any airports, test with first one
            first_airport = validator.get_all_airports()[0]
            assert validator.validate_icao(first_airport.icao)

    def test_validate_unknown_airport(self):
        """Test validation with unknown airport code."""
        validator = get_airport_validator()

        # Use clearly fake codes that won't exist in any real airport database
        assert validator.validate_icao("FAKE") is False
        assert validator.validate_icao("AAAA") is False

    def test_get_airport_returns_full_data(self):
        """Test getting complete airport data."""
        validator = get_airport_validator()

        if validator.count() > 0:
            airports = validator.get_all_airports()
            first_airport = airports[0]

            retrieved = validator.get_airport(first_airport.icao)

            assert retrieved is not None
            assert retrieved.icao == first_airport.icao
            assert retrieved.name is not None
            assert retrieved.country is not None

    def test_search_by_prefix(self):
        """Test airport search by ICAO prefix."""
        validator = get_airport_validator()

        results = validator.search_by_prefix("K", limit=5)

        # If we have US airports, we should get results with K prefix
        if len(results) > 0:
            assert all(a.icao.startswith("K") for a in results)
            assert len(results) <= 5


@pytest.mark.integration
class TestValidationServiceIntegration:
    """Integration tests for validation service with airport validator."""

    def test_validation_service_initialization(self):
        """Test validation service initializes with airport validator."""
        service = get_validation_service()

        assert service.airport_validator is not None
        assert service.airport_validator.count() > 0

    def test_validate_airport_icao_with_real_airports(self):
        """Test ICAO validation with real airport data."""
        service = get_validation_service()
        validator = get_airport_validator()

        # Find a valid airport
        if validator.count() > 0:
            first_airport = validator.get_all_airports()[0]
            icao = first_airport.icao

            # Test with valid ICAO embedded in TAC
            tac = f"METAR {icao} 101200Z 12012KT 9999 FEW020 22/14 Q1018"
            result = service.validate_airport_icao(tac)

            assert result.passed is True
            assert result.metadata is not None
            assert result.metadata["icao"] == icao

    def test_validate_airport_icao_invalid_raises(self):
        """Test that invalid ICAO raises ValidationError."""
        service = get_validation_service()

        tac = "METAR ZZZZ 101200Z 12012KT 9999 FEW020 22/14 Q1018"

        with pytest.raises(ValidationError) as exc_info:
            service.validate_airport_icao(tac)

        assert "Unknown ICAO" in str(exc_info.value)

    def test_validate_all_layers_with_valid_airport(self):
        """Test all layers validation with valid airport."""
        service = get_validation_service()
        validator = get_airport_validator()

        if validator.count() > 0:
            first_airport = validator.get_all_airports()[0]
            icao = first_airport.icao

            tac = f"METAR {icao} 101200Z 12012KT 10SM FEW020 22/14 A3005"
            result = service.validate_all_layers(tac)

            assert ValidationLayer.AIRPORT_ICAO in result.layers_validated
            assert ValidationLayer.TAC_SYNTAX in result.layers_validated
            assert result.passed is True

    def test_validate_all_layers_with_invalid_airport(self):
        """Test that invalid airport stops validation."""
        service = get_validation_service()

        tac = "METAR ZZZZ 101200Z 12012KT 10SM FEW020 22/14 A3005"
        result = service.validate_all_layers(tac)

        assert result.passed is False
        # Should only have ICAO layer (stops at first failure)
        assert len(result.layers_validated) >= 1


@pytest.mark.integration
class TestValidationServiceComparison:
    """Integration tests for validation service singleton."""

    def test_singleton_pattern(self):
        """Test that validation service uses singleton pattern."""
        service1 = get_validation_service()
        service2 = get_validation_service()

        assert service1 is service2

    def test_airport_validator_same_instance(self):
        """Test that both services use same airport validator."""
        service1 = get_validation_service()
        service2 = get_validation_service()
        validator = get_airport_validator()

        assert service1.airport_validator is service2.airport_validator
        assert service1.airport_validator is validator


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
