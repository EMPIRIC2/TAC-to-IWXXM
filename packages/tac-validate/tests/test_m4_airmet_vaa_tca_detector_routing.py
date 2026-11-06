"""M4 AIRMET/VAA/TCA detector routing coverage (#1230)."""

from __future__ import annotations

import pytest
from tac_validate.api import lint
from tac_validate.product_rules import check_product_rules

_AIRMET = "YUDD AIRMET 1 VALID 151520/151800 YUSO- YUDD SFC WSPD 20MPS="


def test_airmet_legacy_and_detector(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "legacy")
    legacy = check_product_rules("AIRMET =", product="AIRMET")
    assert any(i.code == "MISSING_VALID" for i in legacy)
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "detector")
    det = check_product_rules(_AIRMET, product="AIRMET")
    assert isinstance(det, list)
    assert any(i.code == "MISSING_VALID" for i in check_product_rules("AIRMET =", product="AIRMET"))


def test_intl_airmet_without_cccc_is_missing_cccc() -> None:
    """Annex 3 skeleton requires CCCC before AIRMET (#1564)."""
    report = lint(
        "AIRMET 1 VALID 151520/151800 YUSO- YUDD SFC WSPD 20MPS=",
        product="AIRMET",
        profile="annex3",
    )
    errors = [issue for issue in report.issues if issue.severity == "error"]
    assert any(issue.code == "MISSING_CCCC" for issue in errors)


def test_vaa_legacy_and_detector(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "legacy")
    legacy = check_product_rules("FVXX01 =\n", product="VAA")
    assert isinstance(legacy, list)
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "detector")
    det = check_product_rules("FVXX01 =\n", product="VAA")
    assert isinstance(det, list)


def test_tca_legacy_and_detector(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "legacy")
    legacy = check_product_rules("FKNT21 =\n", product="TCA")
    assert isinstance(legacy, list)
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "detector")
    det = check_product_rules("FKNT21 =\n", product="TCA")
    assert isinstance(det, list)
