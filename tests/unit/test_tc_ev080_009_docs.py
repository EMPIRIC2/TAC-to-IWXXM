"""TC-EV080-009 — standing docs + ADR-007 cite 100% coverage gate.

[Corpus: tests] [Corpus: adr/ADR-007] [Corpus: tech-spec] EV-080 / #1077
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

ADR = ROOT / "docs" / "adr" / "ADR-007-universal-coverage-gate.md"
TYPING = ROOT / "docs" / "typing-policy.md"
TEST_PLAN = ROOT / "docs" / "test-plan.md"


@pytest.mark.unit
class TestTcEv080StandingDocs:
    """AC6 / TC-EV080-009 — docs greppable for 100% gate."""

    def test_adr_007_title_and_floor(self) -> None:
        text = ADR.read_text(encoding="utf-8")
        assert "100%" in text
        assert "Universal 100% Coverage Gate" in text
        assert "fail_under = 100" in text or "fail_under **100**" in text

    def test_typing_policy_coverage_section(self) -> None:
        text = TYPING.read_text(encoding="utf-8")
        assert "**100%** line and branch" in text
        assert "fail_under = 100" in text
        assert "scripts/**/*.py" in text or "scripts/**/*.sh" in text

    def test_test_plan_metrics_and_tc_block(self) -> None:
        text = TEST_PLAN.read_text(encoding="utf-8")
        assert "**100%** line+branch" in text
        assert "TC-EV080-009" in text
        assert "ADR-007" in text
