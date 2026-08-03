"""F29 / #831 quality-matrix runners (EV-030 T1.2).

Thin wrappers over ``tac_validate.lint``, ``tac2iwxxm.convert``, and
``iwxxm_validate.validate`` with shared ``needs-fixture`` / ``oos`` skip policy.
"""

from __future__ import annotations

from typing import Any, cast

import pytest
from iwxxm_validate import validate as validate_iwxxm
from tac_validate import lint as lint_tac
from tests.quality_matrices.loaders import RuleCase

from tac2iwxxm import convert as convert_tac

_DEFAULT_IWXXM_VERSION = "2025-2"
_DEFAULT_PROFILE = "annex3"


def apply_skip_policy(case: RuleCase) -> None:
    """Skip ``needs-fixture`` / ``oos`` cases with a cite in the skip message.

    Inventory gate (T1.6) still treats these slots as explicit — not silent gaps.
    """
    if case.status == "needs-fixture":
        reason = _meta_str(case.meta, "reason") or "needs-fixture"
        pytest.skip(f"{case.node_id}: needs-fixture — {reason}")
    if case.status == "oos":
        cite = (
            _meta_str(case.meta, "cite")
            or _meta_str(case.meta, "oos_cite")
            or _meta_str(case.meta, "reason")
            or "oos"
        )
        pytest.skip(f"{case.node_id}: oos — {cite}")


def run_rule_case(case: RuleCase) -> None:
    """Dispatch one RuleCase to the engine runner (after skip policy)."""
    apply_skip_policy(case)
    if case.engine == "lint":
        run_lint_case(case)
    elif case.engine == "convert":
        run_convert_case(case)
    elif case.engine == "validate":
        run_validate_case(case)
    else:  # pragma: no cover — loaders already narrow engine
        raise ValueError(f"unknown engine {case.engine!r}")


def run_lint_case(case: RuleCase) -> None:
    """Execute a lint RuleCase (``ready`` only — call after skip policy)."""
    apply_skip_policy(case)
    tac = _require_tac(case)
    product = _meta_str(case.meta, "product") or "METAR"
    report = lint_tac(tac, product=product)
    _assert_lint_expect(case, report)


def run_convert_case(case: RuleCase) -> None:
    """Execute a convert RuleCase."""
    apply_skip_policy(case)
    tac = _require_tac(case)
    product = _meta_str(case.meta, "product") or "METAR"
    profile = _meta_str(case.meta, "profile") or _DEFAULT_PROFILE
    iwxxm_version = _meta_str(case.meta, "iwxxm_version") or _DEFAULT_IWXXM_VERSION
    result = convert_tac(
        tac,
        product=product,
        profile=profile,
        iwxxm_version=iwxxm_version,
    )
    _assert_convert_expect(case, result)


def run_validate_case(case: RuleCase) -> None:
    """Execute a validate RuleCase.

    Prefer ``meta.xml`` / ``expect.xml`` when present; otherwise convert ``tac``
    first (METAR/SPECI pilot default).
    """
    apply_skip_policy(case)
    product = _meta_str(case.meta, "product") or "METAR"
    profile = _meta_str(case.meta, "profile") or _DEFAULT_PROFILE
    iwxxm_version = _meta_str(case.meta, "iwxxm_version") or _DEFAULT_IWXXM_VERSION
    xml = _xml_payload(case)
    if xml is None:
        tac = _require_tac(case)
        converted = convert_tac(
            tac,
            product=product,
            profile=profile,
            iwxxm_version=iwxxm_version,
        )
        if not converted.ok or not converted.xml:
            codes = [i.code for i in converted.issues]
            pytest.fail(f"{case.node_id}: convert failed before validate ({codes})")
        xml = converted.xml
    report = validate_iwxxm(xml, iwxxm_version=iwxxm_version, profile=profile)
    _assert_validate_expect(case, report)


def _meta_str(meta: dict[str, Any], key: str) -> str | None:
    value = meta.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _require_tac(case: RuleCase) -> str:
    if not isinstance(case.tac, str) or not case.tac.strip():
        raise AssertionError(f"{case.node_id}: ready case missing tac")
    return case.tac


def _xml_payload(case: RuleCase) -> str | None:
    for source in (case.meta, case.expect):
        value = source.get("xml")
        if isinstance(value, str) and value.strip():
            return value
    return None


def _issue_codes(issues: list[Any]) -> set[str]:
    return {str(i.code) for i in issues}


def _as_str_list(value: object, *, case: RuleCase, field_name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise AssertionError(
            f"{case.node_id}: expect.{field_name} must be a non-empty list"
        )
    raw_items = cast(list[object], value)
    return [str(item) for item in raw_items]


def _assert_codes_present(case: RuleCase, codes: set[str], expected: list[str]) -> None:
    missing = [code for code in expected if code not in codes]
    assert not missing, f"{case.node_id}: missing codes {missing}; got {sorted(codes)}"


def _assert_lint_expect(case: RuleCase, report: Any) -> None:
    expect = case.expect
    if "accept" in expect:
        assert report.ok is bool(expect["accept"]), (
            f"{case.node_id}: lint ok={report.ok} expected accept={expect['accept']}"
        )
    if "codes" in expect:
        wanted = _as_str_list(expect["codes"], case=case, field_name="codes")
        _assert_codes_present(case, _issue_codes(report.issues), wanted)
    if "ok" in expect:
        assert report.ok is bool(expect["ok"]), (
            f"{case.node_id}: lint ok={report.ok} expected {expect['ok']}"
        )


def _assert_convert_expect(case: RuleCase, result: Any) -> None:
    expect = case.expect
    encode_ok = expect.get("encode_ok", expect.get("ok"))
    if encode_ok is not None:
        assert result.ok is bool(encode_ok), (
            f"{case.node_id}: convert ok={result.ok} expected {encode_ok}"
        )
    if "codes" in expect:
        wanted = _as_str_list(expect["codes"], case=case, field_name="codes")
        _assert_codes_present(case, _issue_codes(result.issues), wanted)
    if expect.get("require_xml") and result.ok:
        assert isinstance(result.xml, str) and result.xml.strip(), (
            f"{case.node_id}: convert expected non-empty xml"
        )


def _assert_validate_expect(case: RuleCase, report: Any) -> None:
    expect = case.expect
    codes = _issue_codes(report.issues)
    if "sch_ids" in expect:
        sch_ids = _as_str_list(expect["sch_ids"], case=case, field_name="sch_ids")
        if "SCHEMATRON_SKIPPED" in codes and not any(sid in codes for sid in sch_ids):
            pytest.skip(
                f"{case.node_id}: Schematron xslt2 skipped on lxml path "
                f"(want {sch_ids}); use native iwxxm-validate or fixture XML"
            )
        _assert_codes_present(case, codes, sch_ids)
    if "codes" in expect:
        wanted = _as_str_list(expect["codes"], case=case, field_name="codes")
        _assert_codes_present(case, codes, wanted)
    if "ok" in expect:
        assert report.ok is bool(expect["ok"]), (
            f"{case.node_id}: validate ok={report.ok} expected {expect['ok']}"
        )
    if "accept" in expect:
        assert report.ok is bool(expect["accept"]), (
            f"{case.node_id}: validate ok={report.ok} expected accept={expect['accept']}"
        )
