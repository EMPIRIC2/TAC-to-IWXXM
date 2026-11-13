"""#1537 — decode US convective SIGMET ellipsis hazard residuals (F9).

Live WST trails leave ``TORNADOES...HAIL`` and ``N IN...WIND`` as coalesced
residuals when unexplained. Convert VOR behavior is out of scope.

[Corpus: product §F9] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac_decoding.decode import _explain_sigmet_airmet, decode_tac

# Live TAC bodies from the 30-day decode-partial dump (US WST family).
_LIVE_SNIPPETS: list[tuple[str, str]] = [
    (
        "tornadoes_1in",
        "WSUS32 KKCI 022355\n"
        "MKCC WST 022355\n"
        "CONVECTIVE SIGMET 55C\n"
        "VALID UNTIL 0155Z\n"
        "TX OK KS\n"
        "FROM SLN-60WSW MCI-40NW TTT-50E ABI-50SSE CDS-SLN\n"
        "AREA SEV TS MOV FROM 22035KT. TOPS ABV FL450.\n"
        "TORNADOES...HAIL TO 1 IN...WIND GUSTS TO 60KT POSS.\n",
    ),
    (
        "tornadoes_2in",
        "WSUS32 KKCI 021955\n"
        "MKCC WST 021955\n"
        "CONVECTIVE SIGMET 32C\n"
        "VALID UNTIL 2155Z\n"
        "TX OK KS\n"
        "FROM 50NNE MMB-20NNW END-30ENE CDS-40ESE AMA-50NNE MMB\n"
        "AREA SEV TS MOV FROM 22025KT. TOPS TO FL450.\n"
        "TORNADOES...HAIL TO 2 IN...WIND GUSTS TO 65KT POSS.\n",
    ),
    (
        "hail_1in_60kt",
        "WSUS32 KKCI 022255\n"
        "MKCC WST 022255\n"
        "CONVECTIVE SIGMET 49C\n"
        "VALID UNTIL 0055Z\n"
        "TX OK KS\n"
        "FROM 20SE ICT-20ESE SPS-30WNW SJT-20E MAF-60NW END-20SE ICT\n"
        "AREA SEV EMBD TS MOV FROM 22035KT. TOPS ABV FL450.\n"
        "HAIL TO 1 IN...WIND GUSTS TO 60KT POSS.\n",
    ),
    (
        "hail_1in_50kt",
        "WSUS32 KKCI 032155\n"
        "MKCC WST 032155\n"
        "CONVECTIVE SIGMET 96C\n"
        "VALID UNTIL 2355Z\n"
        "MS LA AR TX AND LA TX CSTL WTRS\n"
        "FROM 10NW LIT-20SSW MEM-10W LSU-70SSW LCH-50SSW IAH-10NW LIT\n"
        "AREA SEV TS MOV FROM 24035KT. TOPS TO FL450.\n"
        "TORNADOES...HAIL TO 1 IN...WIND GUSTS TO 50KT POSS.\n",
    ),
]


def _codes(tac: str) -> dict[str, str]:
    return {segment.code: segment.explanation for segment in decode_tac(tac, product="SIGMET").segments}


def _residual_text(tac: str) -> str:
    return " ".join(item.text for item in decode_tac(tac, product="SIGMET").residuals)


@pytest.mark.parametrize(("label", "tac"), _LIVE_SNIPPETS, ids=[row[0] for row in _LIVE_SNIPPETS])
def test_live_convective_ellipsis_hazards_explained(label: str, tac: str) -> None:
    """Live WST ellipsis hazard clauses must not remain as residuals."""
    del label  # id-only; keep parametrize tuple shape stable
    codes = _codes(tac)
    residual = _residual_text(tac)
    assert "TORNADOES...HAIL" not in residual
    assert "1 IN...WIND" not in residual
    assert "2 IN...WIND" not in residual
    assert "IN...WIND" not in residual.split()
    if "TORNADOES...HAIL" in codes:
        assert "tornado" in codes["TORNADOES...HAIL"].lower()
        assert "hail" in codes["TORNADOES...HAIL"].lower()
    assert "IN...WIND" in codes
    assert "inch" in codes["IN...WIND"].lower() or "wind" in codes["IN...WIND"].lower()
    # Digit before IN...WIND is hail size (1 or 2 in the live set).
    digit = "1" if " 1 IN...WIND" in tac or "TO 1 IN...WIND" in tac else "2"
    assert digit in codes
    assert "inch" in codes[digit].lower()
    assert codes.get("POSS.") == "Possible" or codes.get("POSS") == "Possible"


def test_digit_in_wind_without_prior_hail_token() -> None:
    """``1 IN...WIND`` alone (no preceding HAIL) must still explain the digit."""
    tac = (
        "WSUS31 KKCI 051455\n"
        "CONVECTIVE SIGMET 27E\n"
        "VALID UNTIL 1655Z\n"
        "NY\n"
        "FROM MSS\n"
        "AREA TS MOV FROM 22035KT. TOPS ABV FL450.\n"
        "1 IN...WIND GUSTS TO 50KT POSS.\n"
    )
    codes = _codes(tac)
    residual = _residual_text(tac)
    assert "1" not in residual.split()
    assert "1 IN...WIND" not in residual
    assert "inch" in codes["1"].lower()
    assert "IN...WIND" in codes
    assert codes["POSS."] == "Possible"


def test_digit_in_wind_with_trailing_period_on_ellipsis() -> None:
    """Arm hail-size when the follow token is ``IN...WIND.`` (report-style period)."""
    tac = "WSUS31 KKCI 051455\nCONVECTIVE SIGMET 27E\nVALID UNTIL 1655Z\nNY\nFROM MSS\nAREA TS.\n2 IN...WIND.\n"
    codes = _codes(tac)
    residual = _residual_text(tac)
    assert "2 IN...WIND" not in residual
    assert "inch" in codes["2"].lower()
    assert "IN...WIND." in codes


def test_glued_and_unit_helpers() -> None:
    """Glued ``1IN...WIND`` and direct helper edges stay explained."""
    residual = _residual_text(
        "YUDD SIGMET 2 VALID 101200/101600 YUSO- YUDD FIR EMBD TS 1IN...WIND GUSTS POSS=",
    )
    assert "1IN...WIND" not in residual
    seen: dict[str, int] = {"station": 1, "seq": 1, "fir_icao": 1, "fir_name": 1}
    assert "Tornadoes" in (_explain_sigmet_airmet("TORNADOES...HAIL", product="SIGMET", seen=dict(seen)) or "")
    assert "inch" in (_explain_sigmet_airmet("IN...WIND", product="SIGMET", seen=dict(seen)) or "").lower()
    assert _explain_sigmet_airmet("POSS", product="SIGMET", seen=dict(seen)) == "Possible"
