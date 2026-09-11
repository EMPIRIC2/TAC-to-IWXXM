"""TC-EV-verify-005 — operator-facing registry templates lack research tokens."""

from __future__ import annotations

import re

from tac_validate.issue_registry import ISSUES
from tac_validate.product_rules_pkg._common import _strip_research_refs

_RESEARCH = re.compile(
    r"research\s+[A-Za-z]?\d+",
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
