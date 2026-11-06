"""Regional dialect profiles — inherits, PROB policy, ICAO resolve, lint_with_profile.

[Corpus: product §F20] [Corpus: product §F36] [Corpus: adr/ADR-046] [Corpus: tests]
"""

from __future__ import annotations

from tac_validate.api import extract_station_icao, lint, lint_with_profile, prefer_station_profile
from tac_validate.lint_profile_catalog import profile_inherit_chain, resolved_lint_profile
from tac_validate.quality_policy_bind import resolve_tac_quality_policy_id

_PROB_PERIOD = "TAF CYOW 301800Z 3018/3118 27010KT P6SM SCT040 PROB30 3020/3024 3SM -SHRA BR BKN020="
_MIL_TX = (
    "TAF KBIX 301800Z 3018/3124 11012KT 9999 FEW050 QNH3003INS "
    "BECMG 3100/3101 07009KT 9999 SCT050 QNH3004INS "
    "TX26/3018Z TN18/3111Z="
)


def test_us_military_inherits_iwxxm_us_chain() -> None:
    assert profile_inherit_chain("us_military") == ("annex3", "iwxxm_us", "us_military")
    resolved = resolved_lint_profile("us_military")
    assert resolved is not None
    assert resolved.accept_end_tx_tn is True
    assert "KBIX" in resolved.stations


def test_prob_period_present_info_under_annex3() -> None:
    report = lint(_PROB_PERIOD, product="TAF", profile="annex3")
    assert "PROB_PERIOD_WITHOUT_TEMPO" not in {i.code for i in report.issues}
    assert any(i.code == "PROB_PRESENT" and i.severity == "info" for i in report.issues)


def test_prob_period_present_under_iwxxm_us() -> None:
    report = lint_with_profile(_PROB_PERIOD, product="TAF", profile="iwxxm_us")
    assert "PROB_PERIOD_WITHOUT_TEMPO" not in {i.code for i in report.issues}
    assert any(i.code == "PROB_PRESENT" for i in report.issues)


def test_prob_period_info_under_us_military_via_parent_bind() -> None:
    assert resolve_tac_quality_policy_id("us_military", product="TAF") == "taf-prob-period-info-quality"


def test_icao_prefer_maps_military_end_tx_tn() -> None:
    assert prefer_station_profile("annex3", "TAF", "KBIX") == "us_military"
    # Explicit national profile wins over station map.
    assert prefer_station_profile("iwxxm_us", "TAF", "KBIX") == "iwxxm_us"
    without = lint(_MIL_TX, product="TAF", profile="annex3")
    assert any(i.code == "INVALID_TX_TN" for i in without.issues)
    auto = lint_with_profile(_MIL_TX, product="TAF", profile="annex3")
    assert not any(i.code == "INVALID_TX_TN" for i in auto.issues)
    assert any(i.code == "TX_TN_PRESENT" for i in auto.issues)


def test_extract_station_icao_from_taf() -> None:
    assert extract_station_icao(_MIL_TX, "TAF") == "KBIX"
    assert extract_station_icao("METAR KBIX 301800Z 18008KT 10SM FEW050=", "METAR") == "KBIX"


def test_policy_bindings_ca_and_uk() -> None:
    assert resolve_tac_quality_policy_id("ca_eccc", product="TAF") == "taf-prob-period-info-quality"
    assert resolve_tac_quality_policy_id("uk_metoffice", product="TAF") == "taf-prob-period-info-quality"


def test_issue_count_preserved_annex3_vs_iwxxm_us() -> None:
    # Compare the engines directly (no ICAO prefer): the national policy changes
    # only severity, not which codes are emitted. lint_with_profile(..., annex3)
    # now reroutes a CY* station to ca_eccc, so use lint() for engine parity.
    annex = lint(_PROB_PERIOD, product="TAF", profile="annex3")
    national = lint(_PROB_PERIOD, product="TAF", profile="iwxxm_us")
    assert len(annex.issues) == len(national.issues)
    assert sorted(i.code for i in annex.issues) == sorted(i.code for i in national.issues)


def test_lint_with_profile_keeps_parse_gate_outside_product_catalog() -> None:
    empty = lint_with_profile("", product="METAR", profile="annex3")
    assert any(i.code == "EMPTY_TAC" and i.severity == "error" for i in empty.issues)
    malformed = lint_with_profile(
        "QQUS31 KZNY 121200\nMETAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=\n",
        product="METAR",
        profile="annex3",
    )
    assert any(i.code == "INVALID_AHL" and i.severity == "error" for i in malformed.issues)


def test_extract_station_icao_rejects_non_matching_taf() -> None:
    assert extract_station_icao("TAF without-station", "TAF") is None


def test_lint_with_profile_can_skip_policy_apply() -> None:
    report = lint_with_profile(_PROB_PERIOD, product="TAF", profile="iwxxm_us", apply_policy=False)
    assert "PROB_PERIOD_WITHOUT_TEMPO" not in {i.code for i in report.issues}
    assert any(i.code == "PROB_PRESENT" for i in report.issues)
