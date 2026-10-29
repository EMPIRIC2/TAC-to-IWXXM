"""TC-EV-verify-005 — operator-facing registry templates lack research tokens."""

from __future__ import annotations

import re
from pathlib import Path

from tac_validate import lint
from tac_validate.issue_registry import ISSUES
from tac_validate.product_rules_pkg._common import _strip_research_refs

_FIXTURES = Path(__file__).resolve().parent / "fixtures"

_RESEARCH = re.compile(
    r"research\s+[A-Za-z]?\d+",
    re.IGNORECASE,
)
_PLANNING_TAG = re.compile(r"^(?:ev\d+|[a-z]{1,2}\d+)$", re.IGNORECASE)
_PLANNING_IN_MESSAGE = re.compile(
    r"(?:\bEV-\d+\b|\bTC-[A-Z0-9-]+\b|(?<!\w)#\d{3,}\b|\bF\d+\b|\btheme\s+[A-Za-z]{0,2}\d+\b|\bUJ-\d+\b)",
    re.IGNORECASE,
)


def test_registry_message_templates_have_no_research_tokens() -> None:
    leaks = [f"{spec.code}: {spec.message_template}" for spec in ISSUES if _RESEARCH.search(spec.message_template)]
    assert leaks == [], "\n".join(leaks)


def test_strip_research_refs_cleans_templates_that_would_leak() -> None:
    dirty = "METAR CAVOK present - research T3 / S1"
    assert _RESEARCH.search(dirty)
    cleaned = _strip_research_refs(dirty)
    assert not _RESEARCH.search(cleaned)
    assert "CAVOK" in cleaned


def test_registry_tags_omit_compact_evolve_ids() -> None:
    leaks = [f"{spec.code}: {tag}" for spec in ISSUES for tag in spec.tags if _PLANNING_TAG.fullmatch(tag)]
    assert leaks == [], "\n".join(leaks)


def test_tc_sigmet_operator_messages_omit_planning_ids() -> None:
    tac = (_FIXTURES / "negative/sigmet/tc_missing_identity.tac").read_text(encoding="utf-8")
    report = lint(tac, product="SIGMET")
    matched = [i for i in report.issues if i.code == "MISSING_TC_IDENTITY"]
    assert matched, f"expected MISSING_TC_IDENTITY; got {[i.code for i in report.issues]}"
    leaks = [f"{issue.code}: {issue.message}" for issue in matched if _PLANNING_IN_MESSAGE.search(issue.message)]
    assert leaks == [], "\n".join(leaks)
