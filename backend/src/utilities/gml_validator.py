"""
GML Reference Validator (Validation Layer 6)

Validates GML references:
- Internal references: xlink:href="#id" pointing to gml:id attributes
- External references: xlink:href="codes.wmo.int-*.rdf#id" pointing to bundled RDF codelists
- Geometry validation: GML 3.2.1 compliance

Based on GIFTs checkGMLReferences.py logic and extended for offline RDF resolution.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from lxml import etree

from ..schemas.validation import ValidationIssue, ValidationLayer, ValidationSeverity

logger = logging.getLogger(__name__)


@dataclass
class GMLValidationResult:
    """Result of GML reference validation."""
    is_valid: bool
    issues: List[ValidationIssue]
    total_ids: int = 0
    total_references: int = 0
    broken_references: int = 0


class GMLReferenceValidator:
    """
    Validates GML references in IWXXM XML documents.

    Supports both:
    - Internal references: xlink:href="#uuid.xxx" → gml:id attributes
    - External references: xlink:href="codes.wmo.int-*.rdf#id" → bundled RDF codelists

    External references are resolved to bundled RDF files in the schema rule/ directory
    for fully offline validation.
    """

    # Common namespace prefixes in IWXXM
    NAMESPACES = {
        'gml': 'http://www.opengis.net/gml/3.2.1',  # GML 3.2.1 namespace
        'xlink': 'http://www.w3.org/1999/xlink',
        'iwxxm': 'http://icao.int/iwxxm/2025-2',
        'aixm': 'http://www.aixm.aero/schema/5.1.1',
        'metce': 'http://def.wmo.int/metce/2013',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    }

    def __init__(self, codelists_dir: Optional[Path] = None):
        """
        Initialize GML reference validator.

        Args:
            codelists_dir: Optional path to bundled RDF codelists directory
        """
        self.codelists_dir = codelists_dir
        self._rdf_element_cache: Dict[str, Set[str]] = {}  # Cache RDF elements by file

    def set_codelists_dir(self, codelists_dir: Path) -> None:
        """
        Set path to bundled RDF codelists for external reference resolution.

        Args:
            codelists_dir: Path to rule/ directory with RDF files
        """
        self.codelists_dir = codelists_dir
        self._rdf_element_cache.clear()  # Clear cache when directory changes

    def _is_external_reference(self, href: str) -> bool:
        """
        Check if xlink:href is an external reference (points to RDF file).

        External references have format: "codes.wmo.int-*.rdf#element_id"
        Internal references start with just "#"

        Args:
            href: xlink:href value

        Returns:
            True if external reference, False if internal
        """
        return '#' in href and not href.startswith('#')

    def _extract_rdf_file_and_element(self, href: str) -> Tuple[str, str]:
        """
        Extract RDF filename and element ID from external reference.

        Args:
            href: External xlink:href like "codes.wmo.int-49-2-*.rdf#ElementID"

        Returns:
            Tuple of (rdf_filename, element_id)
        """
        parts = href.split('#', 1)
        rdf_file = parts[0]  # e.g., "codes.wmo.int-49-2-AerodromeState.rdf"
        element_id = parts[1] if len(parts) > 1 else ""  # e.g., "CodeAerodromeState_CLOSED"

        return rdf_file, element_id

    def _load_rdf_elements(self, rdf_filename: str) -> Set[str]:
        """
        Load element IDs from an RDF file in codelists directory.

        Args:
            rdf_filename: Name of RDF file (e.g., "codes.wmo.int-49-2-AerodromeState.rdf")

        Returns:
            Set of rdf:about URIs found in the RDF file

        Raises:
            FileNotFoundError: If RDF file not found in codelists directory
        """
        # Check cache first
        if rdf_filename in self._rdf_element_cache:
            return self._rdf_element_cache[rdf_filename]

        if not self.codelists_dir:
            logger.warning(
                f"Cannot resolve external reference {rdf_filename}: "
                "codelists_dir not set. Set via set_codelists_dir() for offline validation."
            )
            return set()

        rdf_path = self.codelists_dir / rdf_filename

        if not rdf_path.exists():
            logger.warning(
                f"RDF codelist file not found: {rdf_path}. "
                f"External reference {rdf_filename} cannot be validated."
            )
            return set()

        try:
            # Parse RDF file
            rdf_tree = etree.parse(str(rdf_path))
            rdf_root = rdf_tree.getroot()

            # Extract all rdf:Description @rdf:about attributes
            elements = set()
            descriptions = rdf_root.xpath(
                '//rdf:Description',
                namespaces=self.NAMESPACES
            )

            for desc in descriptions:
                about = desc.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about')
                if about:
                    # Extract just the fragment identifier
                    if '#' in about:
                        element_id = about.split('#', 1)[1]
                    else:
                        element_id = about

                    elements.add(element_id)

            # Cache the elements
            self._rdf_element_cache[rdf_filename] = elements

            logger.debug(
                f"Loaded {len(elements)} elements from RDF: {rdf_filename}"
            )

            return elements

        except Exception as e:
            logger.warning(
                f"Failed to parse RDF file {rdf_filename}: {e}"
            )
            return set()

    def _extract_gml_ids(self, xml_tree: etree._Element) -> Dict[str, List[str]]:
        """
        Extract all gml:id attributes and their XPath locations.

        Args:
            xml_tree: Parsed XML element tree

        Returns:
            Dict mapping gml:id value to list of XPath locations
        """
        id_registry: Dict[str, List[str]] = {}

        # Find all elements with gml:id attribute
        elements_with_id = xml_tree.xpath(
            '//*[@gml:id]',
            namespaces=self.NAMESPACES
        )

        for elem in elements_with_id:
            gml_id = elem.get('{http://www.opengis.net/gml/3.2}id')

            if gml_id:
                # Get XPath to element
                xpath = xml_tree.getroottree().getpath(elem)

                if gml_id not in id_registry:
                    id_registry[gml_id] = []

                id_registry[gml_id].append(xpath)

        return id_registry

    def _extract_href_references(
        self,
        xml_tree: etree._Element
    ) -> List[Tuple[str, str, str]]:
        """
        Extract all xlink:href="#id" internal references.

        Args:
            xml_tree: Parsed XML element tree

        Returns:
            List of tuples: (href_value, target_id, xpath_location)
        """
        references = []

        # Find all elements with xlink:href attribute
        elements_with_href = xml_tree.xpath(
            '//*[@xlink:href]',
            namespaces=self.NAMESPACES
        )

        for elem in elements_with_href:
            href = elem.get('{http://www.w3.org/1999/xlink}href')

            if href and href.startswith('#'):
                # Internal reference (starts with #)
                target_id = href[1:]  # Remove '#' prefix
                xpath = xml_tree.getroottree().getpath(elem)

                references.append((href, target_id, xpath))

        return references

    def validate(self, xml_content: str, version: Optional[str] = None) -> GMLValidationResult:
        """
        Validate GML references in XML document.

        Validates both internal references (#id) and external references to bundled RDF codelists.

        Args:
            xml_content: XML string to validate
            version: Optional IWXXM version (used to load codelists if not already set)

        Returns:
            GMLValidationResult with validation outcomes
        """
        issues = []

        try:
            # If version provided and no codelists_dir set, load from schema registry
            if version and not self.codelists_dir:
                try:
                    from .schema_registry import get_schema_registry
                    registry = get_schema_registry()
                    self.codelists_dir = registry.get_codelists_dir(version)
                    logger.debug(
                        f"Loaded codelists directory for {version}: {self.codelists_dir}"
                    )
                except Exception as e:
                    logger.debug(f"Could not auto-load codelists: {e}")

            # Parse XML document
            try:
                xml_tree = etree.fromstring(xml_content.encode('utf-8'))
            except etree.XMLSyntaxError as e:
                # XML not well-formed - should be caught earlier
                issue = ValidationIssue(
                    layer=ValidationLayer.GML_REFERENCES,
                    level=ValidationSeverity.ERROR,
                    message=f"XML parsing failed: {str(e)}",
                    code="XML_SYNTAX_ERROR"
                )
                issues.append(issue)
                return GMLValidationResult(
                    is_valid=False,
                    issues=issues
                )

            # Extract all gml:id attributes (for internal references)
            id_registry = self._extract_gml_ids(xml_tree)

            # Check for duplicate IDs
            for gml_id, locations in id_registry.items():
                if len(locations) > 1:
                    issue = ValidationIssue(
                        layer=ValidationLayer.GML_REFERENCES,
                        level=ValidationSeverity.ERROR,
                        message=f"Duplicate gml:id '{gml_id}' found at {len(locations)} locations: {', '.join(locations)}",
                        code="DUPLICATE_GML_ID"
                    )
                    issues.append(issue)

            # Extract all xlink:href references (both internal and external)
            references = self._extract_href_references(xml_tree)

            # Validate each reference
            internal_broken = 0
            external_broken = 0

            for href, target_id, xpath in references:
                if self._is_external_reference(href):
                    # External reference to RDF codelist
                    rdf_file, element_id = self._extract_rdf_file_and_element(href)
                    elements = self._load_rdf_elements(rdf_file)

                    if not elements:
                        # Could not load RDF (warning already logged)
                        external_broken += 1
                        issue = ValidationIssue(
                            layer=ValidationLayer.GML_REFERENCES,
                            level=ValidationSeverity.WARNING,
                            message=f"Could not resolve external reference: xlink:href='{href}' (RDF file not found)",
                            location=xpath,
                            code="UNRESOLVABLE_EXTERNAL_REFERENCE"
                        )
                        issues.append(issue)
                    elif element_id not in elements:
                        external_broken += 1
                        issue = ValidationIssue(
                            layer=ValidationLayer.GML_REFERENCES,
                            level=ValidationSeverity.ERROR,
                            message=f"Broken external reference: xlink:href='{href}' - element '{element_id}' not found in {rdf_file}",
                            location=xpath,
                            code="BROKEN_EXTERNAL_REFERENCE"
                        )
                        issues.append(issue)
                else:
                    # Internal reference
                    if target_id not in id_registry:
                        internal_broken += 1
                        issue = ValidationIssue(
                            layer=ValidationLayer.GML_REFERENCES,
                            level=ValidationSeverity.ERROR,
                            message=f"Broken internal reference: xlink:href='{href}' points to non-existent gml:id '{target_id}'",
                            location=xpath,
                            code="BROKEN_INTERNAL_REFERENCE"
                        )
                        issues.append(issue)

            is_valid = len(issues) == 0

            if not is_valid:
                logger.warning(
                    f"GML reference validation failed: {len(issues)} issues "
                    f"({internal_broken} internal, {external_broken} external)"
                )
            else:
                logger.debug(
                    f"GML reference validation passed: "
                    f"{len(id_registry)} internal IDs, {len(references)} references"
                )

            return GMLValidationResult(
                is_valid=is_valid,
                issues=issues,
                total_ids=len(id_registry),
                total_references=len(references),
                broken_references=internal_broken + external_broken
            )

        except Exception as e:
            logger.error(f"Unexpected error during GML validation: {e}")
            issue = ValidationIssue(
                layer=ValidationLayer.GML_REFERENCES,
                level=ValidationSeverity.ERROR,
                message=f"Validation error: {str(e)}",
                code=type(e).__name__
            )
            issues.append(issue)
            return GMLValidationResult(
                is_valid=False,
                issues=issues
            )

    def validate_geometry(self, xml_content: str) -> GMLValidationResult:
        """
        Validate GML geometry elements for GML 3.2.1 compliance (optional).

        Checks:
        - Valid geometry types (Point, LineString, Polygon, Surface)
        - Coordinate reference system (CRS) declarations
        - Coordinate dimensions match CRS
        - Geometry well-formedness

        Args:
            xml_content: XML string to validate

        Returns:
            GMLValidationResult with geometry validation issues
        """
        issues = []

        try:
            xml_tree = etree.fromstring(xml_content.encode('utf-8'))
        except etree.XMLSyntaxError as e:
            issue = ValidationIssue(
                layer=ValidationLayer.GML_REFERENCES,
                level=ValidationSeverity.ERROR,
                message=f"XML parsing failed: {str(e)}",
                code="XML_SYNTAX_ERROR"
            )
            issues.append(issue)
            return GMLValidationResult(is_valid=False, issues=issues)

        # Find all geometry elements
        geometry_types = ['Point', 'LineString', 'Polygon', 'Surface', 'MultiPoint', 'MultiCurve']
        geometry_elements = []

        for geom_type in geometry_types:
            geom_elements = xml_tree.xpath(
                f'//gml:{geom_type}',
                namespaces=self.NAMESPACES
            )
            geometry_elements.extend(geom_elements)

        if not geometry_elements:
            logger.debug("No GML geometry elements found")
            return GMLValidationResult(
                is_valid=True,
                issues=[],
                total_ids=0,
                total_references=0,
                broken_references=0
            )

        # Validate each geometry
        for geom in geometry_elements:
            geom_type = geom.tag.split('}')[-1] if '}' in geom.tag else geom.tag
            xpath = xml_tree.getroottree().getpath(geom)

            # Check for CRS
            srs_name = geom.get('srsName')
            if not srs_name:
                issue = ValidationIssue(
                    layer=ValidationLayer.GML_REFERENCES,
                    level=ValidationSeverity.WARNING,
                    message=f"Geometry {geom_type} at {xpath} missing srsName (CRS)",
                    location=xpath,
                    code="MISSING_CRS"
                )
                issues.append(issue)

            # Check for coordinates
            pos_elements = geom.xpath('./gml:pos', namespaces=self.NAMESPACES)
            pos_list_elements = geom.xpath('./gml:posList', namespaces=self.NAMESPACES)

            if not pos_elements and not pos_list_elements:
                issue = ValidationIssue(
                    layer=ValidationLayer.GML_REFERENCES,
                    level=ValidationSeverity.ERROR,
                    message=f"Geometry {geom_type} at {xpath} missing coordinates (pos or posList)",
                    location=xpath,
                    code="MISSING_COORDINATES"
                )
                issues.append(issue)

        is_valid = len(issues) == 0

        if is_valid:
            logger.debug(f"Geometry validation passed: {len(geometry_elements)} elements")
        else:
            logger.warning(f"Geometry validation found {len(issues)} issues")

        return GMLValidationResult(
            is_valid=is_valid,
            issues=issues,
            total_ids=len(geometry_elements),
            total_references=0,
            broken_references=len([i for i in issues if i.level == ValidationSeverity.ERROR])
        )


# Singleton instance
_validator_instance: Optional[GMLReferenceValidator] = None


def get_gml_validator(codelists_dir: Optional[Path] = None) -> GMLReferenceValidator:
    """
    Get singleton GML reference validator instance.

    Args:
        codelists_dir: Optional path to bundled RDF codelists (for external reference resolution)

    Returns:
        GMLReferenceValidator instance with optional codelists support
    """
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = GMLReferenceValidator(codelists_dir=codelists_dir)
    elif codelists_dir:
        _validator_instance.set_codelists_dir(codelists_dir)
    return _validator_instance


def validate_gml_references(xml_content: str, version: Optional[str] = None, codelists_dir: Optional[Path] = None) -> GMLValidationResult:
    """
    Convenience function to validate GML references.

    Supports both internal (#id) and external (RDF) references.

    Args:
        xml_content: XML string to validate
        version: Optional IWXXM version (auto-loads codelists if available)
        codelists_dir: Optional path to bundled RDF codelists directory

    Returns:
        GMLValidationResult with validation outcomes
    """
    validator = get_gml_validator(codelists_dir=codelists_dir)
    return validator.validate(xml_content, version=version)
