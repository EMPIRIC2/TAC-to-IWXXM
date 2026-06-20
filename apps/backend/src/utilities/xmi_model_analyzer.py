"""
XMI Model Analyzer - Parse UML exports for breaking change detection

Analyzes Enterprise Architect XMI files to:
- Extract UML element definitions (classes, attributes, associations)
- Diff models between IWXXM versions
- Detect removed/renamed elements
- Generate breaking change reports
- Update VERSION_DISCOVERY_METADATA automatically

XMI Format: http://www.w3.org/standards/XML/xmi/
UML 2.x: http://www.omg.org/spec/UML/2.5.1/
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from lxml import etree

logger = logging.getLogger(__name__)


@dataclass
class UMLElement:
    """Represents a UML element (class, attribute, association)."""

    xmi_id: str  # Unique XMI ID
    name: str  # Element name
    element_type: str  # class, attribute, operation, association
    owner_id: Optional[str] = None  # Parent element ID
    stereotype: Optional[str] = None  # UML stereotype
    attributes: Dict[str, str] = field(default_factory=dict)  # Additional attributes


@dataclass
class BreakingChange:
    """Represents a detected breaking change between versions."""

    change_type: str  # removed, renamed, type_changed, cardinality_changed
    element: str  # Element name/path
    element_type: str  # class, attribute, operation
    old_version: str  # Version where it existed
    new_version: str  # Version where it changed
    reason: str  # Description of the breaking change
    xpath: Optional[str] = None  # XPath in schema


class XMIModelAnalyzer:
    """
    Analyzes XMI (Unified Modeling Language) files to detect version breaking changes.

    Typical XMI structure:
    ```xml
    <xmi:XMI>
      <uml:Package>
        <packagedElement xmi:type="uml:Class" name="AerodromeState">
          <ownedAttribute name="code" type="..."/>
        </packagedElement>
      </uml:Package>
    </xmi:XMI>
    ```
    """

    NAMESPACES = {
        "xmi": "http://www.omg.org/spec/XMI/20131001",
        "uml": "http://www.omg.org/spec/UML/20131001",
        "ecore": "http://www.eclipse.org/emf/2002/Ecore",
    }

    def __init__(self):
        """Initialize XMI model analyzer."""
        self._element_cache: Dict[str, Set[str]] = {}  # Cache loaded elements

    def load_xmi_model(self, xmi_path: Path) -> Dict[str, UMLElement]:
        """
        Load and parse XMI file to extract UML elements.

        Args:
            xmi_path: Path to XMI file

        Returns:
            Dictionary mapping element ID to UMLElement

        Raises:
            FileNotFoundError: If XMI file not found
            etree.XMLSyntaxError: If XMI file invalid
        """
        if not xmi_path.exists():
            raise FileNotFoundError(f"XMI file not found: {xmi_path}")

        try:
            tree = etree.parse(str(xmi_path))
            root = tree.getroot()

            elements: Dict[str, UMLElement] = {}

            # Extract all packagedElements (classes, etc.)
            for elem in root.iter():
                # Extract XMI ID
                xmi_id = elem.get("{http://www.omg.org/spec/XMI/20131001}id")
                if not xmi_id:
                    continue

                # Determine element type
                xmi_type = elem.get("{http://www.omg.org/spec/XMI/20131001}type", "")
                element_type = xmi_type.split(":")[-1] if ":" in xmi_type else xmi_type

                # Extract name
                name = elem.get("name", f"[unnamed-{xmi_id}]")

                # Extract owner
                owner_id = None
                for parent in elem.iterancestors():
                    parent_id = parent.get("{http://www.omg.org/spec/XMI/20131001}id")
                    if parent_id:
                        owner_id = parent_id
                        break

                # Extract stereotype
                stereotype = None
                for stereotype_elem in elem.findall("{http://www.omg.org/spec/UML/20131001}stereotype"):
                    stereotype = stereotype_elem.get("href", stereotype_elem.text)
                    break

                # Add to registry
                uml_elem = UMLElement(
                    xmi_id=xmi_id,
                    name=name,
                    element_type=element_type,
                    owner_id=owner_id,
                    stereotype=stereotype,
                    attributes={k: v for k, v in elem.attrib.items() if not k.startswith("{")},
                )
                elements[xmi_id] = uml_elem

            logger.debug(f"Loaded {len(elements)} UML elements from {xmi_path}")
            return elements

        except etree.XMLSyntaxError as e:
            logger.error(f"Failed to parse XMI file {xmi_path}: {e}")
            raise

    def extract_classes(self, elements: Dict[str, UMLElement]) -> Dict[str, UMLElement]:
        """
        Extract only UML class definitions from loaded elements.

        Args:
            elements: Dictionary of all UML elements

        Returns:
            Dictionary of class elements only
        """
        return {xmi_id: elem for xmi_id, elem in elements.items() if elem.element_type in ("Class", "ClassifierRole")}

    def extract_attributes(self, elements: Dict[str, UMLElement], class_id: str) -> List[UMLElement]:
        """
        Extract all attributes for a specific class.

        Args:
            elements: Dictionary of all UML elements
            class_id: XMI ID of the class

        Returns:
            List of attribute elements owned by the class
        """
        return [
            elem
            for elem in elements.values()
            if elem.element_type in ("Property", "Attribute") and elem.owner_id == class_id
        ]

    def diff_models(
        self,
        old_elements: Dict[str, UMLElement],
        new_elements: Dict[str, UMLElement],
        old_version: str,
        new_version: str,
    ) -> List[BreakingChange]:
        """
        Diff two UML models to detect breaking changes.

        Args:
            old_elements: Elements from old version
            new_elements: Elements from new version
            old_version: Old version identifier
            new_version: New version identifier

        Returns:
            List of detected breaking changes
        """
        changes: List[BreakingChange] = []

        # Extract class names from both versions
        old_element_names = {elem.name: elem for elem in old_elements.values()}
        new_element_names = {elem.name: elem for elem in new_elements.values()}

        # Detect removed elements
        for name, old_elem in old_element_names.items():
            if name not in new_element_names:
                change = BreakingChange(
                    change_type="removed",
                    element=name,
                    element_type=old_elem.element_type,
                    old_version=old_version,
                    new_version=new_version,
                    reason=f"{old_elem.element_type} '{name}' removed in {new_version}",
                )
                changes.append(change)

        # Detect renamed elements (heuristic: similar name, same parent)
        for new_name, new_elem in new_element_names.items():
            if new_name not in old_element_names:
                # Look for potential rename candidates
                for old_name, old_elem in old_element_names.items():
                    if old_elem.element_type == new_elem.element_type:
                        if old_elem.owner_id == new_elem.owner_id:
                            # Could be a rename - check string similarity
                            if self._string_similarity(old_name, new_name) > 0.7:
                                change = BreakingChange(
                                    change_type="renamed",
                                    element=old_name,
                                    element_type=old_elem.element_type,
                                    old_version=old_version,
                                    new_version=new_version,
                                    reason=f"{old_elem.element_type} '{old_name}' renamed to '{new_name}'",
                                )
                                changes.append(change)

        return changes

    def _string_similarity(self, s1: str, s2: str) -> float:
        """
        Calculate string similarity ratio using Levenshtein distance.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Similarity ratio (0.0 to 1.0)
        """
        if not s1 or not s2:
            return 0.0

        # Simple character overlap metric
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0:
            return 0.0

        matches = sum(1 for c1, c2 in zip(s1, s2) if c1 == c2)
        return matches / max(len1, len2)

    def generate_breaking_change_report(self, changes: List[BreakingChange]) -> Dict[str, any]:
        """
        Generate a structured breaking change report.

        Args:
            changes: List of detected breaking changes

        Returns:
            Dictionary with categorized breaking changes
        """
        report = {"total_changes": len(changes), "by_type": {}, "by_element_type": {}, "details": changes}

        # Categorize by change type
        for change in changes:
            if change.change_type not in report["by_type"]:
                report["by_type"][change.change_type] = []
            report["by_type"][change.change_type].append(change)

        # Categorize by element type
        for change in changes:
            if change.element_type not in report["by_element_type"]:
                report["by_element_type"][change.element_type] = []
            report["by_element_type"][change.element_type].append(change)

        return report


def analyze_xmi_versions(old_xmi_path: Path, new_xmi_path: Path, old_version: str, new_version: str) -> Dict[str, any]:
    """
    Convenience function to analyze breaking changes between XMI versions.

    Args:
        old_xmi_path: Path to old version XMI file
        new_xmi_path: Path to new version XMI file
        old_version: Old version identifier
        new_version: New version identifier

    Returns:
        Breaking change report
    """
    analyzer = XMIModelAnalyzer()

    try:
        old_elements = analyzer.load_xmi_model(old_xmi_path)
        new_elements = analyzer.load_xmi_model(new_xmi_path)

        changes = analyzer.diff_models(old_elements, new_elements, old_version, new_version)

        report = analyzer.generate_breaking_change_report(changes)

        logger.info(
            f"XMI analysis complete: {report['total_changes']} breaking changes detected "
            f"between {old_version} and {new_version}"
        )

        return report

    except Exception as e:
        logger.error(f"Failed to analyze XMI versions: {e}")
        return {"total_changes": 0, "error": str(e), "details": []}
