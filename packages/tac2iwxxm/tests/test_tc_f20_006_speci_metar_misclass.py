"""TC-F20-006 / S2 - SPECI↔METAR mis-classification guards (S020 / EV-015 T3.3).

Deepens TC-F15-005 / R7 adjacency for #734 full AC: Auto-detect / product hint
must never silent-swap SPECI↔METAR; lint + convert keep per-report identity.
T3.4 only if any assertion fails.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from tac_validate import lint
from tac_validate.issue_registry import by_code

from tac2iwxxm import convert

ANNEX3 = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
TAC_VALIDATE = Path(__file__).resolve().parents[2] / "tac-validate" / "tests" / "fixtures" / "accept"

# S1 deepen fixtures (T3.1) - each must fail under the wrong product hint.
_S1_SPECI_ACCEPT = (
    "speci_s1_nil.tac",
    "speci_s1_cavok.tac",
    "speci_s1_nsc.tac",
    "speci_s1_nosig.tac",
    "speci_s1_cor.tac",
    "speci_s1_rvr.tac",
)


def _read_speci_s1(name: str) -> str:
    path = TAC_VALIDATE / name
    assert path.is_file(), f"missing S1 fixture: {path}"
    return path.read_text(encoding="utf-8")


def test_tc_f20_006_keyword_presence_for_auto_detect() -> None:
    """TAC keyword is the auto-detect signal - SPECI… must not look like METAR-only."""
    speci = "SPECI KJFK 232045Z 18012KT 5SM BKN015 15/07 A3005="
    metar = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="
    assert "SPECI" in speci.upper().split()[0]
    assert "METAR" in metar.upper().split()[0]
    # Without an explicit product keyword, operators default to METAR - never SPECI.
    bare = "KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="
    assert not bare.upper().lstrip().startswith("SPECI")
    assert lint(bare, product="SPECI").ok is False


@pytest.mark.parametrize("name", _S1_SPECI_ACCEPT)
def test_tc_f20_006_s1_speci_rejected_as_metar(name: str) -> None:
    tac = _read_speci_s1(name)
    assert tac.upper().lstrip().startswith("SPECI")
    report = lint(tac, product="METAR")
    assert report.ok is False
    assert "MISSING_PRODUCT_KEYWORD" in {i.code for i in report.issues}
    assert by_code("MISSING_PRODUCT_KEYWORD").severity == "error"
    bad = convert(tac, product="METAR", profile="annex3", iwxxm_version="2025-2")
    assert bad.ok is False
    assert any("product mismatch" in (i.message or "").lower() for i in bad.issues)


def test_tc_f20_006_metar_rejected_as_speci() -> None:
    tac = (ANNEX3 / "metar_basic.tac").read_text(encoding="utf-8")
    report = lint(tac, product="SPECI")
    assert report.ok is False
    assert "MISSING_PRODUCT_KEYWORD" in {i.code for i in report.issues}
    bad = convert(tac, product="SPECI", profile="annex3", iwxxm_version="2025-2")
    assert bad.ok is False


def test_tc_f20_006_matched_product_keeps_iwxxm_root() -> None:
    for fname, product, root in (
        ("metar_basic.tac", "METAR", "iwxxm:METAR"),
        ("speci_basic.tac", "SPECI", "iwxxm:SPECI"),
        ("speci_cor.tac", "SPECI", "iwxxm:SPECI"),
    ):
        tac = (ANNEX3 / fname).read_text(encoding="utf-8")
        assert lint(tac, product=product).ok is True
        result = convert(tac, product=product, profile="annex3", iwxxm_version="2025-2")
        assert result.ok is True
        assert result.product == product
        assert root in result.xml


def test_tc_f20_006_bulletin_neighbors_no_silent_swap() -> None:
    """Paired METAR+SPECI bulletin: wrong product hint fails; correct hint preserves root."""
    metar = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="
    speci = "SPECI KJFK 232045Z 18012KT 5SM BKN015 15/07 A3005="
    assert lint(metar, product="SPECI").ok is False
    assert lint(speci, product="METAR").ok is False
    m = convert(metar, product="METAR", profile="annex3", iwxxm_version="2025-2")
    s = convert(speci, product="SPECI", profile="annex3", iwxxm_version="2025-2")
    assert m.ok
    assert "iwxxm:METAR" in m.xml
    assert s.ok
    assert "iwxxm:SPECI" in s.xml
    assert convert(speci, product="METAR", profile="annex3", iwxxm_version="2025-2").ok is False
    assert convert(metar, product="SPECI", profile="annex3", iwxxm_version="2025-2").ok is False
