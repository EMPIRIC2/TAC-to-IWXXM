"""Research R4 / TC-F15-003 - clouds / CAVOK / VV / CB/TCU (T3.7/T3.8).

Accept cases cover CAVOK, FEW/height, VV, NSC. Malformed cloud groups emit
``INVALID_CLOUD_TOKEN``. CB/TCU suffixes emit ``CLOUD_CB_OR_TCU`` (info).
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
_R4_ACCEPT = [c for c in _MANIFEST["accept"] if c.get("theme") == "R4"]
_CLOUD_ERRORS = list(_MANIFEST.get("cloud_errors", []))
_CB_TCU_INFO = list(_MANIFEST.get("cloud_cb_tcu_info", []))


def test_r4_manifest_sections_present() -> None:
    assert len(_R4_ACCEPT) >= 4
    assert {c["product"] for c in _R4_ACCEPT} == {"METAR"}
    assert len(_CLOUD_ERRORS) >= 4
    assert {c["product"] for c in _CLOUD_ERRORS} == {"METAR", "SPECI"}
    assert len(_CB_TCU_INFO) >= 2
    assert {c["product"] for c in _CB_TCU_INFO} == {"METAR", "SPECI"}
    for case in _R4_ACCEPT + _CLOUD_ERRORS + _CB_TCU_INFO:
        assert (_read_tac(case["tac"])).strip()
    for case in _CLOUD_ERRORS:
        assert case["expected_codes"] == ["INVALID_CLOUD_TOKEN"]
    for case in _CB_TCU_INFO:
        assert case["expected_codes"] == ["CLOUD_CB_OR_TCU"]
        assert case["expected_severity"] == "info"


@pytest.mark.parametrize("case", _R4_ACCEPT, ids=_case_ids(_R4_ACCEPT))
def test_r4_accept_cloud_grammar_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.code == "INVALID_CLOUD_TOKEN" for i in report.issues)


@pytest.mark.parametrize("case", _CLOUD_ERRORS, ids=_case_ids(_CLOUD_ERRORS))
def test_r4_invalid_cloud_emits_error(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is False
    codes = {i.code for i in report.issues if i.severity == "error"}
    assert "INVALID_CLOUD_TOKEN" in codes
    assert by_code("INVALID_CLOUD_TOKEN").severity == "error"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code == "INVALID_CLOUD_TOKEN"]
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)


@pytest.mark.parametrize("case", _CB_TCU_INFO, ids=_case_ids(_CB_TCU_INFO))
def test_r4_cb_tcu_emits_info(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    matched = [i for i in report.issues if i.code == "CLOUD_CB_OR_TCU"]
    assert matched
    assert all(i.severity == "info" for i in matched)
    assert by_code("CLOUD_CB_OR_TCU").severity == "info"
    if case.get("require_spans"):
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)
