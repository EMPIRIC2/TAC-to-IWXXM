"""TC-F10-002 §1–2 — MISSING_TERMINATOR is info-level with add_terminator fix (S013 / EV-009).

Spec: docs/test-plan.md TC-F10-002; ADR-025 §2; api-contract §lint-tac.
``ok`` stays keyed to error-severity only — an otherwise-clean single report without
``=`` must lint ``ok: true``.
"""

from __future__ import annotations

from tac_validate import lint

CLEAN_NO_EQ = "METAR KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034"
EXPECTED_COPY = "Reports in bulletins end with '=' — add it before publishing"


def test_missing_terminator_severity_info() -> None:
    report = lint(CLEAN_NO_EQ, product="METAR")
    term = next(i for i in report.issues if i.code == "MISSING_TERMINATOR")
    assert term.severity == "info"
    assert term.message == EXPECTED_COPY


def test_missing_terminator_ok_true_when_otherwise_clean() -> None:
    report = lint(CLEAN_NO_EQ, product="METAR")
    assert report.ok is True
    assert all(i.severity != "error" for i in report.issues)
    assert any(i.code == "MISSING_TERMINATOR" for i in report.issues)


def test_add_terminator_fix_appends_equals() -> None:
    report = lint(CLEAN_NO_EQ, product="METAR")
    fix = next(f for f in report.fixes if f.code == "add_terminator")
    assert fix.replacement == CLEAN_NO_EQ.rstrip() + "="
    assert "=" in fix.message or "terminator" in fix.message.lower() or "Add" in fix.message


def test_clean_report_with_equals_has_no_terminator_issue() -> None:
    report = lint(CLEAN_NO_EQ + "=", product="METAR")
    assert report.ok is True
    assert not any(i.code == "MISSING_TERMINATOR" for i in report.issues)


def test_taf_and_speci_same_info_semantics() -> None:
    for product, tac in (
        ("TAF", "TAF KJFK 101730Z 1018/1124 24008KT"),
        ("SPECI", "SPECI KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034"),
    ):
        report = lint(tac, product=product)
        term = next(i for i in report.issues if i.code == "MISSING_TERMINATOR")
        assert term.severity == "info"
        assert report.ok is True
        fix = next(f for f in report.fixes if f.code == "add_terminator")
        assert fix.replacement.endswith("=")
