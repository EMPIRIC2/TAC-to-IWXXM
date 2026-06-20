"""Tests for canonical XML normalization (TC-M003 / REQ-018)."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from metar_shared.xml_canonical import (
    canonicalize_xml,
    compare_canonical_xml,
    diff_canonical_xml,
    iter_local_names,
    local_name,
    strip_volatile_attributes,
)


def test_local_name_strips_namespace() -> None:
    assert local_name("{http://example.com}METAR") == "METAR"
    assert local_name("iwxxm:observation") == "observation"


def test_canonicalize_xml_ignores_whitespace() -> None:
    compact = "<root><child>text</child></root>"
    spaced = """
    <root>
      <child>
        text
      </child>
    </root>
    """
    assert canonicalize_xml(compact) == canonicalize_xml(spaced)


def test_canonicalize_xml_order_insensitive_siblings() -> None:
    first = "<root><b v='2'/><a v='1'/></root>"
    second = "<root><a v='1'/><b v='2'/></root>"
    assert compare_canonical_xml(first, second)


def test_canonicalize_xml_strips_volatile_uuid_attrs() -> None:
    with_uuid = (
        '<iwxxm:observation gml:id="uuid.abc-123">'
        '<iwxxm:MeteorologicalAerodromeObservation gml:id="uuid.def-456">'
        "<iwxxm:airTemperature>15</iwxxm:airTemperature>"
        "</iwxxm:MeteorologicalAerodromeObservation></iwxxm:observation>"
    )
    without_uuid = (
        "<iwxxm:observation>"
        "<iwxxm:MeteorologicalAerodromeObservation>"
        "<iwxxm:airTemperature>15</iwxxm:airTemperature>"
        "</iwxxm:MeteorologicalAerodromeObservation></iwxxm:observation>"
    )
    assert compare_canonical_xml(with_uuid, without_uuid)


def test_diff_canonical_xml_reports_mismatch() -> None:
    diff = diff_canonical_xml("<root><a>1</a></root>", "<root><a>2</a></root>")
    assert diff is not None
    assert "expected canonical preview" in diff


def test_diff_canonical_xml_none_when_equal() -> None:
    xml = "<root><item>x</item></root>"
    assert diff_canonical_xml(xml, xml) is None


def test_canonicalize_xml_strips_uuid_attribute_values() -> None:
    xml = (
        '<root data-id="uuid.aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee">'
        "<value>1</value></root>"
    )
    canonical = canonicalize_xml(xml)
    assert "data-id" not in canonical


def test_canonicalize_invalid_xml_raises() -> None:
    import pytest

    with pytest.raises(ValueError, match="Cannot parse XML"):
        canonicalize_xml("<not>valid</unclosed>")


def test_local_name_plain_tag() -> None:
    assert local_name("root") == "root"


def test_strip_volatile_attributes_removes_uuid_href_only() -> None:
    xml = (
        '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
        '<child xlink:href="#uuid.222" xlink:title="keep">ok</child></root>'
    )
    root = ET.fromstring(xml)
    strip_volatile_attributes(root)
    child = root.find("child")
    assert child is not None
    assert not any("href" in key for key in child.attrib)
    assert child.attrib.get("{http://www.w3.org/1999/xlink}title") == "keep"


def test_iter_local_names_yields_tags() -> None:
    root = ET.fromstring("<root><a/><b/></root>")
    assert list(iter_local_names(root)) == ["root", "a", "b"]
