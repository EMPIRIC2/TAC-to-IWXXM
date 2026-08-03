"""EV-030 / #829 — TC SIGMET accept + negatives (TC-EV030-004).

Peer to ``test_tc_f23_v1_va_sigmet.py`` (VA theme V1). T2.1 pack + T2.2 registry
codes ``TC_CYCLONE_IDENTITY`` / ``TC_CB_GEOMETRY`` / ``MISSING_TC_IDENTITY``.
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
    "TC_CYCLONE_IDENTITY",
    "TC_CB_GEOMETRY",
    "STNR_MOVEMENT",
    "POLYGON_LOCATION",
    "SIGMET_CNL",
}
_ERROR_CODES = {
    "INVALID_STNR_MOVEMENT",
    "MISSING_TC_IDENTITY",
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
_TC_ACCEPT = [c for c in _MANIFEST["accept"] if c.get("theme") == "TC" and c.get("product") == "SIGMET"]
_TC_INFO = list(_MANIFEST.get("tc_modifier_info", []))
_TC_ERRORS = list(_MANIFEST.get("tc_errors", []))


def test_tc_manifest_sections_present() -> None:
    assert len(_TC_ACCEPT) >= 3
    assert {c["product"] for c in _TC_ACCEPT} == {"SIGMET"}
    assert {c["id"] for c in _TC_ACCEPT} >= {
        "accept_sigmet_tc_a6_2",
        "accept_sigmet_tc_cnl",
        "accept_sigmet_tc_stnr",
    }
    assert len(_TC_INFO) >= 5
    assert len(_TC_ERRORS) >= 2
    for case in _TC_ACCEPT + _TC_INFO + _TC_ERRORS:
        assert (_read_tac(case["tac"])).strip()
    codes = {c["expected_codes"][0] for c in _TC_INFO}
    assert codes == _INFO_CODES
    for case in _TC_ERRORS:
        assert case["expected_codes"][0] in _ERROR_CODES


@pytest.mark.parametrize("case", _TC_ACCEPT, ids=_case_ids(_TC_ACCEPT))
def test_tc_accept_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.severity == "error" for i in report.issues)


@pytest.mark.parametrize("case", _TC_INFO, ids=_case_ids(_TC_INFO))
def test_tc_modifier_emits_info(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    matched = [i for i in report.issues if i.code == code]
    assert matched, f"expected info code {code}; got {[i.code for i in report.issues]}"
    assert all(i.severity == "info" for i in matched)
    assert by_code(code).severity == "info"
    if case.get("require_spans"):
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)


@pytest.mark.parametrize("case", _TC_ERRORS, ids=_case_ids(_TC_ERRORS))
def test_tc_invalid_emits_error(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is False
    codes = {i.code for i in report.issues if i.severity == "error"}
    assert code in codes
    assert by_code(code).severity == "error"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code == code]
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)


def test_tc_a6_2_allows_six_hour_validity() -> None:
    """WC/TC family uses 6h max validity (G2 is_tc); A6-2-TC is 251600/252200."""
    report = lint(_read_tac("accept/sigmet_tc_a6_2.tac"), product="SIGMET")
    assert report.ok is True
    assert not any(i.code == "INVALID_VALIDITY_DURATION" for i in report.issues)


def test_tc_stnr_in_scope_and_geometry_oos_documented() -> None:
    """T2.3 / S02.M2 — STNR covered on TC bodies; exceptional geometry OOS with cite."""
    oos_note = (
        Path(__file__).resolve().parents[3]
        / "docs"
        / "sessions"
        / "S037-quality-residuals-831"
        / "reports"
        / "t2.3-tc-geometry-oos.md"
    )
    assert oos_note.is_file(), f"missing OOS cite note: {oos_note}"
    text = oos_note.read_text(encoding="utf-8")
    assert "D-S037-T2.3-oos" in text
    assert "#797" in text
    assert "WI … OF TC CENTRE" in text or "WI ... OF TC CENTRE" in text or "OF TC CENTRE" in text

    # STNR accept + STNR+MOV negative remain in the TC pack (not deferred).
    stnr_ids = {c["id"] for c in _TC_INFO + _TC_ERRORS}
    assert "sigmet_tc_stnr_info" in stnr_ids
    assert "sigmet_tc_stnr_with_mov" in {c["id"] for c in _TC_ERRORS}

    stnr = lint(_read_tac("accept/sigmet_tc_stnr.tac"), product="SIGMET")
    assert stnr.ok is True
    assert any(i.code == "STNR_MOVEMENT" for i in stnr.issues)

    bad = lint(_read_tac("negative/sigmet/tc_stnr_with_mov.tac"), product="SIGMET")
    assert bad.ok is False
    assert any(i.code == "INVALID_STNR_MOVEMENT" for i in bad.issues)
