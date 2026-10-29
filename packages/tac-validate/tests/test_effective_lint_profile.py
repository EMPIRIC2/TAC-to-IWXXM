"""Mutation-hardened tests for effective_lint_profile (VAA / national N/A).

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac_validate.profiles import (
    PROFILE_ANNEX3,
    PROFILE_CA_ECCC,
    PROFILE_CA_MSC_SIGMET,
    PROFILE_IN_IMD,
    PROFILE_IWXXM_US,
    PROFILE_US_NWS_CONVECTIVE_SIGMET,
    PROFILE_US_NWS_G_AIRMET,
    effective_lint_profile,
    iwxxm_us_lint_applicable,
)


@pytest.mark.parametrize(
    ("profile", "product", "expected"),
    [
        (PROFILE_ANNEX3, "VAA", PROFILE_ANNEX3),
        (PROFILE_ANNEX3, "METAR", PROFILE_ANNEX3),
        (PROFILE_IWXXM_US, "VAA", PROFILE_ANNEX3),
        (PROFILE_IWXXM_US, "METAR", PROFILE_IWXXM_US),
        (PROFILE_IWXXM_US, "SPECI", PROFILE_IWXXM_US),
        (PROFILE_CA_ECCC, "VAA", PROFILE_CA_ECCC),
        (PROFILE_CA_ECCC, "TCA", PROFILE_ANNEX3),
        (PROFILE_IN_IMD, "VAA", PROFILE_ANNEX3),
        (PROFILE_IN_IMD, "TAF", PROFILE_IN_IMD),
        (PROFILE_US_NWS_CONVECTIVE_SIGMET, "VAA", PROFILE_ANNEX3),
        (PROFILE_US_NWS_CONVECTIVE_SIGMET, "METAR", PROFILE_ANNEX3),
        (PROFILE_US_NWS_CONVECTIVE_SIGMET, "SIGMET", PROFILE_US_NWS_CONVECTIVE_SIGMET),
        # Catalog overlays outside the hard-coded national trio fall back when N/A.
        (PROFILE_US_NWS_G_AIRMET, "METAR", PROFILE_ANNEX3),
        (PROFILE_CA_MSC_SIGMET, "TAF", PROFILE_ANNEX3),
        ("not-a-real-profile", "METAR", PROFILE_ANNEX3),
        ("IWXXM_US", "vaa", PROFILE_ANNEX3),
    ],
)
def test_effective_lint_profile_matrix(profile: str, product: str, expected: str) -> None:
    """National overlays fall back to annex3 when N/A for the product."""
    assert effective_lint_profile(profile, product) == expected


def test_iwxxm_us_lint_applicable_excludes_vaa() -> None:
    """US library lint products do not include VAA."""
    assert iwxxm_us_lint_applicable("METAR") is True
    assert iwxxm_us_lint_applicable("VAA") is False
    assert iwxxm_us_lint_applicable("vaa") is False
