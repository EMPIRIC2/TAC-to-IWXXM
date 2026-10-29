"""Unit tests: strip research / planning tokens from operator lint messages."""

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


def test_strip_planning_ticket_and_tc_ev_suffix() -> None:
    dirty = "TC SIGMET missing cyclone identity (TC … PSN) - #829 / TC-EV030-004"
    cleaned = _strip_research_refs(dirty)
    assert cleaned == "TC SIGMET missing cyclone identity (TC … PSN)"
    assert "#829" not in cleaned
    assert "TC-EV030" not in cleaned
    assert "EV-030" not in cleaned


def test_strip_parenthetical_tc_ev_token() -> None:
    dirty = "METAR NSC with FEW/SCT/BKN/OVC in same group - FAQ §14.3 exclusivity (TC-EV023-001)"
    cleaned = _strip_research_refs(dirty)
    assert "TC-EV023" not in cleaned
    assert "FAQ §14.3 exclusivity" in cleaned


def test_strip_feature_theme_and_vague_filler() -> None:
    dirty = "VAA forecast NO VA EXP - status NO_VOLCANIC_ASH_EXPECTED (F26 theme V1)"
    cleaned = _strip_research_refs(dirty)
    assert cleaned == "VAA forecast NO VA EXP - status NO_VOLCANIC_ASH_EXPECTED"
    assert "F26" not in cleaned
    assert "theme" not in cleaned.lower()
    field = _strip_research_refs("VAA missing VOLCANO: template field - F26 theme V1 / A2-1")
    assert field == "VAA missing VOLCANO: template field - A2-1"
    assert _strip_research_refs("Do not paste random stuff here") == "Do not paste random here"
    # Grammatical articles are not stripped.
    assert _strip_research_refs("Paste the TAC into the editor") == "Paste the TAC into the editor"
