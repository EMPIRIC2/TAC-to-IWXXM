"""M4 SIGMET detector routing coverage (#1230)."""

from __future__ import annotations

import pytest
from tac_validate.product_rules import check_product_rules

_MINIMAL_SIGMET = "YUDD SIGMET 2 VALID 101200/101600 YUSO- YUDD OBSC TS FCST="


def test_sigmet_legacy_mode_uses_check_sigmet(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "legacy")
    issues = check_product_rules("SIGMET =", product="SIGMET")
    assert any(i.code == "MISSING_VALID" for i in issues)


def test_sigmet_detector_mode_uses_sigmet_core_pack(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "detector")
    issues = check_product_rules(_MINIMAL_SIGMET, product="SIGMET")
    assert isinstance(issues, list)
    bad = check_product_rules("SIGMET =", product="SIGMET")
    assert any(i.code == "MISSING_VALID" for i in bad)
