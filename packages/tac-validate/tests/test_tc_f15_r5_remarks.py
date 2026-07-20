"""Research R5 / TC-F15-003 — US remarks AO1/AO2/SLP/P/T/PK WND (T3.9/T3.10).

Accept cases keep body lint green with RMK present. Known US remark tokens emit
``REMARK_US_EXTENSION`` (info, iwxxm_us awareness). Malformed remark groups emit
``INVALID_REMARK``.
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
_R5_ACCEPT = [c for c in _MANIFEST["accept"] if c.get("theme") == "R5"]
_REMARK_INFO = list(_MANIFEST.get("remark_us_info", []))
_REMARK_ERRORS = list(_MANIFEST.get("remark_errors", []))


def test_r5_manifest_sections_present() -> None:
    assert len(_R5_ACCEPT) >= 4
    assert {c["product"] for c in _R5_ACCEPT} == {"METAR", "SPECI"}
    assert len(_REMARK_INFO) >= 4
    assert len(_REMARK_ERRORS) >= 4
    for case in _R5_ACCEPT + _REMARK_INFO + _REMARK_ERRORS:
        assert (_read_tac(case["tac"])).strip()
    for case in _REMARK_INFO:
        assert case["expected_codes"] == ["REMARK_US_EXTENSION"]
        assert case["expected_severity"] == "info"
    for case in _REMARK_ERRORS:
        assert case["expected_codes"] == ["INVALID_REMARK"]


@pytest.mark.parametrize("case", _R5_ACCEPT, ids=_case_ids(_R5_ACCEPT))
def test_r5_accept_body_with_rmk_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.code == "INVALID_REMARK" for i in report.issues)


@pytest.mark.parametrize("case", _REMARK_INFO, ids=_case_ids(_REMARK_INFO))
@pytest.mark.xfail(strict=True, reason="T3.10 encodes REMARK_US_EXTENSION info")
def test_r5_us_remark_emits_info(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    matched = [i for i in report.issues if i.code == "REMARK_US_EXTENSION"]
    assert matched
    assert all(i.severity == "info" for i in matched)
    assert by_code("REMARK_US_EXTENSION").severity == "info"
    assert any("iwxxm_us" in i.message.lower() for i in matched)
    if case.get("require_spans"):
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)


@pytest.mark.parametrize("case", _REMARK_ERRORS, ids=_case_ids(_REMARK_ERRORS))
@pytest.mark.xfail(strict=True, reason="T3.10 encodes INVALID_REMARK")
def test_r5_invalid_remark_emits_error(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is False
    codes = {i.code for i in report.issues if i.severity == "error"}
    assert "INVALID_REMARK" in codes
    assert by_code("INVALID_REMARK").severity == "error"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code == "INVALID_REMARK"]
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)
