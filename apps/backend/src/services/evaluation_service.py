"""Service for comparing IWXXM outputs."""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any


@dataclass
class ComparisonResult:
    """Result of IWXXM comparison."""

    passed: bool
    our_elements: int
    their_elements: int
    missing_elements: list[str]
    extra_elements: list[str]
    value_mismatches: list[dict[str, str]]
    error_message: str | None = None


class EvaluationService:
    """Service for evaluating METAR conversions."""

    @staticmethod
    def _local(tag: str) -> str:
        """Extract local tag name from qualified name."""
        if tag.startswith("{"):
            return tag.split("}", 1)[1]
        return tag

    @staticmethod
    def _norm_text(t: str | None) -> str:
        """Normalize text by collapsing whitespace."""
        if t is None:
            return ""
        return " ".join(t.split())

    @staticmethod
    def strip_dynamic_attrs(elem: ET.Element) -> None:
        """Remove dynamic attributes from XML element tree.

        Removes: id, schemaLocation, UUID-like values, timestamps
        """
        for a in list(elem.attrib.keys()):
            local_name = EvaluationService._local(a)
            if local_name in {"id", "schemaLocation", "uuid"}:
                elem.attrib.pop(a, None)

        for child in list(elem):
            EvaluationService.strip_dynamic_attrs(child)

    def compare_iwxxm(self, our_xml: str, their_xml: str, strict: bool = False) -> ComparisonResult:
        """Compare two IWXXM XML documents.

        Args:
            our_xml: XML from our conversion
            their_xml: XML from aviationweather.gov
            strict: If True, require exact match; if False, allow version differences

        Returns:
            ComparisonResult with detailed comparison
        """
        try:
            our_tree = ET.fromstring(our_xml)
            their_tree = ET.fromstring(their_xml)
        except ET.ParseError as e:
            return ComparisonResult(
                passed=False,
                our_elements=0,
                their_elements=0,
                missing_elements=[],
                extra_elements=[],
                value_mismatches=[],
                error_message=f"XML parse error: {e!s}",
            )

        # Strip dynamic attributes before comparison
        self.strip_dynamic_attrs(our_tree)
        self.strip_dynamic_attrs(their_tree)

        # Count elements
        our_count = len(list(our_tree.iter()))
        their_count = len(list(their_tree.iter()))

        # Collect element paths
        our_paths = self._collect_element_paths(our_tree)
        their_paths = self._collect_element_paths(their_tree)

        # Find differences
        missing = [p for p in their_paths if p not in our_paths]
        extra = [p for p in our_paths if p not in their_paths]

        # Check for value mismatches in common elements
        value_mismatches = self._find_value_mismatches(our_tree, their_tree)

        # Determine pass/fail
        passed = len(missing) == 0 and len(extra) == 0 and len(value_mismatches) == 0

        return ComparisonResult(
            passed=passed,
            our_elements=our_count,
            their_elements=their_count,
            missing_elements=missing[:10],  # Limit to first 10
            extra_elements=extra[:10],
            value_mismatches=value_mismatches[:10],
            error_message=None,
        )

    def _collect_element_paths(self, root: ET.Element, prefix: str = "") -> list[str]:
        """Collect all element paths in the tree."""
        paths: list[str] = []
        local_tag = self._local(root.tag)
        current_path = f"{prefix}/{local_tag}" if prefix else local_tag
        paths.append(current_path)

        for child in root:
            paths.extend(self._collect_element_paths(child, current_path))

        return paths

    def _find_value_mismatches(
        self, our_tree: ET.Element, their_tree: ET.Element, path: str = ""
    ) -> list[dict[str, str]]:
        """Find value mismatches between trees."""
        mismatches: list[Any] = []

        our_tag = self._local(our_tree.tag)
        their_tag = self._local(their_tree.tag)

        if our_tag != their_tag:
            return mismatches

        current_path = f"{path}/{our_tag}" if path else our_tag

        # Compare text content
        our_text = self._norm_text(our_tree.text)
        their_text = self._norm_text(their_tree.text)

        if our_text != their_text:
            mismatches.append(
                {
                    "path": current_path,
                    "our_value": our_text[:100],  # Truncate
                    "their_value": their_text[:100],
                    "type": "text",
                }
            )

        # Compare matching children
        our_children = list(our_tree)
        their_children = list(their_tree)

        min_children = min(len(our_children), len(their_children))
        for i in range(min_children):
            child_mismatches = self._find_value_mismatches(our_children[i], their_children[i], current_path)
            mismatches.extend(child_mismatches)

        return mismatches
