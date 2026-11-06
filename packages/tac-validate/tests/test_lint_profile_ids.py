"""Canonical lint-profile id casing (EV-packages-module-reorg L1).

[Corpus: product §F15] [Corpus: product §F36] [Corpus: tests]
"""

from __future__ import annotations

from tac_validate.lint_profile_ids import canonical_lint_profile_id
from tac_validate.profiles import normalize_profile


def test_canonical_casefolds_uppercase_qm_leaf() -> None:
    assert canonical_lint_profile_id("CA_MSC_SIGMET") == "ca_msc_sigmet"
    assert canonical_lint_profile_id("US_NWS_CONVECTIVE_SIGMET") == "us_nws_convective_sigmet"
    assert canonical_lint_profile_id("IWXXM_US") == "iwxxm_us"


def test_normalize_profile_accepts_uppercase_catalog_leaf() -> None:
    assert normalize_profile("CA_MSC_SIGMET") == "ca_msc_sigmet"
    assert normalize_profile("us_military") == "us_military"


def test_inherit_chain_unchanged_for_us_military() -> None:
    from tac_validate.lint_profile_catalog import profile_inherit_chain

    assert profile_inherit_chain("us_military") == ("annex3", "iwxxm_us", "us_military")
    assert profile_inherit_chain("US_MILITARY") == ("annex3", "iwxxm_us", "us_military")
