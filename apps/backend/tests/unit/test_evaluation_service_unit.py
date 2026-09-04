"""Unit tests for evaluation service comparison logic."""

from __future__ import annotations

from src.services.evaluation_service import EvaluationService


def test_compare_iwxxm_parse_error_returns_failed():
    service = EvaluationService()

    result = service.compare_iwxxm("<root>", "<root/>")

    assert result.passed is False
    assert "XML parse error" in (result.error_message or "")


def test_strip_dynamic_attrs_removes_ids_and_schema_location():
    service = EvaluationService()
    xml = """
    <root id="abc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="x y">
      <child uuid="u1" keep="yes" />
    </root>
    """

    import xml.etree.ElementTree as ET

    elem = ET.fromstring(xml)
    service.strip_dynamic_attrs(elem)

    assert "id" not in elem.attrib
    assert "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation" not in elem.attrib
    child = next(iter(elem))
    assert "uuid" not in child.attrib
    assert child.attrib["keep"] == "yes"


def test_compare_iwxxm_detects_missing_extra_and_mismatch():
    service = EvaluationService()

    our = "<root><a>one</a><extra>z</extra></root>"
    theirs = "<root><a>two</a><missing>x</missing></root>"

    result = service.compare_iwxxm(our, theirs)

    assert result.passed is False
    assert result.missing_elements
    assert result.extra_elements
    assert any(m["type"] == "text" for m in result.value_mismatches)


def test_compare_iwxxm_passes_when_structurally_equal_after_normalization():
    service = EvaluationService()

    our = "<root id='a'><a> one   two </a></root>"
    theirs = "<root id='b'><a>one two</a></root>"

    result = service.compare_iwxxm(our, theirs)

    assert result.passed is True
    assert result.missing_elements == []
    assert result.extra_elements == []
    assert result.value_mismatches == []
