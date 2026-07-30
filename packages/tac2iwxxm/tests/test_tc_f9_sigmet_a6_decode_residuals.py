"""EV-022 / F9 deepen — WMO SIGMET A6-1a-TS decode should not leave header/body residuals.

Previously convert succeeded while Decode listed residuals for sequence, VALID, MWO,
FIR name, SE-box geometry, FL, and MOV direction/speed.
"""

from __future__ import annotations

from tac2iwxxm.decode import decode_tac

SIGMET_A6_1A_TS = (
    "YUDD SIGMET 2 VALID 101200/101600 YUSO-\n"
    "YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN=\n"
)

AIRMET_A6_1A = "YUDD AIRMET 1 VALID 151520/151800 YUSO- YUDD SHANLON FIR ISOL TS OBS N OF S50 TOP ABV FL100 STNR WKN="


def test_sigmet_a6_1a_decode_covers_former_residuals() -> None:
    result = decode_tac(SIGMET_A6_1A_TS, product="SIGMET")
    residual_text = " ".join(r.text for r in result.residuals)
    for needle in (
        "2 VALID",
        "YUSO-",
        "SHANLON",
        "S OF N54",
        "FL390",
        "E 20KT",
    ):
        assert needle not in residual_text, f"{needle!r} still residual: {residual_text!r}"

    by_code = {seg.code: seg.explanation for seg in result.segments}
    assert "Sequence number" in by_code["2"]
    assert "Validity" in by_code["VALID"]
    assert "meteorological watch office" in by_code["YUSO-"].lower()
    assert "FIR name" in by_code["SHANLON"]
    assert "Flight level 390" in by_code["FL390"]
    assert "Movement direction" in by_code["E"]
    assert "Speed 20 kt" in by_code["20KT"]
    assert "Latitude" in by_code["N54"]
    assert "Longitude" in by_code["W012"]
    assert result.residuals == []
    assert "Not decoded:" not in result.summary


def test_airmet_a6_decode_covers_geometry_and_fl() -> None:
    result = decode_tac(AIRMET_A6_1A, product="AIRMET")
    by_code = {seg.code: seg.explanation for seg in result.segments}
    assert "Sequence number" in by_code["1"]
    assert "meteorological watch office" in by_code["YUSO-"].lower()
    assert "Flight level 100" in by_code["FL100"]
    assert "Latitude" in by_code["S50"]
    assert result.residuals == []
