"""Hypothesis fuzz for Caribbean TAC normalize paths.

Covers GTS peel, lowercase keywords, slash-nil visibility, weather tokens,
and common typo/incomplete groups. [Corpus: tests] [Corpus: product §F6]
"""

from __future__ import annotations

import re

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from tac2iwxxm.convert import convert
from tac_validate import lint

_WEATHER = ("VCSH", "VCTS", "TS", "SHRA", "-SHRA", "TSRA", "BR", "FG", "HZ", "RA")
_STATIONS = ("TTPP", "TNCM", "TKPK", "SYCJ", "MZBZ", "MKJP", "TUPJ")


@st.composite
def metar_with_weather(draw: st.DrawFn) -> str:
    station = draw(st.sampled_from(_STATIONS))
    wx = draw(st.sampled_from(_WEATHER))
    lower = draw(st.booleans())
    gts = draw(st.booleans())
    body = f"METAR {station} 081200Z 14006KT 9999 {wx} FEW020 28/24 Q1013="
    if lower:
        body = body.lower()
    if gts:
        body = f"SAXX31 {station} 081200\n{body}"
    return body


@given(metar_with_weather())
@settings(max_examples=40, deadline=None)
def test_fuzz_metar_weather_converts_or_reports_issues(tac: str) -> None:
    result = convert(tac, product="METAR", bulletin_date="2026-10-08")
    # Must not crash; either XML or a structured issue list
    assert result.xml is not None or result.issues
    codes = {issue.code for issue in lint(tac, product="METAR").issues}
    # Valid vicinity/thunder tokens must not be INVALID_WEATHER
    upper = tac.upper()
    if re.search(r"\b(VCSH|VCTS|TS|SHRA|TSRA)\b", upper):
        assert "INVALID_WEATHER" not in codes


@given(
    st.sampled_from(_STATIONS),
    st.sampled_from(("2023-1", "2025-2")),
    st.booleans(),
)
@settings(max_examples=20, deadline=None)
def test_fuzz_gts_metar_on_pins(station: str, pin: str, lowercase: bool) -> None:
    body = f"METAR {station} 081200Z VRB03KT 9999 FEW020 28/24 Q1013="
    if lowercase:
        body = body.lower()
    tac = f"SAXX31 {station} 081200\n{body}"
    result = convert(
        tac, product="METAR", iwxxm_version=pin, bulletin_date="2026-10-08"
    )
    assert result.ok is True
    assert result.xml is not None
    assert "[kn_i]" in result.xml


@pytest.mark.parametrize(
    ("tac", "product", "expect_issue_substr"),
    [
        ("METAR TKPK 232100Z VBR02KT 9999 FEW014CB 29/25 Q1013=", "METAR", "wind"),
        (
            "METAR TRPG 081100Z 13013KT 080V150 9999 BKN019 27/ Q1016",
            "METAR",
            "temperature/dewpoint",
        ),
        ("METAR MKJP 072300Z 12012KT //// ////// 30/26 Q1013=", "METAR", None),
        ("taf tncm 081200z 0812/0912 14006kt 9999 few020=", "TAF", None),
        (
            "FTXX31 TNCM 081200\nTAF TNCM 081200Z 0812/0912 14006KT 9999 FEW020=",
            "TAF",
            None,
        ),
    ],
)
def test_fuzz_malformed_and_edge_cases(
    tac: str, product: str, expect_issue_substr: str | None
) -> None:
    result = convert(tac, product=product, bulletin_date="2026-10-08")
    if expect_issue_substr is None:
        assert result.ok is True
        assert result.xml is not None
    else:
        assert any(expect_issue_substr in issue.message for issue in result.issues)
