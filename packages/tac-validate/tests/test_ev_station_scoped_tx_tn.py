"""EV-station-profile-tx-tn — military and LatAm TX/TN after change groups.

Under us_military / latam_taf, that placement is TX_TN_PRESENT; annex3 keeps
INVALID_TX_TN. resolve_profile_for_station maps ICAO → profile from YAML.
[Corpus: product §F20] [Corpus: product §F36] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac_validate import lint
from tac_validate.station_scoped_policy import (
    accepts_end_tx_tn,
    resolve_profile_for_station,
    station_scoped_policies,
    stations_for,
)

# Live-campaign shaped samples (HF / post-1490).
_MILITARY_END_TX_TN: dict[str, str] = {
    "KBIX": (
        "TAF KBIX 301800Z 3018/3124 11012KT 9999 FEW050 SCT180 BKN250 QNH3003INS "
        "BECMG 3100/3101 07009KT 9999 SCT050 BKN180 OVC250 QNH3004INS "
        "TEMPO 3118/3124 8000 -SHRA VCTS BKN025CB OVC080 TX26/3018Z TN18/3111Z="
    ),
    "KCVS": (
        "TAF AMD KCVS 301900Z 3019/3124 15015KT 6000 -RA BR OVC004 QNH3008INS "
        "TEMPO 3019/3022 3200 BKN010 BECMG 3021/3022 15006KT 9999 NSW BKN015 "
        "TX22/3020Z TN12/3112Z="
    ),
    "KGRK": (
        "TAF KGRK 301600Z 3016/3122 08009KT 9999 VCSH SCT060 OVC110 QNH3008INS "
        "BECMG 3017/3018 08009KT 8000 -SHRA SCT020 OVC040 QNH3002INS "
        "TX28/3018Z TN16/3110Z="
    ),
    "KNID": (
        "TAF KNID 302300Z 3023/3123 25010KT 9999 SCT050 QNH2998INS "
        "BECMG 3108/3109 28012KT 9999 SCT040 QNH3002INS "
        "TX24/3023Z TN12/3112Z="
    ),
    "KNYL": (
        "TAF KNYL 301800Z 3018/3124 14010KT 9999 FEW050 QNH2995INS "
        "FM310600 16012KT 9999 SCT040 QNH2998INS "
        "TX25/3118Z TN18/3111Z LAST NO AMDS="
    ),
    "KPOE": (
        "TAF AMD KPOE 301900Z 3019/0101 18008KT 9999 SCT040 QNH3005INS "
        "BECMG 3102/3103 20010KT 9999 BKN035 QNH3002INS "
        "TEMPO 3118/3124 8000 -SHRA BKN025 TX27/3019Z TN17/3111Z="
    ),
    "KSZL": (
        "TAF AMD KSZL 301900Z 3019/0101 VRB06KT 9999 FEW050 BKN250 QNH3014INS "
        "TEMPO 3100/3103 18012G18KT 4800 -TSRA OVC050CB "
        "BECMG 3103/3104 15009KT 8000 -RA BKN050 OVC090 "
        "TX26/3019Z TN14/3112Z="
    ),
}

_LATAM_END_TX_TN: dict[str, str] = {
    "SKBO": (
        "TAF SKBO 301700Z 3018/3118 36010KT 9999 SCT020 BKN050 "
        "FM310600 05008KT 9999 SCT018 BKN040 "
        "TX19/3119Z TN10/0110Z="
    ),
    "SEQM": (
        "TAF SEQM 301645Z 3018/3118 36012KT 9999 SCT033 SCT100 "
        "TEMPO 3021/3023 TSRA FEW023CB BKN030 "
        "BECMG 3102/3104 VRB03KT NSW SCT005 BKN020 "
        "TX22/3019Z TN10/3111Z="
    ),
    "SKBQ": (
        "TAF SKBQ 301655Z 3018/3118 01008KT 9999 SCT020 "
        "TEMPO 3018/3022 SHRA SCT025TCU "
        "BECMG 3104/3106 VRB05KT "
        "PROB30 TEMPO 3110/3113 5000 BR BKN010 "
        "TX35/3019Z TN25/3111Z="
    ),
    "SVMI": (
        "TAF SVMI 302200Z 3100/0100 09006KT 9999 SCT016 "
        "TEMPO 3100/3104 09003KT 9000 -VCDZ SCT013 SCT070 "
        "TX34/3118Z TN24/3108Z="
    ),
}

_BASE_TX_TN = "TAF LFPG 301700Z 3018/3124 27010KT CAVOK TX17/3114Z TN02/3104Z BECMG 3021/3023 4000 BR="


def test_policies_register_expected_stations() -> None:
    assert stations_for("us_military") == frozenset(_MILITARY_END_TX_TN)
    assert stations_for("latam_taf") == frozenset(_LATAM_END_TX_TN)
    assert accepts_end_tx_tn("us_military") is True
    assert accepts_end_tx_tn("latam_taf") is True
    ids = {p.profile_id for p in station_scoped_policies()}
    assert ids == {"us_military", "latam_taf"}


@pytest.mark.parametrize("icao", sorted(_MILITARY_END_TX_TN))
def test_resolve_military_stations(icao: str) -> None:
    assert resolve_profile_for_station(icao) == "us_military"


@pytest.mark.parametrize("icao", sorted(_LATAM_END_TX_TN))
def test_resolve_latam_stations(icao: str) -> None:
    assert resolve_profile_for_station(icao) == "latam_taf"


def test_resolve_unknown_station() -> None:
    assert resolve_profile_for_station("KORD") is None
    assert resolve_profile_for_station("") is None


def test_accepts_end_tx_tn_helpers() -> None:
    assert accepts_end_tx_tn("us_military") is True
    assert accepts_end_tx_tn("latam_taf") is True
    assert accepts_end_tx_tn("annex3") is False
    assert accepts_end_tx_tn("iwxxm_us") is False


@pytest.mark.parametrize(("icao", "tac"), sorted(_MILITARY_END_TX_TN.items()))
def test_military_end_tx_tn_info_under_us_military(icao: str, tac: str) -> None:
    report = lint(tac, product="TAF", profile="us_military")
    assert not any(i.code == "INVALID_TX_TN" for i in report.issues)
    assert any(i.code == "TX_TN_PRESENT" and i.severity == "info" for i in report.issues)


@pytest.mark.parametrize(("icao", "tac"), sorted(_LATAM_END_TX_TN.items()))
def test_latam_end_tx_tn_info_under_latam_taf(icao: str, tac: str) -> None:
    report = lint(tac, product="TAF", profile="latam_taf")
    assert not any(i.code == "INVALID_TX_TN" for i in report.issues)
    assert any(i.code == "TX_TN_PRESENT" and i.severity == "info" for i in report.issues)


def test_annex3_still_errors_end_tx_tn() -> None:
    tac = _MILITARY_END_TX_TN["KBIX"]
    report = lint(tac, product="TAF", profile="annex3")
    assert any(i.code == "INVALID_TX_TN" and i.severity == "error" for i in report.issues)


def test_base_forecast_tx_tn_info_all_profiles() -> None:
    for profile in ("annex3", "us_military", "latam_taf"):
        report = lint(_BASE_TX_TN, product="TAF", profile=profile)
        assert not any(i.code == "INVALID_TX_TN" for i in report.issues)
        assert any(i.code == "TX_TN_PRESENT" for i in report.issues)


def test_latam_inherits_annex3_not_br_decea() -> None:
    from tac_validate.lint_profile_catalog import lint_profile_spec

    spec = lint_profile_spec("latam_taf")
    assert spec is not None
    assert spec.inherits == "annex3"
