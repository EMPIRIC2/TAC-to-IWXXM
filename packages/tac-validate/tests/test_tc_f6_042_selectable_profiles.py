"""Lint gates for the four selectable profiles.

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac_validate import lint


def test_convective_profile_accepts_convective_text() -> None:
    report = lint("CONVECTIVE SIGMET 75C", product="SIGMET", profile="US_NWS_CONVECTIVE_SIGMET")
    assert report.ok
    assert report.issues == []


def test_convective_profile_rejects_an_international_sigmet() -> None:
    report = lint("YUDD SIGMET 2 VALID 101200/101600", product="SIGMET", profile="us_nws_convective_sigmet")
    assert report.ok is False
    assert report.issues[0].code == "NOT_CONVECTIVE_SIGMET"


def test_convective_profile_rejects_other_products() -> None:
    with pytest.raises(ValueError, match="not applicable"):
        lint("METAR KORD", product="METAR", profile="US_NWS_CONVECTIVE_SIGMET")


@pytest.mark.parametrize(
    ("profile", "product", "tac"),
    [
        ("US_NWS_G_AIRMET", "AIRMET", "AIRMET ZULU"),
        ("US_NWS_VONA", "VONA", "VONA"),
        ("CA_MSC_SIGMET", "SIGMET", "CZQX SIGMET"),
    ],
)
def test_waiting_profiles_refuse(profile: str, product: str, tac: str) -> None:
    report = lint(tac, product=product, profile=profile)
    assert report.ok is False
    assert report.issues[0].code == "SOURCE_UNAVAILABLE"


@pytest.mark.parametrize(
    "profile",
    ["US_NWS_G_AIRMET", "US_NWS_VONA", "CA_MSC_SIGMET"],
)
def test_waiting_profiles_reject_other_products(profile: str) -> None:
    with pytest.raises(ValueError, match="not applicable"):
        lint("METAR KORD", product="METAR", profile=profile)
