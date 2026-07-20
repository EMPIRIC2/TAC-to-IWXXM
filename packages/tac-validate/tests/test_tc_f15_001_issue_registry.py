"""TC-F15-001 — issue registry API (S015 / EV-011, F15 / ADR-028).

Contract for ``tac_validate.issue_registry``:

* frozen ``IssueSpec`` rows (code, severity, message_template, optional product/tags)
* ``ISSUES`` sequence + ``by_code`` / ``issue_from`` helpers
* unknown codes rejected (KeyError)

T1.1 is red until T1.2 lands the module and seeds existing emitted codes.
"""

from __future__ import annotations

import re

import msgspec
import pytest

_SCREAMING_SNAKE = re.compile(r"^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$")
_SEVERITIES = frozenset({"error", "warning", "info"})

# Codes already emitted by rules.py / product_rules.py — must be registered in T1.2.
_EXISTING_EMITTED_CODES = frozenset(
    {
        "UNKNOWN_PRODUCT",
        "EMPTY_TAC",
        "MISSING_PRODUCT_KEYWORD",
        "MISSING_TERMINATOR",
        "MISSING_CCCC",
        "MISSING_OBS_TIME",
        "MISSING_WIND",
        "MISSING_VISIBILITY",
        "MISSING_TEMP_DEWPOINT",
        "MISSING_QNH",
        "INVALID_CLOUD_TOKEN",
        "MISSING_ISSUE_TIME",
        "MISSING_VALIDITY",
        "INVALID_CNL_SHAPE",
        "MISSING_VALID",
        "MULTIPLE_PHENOMENA",
        "MISSING_DTG",
        "MISSING_VAAC",
        "MISSING_MAX_WIND",
    }
)


def test_issue_spec_is_frozen_msgspec_struct() -> None:
    from tac_validate.issue_registry import IssueSpec

    assert issubclass(IssueSpec, msgspec.Struct)
    spec = IssueSpec(
        code="EMPTY_TAC",
        severity="error",
        message_template="TAC text is empty",
    )
    assert spec.code == "EMPTY_TAC"
    assert spec.severity == "error"
    assert spec.message_template == "TAC text is empty"
    assert spec.product is None
    assert tuple(spec.tags) == ()
    with pytest.raises(AttributeError):
        spec.code = "OTHER"  # type: ignore[misc]


def test_issues_sequence_nonempty_and_unique_codes() -> None:
    from tac_validate.issue_registry import ISSUES

    assert len(ISSUES) >= 1
    codes = [spec.code for spec in ISSUES]
    assert len(codes) == len(set(codes))


def test_by_code_returns_registered_spec() -> None:
    from tac_validate.issue_registry import ISSUES, by_code

    first = ISSUES[0]
    found = by_code(first.code)
    assert found is first or found == first
    assert found.code == first.code
    assert found.severity == first.severity


def test_by_code_rejects_unknown_code() -> None:
    from tac_validate.issue_registry import by_code

    with pytest.raises(KeyError):
        by_code("NOT_A_REAL_ISSUE_CODE_XYZ")


def test_issue_from_builds_issue_from_registry() -> None:
    from tac_validate.issue_registry import by_code, issue_from
    from tac_validate.models import Issue

    spec = by_code("MISSING_TERMINATOR")
    issue = issue_from(
        "MISSING_TERMINATOR",
        location="terminator",
        start=10,
        end=11,
    )
    assert isinstance(issue, Issue)
    assert issue.code == "MISSING_TERMINATOR"
    assert issue.severity == spec.severity
    assert issue.message == spec.message_template
    assert issue.location == "terminator"
    assert issue.start == 10
    assert issue.end == 11


def test_issue_from_formats_message_template() -> None:
    from tac_validate.issue_registry import issue_from

    issue = issue_from("MISSING_CCCC", product="METAR")
    assert "METAR" in issue.message
    assert issue.severity == "error"
    assert issue.code == "MISSING_CCCC"


def test_issue_from_message_override() -> None:
    from tac_validate.issue_registry import issue_from

    issue = issue_from("EMPTY_TAC", message="custom empty note")
    assert issue.message == "custom empty note"
    assert issue.severity == "error"


def test_issue_from_rejects_unknown_code() -> None:
    from tac_validate.issue_registry import issue_from

    with pytest.raises(KeyError):
        issue_from("NOT_A_REAL_ISSUE_CODE_XYZ")


def test_all_existing_emitted_codes_are_registered() -> None:
    from tac_validate.issue_registry import by_code

    missing = sorted(code for code in _EXISTING_EMITTED_CODES if _missing(code, by_code))
    assert missing == [], f"emitted codes missing from registry: {missing}"


def test_registry_rows_use_screaming_snake_and_valid_severity() -> None:
    from tac_validate.issue_registry import ISSUES

    for spec in ISSUES:
        assert _SCREAMING_SNAKE.fullmatch(spec.code), spec.code
        assert spec.severity in _SEVERITIES, (spec.code, spec.severity)
        assert isinstance(spec.message_template, str) and spec.message_template
        if spec.product is not None:
            assert isinstance(spec.product, str)
        assert all(isinstance(t, str) for t in spec.tags)


def test_missing_terminator_default_severity_is_info() -> None:
    """ADR-025 / ADR-028 — MISSING_TERMINATOR remains info."""
    from tac_validate.issue_registry import by_code

    assert by_code("MISSING_TERMINATOR").severity == "info"


def test_catalog_entries_returns_full_registry_when_unfiltered() -> None:
    from tac_validate.issue_registry import ISSUES, catalog_entries

    assert catalog_entries() is ISSUES
    assert catalog_entries(product=None) is ISSUES
    assert catalog_entries(product="  ") is ISSUES


def test_catalog_entries_filters_by_product_tag_or_field() -> None:
    from tac_validate.issue_registry import catalog_entries

    metar_codes = {spec.code for spec in catalog_entries(product="METAR")}
    assert "MISSING_OBS_TIME" in metar_codes
    assert "MISSING_TERMINATOR" in metar_codes
    assert "MISSING_VALIDITY" not in metar_codes

    taf_codes = {spec.code for spec in catalog_entries(product="taf")}
    assert "MISSING_VALIDITY" in taf_codes
    assert "MISSING_OBS_TIME" not in taf_codes


def _missing(code: str, by_code: object) -> bool:
    try:
        by_code(code)  # type: ignore[operator]
    except KeyError:
        return True
    return False
