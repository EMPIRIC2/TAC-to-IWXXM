"""
Schematron Validator with Docker Backend for XSLT2 Support

This module provides XSLT2-compatible Schematron validation for IWXXM 2023-1
and other versions that require ISO Schematron processing.

Uses Docker container with Java/Saxon to process XSLT2 features that lxml
doesn't support natively.
"""

import json
import logging
import subprocess
import tempfile
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SchematronValidationResult:
    """Result from Schematron validation."""
    
    valid: bool
    status: str = 'UNKNOWN'  # 'PASS' or 'FAIL'
    assertions_passed: int = 0
    assertions_failed: int = 0
    failed_constraints: List[Dict] = field(default_factory=list)
    passed_constraints: List[Dict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class SchematronValidatorDocker:
    """Schematron validator using Docker container with Saxon XSLT2 support."""
    
    def __init__(self, schema_path: str, version: str = "2023-1"):
        """
        Initialize Schematron validator.
        
        Args:
            schema_path: Path to Schematron .sch file
            version: IWXXM version (e.g., "2023-1")
        """
        self.schema_path = Path(schema_path)
        self.version = version
        self.container_image = "metar-iwxxm-schematron:latest"
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schematron schema not found: {schema_path}")
        
        self.logger.info(f"Initialized Schematron validator for version {version}")
        self.logger.info(f"Schema: {schema_path}")
    
    def validate(self, xml_content: str) -> SchematronValidationResult:
        """
        Validate XML against Schematron schema.
        
        Args:
            xml_content: XML content as string
        
        Returns:
            SchematronValidationResult with validation details
        """
        
        try:
            self.logger.debug(f"Validating XML ({len(xml_content)} bytes)")
            
            # Write XML to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as tmp:
                tmp.write(xml_content)
                xml_file = tmp.name
            
            # Run Docker validation
            result = self._run_docker_validation(xml_file)
            
            # Clean up temp file
            Path(xml_file).unlink(missing_ok=True)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}", exc_info=True)
            result = SchematronValidationResult(
                valid=False,
                status='ERROR',
                errors=[str(e)]
            )
            return result
    
    def _run_docker_validation(self, xml_file: str) -> SchematronValidationResult:
        """
        Run Docker container for validation.
        
        Args:
            xml_file: Path to XML file to validate
        
        Returns:
            SchematronValidationResult
        """
        
        try:
            xml_path = Path(xml_file).resolve()
            schema_path = self.schema_path.resolve()
            
            self.logger.debug(f"Running Docker validation")
            self.logger.debug(f"  XML: {xml_path}")
            self.logger.debug(f"  Schema: {schema_path}")
            
            # Build Docker run command
            cmd = [
                'docker', 'run', '--rm',
                '-v', f'{xml_path.parent}:/work',
                '-v', f'{schema_path.parent}:/schemas',
                self.container_image,
                str(xml_path),
                str(schema_path),
                '--output', 'json'
            ]
            
            self.logger.debug(f"Command: {' '.join(cmd)}")
            
            # Run Docker container
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                self.logger.warning(f"Docker returned code {result.returncode}")
                if result.stderr:
                    self.logger.warning(f"STDERR: {result.stderr[:200]}")
            
            # Parse JSON output
            try:
                output = json.loads(result.stdout)
                
                # Convert to SchematronValidationResult
                return SchematronValidationResult(
                    valid=output.get('status') == 'PASS',
                    status=output.get('status', 'UNKNOWN'),
                    assertions_passed=output.get('assertions_passed', 0),
                    assertions_failed=output.get('assertions_failed', 0),
                    failed_constraints=output.get('failed_assertions', []),
                    passed_constraints=output.get('passed_assertions', []),
                    errors=output.get('error', []) if isinstance(output.get('error'), list) else (
                        [output.get('error')] if output.get('error') else []
                    )
                )
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse Docker output: {e}")
                self.logger.debug(f"Output was: {result.stdout[:200]}")
                return SchematronValidationResult(
                    valid=False,
                    status='ERROR',
                    errors=[f'Invalid JSON output: {str(e)}']
                )
        
        except subprocess.TimeoutExpired:
            self.logger.error("Docker validation timeout (>60s)")
            return SchematronValidationResult(
                valid=False,
                status='ERROR',
                errors=['Validation timeout']
            )
        except Exception as e:
            self.logger.error(f"Docker execution error: {e}", exc_info=True)
            return SchematronValidationResult(
                valid=False,
                status='ERROR',
                errors=[str(e)]
            )
    
    def check_docker_image(self) -> bool:
        """Check if Docker image exists and is ready."""
        try:
            cmd = ['docker', 'image', 'inspect', self.container_image]
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            exists = result.returncode == 0
            
            if exists:
                self.logger.info(f"✓ Docker image '{self.container_image}' is available")
            else:
                self.logger.warning(f"✗ Docker image '{self.container_image}' not found")
            
            return exists
            
        except Exception as e:
            self.logger.error(f"Could not check Docker: {e}")
            return False


# Convenience function for direct validation
def validate_against_schematron(
    xml_content: str,
    schema_path: str,
    version: str = "2023-1"
) -> SchematronValidationResult:
    """
    Validate XML against Schematron schema.
    
    Args:
        xml_content: XML content as string
        schema_path: Path to .sch Schematron file
        version: IWXXM version
    
    Returns:
        SchematronValidationResult
    """
    validator = SchematronValidatorDocker(schema_path, version)
    return validator.validate(xml_content)
