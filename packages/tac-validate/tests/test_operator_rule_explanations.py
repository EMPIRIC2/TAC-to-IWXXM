"""Naturalistic operator rule explanations (registry templates + formatting).

Covers evolve-auto test-matrix dimensions: success, mutation, failure, and
validation permutations for message templates and ``format_operator_message``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tac_validate.issue_registry import (
    ISSUES,
    IssueSpec,
    by_code,
    format_operator_message,
    issue_from,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CATALOG_JSON = _REPO_ROOT / "config" / "rules" / "ISSUE_CATALOG.json"

_BOILERPLATE = (
    "Informational:",
    "noted for operator awareness",
    "does not by itself block conversion",
    "Full normative text may require purchase",
    "profile awareness",
    "Error: the TAC does not meet a required format",
)


@pytest.mark.parametrize(
    ("code", "product", "needle"),
    [
        ("AMD_PRESENT", "TAF", "amendment (AMD)"),
        ("COR_PRESENT", "METAR", "correction (COR)"),
        ("CAVOK_PRESENT", "SPECI", "CAVOK"),
        ("SIGMET_CNL", "SIGMET", "cancel (CNL)"),
        ("AUTO_PRESENT", "METAR", "automatic station"),
    ],
)
def test_sample_issues_render_naturalistic_text(code: str, product: str, needle: str) -> None:
    """Success: sample issues render plain STE text without raw braces."""
    issue = issue_from(code, product=product)
    assert "{" not in issue.message
    assert "}" not in issue.message
    assert needle in issue.message
    assert "Informational:" not in issue.message
    assert issue.severity == by_code(code).severity


def test_amd_present_example_before_after_shape() -> None:
    """Success: AMD follows what-it-means + conversion-can-continue pattern."""
    msg = issue_from("AMD_PRESENT", product="TAF").message
    assert msg == "This TAF is an amendment (AMD). Conversion can continue."


@pytest.mark.parametrize("spec", ISSUES, ids=lambda s: s.code)
def test_every_registry_message_is_operator_plain(spec: IssueSpec) -> None:
    """Validation success: full catalog rows are free of stiff boilerplate."""
    template = spec.message_template
    assert isinstance(template, str)
    assert template.strip()
    for phrase in _BOILERPLATE:
        assert phrase not in template, (spec.code, phrase)
    rendered = format_operator_message(
        template,
        product=spec.product or "METAR",
        token="XX",
        expected="METAR, TAF",
        keywords="TAF",
        hit="TS",
        family="weather",
    )
    assert "{product" not in rendered
    assert "{token" not in rendered


def test_unknown_code_fails_closed() -> None:
    """Failure: unknown registry code raises KeyError."""
    with pytest.raises(KeyError, match="unknown lint issue code"):
        issue_from("NOT_A_REAL_ISSUE_CODE_XYZ")


def test_format_missing_keys_falls_back_without_braces() -> None:
    """Failure / validation: missing kwargs use defaults; no raw braces."""
    text = format_operator_message("This {product} saw {token!r} in {family}.")
    assert "{" not in text
    assert "report" in text
    assert "token" in text
    assert "register" in text


def test_format_unknown_placeholder_omits_braces() -> None:
    """Failure: unknown placeholder names are omitted, not shown as braces."""
    text = format_operator_message("Keep {product} drop {no_such_field}.")
    assert "{" not in text
    assert "report" in text
    assert "no_such_field" not in text


def test_catalog_json_mutation_reflects_amd_wording() -> None:
    """Mutation (update): regenerated ISSUE_CATALOG carries AMD wording."""
    assert _CATALOG_JSON.is_file(), "run make catalog-regen"
    payload = json.loads(_CATALOG_JSON.read_text(encoding="utf-8"))
    rows = payload["issues"]
    amd = next(row for row in rows if row["code"] == "AMD_PRESENT")
    assert "amendment (AMD)" in amd["message_template"]
    assert "Informational:" not in amd["message_template"]
    assert amd["severity"] == "info"


def test_info_severity_wording_does_not_claim_blocking() -> None:
    """Validation: info rows do not claim a hard conversion block."""
    for spec in ISSUES:
        if spec.severity != "info":
            continue
        lower = spec.message_template.lower()
        assert "must be corrected" not in lower
        assert "blocks conversion" not in lower


@pytest.mark.parametrize(
    ("code", "product", "severity"),
    [
        ("AMD_PRESENT", "TAF", "info"),
        ("INVALID_NIL", "METAR", "error"),
        ("PARTIAL_DECODE", "SPECI", "warning"),
        ("CAVOK_PRESENT", "TAF", "info"),
        ("MISSING_CCCC", "SIGMET", "error"),
    ],
)
def test_permute_codes_products_severities(code: str, product: str, severity: str) -> None:
    """Permute several codes x products x severities."""
    issue = issue_from(code, product=product)
    assert issue.severity == severity
    assert issue.code == code
    assert "{" not in issue.message
    template = by_code(code).message_template
    if "{product}" in template:
        assert product in issue.message


@pytest.mark.parametrize(
    ("template", "kwargs", "needle", "forbidden"),
    [
        # Create + validation pass: build operator text from a template.
        (
            "This {product} is an amendment (AMD). Conversion can continue.",
            {"product": "TAF"},
            "This TAF is an amendment (AMD)",
            "{",
        ),
        # Update + validation pass: override default product label.
        (
            "This {product} includes CAVOK. Conversion can continue.",
            {"product": "speci"},
            "This SPECI includes CAVOK",
            "{product}",
        ),
        # Create + validation fail surface: blank product falls back (still valid output).
        (
            "This {product} includes CAVOK. Conversion can continue.",
            {"product": ""},
            "This report includes CAVOK",
            "{",
        ),
        # Delete + allowed: unknown field removed from rendered text.
        (
            "Keep {product} drop {orphan}.",
            {"product": "METAR"},
            "Keep METAR drop ",
            "orphan",
        ),
    ],
)
def test_format_mutation_validation_permutations(
    template: str,
    kwargs: dict[str, str],
    needle: str,
    forbidden: str,
) -> None:
    """Mutation × validation permutations for ``format_operator_message``."""
    text = format_operator_message(template, **kwargs)
    assert needle in text
    assert forbidden not in text


def test_format_delete_rejected_keeps_known_defaults() -> None:
    """Delete + rejected: stripping known defaults is not allowed (fallback stays)."""
    text = format_operator_message("Need a {product} label.")
    assert text == "Need a report label."


def test_issue_from_message_override_is_update_success() -> None:
    """Update + validation pass: explicit message override replaces template."""
    issue = issue_from(
        "AMD_PRESENT",
        product="TAF",
        message="Custom AMD note for operators.",
    )
    assert issue.message == "Custom AMD note for operators."
    assert issue.code == "AMD_PRESENT"


def test_issue_from_message_override_rejects_blank_as_keep_template() -> None:
    """Update + validation fail path: blank override does not wipe template."""
    issue = issue_from("AMD_PRESENT", product="TAF", message="")
    # Empty string is falsy → registry keeps formatted template.
    assert "amendment (AMD)" in issue.message
