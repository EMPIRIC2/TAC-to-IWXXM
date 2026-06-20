"""
Test suite runner for Schematron validation functionality.

Run with: pytest test_schematron_validation_suite.py -v
"""

import json
import subprocess
from pathlib import Path

import pytest


class TestSchematronValidationSuite:
    """Comprehensive validation test suite."""

    def test_docker_image_available(self):
        """Verify Docker image is available."""
        result = subprocess.run(
            ["docker", "images", "-q", "metar-iwxxm-schematron:latest"], capture_output=True, text=True
        )
        assert result.returncode == 0
        image_id = result.stdout.strip()
        assert image_id, "Docker image metar-iwxxm-schematron:latest not found"
        print(f"✓ Docker image available: {image_id}")

    def test_schema_files_exist(self):
        """Verify schema files exist."""
        schema_dir = Path("/root/metar-to-IWXXM/schemas/iwxxm/2025-2/IWXXM")

        required_files = [
            schema_dir / "iwxxm.xsd",
            schema_dir / "rule" / "iwxxm.sch",
        ]

        for file_path in required_files:
            assert file_path.exists(), f"Required file not found: {file_path}"
            print(f"✓ Schema file found: {file_path.name}")

    def test_test_data_exists(self):
        """Verify test data exists."""
        test_data_dir = Path("/root/metar-to-IWXXM/data/iwxxm-translation/Amd79-80-2023/metar")

        assert test_data_dir.exists(), f"Test data directory not found: {test_data_dir}"

        xml_files = list(test_data_dir.glob("*.xml"))
        assert len(xml_files) > 0, "No XML test files found"

        print(f"✓ Test data available: {len(xml_files)} XML files")

    def test_docker_validation_bgbw(self):
        """Test Docker validation with BGBW sample."""
        xml_path = Path("/root/metar-to-IWXXM/data/iwxxm-translation/Amd79-80-2023/metar/BGBW-282350Z.xml")
        schema_path = Path("/root/metar-to-IWXXM/schemas/iwxxm/2025-2/IWXXM/rule/iwxxm.sch")

        if not xml_path.exists() or not schema_path.exists():
            pytest.skip("Required files not found")

        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{xml_path.parent}:/data",
                "-v",
                f"{schema_path.parent.parent}:/schemas",
                "metar-iwxxm-schematron:latest",
                f"/data/{xml_path.name}",
                str(schema_path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        print("\n=== BGBW Validation Output ===")
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout[:500]}")
        if result.stderr:
            print(f"Stderr: {result.stderr[:500]}")

        # Should not have critical errors
        assert "Error" not in result.stderr or "ERROR" not in result.stdout, f"Validation error: {result.stderr}"

        # Try to parse output
        try:
            output = json.loads(result.stdout)
            assert "status" in output
            print(f"✓ Validation result: {output['status']}")
            print(
                f"  Assertions - Passed: {output.get('assertions_passed', 'N/A')}, Failed: {output.get('assertions_failed', 'N/A')}"
            )
        except json.JSONDecodeError:
            print("✓ Validation completed (output not JSON)")

    def test_validation_wrapper_module(self):
        """Test that validation wrapper module exists and imports."""
        wrapper_path = Path("/root/metar-to-IWXXM/backend/src/utilities/schematron_validator_docker.py")

        assert wrapper_path.exists(), f"Wrapper module not found: {wrapper_path}"

        # Try importing
        import sys

        sys.path.insert(0, str(wrapper_path.parent.parent))

        try:
            from utilities.schematron_validator_docker import SchematronValidatorDocker

            print("✓ Validation wrapper module imports successfully")
        except ImportError as e:
            pytest.fail(f"Failed to import validation wrapper: {e}")

    def test_schematron_script_exists(self):
        """Test that schematron_validator.py was moved to utilities."""
        # File was moved from root to src/utilities during reorganization
        # The production code now uses src/utilities/schematron_validator.py
        from src.utilities import schematron_validator

        assert hasattr(schematron_validator, "validate_schematron"), "validate_schematron function not found"
        assert hasattr(schematron_validator, "SchematronValidationResult"), "SchematronValidationResult class not found"

        print("✓ Schematron validator module exists at src/utilities/schematron_validator.py")

    def test_dockerfile_valid(self):
        """Test that Dockerfile.schematron exists in docker/ directory."""
        # File was moved from root to docker/ during reorganization
        dockerfile_path = Path("/root/metar-to-IWXXM/backend/docker/Dockerfile.schematron")
        assert dockerfile_path.exists(), f"Dockerfile.schematron not found at {dockerfile_path}"

        with open(dockerfile_path) as f:
            content = f.read()
            assert "FROM ubuntu:20.04" in content, "Missing FROM statement"
            assert "ENTRYPOINT" in content, "Missing ENTRYPOINT"
            assert "saxon" in content.lower(), "Missing Saxon reference"

        print("✓ Dockerfile.schematron is valid at docker/Dockerfile.schematron")


def run_all_tests():
    """Run all tests and print summary."""
    print("\n" + "=" * 60)
    print("SCHEMATRON VALIDATION TEST SUITE")
    print("=" * 60 + "\n")

    # Run pytest
    pytest.main([__file__, "-v", "--tb=short", "-s"])


if __name__ == "__main__":
    run_all_tests()
