"""SPECI pasted while the form says TCA must not explain every group as TCA token."""

from __future__ import annotations

from tac_decoding.decode import decode_tac

SPECI = (
    "SPECI YUDO 151115Z 05025G37KT 3000 1200NE +TSRA BKN005CB "
    "25/22 Q1008 TEMPO TL1200 0600 BECMG AT1200 8000 NSW NSC="
)


def test_bug_2026_09_30_speci_is_not_a_wall_of_tca_tokens() -> None:
    result = decode_tac(SPECI, product="TCA")
    explanations = [seg.explanation for seg in result.segments]
    assert result.product == "SPECI"
    assert "TCA token" not in explanations
    assert "TCA token" not in result.summary
    assert any("special" in text.lower() for text in explanations)
    assert all("—" not in text and " - " not in text for text in explanations)
    assert "—" not in result.summary
    assert result.summary.lower().count("unrecognized group") <= 1
