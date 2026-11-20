"""Integration: package ``lint`` entrypoint + SPECI product path for WMO-782 rules."""

from __future__ import annotations

import pytest
from tac_validate import lint
from tac_validate.api import lint as lint_api

from .cases import RULE_CASES

# Representative subset for SPECI product parity (full METAR matrix covers each code).
_SPECI_SAMPLE = [
    c
    for c in RULE_CASES
    if c[0]
    in {
        "CAVOK_EXCLUDES_RVR",
        "WEATHER_SHPL_FORBIDDEN",
        "CLOUD_HEIGHT_NOT_ASCENDING",
        "WIND_CALM_MISENCODE",
        "TREND_PROB_FORBIDDEN",
        "RVR_MAX_GROUPS",
        "NATIONAL_RMK_NOT_INTERNATIONAL",
    }
]


@pytest.mark.parametrize(
    ("code", "severity", "fail_tac", "pass_tac"),
    RULE_CASES,
    ids=[c[0] for c in RULE_CASES],
)
def test_lint_api_entrypoint_matches_package(
    code: str,
    severity: str,
    fail_tac: str,
    pass_tac: str,
) -> None:
    """``tac_validate.api.lint`` and package ``lint`` agree on the target code."""
    del severity, pass_tac
    product = "SPECI" if fail_tac.startswith("SPECI") else "METAR"
    via_pkg = {i.code for i in lint(fail_tac, product=product).issues}
    via_api = {i.code for i in lint_api(fail_tac, product=product).issues}
    assert code in via_pkg
    assert code in via_api


@pytest.mark.parametrize(
    ("code", "severity", "fail_tac", "pass_tac"),
    _SPECI_SAMPLE,
    ids=[c[0] for c in _SPECI_SAMPLE],
)
def test_speci_product_path(
    code: str,
    severity: str,
    fail_tac: str,
    pass_tac: str,
) -> None:
    """Same TAC lead rewritten as SPECI still emits the rule on the SPECI path."""
    del severity
    speci_fail = fail_tac.replace("METAR", "SPECI", 1)
    speci_pass = pass_tac.replace("METAR", "SPECI", 1)
    fail_codes = {i.code for i in lint(speci_fail, product="SPECI").issues}
    pass_codes = {i.code for i in lint(speci_pass, product="SPECI").issues}
    assert code in fail_codes
    assert code not in pass_codes
