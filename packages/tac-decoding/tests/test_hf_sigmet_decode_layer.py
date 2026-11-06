"""Decode the oceanic SIGMET without false residuals."""

from __future__ import annotations

from tac_decoding.decode import decode_tac

_TAC = """WSPSZ1 NZKL 050806
NZZO SIGMET 2 VALID 050811/051211 NZKL-
NZZO AUCKLAND OCEANIC FIR SEV TURB FCST WI S7520
W14200 - S7728 W13100 - S7700 W14410 - S7520 W14200
9000FT/FL290 MOV
S 20KT INTSF="""


def test_screenshot_sigmet_has_no_false_residuals() -> None:
    result = decode_tac(_TAC, product="SIGMET")
    residual = " ".join(item.text for item in result.residuals)
    explanations = {segment.code: segment.explanation for segment in result.segments}
    assert residual == ""
    assert explanations["9000FT/FL290"] == "Altitude 9000 ft to flight level 290"
    assert explanations["AUCKLAND"] == "FIR name (AUCKLAND)"
    assert "Abbreviated heading WSPSZ1" in explanations["WSPSZ1 NZKL 050806"]


def test_metres_layer_is_explained() -> None:
    result = decode_tac(
        "YUDD SIGMET 2 VALID 101200/101600 YUSO- YUDD FIR SEV TURB FCST 1000M/FL100 MOV E NC=",
        product="SIGMET",
    )
    explanations = {segment.code: segment.explanation for segment in result.segments}
    assert explanations["1000M/FL100"] == "Altitude 1000 m to flight level 100"
