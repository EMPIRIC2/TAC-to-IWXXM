"""Plain language for remarks that stay out of the international report."""

from __future__ import annotations

import pytest
from tac_decoding import decode_tac
from tac_decoding.remark_plain import explain_remark_plain

_VCSH = "METAR MKJP 081200Z 14006KT 9999 FEW020 28/24 Q1013 RMK VCSH S="
_VIS = "METAR MKJP 081200Z 14006KT 9999 FEW020 28/24 Q1013 RMK VIS16KM="


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        ("VCSH", "Showers in the vicinity"),
        ("VIS1KM", "Visibility 1 kilometre"),
        ("VIS16KM", "Visibility 16 kilometres"),
        ("VIS100KM", None),
        ("FOO", None),
        ("", None),
    ],
)
def test_explain_remark_plain_edges(token: str, expected: str | None) -> None:
    assert explain_remark_plain(token) == expected


def test_decode_explains_vicinity_showers_and_south_after_rmk() -> None:
    result = decode_tac(_VCSH, product="METAR")
    explanations = {segment.code: segment.explanation for segment in result.segments}
    assert explanations["VCSH"] == "Showers in the vicinity"
    assert explanations["S"] == "South"


def test_decode_explains_sixteen_kilometre_visibility_after_rmk() -> None:
    result = decode_tac(_VIS, product="METAR")
    explanations = {segment.code: segment.explanation for segment in result.segments}
    assert explanations["VIS16KM"] == "Visibility 16 kilometres"


def test_body_vicinity_showers_stay_a_residual() -> None:
    result = decode_tac(
        "METAR MKJP 081200Z 14006KT 9999 VCSH FEW020 28/24 Q1013=",
        product="METAR",
    )
    assert all(segment.code != "VCSH" for segment in result.segments)
    assert any(residual.text == "VCSH" for residual in result.residuals)
