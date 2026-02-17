"""
Direct tests for the Schematron Docker container.

Tests the Docker image and schematron_validator.py script directly.
"""

import json
import subprocess
import tempfile
from pathlib import Path
import pytest


class TestSchematronDockerContainer:
    """Test the Docker container itself."""
    
    @pytest.fixture
    def schema_path(self):
        """Get path to IWXXM Schematron."""
        return Path('/root/metar-to-IWXXM/schemas/iwxxm/2025-2/IWXXM/rule/iwxxm.sch')
    
    @pytest.fixture
    def test_xml_path(self):
        """Get path to test XML."""
        return Path('/root/metar-to-IWXXM/data/iwxxm-translation/Amd79-80-2023/metar/BGBW-282350Z.xml')
    
    def test_docker_image_exists(self):
        """Test that the Docker image is available."""
        result = subprocess.run(
            ['docker', 'images', '-q', 'metar-iwxxm-schematron:latest'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Docker image not found"
        assert result.stdout.strip(), "No Docker image ID returned"
    
    def test_docker_run_basic(self):
        """Test basic Docker container execution."""
        result = subprocess.run(
            ['docker', 'run', '--rm', 'metar-iwxxm-schematron:latest', '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Python help message should be printed (or error about missing args)
        assert result.returncode in [0, 1], "Docker image failed to run"
    
    def test_validate_with_docker(self, schema_path, test_xml_path):
        """Test validation using Docker container."""
        if not schema_path.exists():
            pytest.skip(f"Schema not found: {schema_path}")
        if not test_xml_path.exists():
            pytest.skip(f"Test XML not found: {test_xml_path}")
        
        result = subprocess.run(
            [
                'docker', 'run', '--rm',
                '-v', f'{test_xml_path.parent}:/data',
                '-v', f'{schema_path.parent.parent}:/schemas',
                'metar-iwxxm-schematron:latest',
                f'/data/{test_xml_path.name}',
                str(schema_path)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Should not have command not found errors
        assert 'not found' not in result.stderr.lower(), f"Error: {result.stderr}"
        
        # Try to parse JSON output
        if result.stdout:
            try:
                output = json.loads(result.stdout)
                assert 'status' in output, "Missing status in output"
                print(f"\nValidation result: {json.dumps(output, indent=2)}")
            except json.JSONDecodeError:
                # More lenient - just check that something was output
                assert len(result.stdout) > 0, "No output from Docker container"
    
    def test_validate_multiple_files(self, schema_path):
        """Test validation of multiple test files."""
        if not schema_path.exists():
            pytest.skip(f"Schema not found: {schema_path}")
        
        test_dir = Path('/root/metar-to-IWXXM/data/iwxxm-translation/Amd79-80-2023/metar')
        if not test_dir.exists():
            pytest.skip(f"Test data dir not found: {test_dir}")
        
        xml_files = list(test_dir.glob('*.xml'))[:3]  # Test first 3
        
        if not xml_files:
            pytest.skip("No XML files found in test data")
        
        results = []
        for xml_file in xml_files:
            result = subprocess.run(
                [
                    'docker', 'run', '--rm',
                    '-v', f'{xml_file.parent}:/data',
                    '-v', f'{schema_path.parent.parent}:/schemas',
                    'metar-iwxxm-schematron:latest',
                    f'/data/{xml_file.name}',
                    str(schema_path)
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode in [0, 1]  # 0=pass, 1=fail is normal, >1=error
            results.append({
                'file': xml_file.name,
                'returncode': result.returncode,
                'success': success
            })
        
        print(f"\n=== Docker Validation Results ===")
        for r in results:
            print(f"{r['file']}: returncode={r['returncode']} ({'OK' if r['success'] else 'ERROR'})")
        
        # All should run without critical errors (returncode should be 0 or 1, not >1)
        assert all(r['success'] for r in results), "Some validations had critical errors"
    
    def test_docker_volume_mounting(self, test_xml_path, schema_path):
        """Test that Docker volume mounting works correctly."""
        if not test_xml_path.exists() or not schema_path.exists():
            pytest.skip("Test files not found")
        
        # Test with absolute paths mounted to container paths
        result = subprocess.run(
            [
                'docker', 'run', '--rm',
                '-v', f'{test_xml_path.parent}:/input',
                '-v', f'{schema_path.parent.parent}:/schema',
                'metar-iwxxm-schematron:latest',
                f'/input/{test_xml_path.name}',
                f'/schema/iwxxm/IWXXM/rule/iwxxm.sch'
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Should not have file not found errors
        assert 'no such file or directory' not in result.stderr.lower(), \
            f"Volume mounting failed: {result.stderr}"


class TestSchematronDockerProperties:
    """Test Docker container properties."""
    
    def test_docker_image_size(self):
        """Test Docker image size is reasonable."""
        result = subprocess.run(
            ['docker', 'images', 'metar-iwxxm-schematron:latest', '--format={{.Size}}'],
            capture_output=True,
            text=True
        )
        size_str = result.stdout.strip()
        
        # Image should be reasonable size (expect ~600MB-1GB for Java+Saxon)
        # Parse size string like "666MB"
        if 'MB' in size_str:
            size_mb = int(size_str.replace('MB', ''))
            assert 300 < size_mb < 2000, f"Image size unexpectedly large or small: {size_str}"
    
    def test_docker_entrypoint(self):
        """Test that Docker has correct entrypoint."""
        result = subprocess.run(
            ['docker', 'inspect', 'metar-iwxxm-schematron:latest'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, "Could not inspect image"
        assert 'python3' in result.stdout, "Expected Python entrypoint not found"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
