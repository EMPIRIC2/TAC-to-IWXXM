"""Advisory field values read in plain language, and the mark sits on the value.

[Corpus: product §F9]
"""

from __future__ import annotations

from pathlib import Path

from tac_decoding.decode import _decode_single_report, _ordinal_day, _plain_advisory_value, decode_tac

_TCA = (Path(__file__).resolve().parents[3] / "apps/frontend/src/fixtures/examples/bodies/tca_a2_2.tac").read_text(
    encoding="utf-8"
)
_VAA = (Path(__file__).resolve().parents[3] / "apps/frontend/src/fixtures/examples/bodies/vaa_a7_2.tac").read_text(
    encoding="utf-8"
)


def test_gloria_values_are_plain_and_the_mark_is_the_value() -> None:
    result = decode_tac(_TCA, product="TCA")
    by_code = {seg.code: seg for seg in result.segments}
    wind = by_code["MAX WIND"]
    assert _TCA[wind.start : wind.end] == "22MPS"
    assert wind.explanation == "Maximum wind: 22 metres per second"
    assert by_code["MOV"].explanation == "Movement: northwest at 20 kilometres per hour"
    assert (
        by_code["CB"].explanation == "Cumulonimbus extent: within 250 nautical miles of the tropical cyclone centre, "
        "top flight level 500"
    )
    assert by_code["C"].explanation == "Central pressure: 965 hectopascals"
    assert by_code["INTST CHANGE"].explanation == "Intensity change: intensifying"
    assert "18:00 UTC on the 25th" in by_code["OBS PSN"].explanation
    assert "27 degrees 06 minutes north" in by_code["OBS PSN"].explanation
    assert "73 degrees 06 minutes west" in by_code["OBS PSN"].explanation
    assert "19:00 UTC on 25 September 2004" in by_code["DTG"].explanation
    assert by_code["RMK"].explanation == "Remarks: none"
    assert not any(seg.explanation in {"Tropical cyclone", "Advisory"} for seg in result.segments)


def test_title_tokens_remain_when_the_advisory_has_no_fields() -> None:
    result = decode_tac("TC ADVISORY", product="TCA")
    assert any(seg.explanation == "Tropical cyclone" for seg in result.segments)
    ash = decode_tac("VA ADVISORY", product="VAA")
    assert any(seg.code == "ADVISORY" and seg.explanation == "Advisory" for seg in ash.segments)
    space = decode_tac("SWX ADVISORY", product="SWXA")
    assert any(seg.code == "SWX" for seg in space.segments)
    assert any(seg.code == "ADVISORY" for seg in space.segments)


def test_single_report_keeps_an_abbreviated_heading() -> None:
    tac = "FKNT21 YUFO 250900\nDTG: 20040925/1900Z\n"
    result = _decode_single_report(tac, product="TCA")
    assert any(seg.code.startswith("FKNT21") for seg in result.segments)


def test_empty_field_keeps_the_label_mark() -> None:
    tac = "TC ADVISORY\nC:\nMAX WIND: 22MPS\n"
    result = decode_tac(tac, product="TCA")
    pressure = next(seg for seg in result.segments if seg.code == "C")
    assert pressure.explanation == "Central pressure"
    assert tac[pressure.start : pressure.end].startswith("C")


def test_volcanic_ash_values_use_the_same_words() -> None:
    result = decode_tac(_VAA, product="VAA")
    cloud = next(seg for seg in result.segments if seg.code == "OBS VA CLD")
    assert "flight level 250 to 300" in cloud.explanation
    assert "southeast at 20 knots" in cloud.explanation
    assert "surface to flight level 200" in cloud.explanation
    elev = next(seg for seg in result.segments if seg.code == "SOURCE ELEV")
    assert "1536 metres above mean sea level" in elev.explanation
    later = next(seg for seg in result.segments if seg.code == "FCST VA CLD +18 HR")
    assert "no volcanic ash expected" in later.explanation


def test_plain_value_covers_remaining_codes() -> None:
    text = _plain_advisory_value(
        "S0102 E15927 WKN NC STNR INTST NO MSG EXP 12KM 20241399/0000Z 20240199/0000Z 00/1200Z 32/1200Z"
    )
    assert "1 degrees 02 minutes south" in text
    assert "159 degrees 27 minutes east" in text
    assert "weakening" in text
    assert "no change" in text
    assert "stationary" in text
    assert "no message expected" in text
    assert "12 kilometres" in text
    assert "intensifying" in text
    assert "20241399/0000Z" in text
    assert "20240199/0000Z" in text
    assert "00/1200Z" in text
    assert "32/1200Z" in text
    assert _plain_advisory_value("   ") == ""
    assert _ordinal_day(1) == "the 1st"
    assert _ordinal_day(2) == "the 2nd"
    assert _ordinal_day(3) == "the 3rd"
    assert _ordinal_day(4) == "the 4th"
    assert _ordinal_day(11) == "the 11th"
    assert _ordinal_day(21) == "the 21st"
