"""A compass visibility such as 2000E is a visibility group."""

from __future__ import annotations

from tac_validate import lint

_SPECI = "SPECI TNCM 061126Z 09008KT 2000E SHRA BKN016 27/24 Q1016 TEMPO SHRA="
_OMITTED = "METAR TNCM 081200Z 14006KT FEW020 28/24 Q1013="


def test_directional_metres_are_not_a_missing_visibility_group() -> None:
    report = lint(_SPECI, product="SPECI")
    assert not any(issue.code == "MISSING_VISIBILITY" for issue in report.issues)


def test_omitted_visibility_is_still_missing() -> None:
    report = lint(_OMITTED, product="METAR")
    assert any(issue.code == "MISSING_VISIBILITY" for issue in report.issues)
