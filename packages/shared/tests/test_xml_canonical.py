"""Tests for canonical XML normalization (TC-M003 / REQ-018)."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch

import pytest

from metar_shared import xml_canonical
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
    with pytest.raises(ValueError, match="Cannot parse XML"):
        canonicalize_xml("<not>valid</unclosed>")


def test_local_name_plain_tag() -> None:
    assert local_name("root") == "root"


def test_canonicalize_xml_strips_codes_wmo_int_href() -> None:
    with_codes = (
        '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
        '<child xlink:href="http://codes.wmo.int/common/nil">ok</child></root>'
    )
    without_codes = "<root><child>ok</child></root>"
    assert compare_canonical_xml(with_codes, without_codes)


def test_strip_volatile_attributes_removes_codes_wmo_int_href() -> None:
    xml = (
        '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
        '<child xlink:href="https://codes.wmo.int/common/nil" xlink:title="keep">ok</child></root>'
    )
    root = ET.fromstring(xml)
    strip_volatile_attributes(root)
    child = root.find("child")
    assert child is not None
    assert not any("href" in key for key in child.attrib)
    assert child.attrib.get("{http://www.w3.org/1999/xlink}title") == "keep"


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


def test_canonicalize_xml_strips_https_codes_wmo_int_href() -> None:
    """https://codes.wmo.int/ href values are omitted from canonical attrs (line 69)."""
    with_codes = (
        '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
        '<child xlink:href="https://codes.wmo.int/common/nil">ok</child></root>'
    )
    without_codes = "<root><child>ok</child></root>"
    assert compare_canonical_xml(with_codes, without_codes)


def test_parse_root_element_keeps_pretty_without_xml_declaration() -> None:
    """Branch when toprettyxml output lacks an XML declaration (111->113)."""
    mock_doc = MagicMock()
    mock_doc.toprettyxml.return_value = "<root><child/></root>\n"

    with patch.object(xml_canonical.minidom, "parseString", return_value=mock_doc):
        root = xml_canonical._parse_root_element("<root><child/></root>")

    assert local_name(root.tag) == "root"


def test_raise_parse_error_without_last_error() -> None:
    with pytest.raises(ValueError, match=r"Cannot parse XML for canonicalization$"):
        xml_canonical._raise_parse_error(None)


def test_raise_parse_error_chains_last_error() -> None:
    cause = ValueError("bad xml")
    with pytest.raises(
        ValueError, match="Cannot parse XML for canonicalization: bad xml"
    ) as exc_info:
        xml_canonical._raise_parse_error(cause)
    assert exc_info.value.__cause__ is cause
