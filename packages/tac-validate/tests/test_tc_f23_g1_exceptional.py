"""F23 / G1 - general SIGMET exceptional accept + negatives (TC-F23-004).

HARD theme G1 from sigmet-research-catalog.md / #733 exceptional-rule table.
T1.1 fixtures + assertions; T1.2 encodes registry rows + rules.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from tac_validate import lint
from tac_validate.issue_registry import by_code

FIXTURES = Path(__file__).resolve().parent / "fixtures"
MANIFEST_PATH = FIXTURES / "manifest.json"

_INFO_CODES = {
    "SIGMET_CNL",
    "STNR_MOVEMENT",
    "POINT_LOCATION",
    "SINGLE_ALTITUDE",
    "POLYGON_LOCATION",
    "TOP_ABV_OR_BLW",
}
_ERROR_CODES = {
    "INVALID_SIGMET_CNL",
    "INVALID_SIGMET_COR",
    "INVALID_STNR_MOVEMENT",
}


def _load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _read_tac(rel: str) -> str:
    path = FIXTURES / rel
    assert path.is_file(), f"missing fixture: {path}"
    text = path.read_text(encoding="utf-8")
    assert text.strip(), f"empty fixture: {path}"
    return text


def _case_ids(cases: list[dict[str, Any]]) -> list[str]:
    return [str(c["id"]) for c in cases]


_MANIFEST = _load_manifest()
_G1_ACCEPT = [c for c in _MANIFEST["accept"] if c.get("theme") == "G1"]
_G1_INFO = list(_MANIFEST.get("g1_modifier_info", []))
_G1_ERRORS = list(_MANIFEST.get("g1_errors", []))


def test_g1_manifest_sections_present() -> None:
    assert len(_G1_ACCEPT) >= 6
    assert {c["product"] for c in _G1_ACCEPT} == {"SIGMET"}
    assert {c["id"] for c in _G1_ACCEPT} >= {
        "accept_sigmet_g1_cnl",
        "accept_sigmet_g1_stnr",
        "accept_sigmet_g1_point",
        "accept_sigmet_g1_single_alt",
        "accept_sigmet_g1_polygon",
        "accept_sigmet_g1_top_abv",
    }
    assert len(_G1_INFO) >= 6
    assert len(_G1_ERRORS) >= 3
    for case in _G1_ACCEPT + _G1_INFO + _G1_ERRORS:
        assert (_read_tac(case["tac"])).strip()
    codes = {c["expected_codes"][0] for c in _G1_INFO}
    assert codes == _INFO_CODES
    for case in _G1_ERRORS:
        assert case["expected_codes"][0] in _ERROR_CODES


@pytest.mark.parametrize("case", _G1_ACCEPT, ids=_case_ids(_G1_ACCEPT))
def test_g1_accept_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.severity == "error" for i in report.issues)


@pytest.mark.parametrize("case", _G1_INFO, ids=_case_ids(_G1_INFO))
def test_g1_modifier_emits_info(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    matched = [i for i in report.issues if i.code == code]
    assert matched, f"expected info code {code}; got {[i.code for i in report.issues]}"
    assert all(i.severity == "info" for i in matched)
    assert by_code(code).severity == "info"
    if case.get("require_spans"):
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)


@pytest.mark.parametrize("case", _G1_ERRORS, ids=_case_ids(_G1_ERRORS))
def test_g1_invalid_emits_error(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is False
    codes = {i.code for i in report.issues if i.severity == "error"}
    assert code in codes
    assert by_code(code).severity == "error"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code == code]
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)
