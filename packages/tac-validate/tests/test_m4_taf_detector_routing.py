"""M4 TAF detector routing coverage (#1230)."""

from __future__ import annotations

import pytest
from tac_validate.product_rules import check_product_rules

_MINIMAL_TAF = "TAF KJFK 121230Z 1212/1312 18010KT P6SM SCT040="


def test_taf_legacy_mode_uses_check_taf(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "legacy")
    issues = check_product_rules("TAF =", product="TAF")
    assert any(i.code == "MISSING_CCCC" for i in issues)


def test_taf_detector_mode_uses_taf_core_pack(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "detector")
    issues = check_product_rules(_MINIMAL_TAF, product="TAF")
    assert isinstance(issues, list)
    bad = check_product_rules("TAF =", product="TAF")
    assert any(i.code == "MISSING_CCCC" for i in bad)
