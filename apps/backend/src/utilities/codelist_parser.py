"""
IWXXM Code List Parser

Parses RDF/XML code lists from WMO repositories and provides
version-specific validation of element values against allowed code lists.
Includes XML validation against code list references.

Supports both offline (RDF files) and online (codes.wmo.int) validation.
"""

import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

import lxml.etree as etree

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    requests = None  # type: ignore[assignment,misc]
    REQUESTS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("requests library not available, online validation disabled")

from ..schemas.validation import ValidationIssue, ValidationLayer, ValidationSeverity

logger = logging.getLogger(__name__)


@dataclass
class CodelistValidationResult:
    """Result of codelist validation."""

    is_valid: bool
    issues: List[ValidationIssue]
    total_references: int = 0
    invalid_references: int = 0


class CodeListParser:
    """
    Parses WMO code list RDF files and provides code list validation.

    Code lists are stored as RDF/XML in the IWXXM schema directories
    and are loaded on-demand per version.

    Supports online validation against live codes.wmo.int registry when
    local RDF files are missing or when enabled via settings.
    """

    def __init__(self, codelists_dir: Path, settings=None):
        """
        Initialize parser for a specific code lists directory.

        Args:
            codelists_dir: Path to the codelists directory (e.g., schemas/iwxxm/IWXXM/rule)
            settings: Optional ValidationSettings instance
        """
        self.codelists_dir = codelists_dir
        self._cache: Dict[str, Set[str]] = {}
        self._loaded = False

        # Online validation cache: {url: (issue, timestamp)}
        self._online_cache: Dict[str, Tuple[ValidationIssue, datetime]] = {}

        # Load settings
        if settings is None:
            try:
                from ..config.validation import get_validation_settings

                self.settings = get_validation_settings()
            except ImportError:
                # Fallback if config not available
                from types import SimpleNamespace

                self.settings = SimpleNamespace(
                    wmo_online_validation=False,
                    wmo_validation_timeout=5,
                    wmo_registry_cache_ttl=3600,
                    wmo_registry_url="https://codes.wmo.int",
                )
        else:
            self.settings = settings

    def load_codelists(self) -> None:
        """
        Load all RDF codelist files from the directory.

        Parses all .rdf files and extracts allowed code values.
        Results are cached in memory.
        """
        if self._loaded:
            return

        if not self.codelists_dir.exists():
            logger.warning(f"Codelists directory not found: {self.codelists_dir}")
            self._loaded = True
            return

        rdf_files = list(self.codelists_dir.glob("*.rdf"))
        logger.info(f"Loading {len(rdf_files)} RDF codelist files")

        for rdf_file in rdf_files:
            try:
                self._parse_rdf_file(rdf_file)
            except Exception as e:
                logger.warning(f"Failed to parse {rdf_file.name}: {e}")

        self._loaded = True
        logger.debug(f"Loaded {len(self._cache)} code lists")

    def _parse_rdf_file(self, rdf_file: Path) -> None:
        """
        Parse a single RDF codelist file.

        Extracts concept URIs/labels from RDF and stores allowed values.

        Args:
            rdf_file: Path to the RDF file
        """
        try:
            tree = ET.parse(rdf_file)
            root = tree.getroot()

            # RDF namespaces
            namespaces = {
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "skos": "http://www.w3.org/2004/02/skos/core#",
                "owl": "http://www.w3.org/2002/07/owl#",
            }

            # Extract codelist name from filename (e.g., codes.wmo.int-49-2-Weather.rdf → Weather)
            codelist_name = rdf_file.stem.split("-")[-1] if "-" in rdf_file.stem else rdf_file.stem

            codes: Set[str] = set()

            # Find all Concept elements (SKOS vocabulary)
            for concept in root.findall(".//skos:Concept", namespaces):
                # Get rdf:about attribute (the URI)
                about = concept.get("{%s}about" % namespaces["rdf"])
                if about:
                    # Extract just the code/value part
                    code = about.split("/")[-1]
                    codes.add(code)

                # Also try to get preferred label
                for label in concept.findall("skos:prefLabel", namespaces):
                    if label.text:
                        codes.add(label.text)

            if codes:
                self._cache[codelist_name] = codes
                logger.debug(f"Loaded {len(codes)} codes from {codelist_name}")

        except Exception as e:
            logger.error(f"Error parsing RDF file {rdf_file}: {e}")

    def get_codes(self, codelist_name: str) -> Set[str]:
        """
        Get allowed codes for a specific code list.

        Args:
            codelist_name: Name of the code list (e.g., "Weather", "CloudAmount")

        Returns:
            Set of allowed code values
        """
        if not self._loaded:
            self.load_codelists()

        return self._cache.get(codelist_name, set())

    def validate_code(self, codelist_name: str, code_value: str) -> bool:
        """
        Validate if a code value is allowed for a code list.

        Args:
            codelist_name: Name of the code list
            code_value: Code value to validate

        Returns:
            True if code is valid, False otherwise
        """
        allowed_codes = self.get_codes(codelist_name)
        return code_value in allowed_codes

    def list_codelists(self) -> List[str]:
        """Get list of available code lists."""
        if not self._loaded:
            self.load_codelists()
        return sorted(self._cache.keys())

    def _extract_codelist_references(self, xml_tree: etree._Element) -> List[Tuple[str, str, str]]:
        """
        Extract all xlink:href code list references from XML.

        Args:
            xml_tree: Parsed XML element tree

        Returns:
            List of tuples: (href_url, codelist_name, xpath_location)
        """
        references = []

        # Namespaces
        namespaces = {
            "xlink": "http://www.w3.org/1999/xlink",
        }

        # Find all xlink:href attributes
        elements_with_href = xml_tree.xpath("//*[@xlink:href]", namespaces=namespaces)

        for elem in elements_with_href:
            href = elem.get("{http://www.w3.org/1999/xlink}href")

            # Only process WMO code list URLs (not internal #id references)
            if href and "codes.wmo.int" in href:
                xpath = xml_tree.getroottree().getpath(elem)

                # Extract codelist name from URL
                # e.g., http://codes.wmo.int/49-2/AerodromeRecentWeather → AerodromeRecentWeather
                try:
                    codelist_name = href.rstrip("/").split("/")[-1]
                    references.append((href, codelist_name, xpath))
                except Exception as e:
                    logger.warning(f"Failed to parse codelist URL {href}: {e}")

        return references

    def validate_xml_codelists(self, xml_content: str) -> CodelistValidationResult:
        """
        Validate all code list references in XML document.

        Extracts xlink:href attributes pointing to WMO code lists and validates
        that the referenced codes exist in the loaded RDF files.

        Args:
            xml_content: XML string to validate

        Returns:
            CodelistValidationResult with validation outcomes
        """
        issues = []

        try:
            # Ensure codelists are loaded
            if not self._loaded:
                self.load_codelists()

            # Parse XML
            try:
                xml_tree = etree.fromstring(xml_content.encode("utf-8"))
            except etree.XMLSyntaxError as e:
                issue = ValidationIssue(
                    layer=ValidationLayer.WMO_CODELISTS,
                    level=ValidationSeverity.ERROR,
                    message=f"XML parsing failed: {str(e)}",
                    code="XML_SYNTAX_ERROR",
                )
                issues.append(issue)
                return CodelistValidationResult(is_valid=False, issues=issues)

            # Extract code list references
            references = self._extract_codelist_references(xml_tree)

            invalid_count = 0

            # Validate each reference
            for href, codelist_name, xpath in references:
                # Check if we have this codelist loaded
                if codelist_name not in self._cache:
                    # Try online validation if enabled
                    if self.settings.wmo_online_validation and REQUESTS_AVAILABLE:
                        issue = self._validate_online(href, xpath)
                        issues.append(issue)
                        if issue.level == ValidationSeverity.ERROR:
                            invalid_count += 1
                        continue
                    else:
                        # Codelist not loaded - could be external or missing
                        issue = ValidationIssue(
                            layer=ValidationLayer.WMO_CODELISTS,
                            level=ValidationSeverity.WARNING,
                            message=f"Code list '{codelist_name}' not found in loaded RDF files (online validation disabled)",
                            location=xpath,
                            code="CODELIST_NOT_FOUND",
                        )
                        issues.append(issue)
                        continue

                # Extract the actual code value from the element's text or attributes
                # This is tricky - the code value might be in element text, an attribute, or the URL itself
                # For now, we check if the URL ends with a valid code
                url_parts = href.rstrip("/").split("/")
                if len(url_parts) > 1:
                    potential_code = url_parts[-1]

                    # If the last part is the codelist name, try the second to last
                    if potential_code == codelist_name and len(url_parts) > 2:
                        potential_code = url_parts[-2]

                    # Validate the code
                    if not self.validate_code(codelist_name, potential_code):
                        invalid_count += 1
                        valid_codes = sorted(list(self.get_codes(codelist_name)))[:20]
                        issue = ValidationIssue(
                            layer=ValidationLayer.WMO_CODELISTS,
                            level=ValidationSeverity.ERROR,
                            message=f"Invalid code '{potential_code}' for codelist '{codelist_name}'. Valid codes include: {', '.join(valid_codes)}",
                            location=xpath,
                            code="INVALID_CODELIST_VALUE",
                        )
                        issues.append(issue)

            is_valid = invalid_count == 0

            if not is_valid:
                logger.warning(
                    f"Codelist validation failed: {invalid_count} invalid references out of {len(references)} total"
                )
            else:
                logger.debug(f"Codelist validation passed: {len(references)} references validated")

            return CodelistValidationResult(
                is_valid=is_valid, issues=issues, total_references=len(references), invalid_references=invalid_count
            )

        except Exception as e:
            logger.error(f"Unexpected error during codelist validation: {e}")
            issue = ValidationIssue(
                layer=ValidationLayer.WMO_CODELISTS,
                level=ValidationSeverity.ERROR,
                message=f"Validation error: {str(e)}",
                code=type(e).__name__,
            )
            issues.append(issue)
            return CodelistValidationResult(is_valid=False, issues=issues)

    def _validate_online(self, code_url: str, xpath: str) -> ValidationIssue:
        """
        Validate code against live codes.wmo.int registry.

        Args:
            code_url: Full URL to code (e.g., http://codes.wmo.int/49-2/CloudAmount/FEW)
            xpath: XPath location of the reference for error reporting

        Returns:
            ValidationIssue with result of online validation
        """
        if not REQUESTS_AVAILABLE:
            return ValidationIssue(
                layer=ValidationLayer.WMO_CODELISTS,
                level=ValidationSeverity.WARNING,
                message="Online validation unavailable (requests library not installed)",
                location=xpath,
                code="ONLINE_VALIDATION_UNAVAILABLE",
            )

        # Check cache with TTL
        if code_url in self._online_cache:
            cached_issue, cached_time = self._online_cache[code_url]
            age = (datetime.utcnow() - cached_time).total_seconds()
            if age < self.settings.wmo_registry_cache_ttl:
                logger.debug(f"Online validation cache hit: {code_url} (age: {age:.0f}s)")
                # Update location for cached issue
                cached_issue.location = xpath
                return cached_issue

        # Fetch from registry
        try:
            logger.info(f"Validating code online: {code_url}")
            if requests is None:
                return ValidationIssue(
                    layer=ValidationLayer.WMO_CODELISTS,
                    level=ValidationSeverity.WARNING,
                    message="Online validation unavailable: requests library not installed",
                    location=xpath,
                    code="CODELIST_REQUESTS_UNAVAILABLE",
                )
            response = requests.get(
                code_url, timeout=self.settings.wmo_validation_timeout, headers={"Accept": "application/rdf+xml"}
            )

            if response.status_code == 200:
                # Parse RDF and extract status
                status = self._parse_rdf_status(response.content)

                if status in ["valid", "stable"]:
                    result = ValidationIssue(
                        layer=ValidationLayer.WMO_CODELISTS,
                        level=ValidationSeverity.INFO,
                        message=f"Code validated online: {code_url} (status: {status})",
                        location=xpath,
                        code="CODELIST_VALID_ONLINE",
                    )
                elif status in ["superseded", "deprecated"]:
                    result = ValidationIssue(
                        layer=ValidationLayer.WMO_CODELISTS,
                        level=ValidationSeverity.WARNING,
                        message=f"Code status '{status}': {code_url}",
                        location=xpath,
                        code="CODELIST_DEPRECATED",
                    )
                else:
                    result = ValidationIssue(
                        layer=ValidationLayer.WMO_CODELISTS,
                        level=ValidationSeverity.WARNING,
                        message=f"Code status unknown ('{status}'): {code_url}",
                        location=xpath,
                        code="CODELIST_STATUS_UNKNOWN",
                    )

                # Cache result
                self._online_cache[code_url] = (result, datetime.utcnow())
                return result

            elif response.status_code == 404:
                result = ValidationIssue(
                    layer=ValidationLayer.WMO_CODELISTS,
                    level=ValidationSeverity.ERROR,
                    message=f"Code not found in WMO registry: {code_url}",
                    location=xpath,
                    code="CODELIST_NOT_FOUND",
                )
                self._online_cache[code_url] = (result, datetime.utcnow())
                return result
            else:
                return ValidationIssue(
                    layer=ValidationLayer.WMO_CODELISTS,
                    level=ValidationSeverity.WARNING,
                    message=f"Registry returned {response.status_code}: {code_url}",
                    location=xpath,
                    code="CODELIST_ONLINE_ERROR",
                )

        except Exception as e:
            timeout_error = getattr(getattr(requests, "exceptions", requests), "Timeout", None)
            if timeout_error is not None and isinstance(e, timeout_error):
                logger.warning(f"Online validation timeout for {code_url}")
                return ValidationIssue(
                    layer=ValidationLayer.WMO_CODELISTS,
                    level=ValidationSeverity.WARNING,
                    message=f"Online validation timeout ({self.settings.wmo_validation_timeout}s): {code_url}",
                    location=xpath,
                    code="CODELIST_TIMEOUT",
                )
            logger.error(f"Online validation error: {e}")
            return ValidationIssue(
                layer=ValidationLayer.WMO_CODELISTS,
                level=ValidationSeverity.WARNING,
                message=f"Online validation failed: {str(e)}",
                location=xpath,
                code="CODELIST_ONLINE_FAILED",
            )

    def _parse_rdf_status(self, rdf_content: bytes) -> str:
        """
        Extract concept status from RDF/XML response.

        Args:
            rdf_content: Raw RDF/XML content from registry

        Returns:
            Status string (e.g., 'valid', 'stable', 'superseded', 'deprecated')
        """
        try:
            root = etree.fromstring(rdf_content)

            # SKOS concept status in RDF
            # <skos:Concept>
            #   <reg:status rdf:resource="http://codes.wmo.int/common/reg-status/valid"/>
            # </skos:Concept>
            namespaces = {
                "reg": "http://purl.org/linked-data/registry#",
                "skos": "http://www.w3.org/2004/02/skos/core#",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            }

            # Find status element
            status_elems = root.xpath(".//reg:status/@rdf:resource", namespaces=namespaces)
            if status_elems:
                status_url = status_elems[0]
                # Extract last part: .../reg-status/valid -> "valid"
                status = status_url.split("/")[-1] if status_url else "unknown"
                logger.debug(f"Parsed RDF status: {status}")
                return status

            # Fallback: if no explicit status, assume valid if concept exists
            concepts = root.xpath(".//skos:Concept", namespaces=namespaces)
            if concepts:
                logger.debug("No explicit status, assuming 'valid' (concept exists)")
                return "valid"

            return "unknown"
        except Exception as e:
            logger.warning(f"Failed to parse RDF status: {e}")
            return "unknown"


class CodeListRegistry:
    """
    Registry for version-specific code list parsers.

    Maintains separate CodeListParser instances for each IWXXM version.
    """

    def __init__(self):
        self._parsers: Dict[str, CodeListParser] = {}

    def get_parser(self, version: str, codelists_dir: Path) -> CodeListParser:
        """
        Get or create a code list parser for a version.

        Args:
            version: IWXXM version string
            codelists_dir: Path to codelists directory for this version

        Returns:
            CodeListParser instance for the version
        """
        if version not in self._parsers:
            self._parsers[version] = CodeListParser(codelists_dir)
        return self._parsers[version]

    def validate_code(self, version: str, codelist_name: str, code_value: str, codelists_dir: Path) -> bool:
        """
        Validate a code value for a specific version and code list.

        Args:
            version: IWXXM version
            codelist_name: Name of the code list
            code_value: Code value to validate
            codelists_dir: Path to codelists directory

        Returns:
            True if code is valid
        """
        parser = self.get_parser(version, codelists_dir)
        return parser.validate_code(codelist_name, code_value)


# Global registry instance
_registry = CodeListRegistry()


def get_codelist_parser(version: str, codelists_dir: Path) -> CodeListParser:
    """Get code list parser for a specific IWXXM version."""
    return _registry.get_parser(version, codelists_dir)


def validate_xml_codelists(xml_content: str, version: str, codelists_dir: Path) -> CodelistValidationResult:
    """
    Convenience function to validate XML codelists.

    Args:
        xml_content: XML string to validate
        version: IWXXM version
        codelists_dir: Path to codelists directory

    Returns:
        CodelistValidationResult with validation outcomes
    """
    parser = get_codelist_parser(version, codelists_dir)
    return parser.validate_xml_codelists(xml_content)
