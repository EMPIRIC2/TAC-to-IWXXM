"""TC-1034: tac-validate fails closed on global-only CA replace tokens.

[Corpus: product §F36] [Corpus: tests]
"""

from __future__ import annotations

from tac_validate.code_list_policy import check_global_only_tokens, national_replace_tokens


def test_tc_1034_006_national_replace_tokens_include_ic_and_gfa() -> None:
    """Replace-kind tokens include IC and GFA compounds."""
    tokens = national_replace_tokens()
    assert "IC" in tokens
    assert "FRQ_TCU_ISOL_TS" in tokens
    assert "LWIS" in tokens


def test_tc_1034_007_global_only_ic_fails_under_ca() -> None:
    """Treating IC as global-only under ca_eccc yields a national-required error."""
    issues = check_global_only_tokens(["IC"], profile="ca_eccc", product="TAF")
    assert len(issues) == 1
    assert issues[0].code == "CA_CODE_LIST_NATIONAL_REQUIRED"
    assert issues[0].severity == "error"


def test_tc_1034_008_annex3_ignores_global_only_check() -> None:
    """Non-CA profiles do not raise national-required issues."""
    assert check_global_only_tokens(["IC"], profile="annex3") == []
