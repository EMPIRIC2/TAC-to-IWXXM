"""Country lint profiles come from one catalog, not one module per country."""

from __future__ import annotations

import pytest
from tac_validate.api import lint
from tac_validate.lint_profile_catalog import apply_profile_deltas, load_lint_profiles
from tac_validate.models import Issue, LintReport

_NZ_AUTO = "METAR NZWN 231800Z AUTO 05003KT 9999 FEW010/// 06/02 Q1030="
_BASIC = "METAR YSSY 231800Z 18008KT 9999 FEW040 22/18 Q1012="
_SAME_AS_ANNEX3 = ("au_bom", "uk_metoffice", "br_decea", "kr_kma", "jp_jma", "hk_hko")


def test_catalog_records_every_thin_profile() -> None:
    rows = load_lint_profiles()
    for profile_id in _SAME_AS_ANNEX3:
        spec = rows[profile_id]
        assert spec.engine == "annex3"
        assert spec.differs is False
        assert spec.deltas == ()
    assert rows["nz_caa_met"].differs is True
    assert rows["iwxxm_us"].recorded == ("US_CONVECTIVE_SIGMET_SHAPE",)


def test_new_zealand_unobserved_cloud_type_is_not_an_annex3_error() -> None:
    annex = lint(_NZ_AUTO, product="METAR", profile="annex3")
    nz = lint(_NZ_AUTO, product="METAR", profile="nz_caa_met")
    assert any(issue.code == "INVALID_CLOUD_TOKEN" for issue in annex.issues)
    assert nz.profile == "nz_caa_met"
    assert not any(issue.code == "INVALID_CLOUD_TOKEN" for issue in nz.issues)


def test_new_zealand_still_rejects_a_malformed_cloud_token() -> None:
    tac = "METAR NZWN 231800Z AUTO 05003KT 9999 FEW010XYZ 06/02 Q1030="
    report = lint(tac, product="METAR", profile="nz_caa_met")
    assert any(issue.code == "INVALID_CLOUD_TOKEN" for issue in report.issues)


@pytest.mark.parametrize("profile_id", _SAME_AS_ANNEX3)
def test_unchanged_profiles_match_annex3(profile_id: str) -> None:
    annex = lint(_BASIC, product="METAR", profile="annex3")
    national = lint(_BASIC, product="METAR", profile=profile_id)
    assert national.profile == profile_id
    assert [issue.code for issue in national.issues] == [issue.code for issue in annex.issues]


def test_australia_does_not_lint_sigmet_until_the_profile_lists_it() -> None:
    with pytest.raises(ValueError, match="not applicable"):
        lint("YMMM SIGMET A1 VALID 010000/010400 YMMC-", product="SIGMET", profile="au_bom")


def test_missing_catalog_row_is_not_applicable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("tac_validate.api.lint_profile_spec", lambda _profile: None)
    with pytest.raises(ValueError, match="not applicable"):
        lint(_BASIC, product="METAR", profile="au_bom")


def test_suppression_ignores_an_issue_without_a_quoted_token() -> None:
    report = LintReport(
        ok=False,
        product="METAR",
        issues=[Issue(severity="error", code="INVALID_CLOUD_TOKEN", message="cloud token missing")],
    )
    adjusted = apply_profile_deltas(report, profile="nz_caa_met", product="METAR")
    assert adjusted.issues[0].code == "INVALID_CLOUD_TOKEN"
    assert adjusted.profile == "nz_caa_met"


def test_suppression_skips_other_products_and_codes() -> None:
    cloud = Issue(
        severity="error",
        code="INVALID_CLOUD_TOKEN",
        message="METAR invalid cloud/VV token 'FEW010///'",
    )
    other = Issue(severity="error", code="MISSING_QNH", message="token 'FEW010///'")
    kept_product = apply_profile_deltas(
        LintReport(ok=False, product="TAF", issues=[cloud]),
        profile="nz_caa_met",
        product="TAF",
    )
    kept_code = apply_profile_deltas(
        LintReport(ok=False, product="METAR", issues=[other]),
        profile="nz_caa_met",
        product="METAR",
    )
    unknown = apply_profile_deltas(
        LintReport(ok=False, product="METAR", issues=[cloud]),
        profile="not-a-profile",
        product="METAR",
    )
    assert kept_product.issues == [cloud]
    assert kept_code.issues == [other]
    assert unknown.issues == [cloud]
