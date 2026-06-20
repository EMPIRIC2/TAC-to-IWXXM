"""
WMO IWXXM Canonical Examples Loader

Loads and catalogs official examples from mirrored WMO schema directories.
Each version at https://schemas.wmo.int/iwxxm/{version}/examples/ contains
60+ official TAC↔IWXXM translation pairs and edge case examples.
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class WMOExample:
    """Represents a single WMO canonical example."""

    example_id: str  # e.g., "metar-A3-1"
    version: str  # IWXXM version (e.g., "2025-2")
    message_type: str  # METAR, TAF, SIGMET, etc.
    xml_path: Path  # Path to XML file
    tac_path: Optional[Path] = None  # Path to TAC file (if exists)
    test_scenario: Optional[str] = None  # Description from filename
    is_nil_report: bool = False
    is_collect: bool = False  # COLLECT bulletin format
    is_translation_failed: bool = False  # Edge case examples
    metadata: Dict = field(default_factory=dict)


class WMOExamplesLoader:
    """
    Loads WMO canonical examples from mirrored schema directories.
    """

    MESSAGE_TYPE_PATTERNS = {
        "METAR": re.compile(r"^metar-", re.IGNORECASE),
        "SPECI": re.compile(r"^speci-", re.IGNORECASE),
        "TAF": re.compile(r"^taf-", re.IGNORECASE),
        "SIGMET": re.compile(r"^sigmet-", re.IGNORECASE),
        "AIRMET": re.compile(r"^airmet-", re.IGNORECASE),
        "TROPICAL_CYCLONE": re.compile(r"^tc-|^tropical", re.IGNORECASE),
        "VOLCANIC_ASH": re.compile(r"^va-|^volcanic", re.IGNORECASE),
        "SPACE_WEATHER": re.compile(r"^spacewx-|^swx-", re.IGNORECASE),
        "WAFS": re.compile(r"^wafs-", re.IGNORECASE),
        "VONA": re.compile(r"^vona-", re.IGNORECASE),
        "QVACI": re.compile(r"^qvaci-", re.IGNORECASE),
    }

    def __init__(self, schemas_base_path: Path):
        """
        Initialize the examples loader.

        Args:
            schemas_base_path: Base path for mirrored schemas (e.g., PROJECT_ROOT/schemas/iwxxm)
        """
        self.schemas_base_path = Path(schemas_base_path)

    def load_examples(self, version: str, message_types: Optional[List[str]] = None) -> List[WMOExample]:
        """
        Load all examples for a specific IWXXM version.

        Args:
            version: IWXXM version string (e.g., "2025-2")
            message_types: Optional filter for specific message types

        Returns:
            List of WMOExample objects
        """
        examples_dir = self.schemas_base_path / version / "examples"

        if not examples_dir.exists():
            logger.warning(f"Examples directory not found: {examples_dir}")
            return []

        examples = []
        xml_files = sorted(examples_dir.glob("*.xml"))

        for xml_file in xml_files:
            example_id = xml_file.stem
            message_type = self._detect_message_type(example_id)

            # Filter by message type if specified
            if message_types and message_type not in message_types:
                continue

            # Check for corresponding TAC file
            tac_file = xml_file.with_suffix(".tac")
            tac_path = tac_file if tac_file.exists() else None

            # Detect special scenarios
            is_nil = "nil" in example_id.lower()
            is_collect = "collect" in example_id.lower()
            is_translation_failed = "translation-failed" in example_id.lower()

            example = WMOExample(
                example_id=example_id,
                version=version,
                message_type=message_type,
                xml_path=xml_file,
                tac_path=tac_path,
                test_scenario=self._extract_scenario(example_id),
                is_nil_report=is_nil,
                is_collect=is_collect,
                is_translation_failed=is_translation_failed,
            )

            examples.append(example)

        logger.info(f"Loaded {len(examples)} examples for IWXXM {version}")
        return examples

    def load_all_versions(self, versions: Optional[List[str]] = None) -> Dict[str, List[WMOExample]]:
        """
        Load examples for multiple versions.

        Args:
            versions: List of version strings. If None, auto-detect from directories.

        Returns:
            Dictionary mapping version -> list of examples
        """
        if versions is None:
            versions = self._detect_available_versions()

        all_examples = {}
        for version in versions:
            examples = self.load_examples(version)
            if examples:
                all_examples[version] = examples

        return all_examples

    def get_tac_xml_pairs(self, version: str, message_type: Optional[str] = None) -> List[Tuple[Path, Path, str]]:
        """
        Get TAC↔XML pairs for testing roundtrip conversions.

        Args:
            version: IWXXM version
            message_type: Optional message type filter

        Returns:
            List of (tac_path, xml_path, example_id) tuples
        """
        examples = self.load_examples(version)
        pairs = []

        for example in examples:
            if example.tac_path and example.tac_path.exists():
                if message_type is None or example.message_type == message_type:
                    pairs.append((example.tac_path, example.xml_path, example.example_id))

        return pairs

    def load_guidance_document(self, version: str) -> Optional[str]:
        """
        Load TAC-to-XML-Guidance.txt if available.

        Args:
            version: IWXXM version

        Returns:
            Guidance document content or None if not found
        """
        guidance_file = self.schemas_base_path / version / "examples" / "TAC-to-XML-Guidance.txt"

        if guidance_file.exists():
            return guidance_file.read_text(encoding="utf-8")

        return None

    def get_example_manifest(self, version: str) -> Dict:
        """
        Generate manifest of all examples for a version.

        Args:
            version: IWXXM version

        Returns:
            Manifest dictionary with counts and categories
        """
        examples = self.load_examples(version)

        manifest = {
            "version": version,
            "total_examples": len(examples),
            "by_message_type": {},
            "with_tac_pairs": 0,
            "nil_reports": 0,
            "collect_bulletins": 0,
            "translation_failed_cases": 0,
        }

        for example in examples:
            # Count by message type
            msg_type = example.message_type
            manifest["by_message_type"][msg_type] = manifest["by_message_type"].get(msg_type, 0) + 1

            # Count special cases
            if example.tac_path:
                manifest["with_tac_pairs"] += 1
            if example.is_nil_report:
                manifest["nil_reports"] += 1
            if example.is_collect:
                manifest["collect_bulletins"] += 1
            if example.is_translation_failed:
                manifest["translation_failed_cases"] += 1

        return manifest

    def _detect_message_type(self, example_id: str) -> str:
        """
        Detect message type from example filename.

        Args:
            example_id: Example ID (filename without extension)

        Returns:
            Message type string
        """
        for msg_type, pattern in self.MESSAGE_TYPE_PATTERNS.items():
            if pattern.match(example_id):
                return msg_type

        return "UNKNOWN"

    def _extract_scenario(self, example_id: str) -> Optional[str]:
        """
        Extract test scenario description from example ID.

        Args:
            example_id: Example ID

        Returns:
            Scenario description or None
        """
        # Remove message type prefix and extract scenario
        parts = example_id.split("-", 1)
        if len(parts) > 1:
            return parts[1]
        return None

    def _detect_available_versions(self) -> List[str]:
        """
        Auto-detect available versions from schemas directory.

        Returns:
            List of version strings that have examples directories
        """
        versions = []

        if not self.schemas_base_path.exists():
            return versions

        for version_dir in self.schemas_base_path.iterdir():
            if version_dir.is_dir() and (version_dir / "examples").exists():
                versions.append(version_dir.name)

        return sorted(versions)


def load_wmo_examples(
    version: str, schemas_base_path: Path, message_types: Optional[List[str]] = None
) -> List[WMOExample]:
    """
    Convenience function to load WMO examples.

    Args:
        version: IWXXM version
        schemas_base_path: Base path for schemas
        message_types: Optional message type filter

    Returns:
        List of WMOExample objects
    """
    loader = WMOExamplesLoader(schemas_base_path)
    return loader.load_examples(version, message_types)
