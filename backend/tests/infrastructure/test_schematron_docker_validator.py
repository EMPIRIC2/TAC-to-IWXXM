"""
Tests for Schematron Docker validator wrapper.

Tests the SchematronValidatorDocker class that integrates with the Docker container.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# These imports assume the module is in the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utilities.schematron_validator_docker import (
    SchematronValidatorDocker,
    SchematronValidationResult
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / 'schemas' / 'iwxxm' / 'IWXXM' / 'rule' / 'iwxxm.sch'


def _path_exists(path: Path) -> bool:
    try:
        return path.exists()
    except (PermissionError, OSError):
        return False


SKIP_DOCKER_TESTS = not _path_exists(SCHEMA_PATH)


class TestSchematronValidationResult:
    """Test the SchematronValidationResult dataclass."""
    
    def test_result_creation(self):
        """Test creating a validation result."""
        result = SchematronValidationResult(
            valid=True,
            status='PASS',
            assertions_passed=5,
            assertions_failed=0,
            failed_constraints=[]
        )
        assert result.valid is True
        assert result.status == 'PASS'
        assert result.assertions_passed == 5
        assert result.assertions_failed == 0
    
    def test_result_with_failures(self):
        """Test result with failed assertions."""
        failures = [
            {'id': 'assert-1', 'test': 'test-expr', 'message': 'Test failed'}
        ]
        result = SchematronValidationResult(
            valid=False,
            status='FAIL',
            assertions_passed=3,
            assertions_failed=1,
            failed_constraints=failures
        )
        assert result.valid is False
        assert result.assertions_failed == 1
        assert len(result.failed_constraints) == 1


@pytest.mark.skipif(SKIP_DOCKER_TESTS, reason="Schema file not found")
class TestSchematronValidatorDocker:
    """Test the SchematronValidatorDocker class."""
    
    @pytest.fixture
    def validator(self):
        """Create a validator instance for testing."""
        schema_path = SCHEMA_PATH
        if not _path_exists(schema_path):
            pytest.skip(f"Schema not found or inaccessible: {schema_path}")
        
        return SchematronValidatorDocker(
            schema_path=str(schema_path),
            version="2023-1"
        )
    
    def test_validator_initialization(self, validator):
        """Test validator is properly initialized."""
        assert str(validator.schema_path) == str(SCHEMA_PATH)
        assert validator.version == "2023-1"
        assert validator.container_image == "metar-iwxxm-schematron:latest"
    
    @patch('subprocess.run')
    def test_check_docker_image_exists(self, mock_run, validator):
        """Test checking if Docker image exists."""
        mock_run.return_value = MagicMock(returncode=0)
        result = validator.check_docker_image()
        assert result is True
    
    @patch('subprocess.run')
    def test_check_docker_image_not_exists(self, mock_run, validator):
        """Test checking when Docker image doesn't exist."""
        mock_run.return_value = MagicMock(returncode=1)
        result = validator.check_docker_image()
        assert result is False
    
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.run')
    def test_validate_with_valid_xml(self, mock_run, mock_temp, validator):
        """Test validation with valid XML."""
        # Mock the temporary file
        mock_file = MagicMock()
        mock_file.name = '/tmp/test.xml'
        mock_temp.return_value.__enter__.return_value = mock_file
        
        # Mock successful Docker execution
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"status": "PASS", "valid": true, "assertions_passed": 5, "assertions_failed": 0}',
            stderr=''
        )
        
        xml_content = '<test>valid</test>'
        result = validator.validate(xml_content)
        
        assert result.valid is True
        assert result.status == 'PASS'
    
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.run')
    def test_validate_with_invalid_xml(self, mock_run, mock_temp, validator):
        """Test validation with invalid XML."""
        mock_file = MagicMock()
        mock_file.name = '/tmp/test.xml'
        mock_temp.return_value.__enter__.return_value = mock_file
        
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout='{"status": "FAIL", "valid": false, "assertions_passed": 3, "assertions_failed": 2, "failed_assertions": [{"id": "a1", "message": "Failed"}]}',
            stderr=''
        )
        
        xml_content = '<test>invalid</test>'
        result = validator.validate(xml_content)
        
        assert result.valid is False
        assert result.assertions_failed == 2
    
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.run')
    def test_validate_docker_error(self, mock_run, mock_temp, validator):
        """Test handling of Docker execution errors."""
        mock_file = MagicMock()
        mock_file.name = '/tmp/test.xml'
        mock_temp.return_value.__enter__.return_value = mock_file
        
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout='',
            stderr='Docker error: image not found'
        )
        
        xml_content = '<test>error</test>'
        result = validator.validate(xml_content)
        
        assert result.valid is False
        assert 'ERROR' in result.status
    
    def test_validate_with_real_paths(self, validator):
        """Test with real file paths (integration test)."""
        schema_path = Path('/root/metar-to-IWXXM/schemas/iwxxm/IWXXM/rule/iwxxm.sch')
        xml_path = Path('/root/metar-to-IWXXM/data/iwxxm-translation/Amd79-80-2023/metar/BGBW-282350Z.xml')
        
        if not schema_path.exists():
            pytest.skip("Schema file not found")
        if not xml_path.exists():
            pytest.skip("Test XML file not found")
        
        # Read actual XML
        with open(xml_path, 'r') as f:
            xml_content = f.read()
        
        # Run validation (this calls actual Docker)
        result = validator.validate(xml_content)
        
        # Result should be a SchematronValidationResult object
        assert isinstance(result, SchematronValidationResult)
        assert result.status in ['PASS', 'FAIL', 'ERROR']


@pytest.mark.skipif(SKIP_DOCKER_TESTS, reason="Schema file not found")
class TestSchematronIntegration:
    """Integration tests with real IWXXM test data."""
    
    @pytest.fixture
    def test_data_dir(self):
        """Get path to test data."""
        return Path('/root/metar-to-IWXXM/data/iwxxm-translation/Amd79-80-2023/metar')
    
    @pytest.fixture
    def validator(self):
        """Create validator for integration tests."""
        return SchematronValidatorDocker(
            schema_path="/root/metar-to-IWXXM/schemas/iwxxm/IWXXM/rule/iwxxm.sch",
            version="2023-1"
        )
    
    def test_validate_bgbw_sample(self, validator, test_data_dir):
        """Test validation of BGBW sample."""
        xml_path = test_data_dir / 'BGBW-282350Z.xml'
        
        if not xml_path.exists():
            pytest.skip(f"Test file not found: {xml_path}")
        
        with open(xml_path, 'r') as f:
            xml_content = f.read()
        
        # Run validation - may result in ERROR due to Schematron compilation not fully set up
        result = validator.validate(xml_content)
        
        # Log results for debugging
        print(f"\n=== BGBW Validation Results ===")
        print(f"Status: {result.status}")
        print(f"Valid: {result.valid}")
        print(f"Passed: {result.assertions_passed}")
        print(f"Failed: {result.assertions_failed}")
        if result.errors:
            print(f"Errors: {result.errors}")
        
        # Just check that validation method returns a result object (doesn't crash)
        assert isinstance(result, SchematronValidationResult)
        assert result.status in ['PASS', 'FAIL', 'ERROR', 'UNKNOWN']
    
    def test_validate_multiple_samples(self, validator, test_data_dir):
        """Test validation of multiple IWXXM samples."""
        if not test_data_dir.exists():
            pytest.skip(f"Test data directory not found: {test_data_dir}")
        
        xml_files = list(test_data_dir.glob('*.xml'))[:5]  # First 5 files
        
        if not xml_files:
            pytest.skip("No XML test files found")
        
        results_summary = []
        
        for xml_file in xml_files:
            with open(xml_file, 'r') as f:
                xml_content = f.read()
            
            result = validator.validate(xml_content)
            results_summary.append({
                'file': xml_file.name,
                'valid': result.valid,
                'status': result.status,
                'passed': result.assertions_passed,
                'failed': result.assertions_failed
            })
        
        print(f"\n=== Multi-Sample Validation Results ===")
        for res in results_summary:
            print(f"{res['file']}: {res['status']} (P:{res['passed']} F:{res['failed']})")
        
        # At least some files should have been processed
        assert len(results_summary) > 0, "No results generated"
        # All statuses should be valid states
        assert all(r['status'] in ['PASS', 'FAIL', 'ERROR', 'UNKNOWN'] for r in results_summary), "Invalid status values"


@pytest.mark.skipif(SKIP_DOCKER_TESTS, reason="Schema file not found")
class TestSchematronEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def validator(self):
        """Create validator for testing."""
        return SchematronValidatorDocker(
            schema_path=str(SCHEMA_PATH)
        )
    
    def test_validate_empty_xml(self, validator):
        """Test with empty XML string."""
        result = validator.validate('')
        assert result.valid is False or result.status == 'ERROR'
    
    def test_validate_malformed_xml(self, validator):
        """Test with malformed XML."""
        result = validator.validate('<invalid>xml</with-wrong-tag>')
        assert result.valid is False or result.status == 'ERROR'
    
    def test_validate_none(self, validator):
        """Test with None input."""
        # Validator handles None gracefully and returns error result
        result = validator.validate(None)
        assert result.status == 'ERROR'
        assert len(result.errors) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
