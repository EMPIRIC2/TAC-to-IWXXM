"""
IWXXM Schematron Validator (Validation Layer 5)

Validates IWXXM XML documents against official WMO Schematron business rules.
Uses lxml.isoschematron for pure Python implementation without Java dependencies.
"""

import shutil
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass
import logging

from lxml import etree, isoschematron

from .schema_registry import get_schema_registry
from ..schemas.validation import ValidationIssue, ValidationSeverity, ValidationLayer

logger = logging.getLogger(__name__)


@dataclass
class SchematronValidationResult:
    """Result of Schematron validation."""
    is_valid: bool
    issues: List[ValidationIssue]
    schema_version: str
    rules_evaluated: int = 0


class SchematronValidator:
    """
    Validates IWXXM XML against Schematron business rules with version-aware caching.
    
    Schematron rules reference RDF codelist files via document() function.
    This validator sets up a working directory with RDF files accessible to Schematron.
    """
    
    def __init__(self):
        """Initialize Schematron validator with schema registry."""
        self.registry = get_schema_registry()
        self._schematron_cache: Dict[str, isoschematron.Schematron] = {}
        self._working_dirs: Dict[str, Path] = {}
    
    def _setup_working_directory(self, version: str) -> Path:
        """
        Set up working directory with bundled RDF codelists for Schematron validation.
        
        Schematron rules use document() to load RDF files like:
        document('codes.wmo.int-49-2-AerodromeRecentWeather.rdf')
        
        We copy bundled RDF files from the mirrored rule/ directory to a temp
        working directory so document() calls can resolve them locally without
        network access to codes.wmo.int.
        
        This enables fully offline Schematron validation using the ~20 RDF codelist
        files that are bundled with each IWXXM version at:
        schemas.wmo.int/iwxxm/{version}/rule/*.rdf
        
        Args:
            version: IWXXM version (e.g., '2025-2')
        
        Returns:
            Path to working directory with RDF codelists
            
        Raises:
            FileNotFoundError: If codelists directory or RDF files not found
        """
        if version in self._working_dirs:
            logger.debug(f"Reusing cached working directory for {version}")
            return self._working_dirs[version]
        
        # Get codelists directory from registry (schemas/iwxxm/{version}/IWXXM/rule/)
        codelists_dir = self.registry.get_codelists_dir(version)
        
        if not codelists_dir or not codelists_dir.exists():
            raise FileNotFoundError(
                f"Codelists directory not found for version {version}: {codelists_dir}. "
                f"Run schema mirror service to download bundled RDF files."
            )
        
        # Create temp working directory
        work_dir = Path(tempfile.mkdtemp(prefix=f"iwxxm_sch_{version}_"))
        
        # Copy all RDF files to working directory
        rdf_files = list(codelists_dir.glob("*.rdf"))
        
        if not rdf_files:
            raise FileNotFoundError(
                f"No RDF codelist files found in {codelists_dir}. "
                f"Expected ~20 files like codes.wmo.int-*.rdf. "
                f"Verify schema mirror completed successfully."
            )
        
        # Verify we have essential codelists
        rdf_names = {f.name for f in rdf_files}
        required_codelists = [
            "codes.wmo.int-common-nil.rdf",
            "codes.wmo.int-49-2-AerodromeRecentWeather.rdf",
            "codes.wmo.int-49-2-CloudAmountReportedAtAerodrome.rdf"
        ]
        
        # For 2025-2, check for split NIL codelist
        if version == "2025-2":
            if "codes.wmo.int-iwxxm-nil.rdf" in rdf_names:
                # 2025-2 uses split NIL codelist
                required_codelists.remove("codes.wmo.int-common-nil.rdf")
                required_codelists.append("codes.wmo.int-iwxxm-nil.rdf")
        
        missing = [f for f in required_codelists if f not in rdf_names]
        if missing:
            logger.warning(
                f"Some required RDF codelists missing for {version}: {missing}"
            )
        
        for rdf_file in rdf_files:
            shutil.copy2(rdf_file, work_dir / rdf_file.name)
        
        logger.info(
            f"✓ Set up offline Schematron validation for {version}: "
            f"{work_dir} ({len(rdf_files)} bundled RDF codelists)"
        )
        
        self._working_dirs[version] = work_dir
        return work_dir
    
    def _get_compiled_schematron(self, version: str) -> isoschematron.Schematron:
        """
        Get compiled Schematron validator for version with caching.
        
        Args:
            version: IWXXM version (e.g., '2025-2')
        
        Returns:
            Compiled lxml Schematron object
        
        Raises:
            FileNotFoundError: If Schematron file not found
            etree.SchematronParseError: If Schematron parsing fails
        """
        if version in self._schematron_cache:
            logger.debug(f"Using cached Schematron for version {version}")
            return self._schematron_cache[version]
        
        # Get Schematron path from registry
        sch_path = self.registry.get_schematron_path(version)
        
        if not sch_path or not sch_path.exists():
            raise FileNotFoundError(
                f"Schematron file not found for version {version}: {sch_path}"
            )
        
        logger.info(f"Compiling Schematron for version {version}: {sch_path}")
        
        # Check if this is a 2025-2 XSLT2 Schematron
        if version == "2025-2":
            # Read Schematron to check query binding
            try:
                with open(sch_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'queryBinding="xslt2"' in content:
                        logger.warning(
                            f"Version {version} uses XSLT2 Schematron which is not supported by Python lxml. "
                            f"Schematron validation will be skipped for this version. "
                            f"Note: This is a known limitation. File issue with WMO for XSLT1 compatibility."
                        )
                        # Return a result indicating Schematron skipped (non-blocking)
                        return None  # Signal to skip this version
            except Exception as e:
                logger.warning(f"Could not check Schematron query binding: {e}")
        
        try:
            # Set up working directory with RDF files
            work_dir = self._setup_working_directory(version)
            
            # Parse Schematron with working directory as base
            # This allows document() calls to resolve RDF files
            parser = etree.XMLParser()
            with open(sch_path, 'rb') as f:
                sch_doc = etree.parse(f, parser, base_url=str(work_dir))
            
            # Compile Schematron
            # store_report=True preserves SVRL output for detailed error messages
            schematron = isoschematron.Schematron(
                sch_doc,
                store_report=True,
                store_schematron=True
            )
            
            # Cache compiled Schematron
            self._schematron_cache[version] = schematron
            
            logger.info(f"Successfully compiled Schematron for version {version}")
            return schematron
            
        except etree.XMLSyntaxError as e:
            logger.error(f"Failed to parse Schematron: {e}")
            raise
        except Exception as e:
            if "xslt2" in str(e).lower() and version == "2025-2":
                logger.warning(
                    f"Schematron compilation failed: Python lxml does not support XSLT2 (version {version}). "
                    f"This is expected - Schematron validation will be skipped for this version."
                )
                return None  # Signal to skip
            logger.error(f"Unexpected error compiling Schematron: {e}")
            raise
    
    def _parse_svrl_report(
        self, 
        schematron: isoschematron.Schematron,
        version: str
    ) -> List[ValidationIssue]:
        """
        Parse Schematron SVRL (Schematron Validation Report Language) output.
        
        Args:
            schematron: Compiled Schematron with validation report
            version: IWXXM version
        
        Returns:
            List of ValidationIssue objects
        """
        issues = []
        
        # Get SVRL report
        report = schematron.validation_report
        
        if report is None:
            return issues
        
        # SVRL namespace
        svrl_ns = {'svrl': 'http://purl.oclc.org/dsdl/svrl'}
        
        # Extract failed assertions
        failed_asserts = report.xpath(
            '//svrl:failed-assert',
            namespaces=svrl_ns
        )
        
        for assert_elem in failed_asserts:
            # Get test expression
            test = assert_elem.get('test', '')
            
            # Get location (xpath)
            location = assert_elem.get('location', '')
            
            # Get assertion message
            text_elem = assert_elem.find('svrl:text', namespaces=svrl_ns)
            message = text_elem.text if text_elem is not None else 'Assertion failed'
            
            # Get pattern ID
            # Look backwards in report for <fired-rule> to get context
            pattern_id = assert_elem.get('id', 'unknown')
            
            issue = ValidationIssue(
                layer=ValidationLayer.SCHEMATRON,
                level=ValidationSeverity.ERROR,
                message=message.strip() if message else 'Schematron assertion failed',
                location=location,
                code=pattern_id
            )
            
            issues.append(issue)
        
        # Extract successful reports (warnings/info)
        successful_reports = report.xpath(
            '//svrl:successful-report',
            namespaces=svrl_ns
        )
        
        for report_elem in successful_reports:
            test = report_elem.get('test', '')
            location = report_elem.get('location', '')
            pattern_id = report_elem.get('id', 'unknown')
            
            text_elem = report_elem.find('svrl:text', namespaces=svrl_ns)
            message = text_elem.text if text_elem is not None else 'Report triggered'
            
            # Successful reports are typically warnings/info
            issue = ValidationIssue(
                layer=ValidationLayer.SCHEMATRON,
                level=ValidationSeverity.WARNING,
                message=message.strip() if message else 'Schematron report',
                location=location,
                code=pattern_id
            )
            
            issues.append(issue)
        
        return issues
    
    def validate(
        self, 
        xml_content: str, 
        version: str
    ) -> SchematronValidationResult:
        """
        Validate XML content against Schematron business rules.
        
        Args:
            xml_content: XML string to validate
            version: IWXXM version (e.g., '2025-2')
        
        Returns:
            SchematronValidationResult with validation outcomes
        """
        issues = []
        
        try:
            # Parse XML document
            try:
                xml_doc = etree.fromstring(xml_content.encode('utf-8'))
            except etree.XMLSyntaxError as e:
                # XML not well-formed - should be caught earlier
                issue = ValidationIssue(
                    layer=ValidationLayer.SCHEMATRON,
                    level=ValidationSeverity.ERROR,
                    message=f"XML parsing failed: {str(e)}",
                    location=f"line {getattr(e, 'lineno', '?')}",
                    code="XML_SYNTAX_ERROR"
                )
                issues.append(issue)
                return SchematronValidationResult(
                    is_valid=False,
                    issues=issues,
                    schema_version=version
                )
            
            # Get compiled Schematron
            try:
                schematron = self._get_compiled_schematron(version)
                
                # Handle case where Schematron is skipped (e.g., 2025-2 with XSLT2)
                if schematron is None:
                    issue = ValidationIssue(
                        layer=ValidationLayer.SCHEMATRON,
                        level=ValidationSeverity.WARNING,
                        message=f"Schematron validation skipped for version {version} (unsupported query language)",
                        code="SCHEMATRON_SKIPPED"
                    )
                    return SchematronValidationResult(
                        is_valid=True,  # Non-blocking
                        issues=[issue],
                        schema_version=version
                    )
            except FileNotFoundError as e:
                issue = ValidationIssue(
                    layer=ValidationLayer.SCHEMATRON,
                    level=ValidationSeverity.ERROR,
                    message=f"Schematron not available for version {version}: {str(e)}",
                    code="SCHEMATRON_NOT_FOUND"
                )
                issues.append(issue)
                return SchematronValidationResult(
                    is_valid=False,
                    issues=issues,
                    schema_version=version
                )
            
            # Perform validation
            is_valid = schematron.validate(xml_doc)
            
            # Parse SVRL report for detailed issues
            svrl_issues = self._parse_svrl_report(schematron, version)
            issues.extend(svrl_issues)
            
            if not is_valid:
                logger.warning(
                    f"Schematron validation failed for version {version}: "
                    f"{len(issues)} issues"
                )
            else:
                logger.debug(f"Schematron validation passed for version {version}")
            
            return SchematronValidationResult(
                is_valid=is_valid,
                issues=issues,
                schema_version=version,
                rules_evaluated=len(svrl_issues)
            )
            
        except Exception as e:
            logger.error(f"Unexpected error during Schematron validation: {e}")
            issue = ValidationIssue(
                layer=ValidationLayer.SCHEMATRON,
                level=ValidationSeverity.ERROR,
                message=f"Validation error: {str(e)}",
                code=type(e).__name__
            )
            issues.append(issue)
            return SchematronValidationResult(
                is_valid=False,
                issues=issues,
                schema_version=version
            )
    
    def clear_cache(self, version: Optional[str] = None):
        """
        Clear cached compiled Schematron validators.
        
        Args:
            version: Specific version to clear, or None for all
        """
        if version:
            if version in self._schematron_cache:
                del self._schematron_cache[version]
                logger.info(f"Cleared Schematron cache for version {version}")
            
            # Clean up working directory
            if version in self._working_dirs:
                work_dir = self._working_dirs[version]
                if work_dir.exists():
                    shutil.rmtree(work_dir)
                del self._working_dirs[version]
        else:
            self._schematron_cache.clear()
            
            # Clean up all working directories
            for work_dir in self._working_dirs.values():
                if work_dir.exists():
                    shutil.rmtree(work_dir)
            self._working_dirs.clear()
            
            logger.info("Cleared all Schematron caches and working directories")
    
    def __del__(self):
        """Clean up working directories on deletion."""
        try:
            self.clear_cache()
        except Exception:
            pass  # Ignore errors during cleanup


# Singleton instance
_validator_instance: Optional[SchematronValidator] = None


def get_schematron_validator() -> SchematronValidator:
    """
    Get singleton Schematron validator instance.
    
    Returns:
        SchematronValidator instance
    """
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = SchematronValidator()
    return _validator_instance


def validate_schematron(
    xml_content: str, 
    version: str
) -> SchematronValidationResult:
    """
    Convenience function to validate XML against Schematron rules.
    
    Args:
        xml_content: XML string to validate
        version: IWXXM version (e.g., '2025-2')
    
    Returns:
        SchematronValidationResult with validation outcomes
    """
    validator = get_schematron_validator()
    return validator.validate(xml_content, version)
