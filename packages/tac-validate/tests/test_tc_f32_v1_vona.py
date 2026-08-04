"""F32 theme V1 — VONA accept + negatives (TC-F32-001 / #741).

T2.2 fixtures (RED until T2.3 registry + product rules). Theme id **V1**.
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
    "VONA_ONSET_NIL",
    "VONA_DUR_NIL",
}
_ERROR_CODES = {
    "MISSING_DTG",
    "MISSING_SVO",
    "MISSING_VONA_VOLCANO",
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
_V1_ACCEPT = list(_MANIFEST.get("f32_v1_accept", []))
_V1_INFO = list(_MANIFEST.get("f32_v1_modifier_info", []))
_V1_ERRORS = list(_MANIFEST.get("f32_v1_errors", []))


def test_f32_v1_manifest_sections_present() -> None:
    assert len(_V1_ACCEPT) >= 2
    assert {c["product"] for c in _V1_ACCEPT} == {"VONA"}
    assert {c["id"] for c in _V1_ACCEPT} >= {
        "accept_vona_basic",
        "accept_vona_v1_onset_dur_nil",
    }
    assert len(_V1_INFO) >= 2
    assert len(_V1_ERRORS) >= 3
    for case in _V1_ACCEPT + _V1_INFO + _V1_ERRORS:
        assert (_read_tac(case["tac"])).strip()
    codes = {c["expected_codes"][0] for c in _V1_INFO}
    assert codes == _INFO_CODES
    for case in _V1_ERRORS:
        assert case["expected_codes"][0] in _ERROR_CODES


@pytest.mark.parametrize("case", _V1_ACCEPT, ids=_case_ids(_V1_ACCEPT))
def test_f32_v1_accept_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.severity == "error" for i in report.issues)


@pytest.mark.parametrize("case", _V1_INFO, ids=_case_ids(_V1_INFO))
def test_f32_v1_modifier_emits_info(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    matched = [i for i in report.issues if i.code == code]
    assert matched, f"expected info code {code}; got {[i.code for i in report.issues]}"
    assert all(i.severity == "info" for i in matched)
    assert by_code(code).severity == "info"
    if case.get("require_spans"):
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)


@pytest.mark.parametrize("case", _V1_ERRORS, ids=_case_ids(_V1_ERRORS))
def test_f32_v1_invalid_emits_error(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is False
    codes = {i.code for i in report.issues if i.severity == "error"}
    assert code in codes
    assert by_code(code).severity == "error"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code == code]
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)
