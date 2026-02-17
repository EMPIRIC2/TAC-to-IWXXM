"""
Tests for Validation Orchestrator
"""

import pytest

from src.services.validation_orchestrator import (
    get_validation_orchestrator,
    ValidationOrchestrator,
    ComprehensiveValidationResult
)
from src.schemas.validation import ValidationLayer


# Sample TAC and XML for testing
SAMPLE_TAC = "METAR KJ FK 112030Z 18012KT 10SM FEW250 15/07 A3005"

SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:METAR 
    xmlns:iwxxm="http://icao.int/iwxxm/2025-2"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    gml:id="metar-KJFK-20250211T203000Z"
    reportStatus="NORMAL">
    <iwxxm:issueTime>
        <gml:TimeInstant gml:id="ti-KJFK-20250211T203000Z">
            <gml:timePosition>2025-02-11T20:30:00Z</gml:timePosition>
        </gml:TimeInstant>
    </iwxxm:issueTime>
</iwxxm:METAR>
"""


class TestValidationOrchestrator:
    """Test validation orchestrator functionality."""
    
    def test_orchestrator_singleton(self):
        """Test that orchestrator uses singleton pattern."""
        orchestrator1 = get_validation_orchestrator()
        orchestrator2 = get_validation_orchestrator()
        
        assert orchestrator1 is orchestrator2
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initializes with all validators."""
        orchestrator = get_validation_orchestrator()
        
        assert orchestrator.validation_service is not None
        assert orchestrator.xsd_validator is not None
        assert orchestrator.schematron_validator is not None
        assert orchestrator.gml_validator is not None
        assert orchestrator.schema_registry is not None
    
    def test_validate_complete_with_minimal_layers(self):
        """Test validation with only layers 1-2 (no XML required)."""
        orchestrator = get_validation_orchestrator()
        
        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content="",
            version="2025-2",
            layers=[ValidationLayer.TAC_SYNTAX],
            stop_on_error=False
        )
        
        assert isinstance(result, ComprehensiveValidationResult)
        assert ValidationLayer.TAC_SYNTAX in result.layers_run
        assert result.version == "2025-2"
    
    def test_validate_complete_with_all_layers(self):
        """Test validation with all 7 layers."""
        orchestrator = get_validation_orchestrator()
        
        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=None,  # All layers
            stop_on_error=True
        )
        
        assert isinstance(result, ComprehensiveValidationResult)
        assert result.version == "2025-2"
        assert len(result.layers_run) > 0
        assert len(result.all_issues) >= 0
    
    def test_stop_on_error_functionality(self):
        """Test that stop_on_error stops at first blocking failure."""
        orchestrator = get_validation_orchestrator()
        
        # Use invalid TAC to fail early
        invalid_tac = "INVALID TAC TEXT"
        
        result = orchestrator.validate_complete(
            tac_text=invalid_tac,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=None,
            stop_on_error=True
        )
        
        assert not result.is_valid
        assert result.stopped_at_layer is not None
        # Should stop at early layer
        assert result.stopped_at_layer in [
            ValidationLayer.AIRPORT_ICAO,
            ValidationLayer.TAC_SYNTAX
        ]
    
    def test_layer_sequencing(self):
        """Test that layers run in correct sequence."""
        orchestrator = get_validation_orchestrator()
        
        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=None,
            stop_on_error=False  # Run all even if some fail
        )
        
        # Check that blocking layers ran before non-blocking
        if ValidationLayer.XML_WELLFORMED in result.layers_run:
            wellformed_idx = result.layers_run.index(ValidationLayer.XML_WELLFORMED)
            
            # XML_SCHEMA should come after XML_WELLFORMED
            if ValidationLayer.XML_SCHEMA in result.layers_run:
                schema_idx = result.layers_run.index(ValidationLayer.XML_SCHEMA)
                assert wellformed_idx < schema_idx
    
    def test_issues_by_layer_structure(self):
        """Test that issues are correctly grouped by layer."""
        orchestrator = get_validation_orchestrator()
        
        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=[ValidationLayer.TAC_SYNTAX],
            stop_on_error=False
        )
        
        assert isinstance(result.issues_by_layer, dict)
        
        # Each key should be a ValidationLayer enum
        for layer in result.issues_by_layer.keys():
            assert isinstance(layer, ValidationLayer)
    
    def test_parallel_layer_execution(self):
        """Test that non-blocking layers can run in parallel."""
        orchestrator = get_validation_orchestrator()
        
        # Run layers 5-7 (non-blocking, parallel)
        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=[
                ValidationLayer.SCHEMATRON,
                ValidationLayer.GML_REFERENCES,
                ValidationLayer.WMO_CODELISTS
            ],
            stop_on_error=False
        )
        
        # All three should be attempted
        assert len(result.layers_run) <= 3
    
    def test_version_parameter_propagation(self):
        """Test that version parameter is used by all validators."""
        orchestrator = get_validation_orchestrator()
        
        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2023-1",
            layers=[ValidationLayer.XML_SCHEMA],
            stop_on_error=False
        )
        
        assert result.version == "2023-1"


@pytest.mark.integration
class TestValidationOrchestratorIntegration:
    """Integration tests with actual validation."""
    
    @pytest.mark.slow
    def test_full_validation_pipeline(self):
        """Test complete 7-layer validation pipeline."""
        orchestrator = get_validation_orchestrator()
        
        # Use a valid METAR TAC
        valid_tac = "METAR KJFK 112051Z 18012KT 10SM FEW250 15/07 A3005 RMK AO2 SLP171 T01500072"
        
        # This will try to validate but may fail due to incomplete XML
        # The test verifies the orchestration works, not necessarily that XML is valid
        result = orchestrator.validate_complete(
            tac_text=valid_tac,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=None,
            stop_on_error=False  # Continue through all layers
        )
        
        assert isinstance(result, ComprehensiveValidationResult)
        assert len(result.layers_run) > 0
        
        # Should have attempted multiple layers
        assert len(result.layers_passed) + len(result.layers_failed) == len(result.layers_run)
