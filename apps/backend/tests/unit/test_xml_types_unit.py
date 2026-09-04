"""Unit tests for lxml typing boundary helpers."""

from __future__ import annotations

from src.utilities.xml_types import XmlElement, lxml_etree


def test_lxml_etree_parse_and_element_tree_roundtrip(tmp_path) -> None:
    xml_path = tmp_path / "sample.xml"
    xml_path.write_text('<root xmlns="urn:example"><child id="1"/></root>', encoding="utf-8")

    tree = lxml_etree.parse(str(xml_path))
    root = tree.getroot()
    assert isinstance(root, object)

    child = lxml_etree.SubElement(root, "added")
    child.set("k", "v")
    assert child.get("k") == "v"

    out_path = tmp_path / "out.xml"
    with out_path.open("wb") as handle:
        tree.write(handle, encoding="utf-8", xml_declaration=True)

    parsed = lxml_etree.fromstring(out_path.read_bytes())
    assert parsed.tag.endswith("root")


def test_xml_element_protocol_typing_accepts_lxml_node() -> None:
    node: XmlElement = lxml_etree.Element("MeteorologicalBulletin")
    node.set("id", "test-id")
    assert node.get("id") == "test-id"
