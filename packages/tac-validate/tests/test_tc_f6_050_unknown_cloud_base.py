"""TC-F6-050: an unknown cloud base with CB or TCU is a valid group.

Spec: docs/test-plan.md TC-F6-050. Issue #1407.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml
from tac_validate import lint
from tac_validate.cloud_amount import known_base_convective_cloud
from tac_validate.theme_checks import r4_cloud

_FEW_CB = "METAR MZBZ 081200Z 12010KT 9999 FEW///CB 28/24 Q1013="
_SCT_CB = "METAR MZBZ 081200Z 12010KT 9999 SCT///CB 28/24 Q1013="
_BKN_TCU = "METAR MZBZ 081200Z 12010KT 9999 BKN///TCU 28/24 Q1013="
_KNOWN_CB = "METAR MZBZ 081200Z 12010KT 9999 FEW020CB 28/24 Q1013="
_KNOWN_TCU = "METAR MZBZ 081200Z 12010KT 9999 BKN015TCU 28/24 Q1013="
_ILLEGAL = "METAR MZBZ 081200Z 12010KT 9999 SCT(0)45 28/24 Q1013="
_MISSING_TYPE = "METAR MZBZ 081200Z 12010KT 9999 FEW020/// 28/24 Q1013="


def _codes(tac: str, product: str = "METAR") -> set[str]:
    return {issue.code for issue in r4_cloud(tac, product)}


@pytest.mark.parametrize("tac", [_FEW_CB, _SCT_CB, _BKN_TCU])
def test_unknown_base_with_convective_type_is_not_flagged(tac: str) -> None:
    assert "CLOUD_CB_OR_TCU" not in _codes(tac)
    assert "INVALID_CLOUD_TOKEN" not in _codes(tac)
    report = lint(tac, product="METAR")
    assert report.ok is True
    assert not any(issue.code == "CLOUD_CB_OR_TCU" for issue in report.issues)
    assert not any(issue.code == "INVALID_CLOUD_TOKEN" for issue in report.issues)


def test_legacy_lint_skips_the_unknown_base_note(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "legacy")
    report = lint(_FEW_CB, product="METAR")
    assert "CLOUD_CB_OR_TCU" not in {issue.code for issue in report.issues}
    assert "INVALID_CLOUD_TOKEN" not in {issue.code for issue in report.issues}


def test_known_base_convective_type_stays_flagged() -> None:
    assert "CLOUD_CB_OR_TCU" in _codes(_KNOWN_CB)
    assert "CLOUD_CB_OR_TCU" in _codes(_KNOWN_TCU)
    report = lint(_KNOWN_CB, product="METAR")
    assert any(issue.code == "CLOUD_CB_OR_TCU" for issue in report.issues)
    assert report.ok is True


def test_illegal_cloud_token_stays_invalid() -> None:
    assert "INVALID_CLOUD_TOKEN" in _codes(_ILLEGAL)
    assert "CLOUD_CB_OR_TCU" not in _codes(_ILLEGAL)
    report = lint(_ILLEGAL, product="METAR")
    assert report.ok is False
    assert any(issue.code == "INVALID_CLOUD_TOKEN" for issue in report.issues)


def test_missing_convective_type_stays_flagged() -> None:
    assert "CLOUD_TYPE_NOT_OBSERVABLE" in _codes(_MISSING_TYPE)
    assert "CLOUD_CB_OR_TCU" not in _codes(_MISSING_TYPE)
    report = lint(_MISSING_TYPE, product="METAR")
    assert any(issue.code == "CLOUD_TYPE_NOT_OBSERVABLE" for issue in report.issues)
    assert not any(issue.code == "CLOUD_CB_OR_TCU" for issue in report.issues)


_HELPER_CASES = (
    ("FEW020CB", True),
    ("SCT015CB", True),
    ("BKN008CB", True),
    ("OVC001CB", True),
    ("FEW020TCU", True),
    ("SCT015TCU", True),
    ("BKN008TCU", True),
    ("OVC001TCU", True),
    ("FEW///CB", False),
    ("SCT///CB", False),
    ("BKN///TCU", False),
    ("FEW///TCU", False),
    ("OVC///CB", False),
    ("FEW020", False),
    ("FEW020///", False),
    ("FEW02CB", False),
    ("FEW0200CB", False),
    ("FEW02XCB", False),
    ("FEWX20CB", False),
    ("FEW020XX", False),
    ("FEW020XTCU", False),
    ("XYZ020CB", False),
    ("VV001", False),
    ("", False),
    ("CB", False),
    ("FEWCB", False),
    ("FEW020cb", False),
    ("NSC", False),
)


@pytest.mark.parametrize(("token", "expected"), _HELPER_CASES)
def test_known_base_convective_cloud_decision(token: str, expected: bool) -> None:
    assert known_base_convective_cloud(token) is expected


def test_detector_pattern_matches_the_helper() -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "tac_validate"
        / "data"
        / "detectors"
        / "metar-speci-r4-cloud.yaml"
    )
    pack = yaml.safe_load(path.read_text(encoding="utf-8"))
    rule = next(item for item in pack["rules"] if item["id"] == "cloud_cb_or_tcu")
    pattern = re.compile(rule["pattern"])
    for token, expected in _HELPER_CASES:
        assert (pattern.search(token) is not None) is expected
        assert known_base_convective_cloud(token) is expected
