"""HF-sigmet-tc-dashed-names — hyphenated Tropical Cyclone names (F23 / F6).

Short hyphenated names such as ``IN-FA`` must decode as the cyclone name after
``TC``, not as undecoded residuals. Convert keeps ``product=sigmet``.
"""

from __future__ import annotations

from tac_decoding.decode import decode_tac


def _codes(tac: str, product: str = "SIGMET") -> dict[str, str]:
    result = decode_tac(tac, product=product)
    return {segment.code: segment.explanation for segment in result.segments}


def test_hyphenated_tc_name_in_fa_decodes_as_cyclone_name() -> None:
    """``TC IN-FA`` must not leave ``IN-FA`` as a residual (first segment length 2)."""
    tac = (
        "YUCC SIGMET 1 VALID 251600/252200 YUDO- "
        "YUCC AMSWELL FIR TC IN-FA PSN N2706 W07306 "
        "CB WI 30NM OF TC CENTRE MOV W 10KT NC="
    )
    result = decode_tac(tac, product="SIGMET")
    codes = {segment.code: segment.explanation for segment in result.segments}
    assert codes.get("IN-FA") == "Tropical cyclone (IN-FA)"
    assert not any(residual.text.strip() == "IN-FA" for residual in result.residuals)
    # Geometry cue ``TC CENTRE`` must not steal cyclone-name labeling.
    assert codes.get("CENTRE") == "Centre"


def test_hyphenated_tc_name_choi_wan_still_decodes() -> None:
    codes = _codes(
        "RJJJ SIGMET F04 VALID 051909/060109 RJTD- RJJJ FUKUOKA FIR TC CHOI-WAN OBS=",
    )
    assert codes["CHOI-WAN"] == "Tropical cyclone (CHOI-WAN)"


def test_tc_center_spelling_is_not_cyclone_name() -> None:
    """US spelling after ``TC`` must stay a centre cue, not a cyclone name."""
    codes = _codes(
        "YUCC SIGMET 1 VALID 251600/252200 YUDO- "
        "YUCC AMSWELL FIR TC GLORIA PSN N2706 W07306 "
        "CB WI 30NM OF TC CENTER MOV W 10KT NC=",
    )
    assert codes["GLORIA"] == "Tropical cyclone (GLORIA)"
    assert codes["CENTER"] == "Center"
