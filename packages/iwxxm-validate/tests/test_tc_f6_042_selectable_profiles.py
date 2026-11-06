"""Published-file checks for the Canadian SIGMET profile.

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

from iwxxm_validate import validate
from iwxxm_validate.declared_package import apply_declared_package
from iwxxm_validate.validate_iwxxm import validate_iwxxm

_STUB = """<?xml version="1.0" encoding="UTF-8"?>
<root xmlns="http://icao.int/iwxxm/3.0"/>
"""


def test_ca_msc_sigmet_keeps_its_profile_on_a_published_file() -> None:
    report = validate(_STUB, iwxxm_version="3.0.0", profile="ca_msc_sigmet", product="SIGMET", levels=["xsd"])
    assert report.profile == "ca_msc_sigmet"
    assert report.issues[0].code != "CA_SCHEMA_NOT_FOUND"


def test_ca_msc_sigmet_rejects_a_non_canadian_version() -> None:
    report = validate("<root/>", iwxxm_version="2025-2", profile="ca_msc_sigmet")
    assert report.ok is False
    assert report.profile == "ca_msc_sigmet"
    assert report.issues[0].code == "INVALID_IWXXM_VERSION"
    assert "ca_msc_sigmet" in report.issues[0].message


def test_public_validate_keeps_the_selected_profile() -> None:
    canadian = validate_iwxxm(_STUB, iwxxm_version="3.0.0", profile="ca_msc_sigmet", product="SIGMET", levels=["xsd"])
    assert canadian.profile == "ca_msc_sigmet"
    assert not any(issue.code == "INVALID_PROFILE" for issue in canadian.issues)
    convective = validate_iwxxm(
        "<root/>",
        iwxxm_version="2025-2",
        profile="us_nws_convective_sigmet",
        levels=["xsd"],
    )
    assert convective.profile == "us_nws_convective_sigmet"
    assert not any(issue.code == "INVALID_PROFILE" for issue in convective.issues)


def test_ca_msc_sigmet_accepts_a_declared_3_0_package() -> None:
    version, issue = apply_declared_package(
        _STUB,
        profile="ca_msc_sigmet",
        iwxxm_version="3.0.0",
    )
    assert version == "3.0.0"
    assert issue is None
