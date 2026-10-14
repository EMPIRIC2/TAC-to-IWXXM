"""AMD NOT SKED is a trailer. A real TAF AMD marker still raises AMD_PRESENT."""

from __future__ import annotations

from tac_validate import lint
from tac_validate.taf_amd import amd_modifier_present

_TRAILER = "TAF MKJP 081200Z 0812/0912 12010KT 9999 FEW020 AMD NOT SKED="
_REAL = "TAF AMD MKJP 081200Z 0812/0912 12010KT 9999 FEW020="
_BOTH = "TAF AMD MKJP 081200Z 0812/0912 12010KT 9999 FEW020 AMD NOT SKED="


def test_trailer_does_not_raise_amd_present() -> None:
    report = lint(_TRAILER, product="TAF")
    assert "AMD_PRESENT" not in {issue.code for issue in report.issues}


def test_real_amd_still_raises_amd_present() -> None:
    report = lint(_REAL, product="TAF")
    assert "AMD_PRESENT" in {issue.code for issue in report.issues}
    both = lint(_BOTH, product="TAF")
    assert "AMD_PRESENT" in {issue.code for issue in both.issues}


def test_amd_modifier_present_token_edges() -> None:
    assert amd_modifier_present([]) is False
    assert amd_modifier_present(["NOT", "SKED"]) is False
    assert amd_modifier_present(["AMD"]) is True
    assert amd_modifier_present(["AMD", "NOT"]) is True
    assert amd_modifier_present(["AMD", "NOT", "OTHER"]) is True
    assert amd_modifier_present(["AMD", "NOT", "SKED"]) is False
    assert amd_modifier_present(["AMD", "NOT", "SKED", "AMD"]) is True
