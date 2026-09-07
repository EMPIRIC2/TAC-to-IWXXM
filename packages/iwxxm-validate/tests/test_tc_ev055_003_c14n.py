"""TC-EV055-003: W3C C14N helper + golden (Python).

Spec: docs/test-plan.md TC-EV055-003; AC3; D-S064-c14n=1; D-S064-c14n-host=1.
Corpus: [Corpus: product §F7] [Corpus: tests]
"""

from __future__ import annotations

import pytest


def test_tc_ev055_003_c14n_equal_for_pretty_vs_compact() -> None:
    """Formatting-only peers must share the same C14N form."""
    from iwxxm_validate.c14n import c14n_equal, c14n_xml

    pretty = """<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2">
  <iwxxm:observation>
    <iwxxm:cloudAmount>FEW</iwxxm:cloudAmount>
  </iwxxm:observation>
</iwxxm:METAR>
"""
    compact = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2">'
        "<iwxxm:observation>"
        "<iwxxm:cloudAmount>FEW</iwxxm:cloudAmount>"
        "</iwxxm:observation>"
        "</iwxxm:METAR>"
    )
    assert c14n_xml(pretty) == c14n_xml(compact)
    assert c14n_equal(pretty, compact) is True


def test_tc_ev055_003_c14n_unequal_for_semantic_diff() -> None:
    """Semantic element text differences must remain unequal under C14N."""
    from iwxxm_validate.c14n import c14n_equal

    a = '<r xmlns="urn:x"><v>1</v></r>'
    b = '<r xmlns="urn:x"><v>2</v></r>'
    assert c14n_equal(a, b) is False


def test_tc_ev055_003_c14n_rejects_malformed() -> None:
    from iwxxm_validate.c14n import c14n_xml

    with pytest.raises(ValueError, match="XML"):
        c14n_xml("<not-closed>")


def test_tc_ev055_003_c14n_ignores_volatile_gml_id() -> None:
    """Volatile gml:id / UUID noise must not break C14N equality (D-S064-c14n-volatile=1)."""
    from iwxxm_validate.c14n import c14n_equal

    a = (
        '<r xmlns="urn:x" xmlns:gml="http://www.opengis.net/gml/3.2">'
        '<n gml:id="uuid.aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"><v>1</v></n></r>'
    )
    b = (
        '<r xmlns="urn:x" xmlns:gml="http://www.opengis.net/gml/3.2">'
        '<n gml:id="uuid.bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"><v>1</v></n></r>'
    )
    assert c14n_equal(a, b) is True


def test_tc_ev055_003_c14n_strips_clark_uuid_and_codelist_hrefs() -> None:
    """Clark-notation ids, bare UUID attrs, and codes.wmo.int hrefs are volatile."""
    from iwxxm_validate.c14n import c14n_xml
    from lxml import etree

    gml_id = "{http://www.opengis.net/gml/3.2}id"
    root_a = etree.fromstring(
        '<r xmlns="urn:x" xmlns:xlink="http://www.w3.org/1999/xlink"><n stable="yes"><v>1</v></n></r>'
    )
    root_b = etree.fromstring(
        '<r xmlns="urn:x" xmlns:xlink="http://www.w3.org/1999/xlink"><n stable="yes"><v>1</v></n></r>'
    )
    child_a = root_a[0]
    child_b = root_b[0]
    child_a.set(gml_id, "uuid.aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    child_b.set(gml_id, "uuid.bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    child_a.set("uuidAttr", "uuid.aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    child_b.set("uuidAttr", "uuid.bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    child_a.set("{http://www.w3.org/1999/xlink}href", "http://codes.wmo.int/common/nil")
    child_b.set("{http://www.w3.org/1999/xlink}href", "https://codes.wmo.int/common/nil")

    assert c14n_xml(etree.tostring(root_a, encoding="unicode")) == c14n_xml(etree.tostring(root_b, encoding="unicode"))
    assert 'stable="yes"' in c14n_xml(etree.tostring(root_a, encoding="unicode"))

    href_uuid_a = '<r xmlns:xlink="http://www.w3.org/1999/xlink"><n xlink:href="#uuid.aaa"/></r>'
    href_uuid_b = '<r xmlns:xlink="http://www.w3.org/1999/xlink"><n xlink:href="#uuid.bbb"/></r>'
    assert c14n_xml(href_uuid_a) == c14n_xml(href_uuid_b)


def test_tc_ev055_003_c14n_strips_whitespace_only_tails() -> None:
    """Whitespace-only element text/tails must not affect C14N equality."""
    from iwxxm_validate.c14n import c14n_equal

    a = "<r><a> </a>\n<b>1</b></r>"
    b = "<r><a/><b>1</b></r>"
    assert c14n_equal(a, b) is True


def test_tc_ev055_003_c14n_helpers_norm_text_and_local_name() -> None:
    """Direct coverage for private helpers used by volatile-attr strip."""
    from iwxxm_validate import c14n as c14n_mod

    assert c14n_mod._local_name("{urn:x}id") == "id"
    assert c14n_mod._local_name("gml:id") == "id"
    assert c14n_mod._local_name("id") == "id"
    assert c14n_mod._norm_text(None) == ""
    assert c14n_mod._norm_text("  a   b  ") == "a b"
    assert c14n_mod._is_volatile_attr("stable", "keep") is False
