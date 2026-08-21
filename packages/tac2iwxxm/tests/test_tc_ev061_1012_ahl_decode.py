"""TC-EV061-1012-001 — golden AHL multi-METAR decode rows (package).

[Corpus: product §F6] [Corpus: product §F9] [Corpus: tests §TC-EV061-1012-001] UJ-065 #1012
"""

from __future__ import annotations

from pathlib import Path

from tac2iwxxm import decode_tac

FIXTURES = Path(__file__).resolve().parent / "fixtures"
GOLDEN = (FIXTURES / "metar_multi_ahl.txt").read_text(encoding="utf-8")

_INTERNAL_DOC_REF = (
    "[Corpus:",
    "docs/sessions/",
    "ADR-",
    "EV-061",
    "TC-EV061",
    "#1012",
)


def test_tc_ev061_1012_001_golden_ahl_decode_per_report_rows() -> None:
    """AHL heading is explained; each METAR gets F9 rows (not a raw dump)."""
    result = decode_tac(GOLDEN, product="METAR")
    codes = [s.code for s in result.segments]
    explanations = " ".join(s.explanation for s in result.segments)
    residual_text = " ".join(r.text for r in result.residuals)

    assert any("SAUS31" in s.code or "SAUS31" in s.explanation for s in result.segments), (
        f"expected AHL heading segment; codes={codes!r} residuals={residual_text!r}"
    )
    assert "KZNY" in explanations or any("KZNY" in s.code for s in result.segments)
    assert "KJFK" in codes
    assert "KLGA" in codes
    assert "METAR" in codes
    assert "SAUS31 KZNY 121200" not in residual_text
    assert "METAR KLGA" not in residual_text
    assert "KJFK" in result.summary
    assert "KLGA" in result.summary
    for token in _INTERNAL_DOC_REF:
        assert token not in result.summary
        assert token not in explanations
