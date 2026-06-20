"""Comprehensive unit tests for evaluation service."""

import xml.etree.ElementTree as ET

import pytest

from src.services.evaluation_service import ComparisonResult, EvaluationService


@pytest.mark.unit
class TestEvaluationServiceComprehensive:
    """Comprehensive tests for EvaluationService."""

    def test_compare_identical_simple_xml(self):
        """Test comparing two identical simple XML documents."""
        service = EvaluationService()
        xml = '<?xml version="1.0"?><root><element>value</element></root>'

        result = service.compare_iwxxm(xml, xml)

        assert result.passed is True
        assert result.our_elements == result.their_elements
        assert len(result.missing_elements) == 0
        assert len(result.extra_elements) == 0
        assert len(result.value_mismatches) == 0

    def test_compare_different_element_counts(self):
        """Test comparing XMLs with different element counts."""
        service = EvaluationService()

        xml1 = '<?xml version="1.0"?><root><a>1</a><b>2</b></root>'
        xml2 = '<?xml version="1.0"?><root><a>1</a><b>2</b><c>3</c></root>'

        result = service.compare_iwxxm(xml1, xml2)

        assert result.passed is False
        assert result.our_elements < result.their_elements
        assert len(result.missing_elements) > 0

    def test_compare_different_values(self):
        """Test comparing XMLs with different element values."""
        service = EvaluationService()

        xml1 = '<?xml version="1.0"?><root><temp>15</temp></root>'
        xml2 = '<?xml version="1.0"?><root><temp>20</temp></root>'

        result = service.compare_iwxxm(xml1, xml2)

        assert result.passed is False
        assert len(result.value_mismatches) > 0

    def test_strip_dynamic_attributes(self):
        """Test stripping of dynamic attributes."""
        service = EvaluationService()

        xml1 = '<?xml version="1.0"?><root id="uuid-123"><temp>15</temp></root>'
        xml2 = '<?xml version="1.0"?><root id="uuid-456"><temp>15</temp></root>'

        result = service.compare_iwxxm(xml1, xml2)

        assert result.passed is True

    def test_compare_complex_nested_xml(self):
        """Test comparing complex nested XML structures."""
        service = EvaluationService()

        xml1 = """<?xml version="1.0"?>
        <METAR>
            <observation>
                <temperature>15</temperature>
                <dewpoint>10</dewpoint>
            </observation>
        </METAR>"""

        xml2 = xml1

        result = service.compare_iwxxm(xml1, xml2)

        assert result.passed is True
        assert result.our_elements == result.their_elements

    def test_compare_invalid_xml(self):
        """Test handling of invalid XML."""
        service = EvaluationService()

        xml1 = "Not valid XML at all"
        xml2 = '<?xml version="1.0"?><root>valid</root>'

        result = service.compare_iwxxm(xml1, xml2)

        assert result.passed is False
        assert result.error_message is not None

    def test_compare_malformed_xml(self):
        """Test handling of malformed XML."""
        service = EvaluationService()

        xml1 = '<?xml version="1.0"?><root><unclosed>'
        xml2 = '<?xml version="1.0"?><root><element>value</element></root>'

        result = service.compare_iwxxm(xml1, xml2)

        assert result.passed is False
        assert result.error_message is not None

    def test_collect_element_paths(self):
        """Test element path collection."""
        service = EvaluationService()

        xml = "<root><child1><grandchild/></child1><child2/></root>"
        tree = ET.fromstring(xml)

        paths = service._collect_element_paths(tree)

        assert "root" in paths
        assert "root/child1" in paths
        assert "root/child1/grandchild" in paths
        assert "root/child2" in paths

    def test_norm_text(self):
        """Test text normalization."""
        service = EvaluationService()

        assert service._norm_text("  hello   world  ") == "hello world"
        assert service._norm_text("\n\t hello \n") == "hello"
        assert service._norm_text(None) == ""
        assert service._norm_text("") == ""

    def test_local_tag_extraction(self):
        """Test local tag name extraction from qualified names."""
        service = EvaluationService()

        assert service._local("{http://example.com}element") == "element"
        assert service._local("element") == "element"
        assert service._local("{ns}tag") == "tag"

    def test_missing_elements_limited_to_10(self):
        """Test that missing elements are limited to first 10."""
        service = EvaluationService()

        xml1 = '<?xml version="1.0"?><root><a>1</a></root>'
        xml2_elements = "".join([f"<elem{i}>{i}</elem{i}>" for i in range(15)])
        xml2 = f'<?xml version="1.0"?><root><a>1</a>{xml2_elements}</root>'

        result = service.compare_iwxxm(xml1, xml2)

        assert len(result.missing_elements) <= 10

    def test_value_mismatches_limited_to_10(self):
        """Test that value mismatches are limited to first 10."""
        service = EvaluationService()

        elems1 = "".join([f"<e{i}>a</e{i}>" for i in range(15)])
        elems2 = "".join([f"<e{i}>b</e{i}>" for i in range(15)])

        xml1 = f'<?xml version="1.0"?><root>{elems1}</root>'
        xml2 = f'<?xml version="1.0"?><root>{elems2}</root>'

        result = service.compare_iwxxm(xml1, xml2)

        assert len(result.value_mismatches) <= 10

    def test_comparison_result_dataclass(self):
        """Test ComparisonResult dataclass."""
        result = ComparisonResult(
            passed=True,
            our_elements=10,
            their_elements=10,
            missing_elements=[],
            extra_elements=[],
            value_mismatches=[],
            error_message=None,
        )

        assert result.passed is True
        assert result.our_elements == 10
        assert result.their_elements == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "unit"])
