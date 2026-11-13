"""WMO-No. 782 METAR/SPECI quality — parameterized success / failure / validation.

[Corpus: product F15] [Corpus: domain] [Corpus: tests]

WMO-No. 782 (*Aerodrome Reports and Forecasts (METAR/SPECI/TAF) — A Users'
Handbook to the Codes*) guides operators through FM 15/16 field order and
weather-group grammar. These cases lock the annex3 lint → convert → IWXXM
validate path for handbook-shaped METAR and SPECI reports.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from tac_validate import lint

IWXXM_VERSION = "2025-2"
PROFILE = "annex3"


@dataclass(frozen=True)
class Wmo782Case:
    """One handbook-shaped METAR/SPECI quality case."""

    case_id: str
    kind: str  # success | failure | validation
    product: str
    tac: str
    cite: str


# Handbook-shaped acceptables (field order, weather grammar, SPECI trigger form).
_SUCCESS: tuple[Wmo782Case, ...] = (
    Wmo782Case(
        case_id="metar-basic-success",
        kind="success",
        product="METAR",
        tac="METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
        cite="WMO-No. 782 §METAR basic group order",
    ),
    Wmo782Case(
        case_id="metar-precip-success",
        kind="success",
        product="METAR",
        tac="METAR KJFK 231851Z 20015G25KT 3SM -RA BR BKN012 OVC025 12/11 A2998=",
        cite="WMO-No. 782 §present weather precip + obscuration",
    ),
    Wmo782Case(
        case_id="metar-thunder-success",
        kind="success",
        product="METAR",
        tac="METAR KORD 231955Z 27020G35KT 2SM TSRA BKN025CB 18/16 A2985=",
        cite="WMO-No. 782 §thunderstorm + precip descriptor",
    ),
    Wmo782Case(
        case_id="speci-vis-success",
        kind="success",
        product="SPECI",
        tac="SPECI KJFK 232045Z 20015G25KT 1SM -SN BKN008 OVC015 M02/M04 A3001=",
        cite="WMO-No. 782 §SPECI significant change form",
    ),
    Wmo782Case(
        case_id="speci-cavok-success",
        kind="success",
        product="SPECI",
        tac="SPECI EGLL 232100Z 27008KT CAVOK 14/06 Q1013=",
        cite="WMO-No. 782 §CAVOK shorthand",
    ),
)

# Handbook failures: broken weather tokens / missing required groups.
_FAILURE: tuple[Wmo782Case, ...] = (
    Wmo782Case(
        case_id="metar-invalid-weather-failure",
        kind="failure",
        product="METAR",
        tac="METAR KJFK 231751Z 18012KT 10SM ZZ FEW040 15/07 A3005=",
        cite="WMO-No. 782 §Code table 4678 — unknown weather group",
    ),
    Wmo782Case(
        case_id="metar-missing-wind-failure",
        kind="failure",
        product="METAR",
        tac="METAR KJFK 231751Z 10SM FEW040 15/07 A3005=",
        cite="WMO-No. 782 §surface wind required after time",
    ),
    Wmo782Case(
        case_id="speci-invalid-weather-failure",
        kind="failure",
        product="SPECI",
        tac="SPECI KJFK 232045Z 20015KT 3SM QQ BKN020 12/06 A3001=",
        cite="WMO-No. 782 §Code table 4678 — unknown weather group",
    ),
    Wmo782Case(
        case_id="metar-missing-temp-failure",
        kind="failure",
        product="METAR",
        tac="METAR KJFK 231751Z 18012KT 10SM FEW040 A3005=",
        cite="WMO-No. 782 §temperature/dewpoint required before QNH",
    ),
)

# Success cases that must also pass IWXXM validation after convert.
_VALIDATION: tuple[Wmo782Case, ...] = tuple(
    Wmo782Case(
        case_id=case.case_id.replace("-success", "-validation"),
        kind="validation",
        product=case.product,
        tac=case.tac,
        cite=f"{case.cite} → IWXXM validate",
    )
    for case in _SUCCESS
)


@pytest.mark.parametrize("case", _SUCCESS, ids=[c.case_id for c in _SUCCESS])
def test_wmo782_metar_speci_success(case: Wmo782Case) -> None:
    """Handbook-shaped TAC lints clean and converts under annex3."""
    from tac2iwxxm import convert

    report = lint(case.tac, product=case.product)
    assert report.ok is True, f"{case.case_id}: lint issues={report.issues!r} cite={case.cite}"
    result = convert(
        case.tac,
        product=case.product,
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"{case.case_id}: convert issues={result.issues!r}"
    assert f"iwxxm:{case.product}" in result.xml


@pytest.mark.parametrize("case", _FAILURE, ids=[c.case_id for c in _FAILURE])
def test_wmo782_metar_speci_failure(case: Wmo782Case) -> None:
    """Handbook violations emit lint errors and stay non-ok."""
    report = lint(case.tac, product=case.product)
    assert report.ok is False, f"{case.case_id}: expected lint failure cite={case.cite}"
    error_codes = {i.code for i in report.issues if i.severity == "error"}
    assert error_codes, f"{case.case_id}: expected error codes cite={case.cite}"


@pytest.mark.parametrize("case", _VALIDATION, ids=[c.case_id for c in _VALIDATION])
def test_wmo782_metar_speci_validation(case: Wmo782Case) -> None:
    """Converted handbook TAC passes IWXXM validate (XSD + Schematron)."""
    from iwxxm_validate import validate

    from tac2iwxxm import convert

    result = convert(
        case.tac,
        product=case.product,
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"{case.case_id}: convert failed before validate"
    outcome = validate(
        result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in outcome.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, (
        f"{case.case_id}: validate failed cite={case.cite} issues={[(i.code, i.message) for i in blocking]}"
    )


def test_wmo782_case_matrix_covers_kinds() -> None:
    """Matrix always ships success, failure, and validation buckets."""
    kinds = {c.kind for c in (*_SUCCESS, *_FAILURE, *_VALIDATION)}
    assert kinds == {"success", "failure", "validation"}
    products = {c.product for c in (*_SUCCESS, *_FAILURE)}
    assert products == {"METAR", "SPECI"}
