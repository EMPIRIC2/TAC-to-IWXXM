"""Decode body VCSH/VCTS/TS and recent weather for Caribbean testers.

St Kitts / St Maarten / TT reported these as residuals. [Corpus: product §F9]
"""

from __future__ import annotations

from tac_decoding import decode_tac
from tac_decoding.remark_plain import explain_remark_plain


def _explanations(tac: str, product: str = "METAR") -> dict[str, str]:
    result = decode_tac(tac, product=product)
    return {segment.code: segment.explanation for segment in result.segments}


def _residual_texts(tac: str, product: str = "METAR") -> list[str]:
    result = decode_tac(tac, product=product)
    return [residual.text for residual in result.residuals]


def test_body_vicinity_showers_are_explained() -> None:
    tac = "METAR TKPK 191600Z 07009KT 9999 VCSH FEW018 31/24 Q1014="
    explanations = _explanations(tac)
    assert "VCSH" in explanations
    assert "vicinity" in explanations["VCSH"].lower()
    assert "shower" in explanations["VCSH"].lower()
    assert "VCSH" not in _residual_texts(tac)


def test_body_vicinity_thunderstorms_are_explained() -> None:
    tac = "METAR TUPJ 072300Z 08004KT 10SM VCTS FEW012CB SCT020 29/26 A3001="
    explanations = _explanations(tac)
    assert "VCTS" in explanations
    assert "vicinity" in explanations["VCTS"].lower()
    assert "thunderstorm" in explanations["VCTS"].lower()
    assert "VCTS" not in _residual_texts(tac)


def test_body_thunderstorm_and_vicinity_showers_together() -> None:
    tac = "METAR TKPK 232000Z 06005KT 9999 TS VCSH FEW006 SCT014CB 29/26 Q1014="
    explanations = _explanations(tac)
    assert explanations["TS"] == "Thunderstorm"
    assert "VCSH" in explanations
    assert "VCSH" not in _residual_texts(tac)


def test_tt_vcsh_is_not_a_residual() -> None:
    tac = "METAR TTPP 080700Z 00000KT 9000 VCSH FEW015 27/24 Q1013 NOSIG="
    assert "VCSH" in _explanations(tac)
    assert "VCSH" not in _residual_texts(tac)


def test_recent_thunderstorm_and_showers_are_explained() -> None:
    rets = "METAR SYCJ 071600Z 07006KT 9999 FEW014CB SCT036 BKN070 27/24 Q1013 RETS NOSIG="
    explanations = _explanations(rets)
    assert "RETS" in explanations
    assert "recent" in explanations["RETS"].lower()
    assert "thunderstorm" in explanations["RETS"].lower()

    resh = "METAR TNCM 081200Z 14006KT 9999 FEW020 28/24 Q1013 RESH="
    resh_ex = _explanations(resh)
    assert "RESH" in resh_ex
    assert "recent" in resh_ex["RESH"].lower()

    reshra = "METAR TAPA 071700Z 10010KT 060V140 9999 BKN018 29/25 Q1016 RESHRA NOSIG="
    assert "RESHRA" in _explanations(reshra)


def test_compound_remark_vicinity_showers_with_direction() -> None:
    assert explain_remark_plain("VCSH-N") == "Showers in the vicinity, North"
    assert explain_remark_plain("VCSH-NE") == "Showers in the vicinity, Northeast"
    tac = "METAR MZBZ 250000Z 00000KT 9999 VCSH BKN016 28/25 A2985 Q1010 NOSIG RMK VCSH-N="
    assert _explanations(tac)["VCSH-N"] == "Showers in the vicinity, North"


def test_speci_body_vcsh_and_ts_are_explained() -> None:
    tac = "SPECI TKPK 231928Z 06011KT 9999 TS VCSH SCT015CB 30/26 Q1013="
    explanations = _explanations(tac, product="SPECI")
    assert "TS" in explanations
    assert "VCSH" in explanations
    assert "VCSH" not in _residual_texts(tac, product="SPECI")


def test_taf_change_group_weather_is_not_left_as_residual() -> None:
    tac = "TAF MZBZ 301500Z 3018/0118 11007KT 9999 SCT023 PROB30 TEMPO 3018/3021 TS FEW012CB="
    residuals = _residual_texts(tac, product="TAF")
    assert "TS" not in residuals
    assert "VCSH" not in residuals
