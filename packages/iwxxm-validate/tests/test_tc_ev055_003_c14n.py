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
