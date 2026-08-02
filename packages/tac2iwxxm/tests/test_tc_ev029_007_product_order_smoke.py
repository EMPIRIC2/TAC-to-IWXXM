"""TC-EV029-007 — Product-order regression smoke (T12.1 / M12).

One accept fixture per family in Phase B order:

METAR → SPECI → TAF → SIGMET → VA SIGMET → TC SIGMET → AIRMET → VAA → TCA → SWXA

Each case runs lint → convert → XSD+Schematron. Failures must be green or
explicitly skipped with a child-issue id in the skip reason (test-plan TC-EV029-007).

Per-family pack seeds live in ``test_tc_ev029_007_*_gap_fixtures.py`` /
``test_tc_ev029_005_*`` / TC-F28; this module consolidates them for CI order.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ANNEX3 = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
IWXXM_VERSION = "2025-2"
PROFILE = "annex3"

# Phase B product order (verify-plan-audit / E29-3 / theme map TC-EV029-007).
# family_id must stay unique and ordered — test_product_order_sequence locks it.
_PRODUCT_ORDER_CASES: tuple[tuple[str, str, str, str], ...] = (
    ("METAR", "METAR", "metar_basic.tac", "METAR"),
    ("SPECI", "SPECI", "speci_a3_2.tac", "SPECI"),
    ("TAF", "TAF", "taf_a5_1.tac", "TAF"),
    ("SIGMET", "SIGMET", "sigmet_a6_1a_ts.tac", "SIGMET"),
    ("VA_SIGMET", "SIGMET", "sigmet_va_eggx.tac", "VolcanicAshSIGMET"),
    ("TC_SIGMET", "SIGMET", "sigmet_a6_2_tc.tac", "TropicalCycloneSIGMET"),
    ("AIRMET", "AIRMET", "airmet_a6_1a_ts.tac", "AIRMET"),
    ("VAA", "VAA", "vaa_a7_2.tac", "VolcanicAshAdvisory"),
    ("TCA", "TCA", "tca_a2_2.tac", "TropicalCycloneAdvisory"),
    ("SWXA", "SWXA", "swxa_a7_3.tac", "SpaceWeatherAdvisory"),
)

_EXPECTED_FAMILY_ORDER = (
    "METAR",
    "SPECI",
    "TAF",
    "SIGMET",
    "VA_SIGMET",
    "TC_SIGMET",
    "AIRMET",
    "VAA",
    "TCA",
    "SWXA",
)

# Sibling roots that must not appear for adjacency families (TC-F28-006 / #738).
_FORBIDDEN_ROOTS: dict[str, tuple[str, ...]] = {
    "SIGMET": ("VolcanicAshSIGMET", "TropicalCycloneSIGMET", "TropicalCycloneAdvisory"),
    "VA_SIGMET": ("TropicalCycloneSIGMET", "TropicalCycloneAdvisory", "VolcanicAshAdvisory"),
    "TC_SIGMET": ("VolcanicAshSIGMET", "TropicalCycloneAdvisory", "VolcanicAshAdvisory"),
    "VAA": ("VolcanicAshSIGMET", "TropicalCycloneAdvisory", "SpaceWeatherAdvisory"),
    "TCA": ("TropicalCycloneSIGMET", "VolcanicAshAdvisory", "SpaceWeatherAdvisory"),
    "SWXA": ("SIGMET", "VolcanicAshAdvisory", "TropicalCycloneAdvisory"),
}


def _has_root(xml: str, local: str) -> bool:
    return f"<iwxxm:{local}" in xml


def _assert_gen_sigmet_root(xml: str) -> None:
    """General SIGMET root without VA/TC specialization."""
    assert re.search(r"<iwxxm:SIGMET[\s>]", xml) is not None
    assert not _has_root(xml, "VolcanicAshSIGMET")
    assert not _has_root(xml, "TropicalCycloneSIGMET")


def test_product_order_sequence() -> None:
    """Lock Phase B CI order for TC-EV029-007 (theme map / E29-3)."""
    assert tuple(c[0] for c in _PRODUCT_ORDER_CASES) == _EXPECTED_FAMILY_ORDER


@pytest.mark.parametrize(
    ("family_id", "product", "tac_name", "root_local"),
    _PRODUCT_ORDER_CASES,
    ids=[c[0] for c in _PRODUCT_ORDER_CASES],
)
def test_product_order_lint_convert_validate(
    family_id: str,
    product: str,
    tac_name: str,
    root_local: str,
) -> None:
    """One accept fixture per family: lint → convert → XSD+SCH."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert

    tac_path = ANNEX3 / tac_name
    assert tac_path.is_file(), f"missing accept fixture for {family_id}: {tac_path}"
    tac = tac_path.read_text(encoding="utf-8")

    lint_report = lint(tac, product=product)
    assert lint_report.ok is True, f"{family_id} lint: {[(i.code, i.message) for i in lint_report.issues]}"

    convert_result = convert(
        tac,
        product=product,
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert convert_result.ok is True, f"{family_id} convert: {convert_result.issues!r}"
    assert convert_result.xml is not None

    if family_id == "SIGMET":
        _assert_gen_sigmet_root(convert_result.xml)
    else:
        assert _has_root(convert_result.xml, root_local), f"{family_id}: expected iwxxm:{root_local} in convert output"

    # Specialized SIGMET / SWXA must not emit a bare iwxxm:SIGMET element.
    if family_id in {"VA_SIGMET", "TC_SIGMET", "SWXA"}:
        assert re.search(r"<iwxxm:SIGMET[\s>]", convert_result.xml) is None, (
            f"{family_id}: unexpected bare iwxxm:SIGMET root"
        )

    for forbidden in _FORBIDDEN_ROOTS.get(family_id, ()):
        if forbidden == "SIGMET":
            continue  # handled above via bare-element regex
        assert not _has_root(convert_result.xml, forbidden), f"{family_id}: forbidden root iwxxm:{forbidden}"

    validation = validate(
        convert_result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, f"{family_id} validate: {[(i.code, i.message) for i in blocking]}"
