"""
WMO Canonical Examples Validation Tests

Validates official WMO examples from schemas.wmo.int/{version}/examples/
against comprehensive validation pipeline (XSD, Schematron, GML, Codelists).

These are the gold standard reference examples - 100% should validate successfully.
"""

from pathlib import Path
from typing import List

import pytest

from src.config.iwxxm_versions import get_versions_by_channel
from src.config.test_corpus_sources import get_corpus_path
from src.utilities.wmo_examples_loader import WMOExample, WMOExamplesLoader

# Project root (4 levels up from test file to repository root, not backend)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Vendor / mirror base: …/iwxxm/{version}/IWXXM/examples → parents[2] == …/iwxxm
SCHEMAS_BASE = get_corpus_path("wmo_canonical_examples", version="2025-2").parents[2]


@pytest.fixture(scope="module")
def examples_loader():
    """Fixture providing WMO examples loader."""
    return WMOExamplesLoader(SCHEMAS_BASE)


@pytest.fixture(scope="module")
def test_versions():
    """Fixture providing IWXXM versions to test."""
    # Test stable versions only by default
    versions = get_versions_by_channel("stable")
    return versions


def collect_wmo_examples(versions: List[str]) -> List[tuple]:
    """
    Collect all WMO canonical examples for parametrization.

    Returns:
        List of (version, example) tuples for pytest.parametrize
    """
    loader = WMOExamplesLoader(SCHEMAS_BASE)
    test_cases = []

    for version in versions:
        examples = loader.load_examples(version)
        if not examples:
            # Skip versions without mirrored / vendor examples
            print(f"Note: Examples not available for {version}. Check vendor/schemas/iwxxm pin.")
            continue

        for example in examples:
            test_cases.append((version, example))

    return test_cases


# Collect examples at module load time
TEST_VERSIONS = get_versions_by_channel("stable")
WMO_EXAMPLES = collect_wmo_examples(TEST_VERSIONS)


class TestWMOCanonicalExamplesValidation:
    """
    Validate all official WMO canonical examples.

    These examples must pass all validation layers as they are the
    gold standard reference implementations.
    """

    @pytest.mark.parametrize("version,example", WMO_EXAMPLES)
    def test_example_xml_well_formed(self, version: str, example: WMOExample):
        """Verify example XML is well-formed."""
        import xml.etree.ElementTree as ET

        try:
            ET.parse(example.xml_path)
        except ET.ParseError as e:
            pytest.fail(f"XML parse error in {example.example_id}: {e}")

    @pytest.mark.parametrize("version,example", WMO_EXAMPLES)
    def test_example_xsd_validation(self, version: str, example: WMOExample):
        """Verify example passes XSD schema validation."""
        from src.utilities.xsd_validator import validate_iwxxm_xml

        xml_content = example.xml_path.read_text()
        result = validate_iwxxm_xml(xml_content, version=version)

        assert result.is_valid, f"XSD validation failed for {example.example_id}:\n{result.error_message}"

    @pytest.mark.parametrize("version,example", WMO_EXAMPLES)
    @pytest.mark.skip(reason="Schematron validator enhancement pending")
    def test_example_schematron_validation(self, version: str, example: WMOExample):
        """Verify example passes Schematron validation with local RDF codelists."""
        from src.utilities.schematron_validator import validate_with_schematron

        xml_content = example.xml_path.read_text()
        result = validate_with_schematron(xml_content, version=version)

        # Translation-failed examples are expected to fail
        if example.is_translation_failed:
            return

        assert result.is_valid, (
            f"Schematron validation failed for {example.example_id}:\n"
            f"Failed rules: {[r.rule_id for r in result.failed_rules]}"
        )

    @pytest.mark.parametrize("version,example", WMO_EXAMPLES)
    def test_example_gml_validation(self, version: str, example: WMOExample):
        """Verify example passes GML validation (internal + external references)."""
        from src.utilities.gml_validator import validate_gml_references

        xml_content = example.xml_path.read_text()
        result = validate_gml_references(xml_content, version=version)

        # Translation-failed examples are expected to fail
        if example.is_translation_failed:
            return

        assert result.is_valid, (
            f"GML validation failed for {example.example_id}:\n"
            f"Broken references: {result.broken_references}\n"
            f"Issues: {[i.message for i in result.issues]}"
        )


# Product-in-scope WMO stems with TAC peers (S031/EV-024 · TC-EV024-007).
# Roadmap SWX/VONA/WAFS/QVACI and TC SIGMET A6-2 are intentionally excluded.
EV024_IN_SCOPE_STEMS = (
    "metar-A3-1",
    "speci-A3-2",
    "taf-A5-1",
    "taf-A5-2",
    "sigmet-A6-1a-TS",
    "sigmet-A6-1b-CNL",
    "sigmet-VA-EGGX",
    "sigmet-multi-location-VA",
    "airmet-A6-1a-TS",
    "va-advisory-A7-2",
    "tc-advisory-A2-2",
)

# Convert soft-compare done for multi-location VA (TC-EV025-008); ADR-032 M-golden
# equality / wmoPass still pending (TC-EV025-009 / #809). Validate XML still required.
EV024_CONVERT_DEFERRED_STEMS = frozenset(
    {
        "sigmet-multi-location-VA",  # soft-compare green; equality/wmoPass pending
        "sigmet-A6-2-TC",  # #738 quality bar
    }
)


class TestWMOExamplesManifest:
    """
    Tests for example manifests and coverage.
    """

    def test_examples_exist_for_all_versions(self, test_versions, examples_loader):
        """Verify examples directory exists for all supported versions."""
        missing_versions = []

        for version in test_versions:
            if not examples_loader.load_examples(version):
                missing_versions.append(version)

        if missing_versions:
            pytest.skip(
                f"Examples not available for: {', '.join(missing_versions)}. "
                f"Check vendor/schemas/iwxxm pin or mirror service."
            )

    def test_example_counts_reasonable(self, test_versions, examples_loader):
        """Verify each version has reasonable number of examples (>20)."""
        for version in test_versions:
            examples = examples_loader.load_examples(version)
            if not examples:
                continue

            assert len(examples) >= 20, f"Too few examples for {version}: {len(examples)} (expected at least 20)"

    def test_tac_xml_pairs_exist(self, test_versions, examples_loader):
        """Verify TAC↔XML pairs exist for conversion testing."""
        for version in test_versions:
            if not examples_loader.load_examples(version):
                continue

            pairs = examples_loader.get_tac_xml_pairs(version)
            assert len(pairs) >= 10, f"Too few TAC↔XML pairs for {version}: {len(pairs)} (expected at least 10)"

    def test_message_type_coverage(self, test_versions, examples_loader):
        """Verify examples cover primary message types."""
        required_types = {"METAR", "TAF", "SIGMET"}

        for version in test_versions:
            if not examples_loader.load_examples(version):
                continue

            manifest = examples_loader.get_example_manifest(version)
            covered_types = set(manifest["by_message_type"].keys())

            missing = required_types - covered_types
            assert not missing, f"Missing message types in {version}: {missing}"

    def test_guidance_document_exists(self, test_versions, examples_loader):
        """Verify TAC-to-XML-Guidance.txt exists."""
        guidance_found = {}

        for version in test_versions:
            if not examples_loader.load_examples(version):
                continue

            guidance = examples_loader.load_guidance_document(version)
            guidance_found[version] = guidance is not None

        if guidance_found:
            # At least one version should have guidance
            assert any(guidance_found.values()), "TAC-to-XML-Guidance.txt not found in any version"

    def test_ev024_in_scope_stems_loaded_with_tac(self, examples_loader):
        """TC-EV024-007: in-scope product stems exist as TAC↔XML pairs under the pin."""
        examples = examples_loader.load_examples("2025-2")
        if not examples:
            pytest.skip("Examples not available for 2025-2 under vendor/mirror")

        by_id = {ex.example_id: ex for ex in examples}
        missing = [stem for stem in EV024_IN_SCOPE_STEMS if stem not in by_id]
        assert not missing, f"Missing in-scope WMO stems: {missing}"

        no_tac = [stem for stem in EV024_IN_SCOPE_STEMS if by_id[stem].tac_path is None]
        assert not no_tac, f"In-scope stems missing TAC peers: {no_tac}"

        # Explicit VA reference stems (UJ-039 sample-menu wire)
        for stem in ("sigmet-VA-EGGX", "sigmet-multi-location-VA"):
            assert by_id[stem].message_type == "SIGMET"
            assert by_id[stem].is_translation_failed is False

    def test_ev024_convert_deferred_stems_documented(self, examples_loader):
        """TC-EV024-007: convert-deferred stems remain on validate inventory when present."""
        examples = examples_loader.load_examples("2025-2")
        if not examples:
            pytest.skip("Examples not available for 2025-2 under vendor/mirror")

        by_id = {ex.example_id: ex for ex in examples}
        for stem in EV024_CONVERT_DEFERRED_STEMS:
            if stem not in by_id:
                continue
            assert by_id[stem].xml_path.exists()


class TestWMOExamplesLoader:
    """
    Unit tests for WMOExamplesLoader utility.
    """

    def test_loader_initialization(self):
        """Test loader initializes correctly."""
        loader = WMOExamplesLoader(SCHEMAS_BASE)
        assert loader.schemas_base_path == SCHEMAS_BASE

    def test_message_type_detection(self, examples_loader):
        """Test message type detection from filenames."""
        test_cases = [
            ("metar-A3-1", "METAR"),
            ("speci-A3-2", "SPECI"),
            ("taf-A5-1", "TAF"),
            ("sigmet-A6-1a-TS", "SIGMET"),
            ("tc-advisory-1", "TROPICAL_CYCLONE"),
            ("spacewx-A7-3", "SPACE_WEATHER"),
        ]

        for example_id, expected_type in test_cases:
            detected_type = examples_loader._detect_message_type(example_id)
            assert detected_type == expected_type, f"Wrong type for {example_id}: {detected_type} != {expected_type}"

    def test_scenario_extraction(self, examples_loader):
        """Test scenario extraction from example IDs."""
        test_cases = [
            ("metar-A3-1", "A3-1"),
            ("taf-NIL-collect", "NIL-collect"),
            ("sigmet-translation-failed", "translation-failed"),
        ]

        for example_id, expected_scenario in test_cases:
            scenario = examples_loader._extract_scenario(example_id)
            assert scenario == expected_scenario


class TestWMOExamplesIntegration:
    """
    Integration tests for WMO examples with corpus sources.
    """

    def test_corpus_source_configuration(self):
        """Test wmo_canonical_examples corpus source is configured."""
        from src.config.test_corpus_sources import get_corpus_source

        config = get_corpus_source("wmo_canonical_examples")
        assert config["type"] == "mirrored"
        assert config["priority"] == "canonical"
        assert config["enabled"] is True

    def test_corpus_path_resolution(self):
        """Test corpus path resolves correctly with version placeholder."""
        from src.config.test_corpus_sources import get_corpus_path

        path = get_corpus_path("wmo_canonical_examples", version="2025-2")
        assert path == SCHEMAS_BASE / "2025-2" / "IWXXM" / "examples"
        assert "vendor" in path.parts
        assert path.name == "examples"

    def test_corpus_path_requires_version(self):
        """Test corpus path raises error without version."""
        from src.config.test_corpus_sources import get_corpus_path

        with pytest.raises(ValueError, match="Version required"):
            get_corpus_path("wmo_canonical_examples")
