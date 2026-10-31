"""PROB30/40: TEMPO info, period-without-TEMPO warning, true defects error."""

from __future__ import annotations

from tac_validate import lint
from tac_validate.taf_prob import ProbGroupKind, classify_probability_group, probability_group_valid

_SAMPLE = (
    "TAF MZBZ 081200Z 0812/0912 12010KT 9999 FEW020 BECMG 0814/0816 14012KT 7000 PROB40 TEMPO 0818/0822 4000 TSRA="
)
_PERIOD_NO_TEMPO = (
    "TAF CYOW 311440Z 3115/0118 VRB03KT P6SM FEW050 "
    "FM010800 25005KT P6SM FEW006 PROB30 0108/0112 1SM BR "
    "FM011500 24008KT P6SM FEW040="
)
_BARE = "TAF MZBZ 081200Z 0812/0912 12010KT 9999 FEW020 PROB30 4000 TSRA="
_INTER = "TAF NVVA 310500Z 3106/0106 11010KT 9999 SCT020 BKN040 PROB30 INTER 3106/3112 9000 SHRA BKN018="
_BECMG = "TAF HKJK 302300Z 3100/0106 02005KT 9999 BKN020 PROB30 BECMG 3114/3117 -RA FEW022CB BKN080="


def test_sample_keeps_prob_present_and_not_invalid() -> None:
    report = lint(_SAMPLE, product="TAF")
    codes = {issue.code for issue in report.issues}
    assert "PROB_PRESENT" in codes
    assert "INVALID_PROB" not in codes
    assert "PROB_PERIOD_WITHOUT_TEMPO" not in codes
    assert report.ok is True


def test_prob_period_without_tempo_is_warning_not_error() -> None:
    report = lint(_PERIOD_NO_TEMPO, product="TAF")
    warn = [i for i in report.issues if i.code == "PROB_PERIOD_WITHOUT_TEMPO"]
    assert warn
    assert all(i.severity == "warning" for i in warn)
    assert "INVALID_PROB" not in {i.code for i in report.issues}
    assert report.ok is True


def test_prob_inter_is_warning() -> None:
    report = lint(_INTER, product="TAF")
    assert any(i.code == "PROB_PERIOD_WITHOUT_TEMPO" and i.severity == "warning" for i in report.issues)
    assert "INVALID_PROB" not in {i.code for i in report.issues}
    assert report.ok is True


def test_prob_on_becmg_remains_error() -> None:
    report = lint(_BECMG, product="TAF")
    assert report.ok is False
    assert any(i.code == "INVALID_PROB" and i.severity == "error" for i in report.issues)


def test_prob30_without_period_or_tempo_is_invalid() -> None:
    report = lint(_BARE, product="TAF")
    assert report.ok is False
    assert any(i.code == "INVALID_PROB" and i.severity == "error" for i in report.issues)
    missing_period = lint(
        "TAF MZBZ 081200Z 0812/0912 12010KT 9999 PROB40 TEMPO 4000 TSRA=",
        product="TAF",
    )
    assert "INVALID_PROB" in {issue.code for issue in missing_period.issues}


def test_classify_probability_group_edges() -> None:
    assert classify_probability_group([], 0) is ProbGroupKind.INVALID
    assert classify_probability_group(["TEMPO", "0818/0822", "PROB40"], -1) is (ProbGroupKind.INVALID)
    assert classify_probability_group(["PROB40"], 1) is ProbGroupKind.INVALID
    assert classify_probability_group(["PROB50", "TEMPO", "0818/0822"], 0) is (ProbGroupKind.INVALID)
    assert classify_probability_group(["PROB30"], 0) is ProbGroupKind.INVALID
    assert classify_probability_group(["PROB30", "TEMPO"], 0) is ProbGroupKind.INVALID
    assert classify_probability_group(["PROB30", "BECMG", "0814/0816"], 0) is (ProbGroupKind.INVALID)
    assert classify_probability_group(["PROB40", "FM081800", "12010KT"], 0) is (ProbGroupKind.INVALID)
    assert classify_probability_group(["PROB30", "EMPO", "0906/0909"], 0) is (ProbGroupKind.TEMPO_OK)
    assert classify_probability_group(["TAF", "PROB40", "TEMPO", "0818/0822"], 1) is ProbGroupKind.TEMPO_OK
    assert classify_probability_group(["PROB40", "TEMPO", "4000"], 0) is (ProbGroupKind.INVALID)
    assert classify_probability_group(["PROB30", "0108/0112", "1SM", "BR"], 0) is ProbGroupKind.PERIOD_WITHOUT_TEMPO
    assert classify_probability_group(["PROB30", "INTER", "3106/3112", "9000"], 0) is ProbGroupKind.INTER
    assert classify_probability_group(["PROB30", "INTER", "9000"], 0) is ProbGroupKind.INVALID


def test_probability_group_valid_compat() -> None:
    assert probability_group_valid(["PROB40", "TEMPO", "0818/0822"], 0) is True
    assert probability_group_valid(["PROB30", "0108/0112", "1SM"], 0) is False
