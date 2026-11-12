"""XML canonical FAILURE / edge paths."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from metar_shared.xml_canonical import (
    canonicalize_xml,
    compare_canonical_xml,
    diff_canonical_xml,
    strip_volatile_attributes,
)


def test_canonicalize_malformed_token_raises() -> None:
    with pytest.raises(ValueError, match="Cannot parse XML"):
        canonicalize_xml("<>")


def test_canonicalize_unclosed_xml_declaration_raises() -> None:
    with pytest.raises(ValueError, match="Cannot parse XML"):
        canonicalize_xml("<?xml")


def test_compare_canonical_xml_false_on_mismatch() -> None:
    assert compare_canonical_xml("<root><a/></root>", "<root><b/></root>") is False


def test_diff_canonical_xml_truncates_long_previews() -> None:
    left = "<root>" + "".join(f"<n{i}/>" for i in range(80)) + "</root>"
    right = "<root>" + "".join(f"<n{i}/>" for i in range(79)) + "<z/></root>"
    diff = diff_canonical_xml(left, right)
    assert diff is not None
    assert "..." in diff
    assert "expected canonical preview:" in diff
    assert "actual canonical preview:" in diff


def test_fragment_without_xmlns_uses_wrapper_then_compares() -> None:
    """Fragments lacking xmlns still parse via the IWXXM wrapper."""
    frag_a = "<iwxxm:observation><iwxxm:airTemperature>1</iwxxm:airTemperature></iwxxm:observation>"
    frag_b = "<iwxxm:observation><iwxxm:airTemperature>2</iwxxm:airTemperature></iwxxm:observation>"
    assert compare_canonical_xml(frag_a, frag_a) is True
    assert compare_canonical_xml(frag_a, frag_b) is False


def test_strip_volatile_attributes_removes_schema_location() -> None:
    xml = (
        '<root xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://icao.int/iwxxm/2025-2 iwxxm.xsd" '
        'keep="yes">'
        "<child/></root>"
    )
    root = ET.fromstring(xml)
    strip_volatile_attributes(root)
    assert not any("schemaLocation" in key for key in root.attrib)
    assert root.attrib.get("keep") == "yes"
