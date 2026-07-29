"""F24 / A2 — AIRMET phenomenon + intensity / STNR / WKN (TC-F24-001/004).

HARD theme A2 from wmo-quality-research-catalog.md / #731.
T1.3 fixtures + assertions; T1.4 encodes A2 checklist rules (reuse OBS/STNR/WKN/TOP codes).
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
    "OBS_OR_FCST",
    "STNR_MOVEMENT",
    "INTENSITY_CHANGE",
    "TOP_ABV_OR_BLW",
}
_ERROR_CODES = {
    "MULTIPLE_PHENOMENA",
    "INVALID_STNR_MOVEMENT",
    "MISSING_OBS_OR_FCST",
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
_A2_ACCEPT = [c for c in _MANIFEST["accept"] if c.get("theme") == "A2" and c["product"] == "AIRMET"]
_A2_INFO = list(_MANIFEST.get("a2_modifier_info", []))
_A2_ERRORS = list(_MANIFEST.get("a2_errors", []))


def test_a2_manifest_sections_present() -> None:
    assert len(_A2_ACCEPT) >= 5
    assert {c["id"] for c in _A2_ACCEPT} >= {
        "accept_airmet_a2_phenomenon",
        "accept_airmet_a2_obs",
        "accept_airmet_a2_stnr",
        "accept_airmet_a2_intensity",
        "accept_airmet_a2_top_abv",
    }
    assert len(_A2_INFO) >= 4
    assert len(_A2_ERRORS) >= 3
    for case in _A2_ACCEPT + _A2_INFO + _A2_ERRORS:
        assert (_read_tac(case["tac"])).strip()
    codes = {c["expected_codes"][0] for c in _A2_INFO}
    assert codes == _INFO_CODES
    for case in _A2_ERRORS:
        assert case["expected_codes"][0] in _ERROR_CODES


@pytest.mark.parametrize("case", _A2_ACCEPT, ids=_case_ids(_A2_ACCEPT))
def test_a2_accept_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.severity == "error" for i in report.issues)


@pytest.mark.parametrize("case", _A2_INFO, ids=_case_ids(_A2_INFO))
def test_a2_modifier_emits_info(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    matched = [i for i in report.issues if i.code == code]
    assert matched, f"expected info code {code}; got {[i.code for i in report.issues]}"
    assert all(i.severity == "info" for i in matched)
    assert by_code(code).severity == "info"
    if case.get("require_spans"):
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)


@pytest.mark.parametrize("case", _A2_ERRORS, ids=_case_ids(_A2_ERRORS))
def test_a2_invalid_emits_error(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is False
    codes = {i.code for i in report.issues if i.severity == "error"}
    assert code in codes
    assert by_code(code).severity == "error"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code == code]
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)
