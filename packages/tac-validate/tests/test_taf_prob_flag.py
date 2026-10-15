"""A probability token that does not qualify a timed TEMPO group is an error."""

from __future__ import annotations

from tac_validate import lint
from tac_validate.taf_prob import probability_group_valid

_SAMPLE = (
    "TAF MZBZ 081200Z 0812/0912 12010KT 9999 FEW020 BECMG 0814/0816 14012KT 7000 PROB40 TEMPO 0818/0822 4000 TSRA="
)
_BARE = "TAF MZBZ 081200Z 0812/0912 12010KT 9999 FEW020 PROB30 4000 TSRA="


def test_sample_keeps_prob_present_and_not_invalid() -> None:
    report = lint(_SAMPLE, product="TAF")
    codes = {issue.code for issue in report.issues}
    assert "PROB_PRESENT" in codes
    assert "INVALID_PROB" not in codes
    assert report.ok is True


def test_prob30_without_tempo_is_invalid() -> None:
    report = lint(_BARE, product="TAF")
    assert report.ok is False
    assert any(issue.code == "INVALID_PROB" and issue.severity == "error" for issue in report.issues)
    period_only = lint(
        "TAF MZBZ 081200Z 0812/0912 12010KT 9999 PROB30 0818/0822 4000 TSRA=",
        product="TAF",
    )
    assert "INVALID_PROB" in {issue.code for issue in period_only.issues}
    missing_period = lint(
        "TAF MZBZ 081200Z 0812/0912 12010KT 9999 PROB40 TEMPO 4000 TSRA=",
        product="TAF",
    )
    assert "INVALID_PROB" in {issue.code for issue in missing_period.issues}


def test_probability_group_valid_edges() -> None:
    assert probability_group_valid([], 0) is False
    assert probability_group_valid(["TEMPO", "0818/0822", "PROB40"], -1) is False
    assert probability_group_valid(["PROB40"], 1) is False
    assert probability_group_valid(["TEMPO"], 0) is False
    assert probability_group_valid(["PROB50", "TEMPO", "0818/0822"], 0) is False
    assert probability_group_valid(["PROB30"], 0) is False
    assert probability_group_valid(["PROB30", "TEMPO"], 0) is False
    assert probability_group_valid(["PROB30", "BECMG", "0814/0816"], 0) is False
    assert probability_group_valid(["PROB40", "FM081800", "12010KT"], 0) is False
    assert probability_group_valid(["PROB30", "EMPO", "0906/0909"], 0) is True
    assert probability_group_valid(["TAF", "PROB40", "TEMPO", "0818/0822"], 1) is True
    assert probability_group_valid(["PROB40", "TEMPO", "4000"], 0) is False
