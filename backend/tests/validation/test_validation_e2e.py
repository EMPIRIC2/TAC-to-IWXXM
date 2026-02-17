"""E2E tests for complete validation workflows."""
import pytest
from pathlib import Path
import sys

# Ensure src is importable
SRC_DIR = Path(__file__).parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from src.services.validation import get_validation_service, ValidationError
from src.services.evaluation_service import EvaluationService
from src.schemas.airport import get_airport_validator
from src.schemas.validation import ValidationLayer, ValidationLevel


@pytest.mark.e2e
class TestCompleteValidationWorkflow:
    """End-to-end tests for complete validation workflows."""
    
    def test_validation_workflow_with_valid_icao(self):
        """Test complete workflow with valid ICAO."""
        validator = get_airport_validator()
        service = get_validation_service()
        
        if validator.count() > 0:
            # Get first available airport
            first_airport = validator.get_all_airports()[0]
            icao = first_airport.icao
            
            # Step 1: Validate airport ICAO
            tac = f"METAR {icao} 101200Z 12012KT 10SM FEW020 22/14 A3005"
            icao_result = service.validate_airport_icao(tac)
            
            assert icao_result.passed is True
            assert icao_result.layer == ValidationLayer.AIRPORT_ICAO
            
            # Step 2: Validate syntax
            syntax_result = service.validate_tac_syntax(tac)
            
            assert syntax_result.passed is True
            assert syntax_result.layer == ValidationLayer.TAC_SYNTAX
            
            # Step 3: Aggregate results
            aggregated_result = service.validate_all_layers(tac)
            
            assert aggregated_result.passed is True
            assert len(aggregated_result.layers_validated) >= 2
    
    def test_validation_blocked_on_invalid_icao(self):
        """Test that validation is blocked on invalid ICAO."""
        service = get_validation_service()
        
        tac = "METAR ZZZZ 101200Z 12012KT 10SM FEW020 22/14 A3005"
        
        # Try direct validation (should raise)
        with pytest.raises(ValidationError):
            service.validate_airport_icao(tac)
        
        # Try aggregated validation (should fail gracefully)
        aggregated = service.validate_all_layers(tac)
        
        assert aggregated.passed is False
        assert aggregated.total_issues >= 1
    
    def test_evaluation_service_with_xml_comparison(self):
        """Test evaluation service XML comparison workflow."""
        evaluator = EvaluationService()
        
        # Our generated XML
        our_xml = '''<?xml version="1.0"?>
        <METAR>
            <temperature unit="C">15</temperature>
            <dewpoint unit="C">10</dewpoint>
            <wind speed="12" direction="270"/>
        </METAR>'''
        
        # Reference XML (identical structure)
        their_xml = our_xml
        
        # Compare
        result = evaluator.compare_iwxxm(our_xml, their_xml)
        
        assert result.passed is True
        assert result.our_elements == result.their_elements
        assert len(result.missing_elements) == 0
        assert len(result.extra_elements) == 0
    
    def test_validation_with_various_icao_formats(self):
        """Test ICAO extraction and validation with various formats."""
        service = get_validation_service()
        validator = get_airport_validator()
        
        test_cases = []
        
        # Add test cases with available airports
        if validator.count() > 0:
            first = validator.get_all_airports()[0]
            test_cases.extend([
                (f"METAR {first.icao} 101200Z ...", True),  # Standard format
                (f"{first.icao} 101200Z ...", True),  # Without keyword
                (f"SPECI {first.icao} 101200Z ...", True),  # SPECI format
            ])
        
        # Add invalid cases
        test_cases.extend([
            ("METAR ZZZZ 101200Z ...", False),  # Invalid ICAO
            ("METAR ABC 101200Z ...", False),   # Too short
        ])
        
        for tac, should_pass in test_cases:
            if should_pass:
                result = service.validate_airport_icao(tac)
                assert result.passed is True, f"Expected to pass for: {tac}"
            else:
                with pytest.raises(ValidationError):
                    service.validate_airport_icao(tac)
    
    def test_tac_syntax_validation_edge_cases(self):
        """Test TAC syntax validation with edge cases."""
        service = get_validation_service()
        
        test_cases = [
            # Valid
            ("METAR KJFK 101200Z 12012KT 10SM FEW020 22/14 A3005", True),
            ("SPECI KJFK 101200Z 12012KT 10SM FEW020 22/14 A3005", True),
            
            # Invalid
            ("KJFK 101200Z 12012KT 10SM", False),  # No METAR/SPECI
            ("METAR", False),  # Too short
            ("some random text", False),  # No keywords
        ]
        
        for tac, should_be_valid in test_cases:
            result = service.validate_tac_syntax(tac)
            
            if should_be_valid:
                assert result.passed is True, f"Expected valid: {tac}"
            else:
                # For invalid cases, should have errors or warnings
                assert len(result.issues) > 0 or result.passed is False


@pytest.mark.e2e
class TestDataLoadingWorkflow:
    """End-to-end tests for data loading and caching."""
    
    def test_airport_data_loads_once(self):
        """Test that airport data loads only once (singleton)."""
        validator1 = get_airport_validator()
        count1 = validator1.count()
        
        # Second access should use cache
        validator2 = get_airport_validator()
        count2 = validator2.count()
        
        assert count1 == count2
        assert count1 > 0
        assert validator1 is validator2
    
    def test_validation_service_uses_loaded_airports(self):
        """Test that validation service uses pre-loaded airports."""
        validator = get_airport_validator()
        service = get_validation_service()
        
        validator_count = validator.count()
        service_count = service.airport_validator.count()
        
        assert validator_count == service_count
        assert service_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
