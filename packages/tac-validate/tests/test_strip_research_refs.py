"""Unit tests: strip research milestone tokens from operator lint messages."""

from __future__ import annotations

from tac_validate.product_rules_pkg._common import _strip_research_refs


def test_strip_research_t3_s1() -> None:
    assert _strip_research_refs("METAR CAVOK present - research T3 / S1") == "METAR CAVOK present"


def test_strip_research_inline_r3() -> None:
    assert (
        _strip_research_refs("METAR invalid present weather token 'XX' - A3-2 #8 / research R3")
        == "METAR invalid present weather token 'XX' - A3-2 #8"
    )


def test_strip_research_preserves_clean_messages() -> None:
    msg = "METAR includes CAVOK (ceiling and visibility OK)."
    assert _strip_research_refs(msg) == msg
