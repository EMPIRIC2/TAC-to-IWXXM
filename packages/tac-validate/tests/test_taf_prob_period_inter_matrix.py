"""Evolve-auto test matrix for #1555 + #1489 (shared PROB lint surface).

Dimensions (validation-only; lint does not mutate durable state):
  S  success - PROB TEMPO / period / INTER -> PROB_PRESENT info
  F  failure - INVALID_PROB for bare / BECMG / FM / INTER-no-period / PROB50
  V+ validation pass under annex3 and cited national prefers
  V- validation fail stays error (not softened)
  M  N/A as CRUD - covered as prefer-profile resolve create/update semantics

No Europe blanket: unmapped EU station (LFPG) uses base Annex 3 path, which
also accepts standalone PROB+period as PROB_PRESENT (not a regional soften).

[Corpus: product §F20] [Corpus: domain] [Corpus: config/rules] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac_validate.api import lint, lint_with_profile
from tac_validate.issue_registry import by_code
from tac_validate.quality_policy_bind import resolve_tac_quality_policy_id
from tac_validate.station_scoped_policy import resolve_profile_for_station
from tac_validate.taf_prob import ProbGroupKind, classify_probability_group

# --- fixtures ----------------------------------------------------------------

_TEMPO = "TAF MZBZ 081200Z 0812/0912 12010KT 9999 FEW020 PROB40 TEMPO 0818/0822 4000 TSRA="
_PERIOD = "TAF CYOW 311440Z 3115/0118 VRB03KT P6SM FEW050 PROB30 0108/0112 1SM BR="
_PERIOD_US = "TAF KSGF 301720Z 3018/0124 18008KT P6SM SCT050 PROB30 0106/0112 2SM BR="
_PERIOD_UK = "TAF EGPF 311100Z 3112/0118 24012KT 9999 SCT025 PROB30 0103/0109 6000 RADZ BKN008="
_PERIOD_AU = "TAF YPAD 301800Z 3018/3118 18010KT 9999 SCT030 PROB30 3106/3112 4000 SHRA="
_PERIOD_EU_UNMAPPED = "TAF LFPG 301800Z 3018/3118 26012KT 9999 SCT030 PROB30 3106/3112 4000 SHRA="
_INTER = "TAF NVVA 310500Z 3106/0106 11010KT 9999 SCT020 BKN040 PROB30 INTER 3106/3112 9000 SHRA BKN018="
_INTER_AU = "TAF YSSY 301800Z 3018/3118 18010KT 9999 SCT030 PROB40 INTER 3106/3112 4000 SHRA="
_BARE = "TAF MZBZ 081200Z 0812/0912 12010KT 9999 FEW020 PROB30 4000 TSRA="
_INTER_NO_PERIOD = "TAF NVVA 310500Z 3106/0106 11010KT 9999 SCT020 PROB30 INTER 9000 SHRA="
_BECMG = "TAF HKJK 302300Z 3100/0106 02005KT 9999 BKN020 PROB30 BECMG 3114/3117 -RA FEW022CB BKN080="
_FM = "TAF YUDO 151800Z 1600/1618 13005MPS 9000 BKN020 PROB40 FM160200 15010MPS="
_PROB50 = "TAF YUDO 151800Z 1600/1618 13005MPS 9000 BKN020 PROB50 TEMPO 1608/1612 2000 RADZ="

_CITED_PREFERS = (
    ("KSGF", "iwxxm_us", _PERIOD_US),
    ("CYOW", "ca_eccc", _PERIOD),
    ("EGPF", "uk_metoffice", _PERIOD_UK),
    ("YPAD", "au_bom", _PERIOD_AU),
)


def _codes(report: object) -> set[str]:
    return {i.code for i in report.issues}  # type: ignore[attr-defined]


def _assert_prob_present_ok(report: object) -> None:
    assert report.ok is True  # type: ignore[attr-defined]
    assert "PROB_PRESENT" in _codes(report)
    assert "INVALID_PROB" not in _codes(report)
    assert "PROB_PERIOD_WITHOUT_TEMPO" not in _codes(report)
    assert any(i.code == "PROB_PRESENT" and i.severity == "info" for i in report.issues)  # type: ignore[attr-defined]


def _assert_invalid_prob(report: object) -> None:
    assert report.ok is False  # type: ignore[attr-defined]
    assert any(i.code == "INVALID_PROB" and i.severity == "error" for i in report.issues)  # type: ignore[attr-defined]


# --- S / V+ success paths ----------------------------------------------------


@pytest.mark.parametrize(
    "tac",
    [_TEMPO, _PERIOD, _INTER, _INTER_AU, _PERIOD_EU_UNMAPPED],
    ids=["tempo", "period", "inter_nvva", "inter_au", "period_eu_unmapped"],
)
def test_s_annex3_accepts_valid_prob_forms(tac: str) -> None:
    """S x V+: Annex 3 base accepts TEMPO / period / INTER (no Europe soften)."""
    _assert_prob_present_ok(lint(tac, product="TAF", profile="annex3"))


@pytest.mark.parametrize(
    ("station", "profile", "tac"),
    _CITED_PREFERS,
    ids=[p[1] for p in _CITED_PREFERS],
)
def test_s_cited_national_prefer_accepts_period(station: str, profile: str, tac: str) -> None:
    """S x V+: cited national prefers remap standalone PROB+period (#1555)."""
    assert resolve_profile_for_station(station) == profile
    assert resolve_tac_quality_policy_id(profile, product="TAF") == ("taf-prob-period-info-quality")
    _assert_prob_present_ok(lint_with_profile(tac, product="TAF", profile="annex3"))


def test_s_no_europe_blanket_prefix() -> None:
    """S: LFPG stays unmapped - acceptance is base Annex 3, not EU prefer."""
    assert resolve_profile_for_station("LFPG") is None
    _assert_prob_present_ok(lint(_PERIOD_EU_UNMAPPED, product="TAF", profile="annex3"))


# --- F / V- failure modes (INVALID_PROB stays error) -------------------------


@pytest.mark.parametrize(
    "tac",
    [_BARE, _INTER_NO_PERIOD, _BECMG, _FM, _PROB50],
    ids=["bare", "inter_no_period", "becmg", "fm", "prob50"],
)
def test_f_invalid_prob_stays_error(tac: str) -> None:
    """F x V-: true defects stay INVALID_PROB error under annex3."""
    _assert_invalid_prob(lint(tac, product="TAF", profile="annex3"))


@pytest.mark.parametrize("profile", ["iwxxm_us", "ca_eccc", "uk_metoffice", "au_bom"])
@pytest.mark.parametrize(
    "tac",
    [_BECMG, _FM, _BARE],
    ids=["becmg", "fm", "bare"],
)
def test_f_national_prefer_does_not_soften_invalid_prob(profile: str, tac: str) -> None:
    """F x V-: national prefer must not soften INVALID_PROB (#1555 out)."""
    _assert_invalid_prob(lint(tac, product="TAF", profile=profile))


def test_f_prob_inter_not_conflated_with_becmg() -> None:
    """F: PROB+INTER accept must not conflate with PROB+BECMG true positive (#1489)."""
    inter = lint(_INTER, product="TAF")
    becmg = lint(_BECMG, product="TAF")
    _assert_prob_present_ok(inter)
    _assert_invalid_prob(becmg)
    assert (
        classify_probability_group(
            ["PROB30", "INTER", "3106/3112", "9000"],
            0,
        )
        is ProbGroupKind.INTER
    )
    assert (
        classify_probability_group(
            ["PROB30", "BECMG", "3114/3117"],
            0,
        )
        is ProbGroupKind.INVALID
    )


# --- Catalog / policy lock (mutation of severity binding) --------------------


def test_m_catalog_default_prob_period_is_info() -> None:
    """M (policy update): catalog default for retired PROB_PERIOD code is info."""
    assert by_code("PROB_PERIOD_WITHOUT_TEMPO").severity == "info"
    assert by_code("INVALID_PROB").severity == "error"
    assert by_code("PROB_PRESENT").severity == "info"


def test_m_annex3_policy_maps_prob_period_info() -> None:
    """M: annex3-taf-quality binds PROB_PERIOD_WITHOUT_TEMPO -> info (#1555)."""
    assert resolve_tac_quality_policy_id("annex3", product="TAF") == "annex3-taf-quality"


# --- Classifier edges (validation unit) --------------------------------------


@pytest.mark.parametrize(
    ("tokens", "kind"),
    [
        (["PROB40", "TEMPO", "0818/0822"], ProbGroupKind.TEMPO_OK),
        (["PROB30", "EMPO", "0906/0909"], ProbGroupKind.TEMPO_OK),
        (["PROB30", "0108/0112", "1SM"], ProbGroupKind.PERIOD_WITHOUT_TEMPO),
        (["PROB30", "INTER", "3106/3112", "9000"], ProbGroupKind.INTER),
        (["PROB30", "INTER", "9000"], ProbGroupKind.INVALID),
        (["PROB30", "BECMG", "0814/0816"], ProbGroupKind.INVALID),
        (["PROB40", "FM081800", "12010KT"], ProbGroupKind.INVALID),
        (["PROB50", "TEMPO", "0818/0822"], ProbGroupKind.INVALID),
    ],
    ids=[
        "tempo",
        "empo",
        "period",
        "inter",
        "inter_no_period",
        "becmg",
        "fm",
        "prob50",
    ],
)
def test_v_classify_probability_group(tokens: list[str], kind: ProbGroupKind) -> None:
    assert classify_probability_group(tokens, 0) is kind
