"""Runway state and QFE leftovers on Russian METAR and SPECI."""

from __future__ import annotations

from tac_decoding.decode import _qfe, _runway_state, decode_tac


def _codes(tac: str, product: str) -> dict[str, str]:
    result = decode_tac(tac, product=product)
    return {segment.code: segment.explanation for segment in result.segments}


def test_pskov_speci_explains_runway_state_and_qfe() -> None:
    tac = "SPECI ULOO 060949Z 27006G13MPS 230V320 9999 BKN025CB 16/11 Q1002 RMK R19/290052 QFE747"
    result = decode_tac(tac, product="SPECI")
    codes = {segment.code: segment.explanation for segment in result.segments}
    assert codes["R19/290052"] == (
        "Runway state runway 19: wet or water patches, 51 to 100 percent covered, "
        "depth less than 1 mm, friction coefficient 0.52"
    )
    assert codes["QFE747"] == "QFE 747 mmHg (about 996 hPa), the pressure at the aerodrome"
    assert result.residuals == []
    assert codes["Q1002"].startswith("QNH 1002")


def test_runway_visual_range_stays_four_digits() -> None:
    codes = _codes("METAR EIKN 051830Z R08///// R19/2900 R35R/2600V3000FT", "METAR")
    assert codes["R08/////"] == "Runway visual range runway 08: not reported"
    assert codes["R19/2900"] == "Runway visual range runway 19: 2900 m"
    assert "2600" in codes["R35R/2600V3000FT"]


def test_runway_state_in_the_body_and_cleared() -> None:
    codes = _codes("METAR USNN 060000Z R03/290359 R26R/490132 R06L/CLRD62 NOSIG", "METAR")
    assert codes["R03/290359"] == (
        "Runway state runway 03: wet or water patches, 51 to 100 percent covered, depth 3 mm, friction coefficient 0.59"
    )
    assert codes["R26R/490132"] == (
        "Runway state runway 26R: dry snow, 51 to 100 percent covered, depth 1 mm, friction coefficient 0.32"
    )
    assert codes["R06L/CLRD62"] == ("Runway state runway 06L: contamination ceased, friction coefficient 0.62")


def test_qfe_with_reported_hectopascals() -> None:
    codes = _codes("METAR UUOO 060000Z Q1023 RMK QFE747/0996", "METAR")
    assert codes["QFE747/0996"] == "QFE 747 mmHg (996 hPa), the pressure at the aerodrome"
    assert codes["Q1023"].startswith("QNH 1023")


def test_runway_state_code_tables() -> None:
    assert _runway_state("R01/0/00//") == (
        "Runway state runway 01: clear and dry, coverage not reported, depth less than 1 mm, friction not reported"
    )
    assert _runway_state("R02/11////") == (
        "Runway state runway 02: damp, less than 10 percent covered, depth not significant, friction not reported"
    )
    assert _runway_state("R04/250091") == (
        "Runway state runway 04: wet or water patches, 26 to 50 percent covered, "
        "depth less than 1 mm, braking action poor"
    )
    assert _runway_state("R05/5599//") == (
        "Runway state runway 05: wet snow, 26 to 50 percent covered, runway not operational, friction not reported"
    )
    assert _runway_state("R07/799995") == (
        "Runway state runway 07: ice, 51 to 100 percent covered, runway not operational, braking action good"
    )
    assert _runway_state("R08/819292") == (
        "Runway state runway 08: compacted or rolled snow, less than 10 percent covered, "
        "depth 10 cm, braking action medium to poor"
    )
    assert _runway_state("R08/829393") == (
        "Runway state runway 08: compacted or rolled snow, 11 to 25 percent covered, depth 15 cm, braking action medium"
    )
    assert _runway_state("R08/859494") == (
        "Runway state runway 08: compacted or rolled snow, 26 to 50 percent covered, "
        "depth 20 cm, braking action medium to good"
    )
    assert "depth 25 cm" in (_runway_state("R08/819500") or "")
    assert "depth 30 cm" in (_runway_state("R08/819600") or "")
    assert "depth 35 cm" in (_runway_state("R08/819700") or "")
    assert "depth 40 cm or more" in (_runway_state("R08/819800") or "")
    assert "slush" in (_runway_state("R09/610000") or "")
    assert "frozen ruts or ridges" in (_runway_state("R09/910000") or "")
    assert "rime or frost" in (_runway_state("R09/310000") or "")
    assert "deposit not reported" in (_runway_state("R09//10000") or "")
    assert _runway_state("R06L/CLRD//") == ("Runway state runway 06L: contamination ceased, friction not reported")
    assert _runway_state("R19/290099") == (
        "Runway state runway 19: wet or water patches, 51 to 100 percent covered, "
        "depth less than 1 mm, friction unreliable"
    )
    assert _runway_state("R19/299100") is None
    assert _runway_state("R19/290096") is None
    assert _runway_state("R06L/CLRD96") is None
    assert _runway_state("R19/2900") is None
    assert _qfe("Q1002") is None
    assert _qfe("QFE") is None
